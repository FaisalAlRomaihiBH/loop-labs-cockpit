"""Agent runner. Step 3: real context loading for the CEO agent.

Sessions are continuous conversations: one ClaudeSDKClient per cockpit
session, connected on the first turn with the full loaded context and kept
open, so later turns continue the same conversation without resending it.
The persistent connection is also what lets the can_use_tool permission
callback answer the CLI's requests — a one-shot query() closes the control
channel before the first tool call arrives.
"""

import asyncio
import contextvars
import json
import logging
import time
from datetime import date
from pathlib import Path
from typing import AsyncIterator, Awaitable, Callable

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    create_sdk_mcp_server,
    tool,
)
from claude_agent_sdk.types import (
    AssistantMessage,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    StreamEvent,
    ToolPermissionContext,
    ToolUseBlock,
)

from . import config, db

logger = logging.getLogger("cockpit.agents")

# The run id of whichever run is executing in the current async task. Read by
# the path guard (to attribute denied-tool warnings to the right run) and by
# anything else in this module that needs to log against the live run without
# threading run_id through every call.
_current_run_id: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "run_id", default=None
)

# The API key lives outside the repo, one directory above the loop-labs
# workspace root: C:\loop-labs\.cockpit-env.txt
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".cockpit-env.txt"

# Cockpit session id -> live SDK client holding that session's conversation.
_clients: dict[int, ClaudeSDKClient] = {}

# Strong refs to in-flight assign_task background tasks. The event loop only
# holds weak references to tasks; without this an assigned run's task could
# be garbage-collected mid-run.
_assigned_tasks: set[asyncio.Task] = set()


class _Killed(Exception):
    """Raised internally when the kill switch trips mid-run, so the run's
    try/except can route to a "killed" finish rather than "failed"."""

# Headings for config.CEO_STATIC_DOCS, in the same order.
_STATIC_HEADINGS = [
    "# Consolidated Specification",
    "# Technical Specification & Implementation Plan",
]


def _load_api_key() -> str:
    """Read ANTHROPIC_API_KEY out of the env file outside the repo.

    Never logs or prints the key value.
    """
    if not _ENV_FILE.exists():
        raise RuntimeError(
            f"API key file not found at {_ENV_FILE}. Create it with a line "
            "like ANTHROPIC_API_KEY=sk-ant-... before running the agent."
        )

    text = _ENV_FILE.read_text(encoding="utf-8")

    fallback: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            if key.startswith("export "):
                key = key[len("export ") :].strip()
            value = value.strip().strip("'\"")
            if key == "ANTHROPIC_API_KEY":
                return value
        elif " " not in line:
            # Bare token with no "key=value" shape; remember as a fallback.
            fallback = line

    if fallback:
        return fallback

    raise RuntimeError(
        f"No ANTHROPIC_API_KEY found in {_ENV_FILE}. Add a line like "
        "ANTHROPIC_API_KEY=sk-ant-... to that file."
    )


def _read(path: Path) -> str:
    """Read a context file, raising a clear error if it is missing.

    Every document referenced here is seeded as part of the company/ setup,
    so a missing file means the setup is broken, not that the file is
    optionally absent.
    """
    if not path.exists():
        raise RuntimeError(f"missing context file: {path}")
    return path.read_text(encoding="utf-8")


def _founder_label(founder: str) -> str:
    name = config.FOUNDERS.get(founder, "")
    return f"Founder {founder} — {name}" if name else f"Founder {founder}"


def _system_prompt() -> str:
    """Identity and rules only: the constitution plus the CEO's brief."""
    constitution = _read(config.CONSTITUTION)
    brief = _read(config.CEO_BRIEF)
    return f"{constitution}\n\n{brief}"


def _first_user_message(founder: str, content: str, session_id: int) -> str:
    """Static docs first (for caching), then volatile docs, then the message.

    If the session already has message history (the cockpit restarted and the
    live SDK conversation was lost), replay it so continuity survives — the
    session model promises context persists for the whole conversation.
    """
    parts: list[str] = []

    for path, heading in zip(config.CEO_STATIC_DOCS, _STATIC_HEADINGS):
        parts.append(f"{heading}\n\n{_read(path)}")

    if not config.CHARTER_READ_FLAG.exists():
        parts.append(f"# Charter (founding context)\n\n{_read(config.CHARTER)}")

    for path, heading in config.CEO_VOLATILE_DOCS:
        parts.append(f"# {heading}\n\n{_read(path)}")

    # Everything before the message just persisted by the caller is prior
    # conversation from before a cockpit restart.
    history = db.list_messages(session_id)[:-1]
    if history:
        lines = []
        for m in history:
            speaker = (
                f"[{_founder_label(m['founder'])}]" if m["role"] == "founder"
                else "[You — the CEO]" if m["role"] == "agent"
                else "[system]"
            )
            lines.append(f"{speaker}\n{m['content']}")
        parts.append(
            "# This Session So Far\n\n"
            "The cockpit restarted mid-session; this is the conversation so "
            "far, replayed verbatim. Continue it — do not start over.\n\n"
            + "\n\n---\n\n".join(lines)
        )

    parts.append(f"# Founder Message\n\n[{_founder_label(founder)}] {content}")

    return "\n\n".join(parts)


def make_path_guard(
    write_paths: list[Path], allow_tool_prefixes: tuple[str, ...] = ()
) -> Callable[[str, dict, ToolPermissionContext], Awaitable[
    PermissionResultAllow | PermissionResultDeny
]]:
    """Build a can_use_tool callback scoped to one agent's write paths.

    Allow a tool call only when its path argument resolves under an allowed
    root. This is the actual enforcement layer — tools=[...] only restricts
    which tools exist at all, not where they may look.

    Reads may range across the allowed roots; writes are confined to
    `write_paths`, which differ per agent (the CEO's memory and two company
    files; an assigned agent's own brief directory and the reports dir).

    `allow_tool_prefixes` lets MCP tools (e.g. "mcp__cockpit__assign_task")
    through with no path check at all — they take no file-path argument in
    the Read/Write sense, so the check below does not apply to them.
    """

    async def _guard(
        tool_name: str,
        tool_input: dict,
        context: ToolPermissionContext,
    ):
        if allow_tool_prefixes and tool_name.startswith(allow_tool_prefixes):
            return PermissionResultAllow()

        raw_path = (
            tool_input.get("file_path")
            or tool_input.get("path")
            or str(config.REPO_ROOT)
        )
        resolved = Path(raw_path).resolve()

        if tool_name == "Write":
            for allowed in write_paths:
                if resolved == allowed or resolved.is_relative_to(allowed):
                    return PermissionResultAllow()
            _log_denied(tool_name, resolved)
            return PermissionResultDeny(
                message=f"write outside the agent's owned paths: {resolved}"
            )

        for root in config.ALLOWED_PATHS:
            if resolved.is_relative_to(root):
                return PermissionResultAllow()

        _log_denied(tool_name, resolved)
        return PermissionResultDeny(message=f"path outside allowed roots: {resolved}")

    return _guard


def _log_denied(tool_name: str, resolved: Path) -> None:
    """Record a denied tool call against the currently-running run, if any.
    The permission callback runs in the same task context as run_ceo_turn, so
    the contextvar it set is visible here."""
    run_id = _current_run_id.get()
    if run_id is not None:
        db.add_run_log(run_id, "warning", f"denied {tool_name}: {resolved}")


def _short_input(tool_input: dict) -> str:
    for key in ("file_path", "pattern", "path"):
        if key in tool_input:
            value = str(tool_input[key])
            return value if len(value) <= 80 else value[:77] + "..."
    return ""


def _log_tool_blocks(run_id: int, message: AssistantMessage) -> list[str]:
    """Record run_log rows for every tool-use block in an assistant message:
    a tool_call row always, plus a file_read/file_write row for Read/Write
    calls specifically. Shared by run_ceo_turn and run_assigned_task so the
    two runners log identically.

    Returns the per-block descriptions, in order, for callers (run_ceo_turn)
    that also stream them to a page.
    """
    descriptions: list[str] = []
    for block in message.content:
        if isinstance(block, ToolUseBlock):
            short_input = _short_input(block.input)
            desc = f"{block.name}: {short_input}" if short_input else block.name
            db.add_run_log(run_id, "tool_call", desc)
            if block.name == "Read":
                path = block.input.get("file_path") or block.input.get("path")
                if path:
                    db.add_run_log(run_id, "file_read", str(path))
            elif block.name == "Write":
                path = block.input.get("file_path") or block.input.get("path")
                if path:
                    db.add_run_log(run_id, "file_write", str(path))
            descriptions.append(desc)
    return descriptions


def _agent_env() -> dict[str, str]:
    return {
        "ANTHROPIC_API_KEY": _load_api_key(),
        # Pin the endpoint so an inherited ANTHROPIC_BASE_URL from the
        # launching shell can never redirect agent traffic elsewhere.
        "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
    }


def _available_agent_names() -> list[str]:
    return sorted(p.parent.name for p in config.AGENTS_DIR.glob("*/brief.md"))


@tool(
    "assign_task",
    "Assign a task to another agent. Asynchronous: returns a run id immediately; "
    "the assigned agent runs separately and writes its report to company/reports/, "
    "which you read in a later session. The agent must have a brief at "
    "company/agents/<name>/brief.md.",
    {"agent": str, "task": str},
)
async def _assign_task_tool(args: dict) -> dict:
    agent = args["agent"].strip().lower()
    task = args["task"]

    if agent == "ceo":
        return {
            "content": [{"type": "text", "text": "the CEO is not assignable"}],
            "is_error": True,
        }

    if not config.agent_exists(agent):
        available = _available_agent_names()
        listing = ", ".join(available) if available else "(none)"
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"no agent named '{agent}'. Available agents: {listing}",
                }
            ],
            "is_error": True,
        }

    run_id = db.create_run(agent, session_id=None, task=task)
    report_path = (
        config.REPORTS_DIR / f"{date.today().isoformat()}-{agent}-run{run_id}.md"
    )

    # Fire-and-forget: assign_task returns immediately, the run happens in
    # its own task. Hold a strong ref so the event loop's weak references to
    # tasks can't garbage-collect it mid-run.
    bg_task = asyncio.create_task(run_assigned_task(agent, task, run_id, report_path))
    _assigned_tasks.add(bg_task)
    bg_task.add_done_callback(_assigned_tasks.discard)

    rel_report_path = report_path.relative_to(config.REPO_ROOT).as_posix()
    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"Assigned to '{agent}' — run {run_id}. Report will be "
                    f"written to {rel_report_path}."
                ),
            }
        ]
    }


_cockpit_mcp = create_sdk_mcp_server(
    name="cockpit", version="1.0.0", tools=[_assign_task_tool]
)


def _ceo_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=_system_prompt(),
        model=config.MODELS["ceo"],
        tools=config.TOOLS["ceo"],
        can_use_tool=make_path_guard(
            config.CEO_WRITE_PATHS, allow_tool_prefixes=("mcp__cockpit__",)
        ),
        include_partial_messages=True,
        cwd=str(config.REPO_ROOT),
        mcp_servers={"cockpit": _cockpit_mcp},
        env=_agent_env(),
    )


async def run_ceo_turn(
    session_id: int, founder: str, content: str
) -> AsyncIterator[tuple[str, str]]:
    """Run one turn of a CEO session, yielding ("text", chunk) and
    ("tool_call", description) events as they arrive.

    First turn of a cockpit session: connect a persistent client and send the
    full loaded context. Later turns send just the founder's message into the
    same live conversation — context is loaded once per session.

    Every turn is one run in the run_log sense: a run row is created up
    front, its events (tool calls, file reads/writes, warnings, usage) are
    logged as they happen, and it is finished with a terminal status
    (completed / failed / killed) before this generator returns.
    """
    # Check the kill switch. Before anything else — no client, no run
    # context, nothing. A refused run still gets a row so it's visible in
    # the log.
    if config.KILL_FILE.exists():
        run_id = db.create_run("ceo", session_id, task=content[:200])
        db.finish_run(run_id, "killed", error="kill switch set — run refused")
        yield ("error", "Kill switch is set — the cockpit is stopped. Clear it to resume.")
        return

    run_id = db.create_run("ceo", session_id, task=content[:200])
    token = _current_run_id.set(run_id)
    killed = False

    try:
        client = _clients.get(session_id)

        if client is None:
            prompt_text = _first_user_message(founder, content, session_id)
            client = ClaudeSDKClient(options=_ceo_options())
            await client.connect()
            _clients[session_id] = client
        else:
            prompt_text = f"[{_founder_label(founder)}] {content}"

        await client.query(prompt_text)

        async for message in client.receive_response():
            # Mid-run kill enforcement: checked on every message so a kill
            # set while the agent is working interrupts it promptly rather
            # than waiting for the turn to finish on its own.
            if config.KILL_FILE.exists():
                await client.interrupt()
                db.add_run_log(run_id, "warning", "kill switch set mid-run — interrupted")
                db.finish_run(run_id, "killed", error="kill switch set mid-run")
                yield ("error", "Kill switch set — run interrupted.")
                killed = True
                break

            if isinstance(message, StreamEvent):
                event = message.event
                if event.get("type") == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        if text:
                            yield ("text", text)

            elif isinstance(message, AssistantMessage):
                for desc in _log_tool_blocks(run_id, message):
                    yield ("tool_call", desc)

            elif isinstance(message, ResultMessage):
                usage = message.usage or {}
                db.add_run_log(
                    run_id,
                    "usage",
                    json.dumps(
                        {
                            "input_tokens": usage.get("input_tokens"),
                            "cache_creation_input_tokens": usage.get(
                                "cache_creation_input_tokens"
                            ),
                            "cache_read_input_tokens": usage.get(
                                "cache_read_input_tokens"
                            ),
                            "total_cost_usd": message.total_cost_usd,
                        }
                    ),
                )
                logger.info(
                    "ceo turn usage: session=%s input_tokens=%s "
                    "cache_creation_input_tokens=%s cache_read_input_tokens=%s "
                    "total_cost_usd=%s",
                    session_id,
                    usage.get("input_tokens"),
                    usage.get("cache_creation_input_tokens"),
                    usage.get("cache_read_input_tokens"),
                    message.total_cost_usd,
                )
                _check_playbook_cap(run_id)

        if not killed:
            db.finish_run(run_id, "completed")

    except Exception as exc:
        db.finish_run(run_id, "failed", error=str(exc))
        raise
    finally:
        _current_run_id.reset(token)


def _check_playbook_cap(run_id: int | None = None) -> None:
    """Flag the playbook when it exceeds its word cap. Until HR exists, the
    CEO consolidates its own playbook when flagged and founders approve."""
    playbook = config.COMPANY_DIR / "agents" / "ceo" / "playbook.md"
    if playbook.exists():
        words = len(playbook.read_text(encoding="utf-8").split())
        if words > config.PLAYBOOK_WORD_CAP:
            logger.warning(
                "playbook.md is %s words — over the %s-word cap; "
                "consolidation (with founder approval) is due",
                words,
                config.PLAYBOOK_WORD_CAP,
            )
            if run_id is not None:
                db.add_run_log(
                    run_id,
                    "warning",
                    f"playbook.md is {words} words — over the "
                    f"{config.PLAYBOOK_WORD_CAP}-word cap",
                )


async def run_assigned_task(
    agent: str, task: str, run_id: int, report_path: Path
) -> None:
    """Run one assigned agent task end to end: connect, do the work,
    disconnect. This is a run, not a session — it loads context, does the
    task, and ends. Not a generator: nothing streams to a page for assigned
    work in v1, the report file is the interface, so this is a plain
    coroutine intended to be run as a background asyncio task.

    Context is scoped to the agent's own domain (its brief, plus the shared
    lessons and ownership map) rather than the CEO's full context — per the
    cost-control rule to scope context to the agent's domain. It never
    raises: this runs unattended as a background task, so every failure
    path ends in a terminal run status instead of an unhandled exception.
    """
    if config.KILL_FILE.exists():
        db.finish_run(run_id, "killed", error="kill switch set — run refused")
        return

    token = _current_run_id.set(run_id)
    try:
        rel_report_path = report_path.relative_to(config.REPO_ROOT).as_posix()

        system_prompt = (
            f"{_read(config.CONSTITUTION)}\n\n"
            f"{_read(config.AGENTS_DIR / agent / 'brief.md')}"
        )
        user_message = (
            f"# Shared Lessons\n\n{_read(config.COMPANY_DIR / 'lessons.md')}\n\n"
            f"# Ownership Map\n\n{_read(config.COMPANY_DIR / 'ownership.md')}\n\n"
            f"# Task\n\n{task}\n\n"
            "Write your report to exactly this path (relative to the "
            f"repository root): {rel_report_path}. That report is your "
            "required closing step."
        )

        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            model=config.MODELS.get(agent, config.MODELS["default"]),
            tools=config.TOOLS.get(agent, config.TOOLS["default"]),
            can_use_tool=make_path_guard(
                [config.REPORTS_DIR, config.AGENTS_DIR / agent]
            ),
            cwd=str(config.REPO_ROOT),
            env=_agent_env(),
        )

        async def _attempt() -> None:
            """One full try: connect, send the task, drain the response,
            always disconnect. Raises _Killed on a mid-run kill, or whatever
            the SDK raises on error/timeout — both are handled by the
            caller's retry-once logic."""
            start = time.monotonic()
            warned_halfway = False
            client = ClaudeSDKClient(options=options)
            try:
                await client.connect()
                await client.query(user_message)

                async for message in client.receive_response():
                    # Mid-run kill enforcement, same as run_ceo_turn.
                    if config.KILL_FILE.exists():
                        await client.interrupt()
                        db.add_run_log(
                            run_id,
                            "warning",
                            "kill switch set mid-run — interrupted",
                        )
                        raise _Killed()

                    if isinstance(message, AssistantMessage):
                        _log_tool_blocks(run_id, message)

                    elif isinstance(message, ResultMessage):
                        usage = message.usage or {}
                        db.add_run_log(
                            run_id,
                            "usage",
                            json.dumps(
                                {
                                    "input_tokens": usage.get("input_tokens"),
                                    "cache_creation_input_tokens": usage.get(
                                        "cache_creation_input_tokens"
                                    ),
                                    "cache_read_input_tokens": usage.get(
                                        "cache_read_input_tokens"
                                    ),
                                    "total_cost_usd": message.total_cost_usd,
                                }
                            ),
                        )
                        logger.info(
                            "assigned run usage: run=%s agent=%s input_tokens=%s "
                            "cache_creation_input_tokens=%s "
                            "cache_read_input_tokens=%s total_cost_usd=%s",
                            run_id,
                            agent,
                            usage.get("input_tokens"),
                            usage.get("cache_creation_input_tokens"),
                            usage.get("cache_read_input_tokens"),
                            message.total_cost_usd,
                        )

                    if not warned_halfway and (
                        time.monotonic() - start > config.RUN_TIMEOUT_SECONDS / 2
                    ):
                        warned_halfway = True
                        db.add_run_log(run_id, "warning", "past halfway timeout mark")
            finally:
                # One-shot runs, not persistent sessions — always disconnect,
                # unlike the CEO's client which stays open for the session.
                await client.disconnect()

        try:
            await asyncio.wait_for(_attempt(), timeout=config.RUN_TIMEOUT_SECONDS)
        except _Killed:
            db.finish_run(run_id, "killed", error="kill switch set mid-run")
            return
        except Exception as exc:
            # Discard anything partial, retry once from scratch, per the
            # build package's failure handling.
            db.add_run_log(
                run_id, "warning", f"attempt 1 failed: {exc} — retrying from scratch"
            )
            if report_path.exists():
                report_path.unlink()
            try:
                await asyncio.wait_for(_attempt(), timeout=config.RUN_TIMEOUT_SECONDS)
            except _Killed:
                db.finish_run(run_id, "killed", error="kill switch set mid-run")
                return
            except Exception as exc2:
                db.finish_run(run_id, "failed", error=str(exc2))
                if report_path.exists():
                    report_path.unlink()
                return

        # Close-protocol check: the report is the required closing step. Its
        # absence is itself the finding — flag it, but the run still ran to
        # completion, so it is still "completed".
        if report_path.exists():
            db.finish_run(run_id, "completed")
        else:
            db.add_run_log(
                run_id, "warning", "close protocol violated: no report written"
            )
            db.finish_run(run_id, "completed")
    finally:
        _current_run_id.reset(token)


async def shutdown() -> None:
    """Disconnect every live session client (called on server shutdown)."""
    for session_id, client in list(_clients.items()):
        try:
            await client.disconnect()
        except Exception:
            logger.exception("error disconnecting session %s", session_id)
        _clients.pop(session_id, None)

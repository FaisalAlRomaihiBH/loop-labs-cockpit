"""Agent runner. Step 3: real context loading for the CEO agent.

Sessions are continuous conversations: one ClaudeSDKClient per cockpit
session, connected on the first turn with the full loaded context and kept
open, so later turns continue the same conversation without resending it.
The persistent connection is also what lets the can_use_tool permission
callback answer the CLI's requests — a one-shot query() closes the control
channel before the first tool call arrives.
"""

import logging
from pathlib import Path
from typing import AsyncIterator

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from claude_agent_sdk.types import (
    AssistantMessage,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    StreamEvent,
    ToolPermissionContext,
    ToolUseBlock,
)

from . import config

logger = logging.getLogger("cockpit.agents")

# The API key lives outside the repo, one directory above the loop-labs
# workspace root: C:\loop-labs\.cockpit-env.txt
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".cockpit-env.txt"

# Cockpit session id -> live SDK client holding that session's conversation.
_clients: dict[int, ClaudeSDKClient] = {}

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
    return "Founder A" if founder == "A" else "Founder B"


def _system_prompt() -> str:
    """Identity and rules only: the constitution plus the CEO's brief."""
    constitution = _read(config.CONSTITUTION)
    brief = _read(config.CEO_BRIEF)
    return f"{constitution}\n\n{brief}"


def _first_user_message(founder: str, content: str) -> str:
    """Static docs first (for caching), then volatile docs, then the message."""
    parts: list[str] = []

    for path, heading in zip(config.CEO_STATIC_DOCS, _STATIC_HEADINGS):
        parts.append(f"{heading}\n\n{_read(path)}")

    if not config.CHARTER_READ_FLAG.exists():
        parts.append(f"# Charter (founding context)\n\n{_read(config.CHARTER)}")

    for path, heading in config.CEO_VOLATILE_DOCS:
        parts.append(f"# {heading}\n\n{_read(path)}")

    parts.append(f"# Founder Message\n\n[{_founder_label(founder)}] {content}")

    return "\n\n".join(parts)


async def _path_guard(
    tool_name: str,
    tool_input: dict,
    context: ToolPermissionContext,
):
    """Allow a tool call only when its path argument resolves under an
    allowed root. This is the actual enforcement layer — tools=[...] only
    restricts which tools exist at all, not where they may look.

    Reads may range across the allowed roots; writes are confined to the
    agent's own memory files and the two company files it owns.
    """
    raw_path = (
        tool_input.get("file_path")
        or tool_input.get("path")
        or str(config.REPO_ROOT)
    )
    resolved = Path(raw_path).resolve()

    if tool_name == "Write":
        for allowed in config.CEO_WRITE_PATHS:
            if resolved == allowed or resolved.is_relative_to(allowed):
                return PermissionResultAllow()
        return PermissionResultDeny(
            message=f"write outside the CEO's owned paths: {resolved}"
        )

    for root in config.ALLOWED_PATHS:
        if resolved.is_relative_to(root):
            return PermissionResultAllow()

    return PermissionResultDeny(message=f"path outside allowed roots: {resolved}")


def _short_input(tool_input: dict) -> str:
    for key in ("file_path", "pattern", "path"):
        if key in tool_input:
            value = str(tool_input[key])
            return value if len(value) <= 80 else value[:77] + "..."
    return ""


def _ceo_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=_system_prompt(),
        model=config.MODELS["ceo"],
        tools=config.TOOLS["ceo"],
        can_use_tool=_path_guard,
        include_partial_messages=True,
        cwd=str(config.REPO_ROOT),
        env={
            "ANTHROPIC_API_KEY": _load_api_key(),
            # Pin the endpoint so an inherited ANTHROPIC_BASE_URL from the
            # launching shell can never redirect agent traffic elsewhere.
            "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
        },
    )


async def run_ceo_turn(
    session_id: int, founder: str, content: str
) -> AsyncIterator[tuple[str, str]]:
    """Run one turn of a CEO session, yielding ("text", chunk) and
    ("tool_call", description) events as they arrive.

    First turn of a cockpit session: connect a persistent client and send the
    full loaded context. Later turns send just the founder's message into the
    same live conversation — context is loaded once per session.
    """
    client = _clients.get(session_id)

    if client is None:
        prompt_text = _first_user_message(founder, content)
        client = ClaudeSDKClient(options=_ceo_options())
        await client.connect()
        _clients[session_id] = client
    else:
        prompt_text = f"[{_founder_label(founder)}] {content}"

    await client.query(prompt_text)

    async for message in client.receive_response():
        if isinstance(message, StreamEvent):
            event = message.event
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    text = delta.get("text", "")
                    if text:
                        yield ("text", text)

        elif isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    short_input = _short_input(block.input)
                    desc = f"{block.name}: {short_input}" if short_input else block.name
                    yield ("tool_call", desc)

        elif isinstance(message, ResultMessage):
            usage = message.usage or {}
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
            _check_playbook_cap()


def _check_playbook_cap() -> None:
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


async def shutdown() -> None:
    """Disconnect every live session client (called on server shutdown)."""
    for session_id, client in list(_clients.items()):
        try:
            await client.disconnect()
        except Exception:
            logger.exception("error disconnecting session %s", session_id)
        _clients.pop(session_id, None)

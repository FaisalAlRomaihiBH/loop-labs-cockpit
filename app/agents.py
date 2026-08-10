"""Agent runner. Step 2: a single hard-coded agent, no context loading yet."""

from pathlib import Path
from typing import AsyncIterator

from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent

# The API key lives outside the repo, one directory above the loop-labs
# workspace root: C:\loop-labs\.cockpit-env.txt
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".cockpit-env.txt"

MODEL = "claude-sonnet-4-6"  # mid-tier; the CEO agent (Step 3) gets the top model
SYSTEM_PROMPT = (
    "You are the Loop Labs cockpit test agent. This is a plumbing test: "
    "answer the founder's message directly, concisely, and in plain English. "
    "You have no tools and no company context yet."
)


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


async def run_test_agent(prompt: str) -> AsyncIterator[str]:
    """Run the hard-coded test agent and yield incremental text chunks."""
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        model=MODEL,
        # tools=[] genuinely disables all tools (--tools ""). allowed_tools=[]
        # would be dropped as falsy and leave the default toolset available.
        tools=[],
        max_turns=1,
        include_partial_messages=True,
        env={
            "ANTHROPIC_API_KEY": _load_api_key(),
            # Pin the endpoint so an inherited ANTHROPIC_BASE_URL from the
            # launching shell can never redirect agent traffic elsewhere.
            "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
        },
    )

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    text = delta.get("text", "")
                    if text:
                        yield text

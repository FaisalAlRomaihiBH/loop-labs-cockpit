"""Terminal fallback: run any agent directly, bypassing FastAPI entirely.

This uses the same runner as `assign_task` (app.agents.run_assigned_task), so
it is what you use if the cockpit itself breaks -- including to run the
agent that fixes it. It talks straight to the SDK and SQLite; no server
needs to be up.

Usage:
    python -m app.cli --agent test --task "..."
    python -m app.cli --agent ceo --task "..."
"""

import argparse
import asyncio
import logging

from datetime import date

from . import agents, config, db

logging.basicConfig(level=logging.INFO)


def _available_agents() -> list[str]:
    return sorted(p.parent.name for p in config.AGENTS_DIR.glob("*/brief.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, help="agent name, e.g. ceo, test")
    parser.add_argument("--task", required=True, help="the task to run")
    args = parser.parse_args()

    agent = args.agent.strip().lower()

    db.init_db()

    # "ceo" has no brief-directory check here even though assign_task
    # refuses to assign to it -- this CLI is the direct escape hatch, not
    # the assignment path, and running the CEO through it is exactly what
    # you need when the cockpit itself is broken. For every other name we
    # require a real brief, same rule assign_task enforces.
    if agent != "ceo" and not config.agent_exists(agent):
        available = _available_agents()
        print(f"no agent named '{agent}'.")
        print(f"available agents: {', '.join(available) if available else '(none)'}")
        return 1

    run_id = db.create_run(agent, session_id=None, task=args.task)
    report_path = (
        config.REPORTS_DIR / f"{date.today().isoformat()}-{agent}-run{run_id}.md"
    )

    # NOTE: run_assigned_task gives every agent -- including "ceo" here --
    # the same scoped context: constitution + brief + shared lessons +
    # ownership map + task. That is deliberately less than a real CEO
    # founder session (no specification, plan, or decision-log memory, and
    # no assign_task tool). It is acceptable for this escape hatch because
    # the CLI exists to run one task or fix the cockpit, not to hold a
    # founder conversation -- see "The terminal fallback" in build-package.md.
    asyncio.run(agents.run_assigned_task(agent, args.task, run_id, report_path))

    run = db.get_run(run_id)
    status = run["status"] if run else "unknown"

    print(f"run {run_id}: {status}")
    print(f"report: {report_path}")
    if run and run.get("error"):
        print(f"error: {run['error']}")
    if report_path.exists():
        print()
        print(report_path.read_text(encoding="utf-8"))

    return 0 if status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

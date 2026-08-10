"""Models, tool permissions, paths. One place to change any of them."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent          # loop-labs-cockpit
LOOP_LABS_DIR = REPO_ROOT.parent                             # C:\loop-labs
ENV_FILE = LOOP_LABS_DIR / ".cockpit-env.txt"                # secrets — outside both repos, never in ALLOWED_PATHS
COMPANY_DIR = REPO_ROOT / "company"
PRODUCT_REPO = LOOP_LABS_DIR / "carwash-app"                 # does not exist yet (Stage 2)
REPORTS_DIR = COMPANY_DIR / "reports"
AGENTS_DIR = COMPANY_DIR / "agents"

# Roots agents may read from. ENV_FILE's directory is deliberately NOT here as a
# root — only the two repositories are.
ALLOWED_PATHS = [REPO_ROOT, PRODUCT_REPO]

# Founder identities. A/B are the permanent identifiers (schema, message
# tags); these are the actual people behind them.
FOUNDERS = {"A": "Hasan", "B": "Faisal"}

# Per-agent model. CEO gets the most capable tier; mid tier is the default for
# future agents per the cost-control section. One line to change.
MODELS = {
    "ceo": "claude-opus-5",
    # Top tier per the cost-control section: judgement with wide blast
    # radius (CEO, Architect, Security). Founder-approved 2026-08-10.
    "architect": "claude-opus-5",
    "default": "claude-sonnet-4-6",
}

# Per-agent tool allow-lists. CEO's full v1 set also includes assign_task
# (added at Step 6) — that arrives via mcp_servers, not this list, since
# `tools` only gates the built-in tool set. No Bash. Edit for the CEO is a
# deliberate, founder-approved (2026-08-10) deviation from the build
# package's "no Edit": Write-only meant rewriting whole memory files to
# change one line, a real content-loss risk. Edit obeys the same
# write-path guard as Write.
TOOLS = {"ceo": ["Read", "Glob", "Grep", "Write", "Edit"]}
# Default allow-list for assigned agents that don't have their own entry
# above (e.g. the throwaway test agent). Same shape as the CEO's for now —
# read broadly, write only within the paths its guard allows.
TOOLS["default"] = ["Read", "Glob", "Grep", "Write"]

# Where the CEO may WRITE. Everything else — including the rest of this
# repository — is read-only to it. Directories cover their whole subtree.
CEO_WRITE_PATHS = [
    COMPANY_DIR / "agents" / "ceo",   # its own memory (and the charter flag)
    COMPANY_DIR / "sprint.md",
    COMPANY_DIR / "backlog.md",
]

# Founder-approved 2026-08-10: glob-scoped write grants beyond the roots
# above. Briefs so the CEO can build the organisation (moves to HR when HR
# exists); reports limited to the CEO's own by filename convention.
CEO_WRITE_GLOBS = [
    str(COMPANY_DIR / "agents" / "*" / "brief.md"),
    str(COMPANY_DIR / "reports" / "*-ceo-*.md"),
]

PLAYBOOK_WORD_CAP = 2000

# Generous, per the build package: long enough that real work is never cut
# off, short enough that a stuck run does not hang indefinitely. A warning
# is logged at the halfway mark (RUN_TIMEOUT_SECONDS / 2) so a run trending
# long is visible before it actually times out.
RUN_TIMEOUT_SECONDS = 600


def agent_exists(name: str) -> bool:
    return (AGENTS_DIR / name / "brief.md").exists()


# The kill switch. If this file exists, no run starts and any in-flight run
# is interrupted at its next check. The founders' emergency stop.
KILL_FILE = COMPANY_DIR / "KILL"

# Context documents for the CEO, in prompt order.
# Static (byte-identical every session — must come FIRST for prompt caching):
CEO_STATIC_DOCS = [COMPANY_DIR / "specification.md", COMPANY_DIR / "plan.md"]
CHARTER = COMPANY_DIR / "charter.md"
# Charter-read-once flag: charter is included only while this file is absent.
CHARTER_READ_FLAG = COMPANY_DIR / "agents" / "ceo" / ".founding-context-read"
# Volatile (changes between sessions — comes after all static content):
CEO_VOLATILE_DOCS = [
    (COMPANY_DIR / "agents" / "ceo" / "decisions.md", "Your Memory — Decision Log"),
    (COMPANY_DIR / "agents" / "ceo" / "playbook.md", "Your Memory — Playbook"),
    (COMPANY_DIR / "agents" / "ceo" / "founders.md", "Your Memory — Founder Preferences"),
    # Part of the founder-approved Option B memory structure — a fresh
    # session must see what's blocked on a decision and since when.
    (COMPANY_DIR / "agents" / "ceo" / "open-questions.md", "Your Memory — Open Questions"),
    (COMPANY_DIR / "lessons.md", "Shared Lessons"),
    (COMPANY_DIR / "ownership.md", "Ownership Map"),
    (COMPANY_DIR / "sprint.md", "Sprint State"),
    (COMPANY_DIR / "backlog.md", "Backlog"),
]
CONSTITUTION = COMPANY_DIR / "constitution.md"
CEO_BRIEF = COMPANY_DIR / "agents" / "ceo" / "brief.md"

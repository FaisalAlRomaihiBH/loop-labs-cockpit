"""Models, tool permissions, paths. One place to change any of them."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent          # loop-labs-cockpit
LOOP_LABS_DIR = REPO_ROOT.parent                             # C:\loop-labs
ENV_FILE = LOOP_LABS_DIR / ".cockpit-env.txt"                # secrets — outside both repos, never in ALLOWED_PATHS
COMPANY_DIR = REPO_ROOT / "company"
PRODUCT_REPO = LOOP_LABS_DIR / "carwash-app"                 # does not exist yet (Stage 2)

# Roots agents may read from. ENV_FILE's directory is deliberately NOT here as a
# root — only the two repositories are.
ALLOWED_PATHS = [REPO_ROOT, PRODUCT_REPO]

# Per-agent model. CEO gets the most capable tier; mid tier is the default for
# future agents per the cost-control section. One line to change.
MODELS = {"ceo": "claude-opus-5", "default": "claude-sonnet-4-6"}

# Per-agent tool allow-lists. CEO's full v1 set also includes assign_task
# (added at Step 6). No Bash, no Edit — per the build package, permissions
# are the enforcement layer, not instructions.
TOOLS = {"ceo": ["Read", "Glob", "Grep", "Write"]}

# Where the CEO may WRITE. Everything else — including the rest of this
# repository — is read-only to it. Directories cover their whole subtree.
CEO_WRITE_PATHS = [
    COMPANY_DIR / "agents" / "ceo",   # its own memory (and the charter flag)
    COMPANY_DIR / "sprint.md",
    COMPANY_DIR / "backlog.md",
]

PLAYBOOK_WORD_CAP = 2000

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
    (COMPANY_DIR / "lessons.md", "Shared Lessons"),
    (COMPANY_DIR / "ownership.md", "Ownership Map"),
    (COMPANY_DIR / "sprint.md", "Sprint State"),
    (COMPANY_DIR / "backlog.md", "Backlog"),
]
CONSTITUTION = COMPANY_DIR / "constitution.md"
CEO_BRIEF = COMPANY_DIR / "agents" / "ceo" / "brief.md"

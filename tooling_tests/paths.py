"""Where things are, for the tooling tests. Importing this also makes scripts/ importable."""
import sys
from pathlib import Path

TOOLING_TESTS = Path(__file__).resolve().parent
REPO = TOOLING_TESTS.parent
SCRIPTS = REPO / "scripts"
WORKFLOW = REPO / ".github" / "workflows" / "tests.yml"

# The scripts are plain files in scripts/, not a package.
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

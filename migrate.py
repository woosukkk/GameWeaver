"""Apply pending GameWeaver database migrations."""

from pathlib import Path

from gameweaver.config import load_env
from gameweaver.migrations import migrate


ROOT = Path(__file__).parent
load_env(ROOT / ".env")

if __name__ == "__main__":
    applied = migrate(ROOT / "migrations")
    print("Applied: " + ", ".join(applied) if applied else "Database is up to date.")

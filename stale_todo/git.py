"""Git helpers for stale-todo."""

import subprocess
import time
from typing import Optional, Tuple


SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}


def blame_age(repo: str, relpath: str, lineno: int) -> Optional[Tuple[str, int]]:
    """Return (author, age_days) for the given line, or None if unavailable."""
    try:
        out = subprocess.run(
            ["git", "-C", repo, "blame", "-L", f"{lineno},{lineno}", "--porcelain", relpath],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if out.returncode != 0 or not out.stdout:
        return None
    author = None
    author_time = None
    for line in out.stdout.splitlines():
        if line.startswith("author "):
            author = line[len("author "):].strip()
        elif line.startswith("author-time "):
            try:
                author_time = int(line.split()[1])
            except (IndexError, ValueError):
                author_time = None
        if author and author_time is not None:
            break
    if author_time is None:
        return None
    age_days = int((time.time() - author_time) / 86400)
    if age_days < 0:
        age_days = 0
    return (author or "unknown", age_days)
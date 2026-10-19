"""Scanning logic for stale-todo."""

import os
import re
from typing import Iterable, List

from .git import SKIP_DIRS, blame_age

DEFAULT_MARKERS = ("TODO", "FIXME", "HACK", "XXX")
MARKER_RE = re.compile(r"(?<![A-Za-z0-9_-])(TODO|FIXME|HACK|XXX)(?![A-Za-z0-9_-])[:\s]*(.*)", re.IGNORECASE)


def iter_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            yield os.path.join(dirpath, name)


def is_text(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(4096)
    except OSError:
        return False
    if b"\x00" in chunk:
        return False
    return True


def scan_file(path: str, root: str, markers: tuple) -> List[dict]:
    results = []
    marker_set = {m.upper() for m in markers}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return results
    relpath = os.path.relpath(path, root)
    for i, line in enumerate(lines, start=1):
        m = MARKER_RE.search(line)
        if not m:
            continue
        marker = m.group(1).upper()
        if marker not in marker_set:
            continue
        prefix = line[:m.start(1)]
        stripped_prefix = prefix.strip()
        comment_indicators = ("#", "//", "/*", "*", "--", ";", "%", "<!--")
        # triple-quoted strings (docstrings) also count as comment context
        triple_single = "''" + "'"
        triple_double = '"""'
        comment_indicators = comment_indicators + (triple_single, triple_double)
        in_comment = stripped_prefix == "" or any(ind in prefix for ind in comment_indicators)
        if not in_comment:
            continue
        info = blame_age(root, relpath, i)
        author, age = (info if info else ("unknown", 0))
        # If no git info available, age stays 0 and author unknown.
        results.append({
            "file": relpath,
            "line": i,
            "marker": marker,
            "text": line.strip(),
            "author": author,
            "age_days": age,
        })
    return results


def scan(root: str, markers: tuple = DEFAULT_MARKERS) -> List[dict]:
    root = os.path.abspath(root)
    all_results = []
    for path in iter_files(root):
        if not is_text(path):
            continue
        all_results.extend(scan_file(path, root, markers))
    return all_results
"""CLI entry point for stale-todo."""

import argparse
import json
import sys

from .scanner import scan, DEFAULT_MARKERS


def format_text(items):
    out = []
    for it in items:
        out.append(f"{it['age_days']:>6}d  {it['author']:<12}  {it['file']}:{it['line']}  {it['text']}")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="stale-todo", description="Find stale TODO/FIXME/HACK/XXX comments.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--min-age", type=int, default=0, help="Only show items at least N days old.")
    parser.add_argument("--markers", default=",".join(DEFAULT_MARKERS), help="Comma-separated markers.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--top", type=int, default=0, help="Limit output to N oldest items (0 = all).")
    args = parser.parse_args(argv)

    markers = tuple(m.strip().upper() for m in args.markers.split(",") if m.strip())
    items = scan(args.path, markers)
    items = [it for it in items if it["age_days"] >= args.min_age]
    items.sort(key=lambda x: x["age_days"], reverse=True)
    if args.top and args.top > 0:
        items = items[:args.top]

    if args.format == "json":
        print(json.dumps(items, indent=2))
    else:
        if not items:
            print("No stale TODOs found.")
            return
        print(format_text(items))


if __name__ == "__main__":
    main()
# stale-todo

Find stale `TODO`/`FIXME`/`HACK`/`XXX` comments in a codebase and rank them by age using `git blame`.

## Description

`stale-todo` scans your repository for leftover task comments and reports how long each has been sitting there (and who wrote it), so you can triage the oldest debt first.

## Features

- Detects `TODO`, `FIXME`, `HACK`, and `XXX` markers in comments across many languages.
- Uses `git blame` to compute each comment's age and original author.
- Sorts results oldest-first by default.
- Filters by minimum age (`--min-age`).
- JSON output for CI/scripting (`--format json`).
- Skips binary files and common junk directories (`.git`, `node_modules`, etc.).

## Install

```sh
git clone https://github.com/yourname/stale-todo.git
cd stale-todo
pip install -e .
```

Or run directly:

```sh
python -m stale_todo /path/to/repo
```

## Usage

```sh
# Scan current directory
stale-todo .

# Only show items older than 30 days
stale-todo . --min-age 30

# JSON output
stale-todo . --format json

# Limit to top 20 oldest
stale-todo . --top 20
```

Example output:

```
  312d  alice   src/api.py:42   TODO: handle rate limiting
   89d  bob     lib/util.js:7   FIXME: off-by-one in parser
    3d  carol   README.md:10    HACK: workaround for upstream bug
```

## License

MIT
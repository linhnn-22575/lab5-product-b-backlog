"""Replace bare task/story codes (BE-9.6.1, S9.6) in Markdown docs with links to their GitHub issues.

Usage: python link-task-codes-to-github-issues.py ../../task-breakdown.md ../../PREMISE.md
Skips code spans (`...`) and codes that are already links. Idempotent.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
# Optional range suffix "–3" means "...through the task whose last number is 3" (BE-1.1.1–3).
CODE = re.compile(r"(?<![\w\[/-])((?:BE|FE|QA|INFRA|PM|BRSE)-\d+\.\d+\.\d+|S\d+\.\d+)(?:–(\d+)(?![\d.]))?"
                  r"(?![\w.]*\d)(?!\s*#\d)")


def _sub(m, issue_map):
    code, end = m[1], m[2]
    if code not in issue_map:
        return m[0]
    out = f"[{code} #{issue_map[code]['number']}]({issue_map[code]['url']})"
    if end:
        last = code.rsplit(".", 1)[0] + "." + end
        out += f"–[{last} #{issue_map[last]['number']}]({issue_map[last]['url']})" if last in issue_map else f"–{end}"
    return out


def link_line(line, issue_map):
    parts = re.split(r"(`[^`]*`|\[[^\]]*\]\([^)]*\))", line)  # keep code spans and existing links intact
    for i in range(0, len(parts), 2):
        parts[i] = CODE.sub(lambda m: _sub(m, issue_map), parts[i])
    return "".join(parts)


def main():
    issue_map = json.loads((HERE / "issue-number-map.json").read_text(encoding="utf-8"))
    for path in map(Path, sys.argv[1:]):
        text = path.read_text(encoding="utf-8")
        new = "\n".join(link_line(l, issue_map) for l in text.split("\n"))
        n = new.count("](https://github.com/") - text.count("](https://github.com/")
        path.write_text(new, encoding="utf-8")
        print(f"{path.name}: {n} links added")


if __name__ == "__main__":
    main()

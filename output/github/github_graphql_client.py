"""Thin wrapper around `gh api graphql` with retry on GitHub secondary rate limits."""
import json
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).parent
OWNER = "linhnn-22575"
REPO = "lab5-product-b-backlog"
CONFIG_FILE = HERE / "github-project-config.json"
STATE_FILE = HERE / "github-push-state.json"


def gql(query, variables=None, retries=6):
    """Run one GraphQL document; returns `data`. Raises on non-retryable errors."""
    body = json.dumps({"query": query, "variables": variables or {}})
    for attempt in range(retries):
        p = subprocess.run(["gh", "api", "graphql", "--input", "-"], input=body,
                           capture_output=True, text=True, encoding="utf-8")
        out = p.stdout or ""
        try:
            res = json.loads(out) if out.strip() else {}
        except json.JSONDecodeError:
            res = {}
        errs = res.get("errors") or []
        msg = " ".join(e.get("message", "") for e in errs) + (p.stderr or "")
        if p.returncode == 0 and not errs:
            return res["data"]
        retryable = any(k in msg.lower() for k in ("secondary rate", "rate limit", "abuse",
                                                    "502", "504", "timeout", "something went wrong"))
        if not retryable or attempt == retries - 1:
            raise RuntimeError(f"GraphQL failed: {msg[:800]}")
        wait = 60 * (attempt + 1)
        print(f"  ...rate limited / transient error, sleep {wait}s ({msg[:120]})", flush=True)
        time.sleep(wait)


def gh_json(args):
    """Run a `gh` REST/CLI command that prints JSON."""
    p = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {p.stderr[:500]}")
    return json.loads(p.stdout) if p.stdout.strip() else None


def load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

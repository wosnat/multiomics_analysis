#!/usr/bin/env bash
# preflight.sh — the "DOA" gate. Run this before opening a research chat.
#
# Produces ONE green/red answer after checking, in order:
#   0. Staleness   — offline tag compare vs the template remote (informational).
#   1. Triple      — template / explorer / KG versions, printed on one line.
#   2. Contract    — kg_release_info: installed explorer satisfies KG.mcp_min_version
#                    and the load-bearing schema shape is present.
#   3. API smoke   — GraphConnection() + gene_overview([...]): import + Neo4j auth
#                    + a real round-trip.
#
# RED means: don't proceed to an analysis chat; fix what's reported. The three
# common failures (env unset, off-subnet, version mismatch) each get a distinct hint.
#
# Usage:  ./scripts/preflight.sh
set -uo pipefail

# Run from the repo root regardless of where invoked (so `.env`, VERSION, and
# pyproject.toml resolve, and the MCP/explorer sees CWD = repo root).
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

bold() { printf '\033[1m%s\033[0m\n' "$1"; }
green() { printf '\033[32m%s\033[0m\n' "$1"; }
red() { printf '\033[31m%s\033[0m\n' "$1"; }
yellow() { printf '\033[33m%s\033[0m\n' "$1"; }

bold "── Preflight: multiomics_research_template ──"

# ── 0. Staleness check (offline tag compare; no auth, works on the lab subnet) ──
LOCAL_VER="$(tr -d '[:space:]' < VERSION 2>/dev/null || echo unknown)"
REMOTE=""
if git remote 2>/dev/null | grep -qx upstream; then REMOTE=upstream
elif git remote 2>/dev/null | grep -qx origin; then REMOTE=origin; fi
if [[ -n "$REMOTE" ]]; then
  git fetch --tags --quiet "$REMOTE" 2>/dev/null || true
  LATEST="$(git tag -l 'v*' | sed 's/^v//' | sort -V | tail -1)"
  if [[ -n "$LATEST" && "$LATEST" != "$LOCAL_VER" ]]; then
    NEWEST="$(printf '%s\n%s\n' "$LOCAL_VER" "$LATEST" | sort -V | tail -1)"
    if [[ "$NEWEST" == "$LATEST" ]]; then
      yellow "⚠ template v${LOCAL_VER} — latest is v${LATEST}"
      yellow "   update:  git pull upstream main && uv sync   (changes: CHANGELOG.md)"
    fi
  fi
fi

# ── 1–3. Version triple + KG contract + API smoke (Python, via the synced venv) ──
# Exit codes from the Python block: 0 = green, 2 = env unset, 3 = cannot connect,
# 4 = version mismatch, 5 = other red.
uv run python - <<'PY'
import sys
import json
import pathlib
from datetime import datetime, timezone

def red(s):    print(f"\033[31m{s}\033[0m")
def green(s):  print(f"\033[32m{s}\033[0m")
def yellow(s): print(f"\033[33m{s}\033[0m")

# --- template version + explorer pin (read from files; no KG needed) ---
template_version = "unknown"
try:
    template_version = pathlib.Path("VERSION").read_text().strip()
except Exception:
    pass

explorer_pin = "unknown"
try:
    import tomllib
    data = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
    explorer_pin = data["tool"]["uv"]["sources"]["multiomics-explorer"].get("tag", "?")
except Exception:
    pass

# --- installed explorer version ---
try:
    from importlib.metadata import version as _pkgver
    explorer_version = _pkgver("multiomics-explorer")
except Exception:
    explorer_version = "unknown"

# --- import the explorer API ---
try:
    from multiomics_explorer import GraphConnection, kg_release_info, gene_overview
    from multiomics_explorer.config.settings import get_settings
except Exception as e:
    red(f"✗ Cannot import multiomics_explorer: {e}")
    yellow("   Did `uv sync` complete? Run it from the repo root, then re-run preflight.")
    sys.exit(5)

settings = get_settings()
uri = settings.neo4j_uri

# --- env / creds present? (distinct hint #1: env unset) ---
if not settings.neo4j_username or not settings.neo4j_password:
    red("✗ KG credentials are not set.")
    yellow("   NEO4J_USERNAME / NEO4J_PASSWORD are empty.")
    yellow("   Fix: cp .env.example .env  then fill in the operator-provided values.")
    yellow("        (The MCP reads .env from the repo root — see the README.)")
    sys.exit(2)

# --- connect (distinct hint #2: off-subnet / unreachable) ---
conn = GraphConnection(settings)
try:
    reachable = conn.verify_connectivity()
except Exception as e:
    reachable = False
    conn_err = e
else:
    conn_err = None

if not reachable:
    red(f"✗ Cannot reach the KG at {uri}")
    if conn_err is not None:
        yellow(f"   {type(conn_err).__name__}: {conn_err}")
    yellow("   Likely causes: off the lab subnet/VPN, wrong NEO4J_URI, or wrong password.")
    yellow("   Check network reachability per the KG connection guide, then re-run.")
    sys.exit(3)

# --- KG compatibility contract (distinct hint #3: version mismatch) ---
report = kg_release_info(conn)
kg = report.get("kg", {}) or {}
kg_version = kg.get("version") or "unknown"
verdict = report.get("verdict", "unknown")

# --- print the version triple ---
print()
print(f"  template  {template_version}")
print(f"  explorer  {explorer_version}   (pinned: {explorer_pin})")
print(f"  KG        {kg_version}   (mcp_min_version: {kg.get('mcp_min_version', '?')})")
print(f"  KG URI    {uri}")
print()

# record the full triple into usage/ (completes §9's per-run triple record)
try:
    usage = pathlib.Path("usage"); usage.mkdir(exist_ok=True)
    with (usage / "preflight.jsonl").open("a") as fh:
        fh.write(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "preflight",
            "template_version": template_version,
            "explorer_version": explorer_version,
            "explorer_pin": explorer_pin,
            "kg_version": kg_version,
            "kg_uri": uri,
            "verdict": verdict,
        }) + "\n")
except Exception:
    pass  # logging is best-effort; never fail preflight on it

version_compat_failed = any(
    a.get("kind") == "version_compat" and not a.get("passed")
    for a in report.get("asserts", [])
)
if version_compat_failed:
    red(f"✗ Version mismatch: {report.get('summary')}")
    yellow("   Either upgrade the explorer (git pull upstream main && uv sync)")
    yellow("   or use a KG release whose mcp_min_version your explorer satisfies.")
    sys.exit(4)

if verdict == "warn":
    fails = [a for a in report.get("asserts", []) if not a.get("passed")]
    yellow(f"⚠ KG compatibility = warn: {report.get('summary')}")
    for a in fails:
        yellow(f"   - {a.get('name')}: {a.get('detail')}")
    yellow("   Tools still work but may emit confusing errors. Proceeding with caution.")
elif verdict == "unknown":
    yellow(f"⚠ KG compatibility = unknown: {report.get('summary')}")
    yellow("   (No Schema_info node — legacy KG build or wrong database.)")

# --- API smoke: a real round-trip ---
try:
    ov = gene_overview(["PMM0001", "PMM0845"], summary=True, conn=conn)
    n = ov.get("total_matching", 0)
except Exception as e:
    red(f"✗ API smoke call failed after connecting: {e}")
    sys.exit(5)
finally:
    conn.close()

if n < 1:
    red("✗ API smoke returned no genes for known loci (PMM0001/PMM0845).")
    yellow("   The KG may be empty or a different database than expected.")
    sys.exit(5)

green(f"✓ API smoke OK — gene_overview matched {n} known loci.")
print()
green("✓ PREFLIGHT GREEN — explorer satisfies the KG, round-trip works. You're clear to start an analysis.")
sys.exit(0)
PY
rc=$?

echo
if [[ $rc -eq 0 ]]; then
  exit 0
else
  red "✗ PREFLIGHT RED — resolve the issue above before opening a research chat."
  exit 1
fi

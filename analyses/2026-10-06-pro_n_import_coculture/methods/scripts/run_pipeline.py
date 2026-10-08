"""Run the full step 1 -> 6 pipeline for one organism, in order, stopping at the first failure.

Order: p1 -> p2a -> p2b -> p2c (re-query with the data-built role map, I6) -> p2a + p2b on the
augmented universe -> p2c --check-only (second pass must add nothing; reported) -> p3 -> p4 -> p5 -> p6
-> p11 (links, transport class, tiers, compound classes; decide gate 2026-10-08)
-> p12 (layered compound classes).
Writes <out-dir>/run_log.json (commands, exit codes, timings).
Usage (repo root):
  .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/run_pipeline.py \
      --organism "Prochlorococcus MED4" --out-dir analyses/2026-10-06-pro_n_import_coculture/methods/data/med4 [--pilot]
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    out = Path(a.out_dir); (out / "raw").mkdir(parents=True, exist_ok=True)
    tag = a.organism.split()[-1].lower()
    base = ["--organism", a.organism, "--out-dir", str(out)]
    pil = ["--pilot"] if a.pilot else []
    uni2 = ["--universe-file", str(out / f"p2c_{tag}_universe.csv")]
    steps = [("p1_collect_transporters.py", base + pil), ("p2a_fetch_pfam_tcdb.py", base),
             ("p2b_pfam_roles.py", base + pil), ("p2c_requery_universe.py", base),
             ("p2a_fetch_pfam_tcdb.py", base + uni2), ("p2b_pfam_roles.py", base + uni2 + pil),
             ("p2c_requery_universe.py", base + uni2 + ["--check-only"]),
             ("p3_group_systems.py", base + pil), ("p4_neighbours.py", base + pil),
             ("p5_substrates.py", base + pil), ("p6_evidence_profiles.py", base + pil),
             ("p11_links_tiers_classes.py", base + pil), ("p12_compound_classes_layered.py", base),
             ("p18_listing_basis.py", base)]
    log = []
    for script, args in steps:
        cmd = [sys.executable, "-W", "ignore::UserWarning", str(HERE / script)] + args
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        log.append({"script": script, "args": args, "exit": r.returncode, "seconds": round(time.time() - t0, 1),
                    "stderr_tail": r.stderr[-1500:] if r.returncode else ""})
        print(f"{script} {' '.join(a for a in args if a.startswith('--') and a not in ('--organism', '--out-dir'))}"
              f" -> exit {r.returncode} ({log[-1]['seconds']} s)", flush=True)
        if r.returncode:
            print(r.stderr[-3000:])
            break
    (out / "run_log.json").write_text(json.dumps(log, indent=1), encoding="utf-8")
    sys.exit(max(x["exit"] for x in log))


if __name__ == "__main__":
    main()

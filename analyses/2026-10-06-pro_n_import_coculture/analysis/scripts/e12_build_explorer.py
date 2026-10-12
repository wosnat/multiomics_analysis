"""Build the interactive system explorer (analysis/system_explorer.html) from the E10 tables.

Presentation only: reads data/explore/e10_{cells,rows,flags,clusters,by_gene,by_class}.csv and
injects them as JSON into templates/system_explorer.template.html. No KG calls, no new numbers.

Run: .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e12_build_explorer.py
"""
import json
import re
from pathlib import Path

import pandas as pd

A = Path(__file__).resolve().parents[1]
X = A / "data" / "explore"

cells = pd.read_csv(X / "e10_cells.csv")
rows = pd.read_csv(X / "e10_rows.csv")
flags = pd.read_csv(X / "e10_flags.csv")
clus = pd.read_csv(X / "e10_clusters.csv")
genes = pd.read_csv(X / "e10_by_gene.csv")
byc = pd.read_csv(X / "e10_by_class.csv")

BLOCKS = ["coculture vs axenic", "N starvation / other N sources", "this study (Weissberg)"]
BLOCK_NAME = ["Coculture vs axenic", "N starvation & other N sources", "This study"]


def short_and_sub(col: str):
    if col.startswith("Aharonovich"):
        return "N-rep", "N-replete"
    m = re.match(r"same study (d\d+)", col)
    if m:
        return m.group(1), "same study"
    m = re.match(r"Tolonen N-dep (\d+h)", col)
    if m:
        return m.group(1), "Tolonen deprivation"
    m = re.match(r"Read N-depleted (\d+h)", col)
    if m:
        return m.group(1), "Read (filtered)"
    if "cyanate" in col:
        return "cyan", "sole N"
    if "urea" in col:
        return "urea", "sole N"
    m = re.match(r"(protein|RNA) (ax|cc) (d\d+)", col)
    if m:
        om, arm, d = m.groups()
        return d, f"{om} {'axenic' if arm == 'ax' else 'coculture'}"
    return col[:6], ""


col_order = cells[["block", "column"]].drop_duplicates()
COLS = []
for _, c in col_order.iterrows():
    s, sub = short_and_sub(c["column"])
    COLS.append({"key": c["column"], "full": c["column"].replace("*", ""), "short": s, "sub": sub,
                 "block": BLOCKS.index(c["block"]), "blockName": BLOCK_NAME[BLOCKS.index(c["block"])]})
colkeys = [c["key"] for c in COLS]

STAT = {"up": "up", "down": "down", "mixed": "mixed", "ns": "ns", "not detected": "nd", "not listed": "nd"}


def num(x):
    return None if pd.isna(x) else float(x)


CELLS = {}
for _, c in cells.iterrows():
    d = {"s": STAT[c["status"]], "p": num(c["median_percentile"])}
    if not pd.isna(c["n_detected"]) and c["status"] not in ("not detected", "not listed"):
        d.update(nu=int(c["n_up"]), ndn=int(c["n_down"]), nd=int(c["n_detected"]))
    CELLS.setdefault(c["row_id"], {})[c["column"]] = d

leaf = dict(zip(clus["row_id"], clus["leaf_order"]))
fl = flags.set_index("row_id")
basis = {}
for _, b in byc.iterrows():
    basis.setdefault(b["system_id"], {})[b["class"]] = "dedicated" if b["listing_basis"] == "dedicated" else "broad"

ROWS = []
for _, r in rows.iterrows():
    classes = [] if pd.isna(r["classes"]) else [c for c in str(r["classes"]).split("|") if c]
    for cl in basis.get(r["row_id"], {}):
        if cl not in classes:
            classes.append(cl)
    strict = str(r["flag_strict"]) == "True"
    loose = str(r["flag_loose"]) == "True"
    cc = [CELLS.get(r["row_id"], {}).get(k, {}).get("p") for k in ("protein cc d60", "protein cc d89")]
    cc = [v for v in cc if v is not None]
    ftxt = ""
    if r["row_id"] in fl.index:
        f = fl.loc[r["row_id"]]
        ftxt = (f"coculture protein d60 {f['cc_d60_protein']} ({f['cc_d60_pct']:.2f}), d89 {f['cc_d89_protein']} "
                f"({f['cc_d89_pct']:.2f}); axenic d14 {f['ax_d14_protein']} ({f['ax_d14_pct']:.2f}); "
                f"Tolonen deprivation max rank {f['ndep_max_pct']:.2f}.")
    base = str(r["base"])
    ROWS.append({"id": r["row_id"], "label": r["label"], "base": base, "short": base.split(":")[0].split(" PMM")[0],
                 "category": r["category"], "loci": "" if pd.isna(r["loci"]) else str(r["loci"]).replace("|", ", "),
                 "tier": "" if pd.isna(r["tier"]) else str(r["tier"]), "classes": classes,
                 "basis": basis.get(r["row_id"], {}), "tag": "" if pd.isna(r["tags"]) else str(r["tags"]),
                 "strict": strict, "loose": loose, "leaf": int(leaf.get(r["row_id"], 999)),
                 "ccScore": (sum(cc) / len(cc)) if cc else None, "flagText": ftxt,
                 "search": (str(r["label"]) + " " + ("" if pd.isna(r["loci"]) else str(r["loci"]))).lower()})

# genes -> system rows via loci
locus2row = {}
for r in ROWS:
    for l in re.split(r"[,| ]+", r["loci"]):
        if l:
            locus2row.setdefault(l, r["id"])
for r in ROWS:  # reference rows: match by panel name start
    pass
GENES = {}
for (panel, lt, gname), g in genes.groupby(["panel", "locus_tag", "gene_name"], sort=False):
    rid = locus2row.get(lt)
    if rid is None:
        # reference rows (markers, urease, cynS/glsF) carry their locus in the row id or loci
        cand = [r["id"] for r in ROWS if lt in r["loci"] or r["id"].endswith(str(gname))]
        rid = cand[0] if cand else None
    if rid is None:
        continue
    cellsd = {c["column"]: {"s": STAT[c["status"]], "p": num(c["rank_percentile"])} for _, c in g.iterrows()}
    GENES.setdefault(rid, []).append({"name": f"{gname} {lt}", "cells": cellsd})

timecols = {om: [{"key": f"{om} ax d14", "label": "ax14"}] + [{"key": f"{om} cc d{d}", "label": f"cc{d}"} for d in (18, 31, 60, 89)]
            for om in ("protein", "RNA")}
CLASS_ORDER = ["ammonium", "urea", "cyanate", "nitrite", "nitrate", "peptides", "amino acids", "polyamines",
               "osmolytes", "amino sugars", "nucleobases/nucleosides"]
CATS = ["N dedicated", "linked enzymes", "markers", "N broad", "non-N reference", "other High/Medium"]

n_strict = sum(r["strict"] for r in ROWS)
DATA = {
    "cols": COLS, "rows": ROWS, "cells": CELLS, "genes": GENES, "geneCols": colkeys,
    "rowById": {r["id"]: r for r in ROWS}, "colByKey": {c["key"]: c for c in COLS},
    "categories": CATS, "classOrder": CLASS_ORDER, "timeCols": timecols,
    "playSeq": [f"protein cc d{d}" for d in (18, 31, 60, 89)] + [f"RNA cc d{d}" for d in (18, 31, 60, 89)],
    "intro": (f"<b>{len(ROWS)} rows</b> × <b>{len(COLS)} experiments</b>. The top of the default order is the N-starvation "
              f"response (markers, cyn, amt1, urease, urt, cynS). <b>{n_strict}</b> systems carry ★: try “Coculture-specific” "
              f"or “★ only”."),
    "playOutro": ("Protein: the N-starvation systems stay up on every coculture day, joined late by a cell-envelope group "
                  "(porin som, murJ, tolC, bamA). RNA: the N systems are mostly not up, because coculture RNA is "
                  "measured against an exponential phase that was already N-stressed."),
}

tpl = (A / "templates" / "system_explorer.template.html").read_text(encoding="utf-8")
out = tpl.replace("/*DATA*/null", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
(A / "system_explorer.html").write_text(out, encoding="utf-8")
print("rows", len(ROWS), "cols", len(COLS), "gene panels", len(GENES), "bytes", len(out))

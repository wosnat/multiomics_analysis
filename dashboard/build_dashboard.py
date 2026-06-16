"""Build the cross-analysis results dashboard (self-contained interactive HTML).

A repo-level presentation layer over the analyses in `analyses/`. Each analysis
contributes one section (a `Section`); the next analysis (characterization) plugs in
by appending another section builder to SECTIONS — no rework of existing ones.

This is a PRESENTATION artifact, not part of the 6-step research pipeline: it reads
each analysis's committed `data/*.csv` and renders interactive Plotly views + a
sortable/filterable shortlist table. The static paper figures remain the source of
record; this is an additional view.

Output: dashboard/index.html  (open in any browser; Plotly + DataTables via CDN)

Run (from repo root):
  uv run python dashboard/build_dashboard.py
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from scipy.cluster.hierarchy import leaves_list, linkage

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "index.html"
PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"
DT_CSS = "https://cdn.datatables.net/1.13.8/css/jquery.dataTables.min.css"
DT_JS = ["https://code.jquery.com/jquery-3.7.1.min.js",
         "https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"]


@dataclass
class Section:
    anchor: str
    title: str
    html: str


def _fig_html(fig) -> str:
    return pio.to_html(fig, full_html=False, include_plotlyjs=False,
                       default_height="520px", config={"displaylogo": False})


def _jitter(v, rng, w=0.18):
    return v + rng.uniform(-w, w, len(v))


def _cluster_order(mat: np.ndarray) -> list[int]:
    """Hierarchical leaf order for rows of mat (NaN filled with 0 for distance)."""
    if mat.shape[0] < 3:
        return list(range(mat.shape[0]))
    z = linkage(np.nan_to_num(mat, nan=0.0), method="average", metric="euclidean")
    return list(leaves_list(z))


def direction_clustermap_fig(hand: pd.DataFrame) -> go.Figure:
    """Filterable clustered direction-by-treatment heatmap (red=up, blue=down, grey=mixed).

    A dropdown toggles the family set (all shortlist / core 14 / by tier); each view is
    clustered independently. Treatments share one clustered order. NaN = no significant
    response (renders blank).
    """
    treatments = ["nitrogen", "carbon", "light", "phosphorus", "iron", "coculture",
                  "viral", "plastic", "darkness", "salt", "diel", "growth_phase",
                  "temperature"]
    code = {"up": 1, "down": -1, "mixed": 0}
    label = {1: "up", -1: "down", 0: "mixed"}

    def row_vec(dbt_str):
        dbt = ast.literal_eval(dbt_str) if isinstance(dbt_str, str) and dbt_str.startswith("{") else {}
        return [code.get(dbt.get(t)) for t in treatments]

    full = pd.DataFrame(
        [row_vec(s) for s in hand["direction_by_treatment"]],
        index=hand["og_id"].str.replace("cyanorak:", "", regex=False),
        columns=treatments).astype(float)
    full = full.dropna(axis=1, how="all")
    treatments = list(full.columns)
    # cluster treatments once (columns), on the full set
    col_order = _cluster_order(full.fillna(0).T.values)
    treatments = [treatments[i] for i in col_order]
    full = full[treatments]

    colorscale = [[0.0, "#3a7ca5"], [0.33, "#3a7ca5"], [0.33, "#cccccc"],
                  [0.66, "#cccccc"], [0.66, "#d1495b"], [1.0, "#d1495b"]]
    views = [
        ("All shortlist (85)", hand["og_id"].str.replace("cyanorak:", "", regex=False).tolist()),
        ("Core 14 (broad & prominent)",
         hand.loc[hand["core14"], "og_id"].str.replace("cyanorak:", "", regex=False).tolist()),
        ("Core tier (>=14 strains)",
         hand.loc[hand["tier"] == "core", "og_id"].str.replace("cyanorak:", "", regex=False).tolist()),
        ("Broad tier (9-13 strains)",
         hand.loc[hand["tier"] == "broad", "og_id"].str.replace("cyanorak:", "", regex=False).tolist()),
    ]
    fig = go.Figure()
    for vi, (name, ogs) in enumerate(views):
        sub = full.loc[[o for o in ogs if o in full.index]]
        order = _cluster_order(sub.values)
        sub = sub.iloc[order]
        text = [[label.get(v, "") if pd.notna(v) else "no sig. response" for v in row]
                for row in sub.values]
        fig.add_trace(go.Heatmap(
            z=sub.values, x=treatments, y=sub.index.tolist(),
            zmin=-1, zmax=1, colorscale=colorscale, showscale=False, xgap=1, ygap=1,
            text=text, hovertemplate="%{y} · %{x}<br>%{text}<extra></extra>",
            visible=(vi == 0)))

    buttons = []
    for vi, (name, _) in enumerate(views):
        vis = [j == vi for j in range(len(views))]
        buttons.append(dict(label=name, method="update",
                            args=[{"visible": vis},
                                  {"title": f"Direction by treatment — {name}"}]))
    fig.update_layout(
        title=f"Direction by treatment — {views[0][0]}",
        updatemenus=[dict(buttons=buttons, direction="down", showactive=True,
                          x=1.0, xanchor="right", y=1.16, yanchor="top")],
        xaxis=dict(side="bottom"), yaxis=dict(autorange="reversed"),
        margin=dict(t=70, l=120))
    return fig


def selection_section() -> Section:
    """Conserved hypothetical genes that are broadly DE (2026-06-16 analysis)."""
    a = ROOT / "analyses" / "2026-06-16-conserved_hypothetical_de"
    scores = pd.read_csv(a / "5_analyze" / "data" / "conserved_og_scores.csv")
    cov = pd.read_csv(a / "6_evaluate" / "data" / "coverage_confound.csv")
    hand = pd.read_csv(a / "6_evaluate" / "data" / "handoff_shortlist.csv")
    rng = np.random.default_rng(0)

    n_hyp = int(scores["is_hypothetical"].sum())
    n_core = int(hand["core14"].sum())
    summary = (f"<b>{n_hyp}</b> conserved hypothetical families scored against "
               f"<b>{len(scores) - n_hyp}</b> characterized conserved families; "
               f"<b>{len(hand)}</b> shortlisted (broad or prominent), "
               f"<b>{n_core}</b> both (core). Conserved hypotheticals respond about as "
               f"broadly as characterized conserved genes; breadth is coverage-"
               f"confounded (r=0.90), so prominence is the robust axis.")

    # --- Plot 1: breadth vs prominence, hypotheticals vs backdrop ---
    s = scores.copy()
    s["group"] = np.where(s["is_hypothetical"], "hypothetical", "characterized")
    s["prominence"] = pd.to_numeric(s["max_abs_log2fc"], errors="coerce").fillna(0).clip(upper=14)
    s["breadth_j"] = _jitter(s["breadth"].to_numpy(float), rng)
    fig1 = px.scatter(
        s, x="breadth_j", y="prominence", color="group",
        color_discrete_map={"hypothetical": "#d1495b", "characterized": "#9fb6c4"},
        opacity=0.55, hover_name="og_id",
        hover_data={"breadth": True, "prominence": ":.2f", "tier": True,
                    "proc_strains": True, "direction": True,
                    "dominant_category": True, "consensus_product": True,
                    "breadth_j": False, "group": False},
        labels={"breadth_j": "breadth (treatments responded, jittered)",
                "prominence": "prominence (max |log2FC|)"})
    fig1.update_layout(title="Breadth vs prominence — hypotheticals vs characterized "
                       "backdrop", legend_title="", margin=dict(t=50))

    # --- Plot 2: coverage confound ---
    c = cov.copy()
    c["breadth_j"] = _jitter(c["breadth"].to_numpy(float), rng)
    c["tested_j"] = _jitter(c["n_treatments_tested"].to_numpy(float), rng)
    fig2 = px.scatter(
        c, x="tested_j", y="breadth_j", color="tier",
        color_discrete_map={"core": "#16425b", "broad": "#5c9ccc"},
        opacity=0.6, hover_name="og_id",
        hover_data={"breadth": True, "n_treatments_tested": True,
                    "response_rate": ":.2f", "proc_strains": True,
                    "consensus_product": True, "breadth_j": False, "tested_j": False},
        labels={"tested_j": "treatments tested (coverage)",
                "breadth_j": "breadth (treatments responded)"})
    fig2.add_trace(go.Scatter(x=[0, 13], y=[0, 13], mode="lines",
                              line=dict(dash="dot", color="#999"), showlegend=False))
    fig2.update_layout(title="Coverage confound: breadth tracks how broadly a family "
                       "was measured (r=0.90)", legend_title="tier", margin=dict(t=50))

    # --- Plot 3: filterable direction clustermap ---
    fig3 = direction_clustermap_fig(hand)
    fig3.update_layout(height=780)

    # --- Shortlist table (DataTables) ---
    tcols = ["og_id", "core14", "tier", "proc_strains", "dominant_category",
             "consensus_product", "breadth", "n_treatments_tested", "response_rate",
             "best_rank", "max_abs_log2fc", "direction"]
    tdf = hand[tcols].copy()
    tdf["response_rate"] = tdf["response_rate"].round(2)
    tdf["core14"] = tdf["core14"].map({True: "★", False: ""})
    table_html = tdf.to_html(table_id="shortlist", classes="display compact",
                             index=False, escape=True, border=0)

    body = f"""
      <p class="summary">{summary}</p>
      <h3>Breadth vs prominence</h3>
      {_fig_html(fig1)}
      <h3>Coverage confound</h3>
      {_fig_html(fig2)}
      <h3>Direction by treatment (clustered, filterable)</h3>
      <p class="note">Red = up, blue = down, grey = mixed, blank = no significant
        response. Use the dropdown (top-right of the plot) to filter the family set.</p>
      {_fig_html(fig3)}
      <h3>Shortlist ({len(hand)} families; ★ = core 14 broad &amp; prominent)</h3>
      <p class="note">Sort any column; use the search box to filter (e.g. type
        "secreted" or "core").</p>
      {table_html}
    """
    return Section("selection", "Selection — conserved hypothetical genes broadly "
                   "differentially expressed", body)


def placeholder_characterization() -> Section:
    body = ("<p class='summary'>Reserved for the follow-on <i>characterization</i> "
            "analysis (homologs, genomic neighbourhood, co-expression, ontology of "
            "neighbours) which takes this shortlist as input. Its section will be "
            "appended here when that analysis runs.</p>")
    return Section("characterization", "Characterization (follow-on — pending)", body)


SECTIONS = [selection_section, placeholder_characterization]


def main() -> None:
    sections = [b() for b in SECTIONS]
    nav = " · ".join(f'<a href="#{s.anchor}">{s.title.split(" — ")[0]}</a>'
                     for s in sections)
    blocks = "\n".join(
        f'<section id="{s.anchor}"><h2>{s.title}</h2>{s.html}</section>'
        for s in sections)
    dt_js = "\n".join(f'<script src="{u}"></script>' for u in DT_JS)
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Multi-omics KG — results dashboard</title>
<script src="{PLOTLY_CDN}"></script>
<link rel="stylesheet" href="{DT_CSS}">
{dt_js}
<style>
  body {{ font-family: system-ui, sans-serif; margin: 0; color: #1a1a1a; }}
  header {{ background: #16425b; color: #fff; padding: 18px 28px; }}
  header h1 {{ margin: 0 0 4px; font-size: 20px; }}
  nav {{ padding: 10px 28px; background: #eef2f5; font-size: 14px; }}
  nav a {{ color: #16425b; text-decoration: none; margin-right: 6px; }}
  section {{ padding: 22px 28px; border-bottom: 1px solid #e3e8ec; }}
  h2 {{ color: #16425b; }}
  h3 {{ margin-top: 26px; color: #3a7ca5; }}
  .summary {{ background: #f7f9fb; border-left: 4px solid #3a7ca5; padding: 10px 14px;
              border-radius: 4px; max-width: 1000px; }}
  .note {{ color: #666; font-size: 13px; }}
  table.dataTable {{ font-size: 13px; }}
  footer {{ padding: 16px 28px; color: #888; font-size: 12px; }}
</style></head>
<body>
<header><h1>Multi-omics knowledge graph — results dashboard</h1>
  <div>Interactive view over the analyses in <code>analyses/</code>. Static paper
  figures remain the source of record.</div></header>
<nav>{nav}</nav>
{blocks}
<footer>Generated by <code>dashboard/build_dashboard.py</code>. Plotly + DataTables via CDN.</footer>
<script>
  document.addEventListener("DOMContentLoaded", function () {{
    if (window.jQuery && jQuery.fn.dataTable) {{
      jQuery("#shortlist").DataTable({{ pageLength: 14, order: [[1, "desc"]] }});
    }}
  }});
</script>
</body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"[out] wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB), "
          f"{len(sections)} sections")


if __name__ == "__main__":
    main()

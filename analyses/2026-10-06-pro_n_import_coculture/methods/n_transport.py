"""n_transport — organism-agnostic transport-system reconstruction (pure functions).

Implements proposal.md §3.2 logic on pandas DataFrames. NO KG access here: fetching lives in
methods/scripts/*.py. Every function accepts data in the form a CSV written by
`multiomics_explorer.to_dataframe(...).to_csv(index=False)` comes back from `pd.read_csv`:
  - booleans may be real bools OR the strings "True"/"False"  -> always go through `to_bool`
  - missing values are NaN                                     -> treated as absent
  - list columns are joined by " | " (to_dataframe convention) -> always go through `parse_list`

Version: 1.6.1 (efflux_annotated flag; tightened class keywords; Q-only dedicated not on efflux systems; MAPEG FP).
1.6.0: Cyanorak Q roles: universe source + lift superfamily-only; listing_basis dedicated/broad.
1.5.0: grouping Rule A3 adjacent_abc; known false positives gst + sodX. 1.4.0: KO + Cyanorak bases upgrade
tcdb_only only; catalogue-only tier Low; fragments; name rules.
"""
from __future__ import annotations

import ast
import math
from collections import defaultdict

import pandas as pd

__version__ = "1.6.1"

# --------------------------------------------------------------------------- constants
#: Pfam accession -> subunit role. Seed set from proposal §3.2 / proposal_notebook item 14.
#: Domains give ROLES, never substrates (the urt domains are named for branched-chain amino acids).
PFAM_ROLE_MAP: dict[str, str] = {
    # substrate-binding proteins
    "PF13379": "substrate_binding",  # NMT1-like family (cynA)
    "PF09084": "substrate_binding",  # NMT1/THI5 like (cynA)
    "PF13433": "substrate_binding",  # periplasmic binding protein (urtA)
    "PF00496": "substrate_binding",  # SBP bacterial family 5 (dppA)
    # permeases (ABC transmembrane)
    "PF00528": "permease",  # BPD_transp_1 (cynB, dppB, dppC)
    "PF02653": "permease",  # BPD_transp_2, branched-chain AA permease (urtB)
    "PF19300": "permease",  # dppB-associated N-terminal domain
    # ATPases and ATPase-associated domains
    "PF00005": "atpase",  # ABC_tran
    "PF12399": "atpase",  # branched-chain AA ABC transporter C-term (urtD)
    "PF08352": "atpase",  # oligopeptide/dipeptide transporter C-term (ddpD)
    # single-gene carriers
    "PF00909": "single_carrier",  # Ammonium transporter (amt1)
    "PF03616": "single_carrier",  # Na+/glutamate symporter (gltS)
}

TRANSPORTER_ROLES = ("substrate_binding", "permease", "atpase", "single_carrier")

#: TCDB classes that count as evidence of being a transporter in `likely_transporter`.
#: 1 channels/pores, 2 electrochemical-potential-driven carriers, 3 primary active transporters.
#: Excluded: 4 group translocators (includes acyl-CoA ligase-coupled 4.C -> fadD-like enzymes),
#: 5 transmembrane electron carriers, 8 accessory factors, 9 incompletely characterized.
TCDB_TRANSPORTER_CLASSES = ("1", "2", "3")

_TRUE = {"true", "t", "1", "yes", "y"}
_FALSE = {"false", "f", "0", "no", "n", "", "nan", "none"}


# --------------------------------------------------------------------------- parsing helpers
def _isna(x) -> bool:
    if x is None:
        return True
    if isinstance(x, float) and math.isnan(x):
        return True
    try:
        return bool(pd.isna(x)) if not isinstance(x, (list, tuple, set)) else False
    except (TypeError, ValueError):
        return False


def to_bool(x) -> bool:
    """Parse a boolean that may have round-tripped through CSV.

    Rule: real bools pass through; NaN/None/"" -> False; strings matched case-insensitively
    against {"true","t","1","yes","y"} / {"false","f","0","no","n"}; numbers -> x != 0;
    any other string raises ValueError (never guess).
    Example: to_bool("False") -> False   (whereas bool("False") is True — the round-1 bug).
    """
    if isinstance(x, bool):
        return x
    if _isna(x):
        return False
    if isinstance(x, (int, float)):
        return x != 0
    s = str(x).strip().lower()
    if s in _TRUE:
        return True
    if s in _FALSE:
        return False
    raise ValueError(f"cannot parse boolean from {x!r}")


def parse_list(x) -> list[str]:
    """Normalise a list-like cell to a list of stripped strings.

    Accepts a real list/tuple/set, a to_dataframe-joined string "a | b", a stringified Python
    list "['a', 'b']", a single scalar string, or NaN/None/"" (-> []).
    Example: parse_list("pfam:PF00528 | pfam:PF19300") -> ["pfam:PF00528", "pfam:PF19300"]
    """
    if isinstance(x, (list, tuple, set)):
        return [str(v).strip() for v in x if not _isna(v) and str(v).strip()]
    if _isna(x):
        return []
    s = str(x).strip()
    if not s:
        return []
    if s.startswith("[") and s.endswith("]"):
        try:
            return parse_list(list(ast.literal_eval(s)))
        except (ValueError, SyntaxError):
            s = s[1:-1]
    return [p.strip().strip("'\"") for p in s.split("|") if p.strip()]


def _pfam_acc(term: str) -> str:
    """'pfam:PF00528' -> 'PF00528'; strips a version suffix 'PF00528.24' -> 'PF00528'."""
    t = term.split(":", 1)[1] if term.lower().startswith("pfam:") else term
    return t.split(".")[0].upper()


def _tcdb_fields(term_id: str) -> list[str]:
    t = term_id[5:] if term_id.lower().startswith("tcdb:") else term_id
    return [f for f in t.split(".") if f]


def tcdb_level(term_id: str) -> int:
    """TCDB hierarchy level from the id: number of dotted fields - 1.

    tcdb.md: 3 = class (0), 3.A = subclass (1), 3.A.1 = family (2), 3.A.1.2 = subfamily (3),
    3.A.1.2.3 = specificity (4).  Example: tcdb_level("tcdb:3.A.1.16.1") -> 4.
    """
    return len(_tcdb_fields(term_id)) - 1


def tcdb_ancestor(term_id: str, level: int) -> str | None:
    """The id truncated to `level` (CURIE form), or None if the id is shallower than `level`.

    Example: tcdb_ancestor("tcdb:3.A.1.16.1", 3) -> "tcdb:3.A.1.16"; tcdb_ancestor("tcdb:3.A.1", 3) -> None.
    """
    f = _tcdb_fields(term_id)
    if len(f) - 1 < level:
        return None
    return "tcdb:" + ".".join(f[: level + 1])


def _tcdb_class(term_id: str) -> str | None:
    f = _tcdb_fields(term_id)
    return f[0] if f else None


def _get(row, key, default=None):
    """Field access that works for a pandas Series, a namedtuple (itertuples) or a dict."""
    if isinstance(row, dict):
        return row.get(key, default)
    if isinstance(row, pd.Series):
        return row[key] if key in row.index else default
    return getattr(row, key, default)


# --------------------------------------------------------------------------- roles
def pfam_role(pfam_ids, role_map: dict | None = None) -> str:
    """Subunit role of a gene from its Pfam domains, via PFAM_ROLE_MAP.

    Rule: map every Pfam accession; collect the distinct transporter roles hit.
      0 roles -> "other"; exactly 1 -> that role; >1 distinct roles -> "mixed" (surfaced, not
      resolved: e.g. a fused binding+ATPase protein).
    Several domains of the same role (dppB PF00528 + PF19300) count as one role.
    role_map: accession -> role; default PFAM_ROLE_MAP (the 12-accession seed). Pilot step 2 passes
    the data-built map. Roles "other" in the map count as no role.
    Example: pfam_role("pfam:PF00005 | pfam:PF08352") -> "atpase"; pfam_role([]) -> "other".
    """
    m = PFAM_ROLE_MAP if role_map is None else role_map
    roles = {m.get(_pfam_acc(p)) for p in parse_list(pfam_ids)} - {None, "other"}
    if not roles:
        return "other"
    if len(roles) == 1:
        return roles.pop()
    return "mixed"


# --------------------------------------------------------------------------- data-built Pfam role map
#: Ordered name rules for Pfam domains (pilot step 2). First match wins; case-insensitive regex
#: on the Pfam NAME. Seeds (PFAM_ROLE_MAP) override these in build_pfam_role_map.
#: Order matters:
#:  enzyme_guard first  - enzyme words beat transport words ("LON protease substrate-binding
#:                        domain", "NADH:quinone oxidoreductase/Mrp antiporter" -> other);
#:  substrate_binding   - before atpase ("ABC transporter, phosphonate, periplasmic substrate-binding")
#:                        and written so "Binding-protein-dependent" does NOT match;
#:  single_carrier      - named carrier families, before permease ("Sulfate permease family" = SulP);
#:  permease            - ABC/TMD permease names, before atpase ("ABC transporter transmembrane region");
#:  atpase              - ABC NBD names; TOBE = transport-associated OB domain of ABC ATPases.
PFAM_NAME_RULES: list[tuple[str, str, str]] = [
    ("enzyme_guard", "other",
     r"protease|peptidase|synthase|synthetase|dehydrogenase|oxidoreductase|reductase|transferase|"
     r"helicase|kinase"),
    ("substrate_binding", "substrate_binding",
     r"solute[- ]binding|substrate[- ]binding|periplasmic binding|PBP superfamily|NMT1|"
     r"uptake complex component A periplasmic"),
    ("single_carrier", "single_carrier",
     r"Ammonium Transporter|Major Facilitator|\bMFS\b|Sugar \(and other\) transporter|symporter|"
     r"antiporter|exchanger|uniporter|Sulfate permease family|Citrate transporter|"
     r"bicarbonate transporter|Divalent cation transporter|Cation transport protein|"
     r"Chromate transporter|Membrane transport protein|AI-2E family transporter|"
     r"EamA-like transporter|Sulfite exporter|channel|porin|HupE / UreJ"),
    ("permease", "permease",
     r"permease|inner membrane component|membrane comp\b|transmembrane region|ABC[- ]2|"
     r"ABC 3 transport|FtsX|MacB-like periplasmic core"),
    ("atpase", "atpase",
     r"^ABC transporter$|ATP-binding cassette|^ABC transporter,|ATP-binding protein DrrA|TOBE domain"),
]


def pfam_name_role(pfam_name) -> tuple[str, str, str]:
    """Role of a Pfam domain from its NAME by PFAM_NAME_RULES (first match wins).

    Returns (role, rule_matched, matched_text). No match -> ("other", "no_match", "").
    Example: pfam_name_role("ATP-dependent protease La (LON) substrate-binding domain")
             -> ("other", "enzyme_guard", "protease").
    """
    import re
    name = "" if _isna(pfam_name) else str(pfam_name)
    for rule, role, pat in PFAM_NAME_RULES:
        m = re.search(pat, name, flags=re.IGNORECASE)
        if m:
            return role, rule, m.group(0)
    return "other", "no_match", ""


def build_pfam_role_map(domains_df: pd.DataFrame, seed: dict | None = None) -> pd.DataFrame:
    """Role per Pfam domain: seed accession overrides, else the ordered name rule.

    domains_df: columns pfam_id (e.g. "pfam:PF00528"), pfam_name (other columns kept).
    Output adds: name_rule_role, name_rule, name_rule_text (what the name rule alone says),
      seed_role (NaN if not a seed), role (final), rule_matched ("seed" or the name rule),
      seed_conflict (seed present and seed_role != name_rule_role).
    Example: PF08352 "Oligopeptide/dipeptide transporter, C-terminal region": name rule -> other,
             seed -> atpase => role atpase, rule_matched seed, seed_conflict True.
    """
    seed = PFAM_ROLE_MAP if seed is None else seed
    m = domains_df.copy()
    nr = m["pfam_name"].map(pfam_name_role)
    m["name_rule_role"] = nr.map(lambda x: x[0])
    m["name_rule"] = nr.map(lambda x: x[1])
    m["name_rule_text"] = nr.map(lambda x: x[2])
    m["seed_role"] = m["pfam_id"].map(lambda p: seed.get(_pfam_acc(p)))
    has_seed = m["seed_role"].notna()
    m["role"] = m["seed_role"].where(has_seed, m["name_rule_role"])
    m["rule_matched"] = m["name_rule"].where(~has_seed, "seed")
    m["seed_conflict"] = has_seed & (m["seed_role"] != m["name_rule_role"])
    return m


def role_map_dict(role_map_df: pd.DataFrame) -> dict:
    """{accession without prefix: role} from build_pfam_role_map output, for pfam_role(role_map=)."""
    return {_pfam_acc(p): r for p, r in zip(role_map_df["pfam_id"], role_map_df["role"])}


# --------------------------------------------------------------------------- coordinates
def adjacent_gaps(genes_df: pd.DataFrame) -> pd.DataFrame:
    """Intergenic gap from each gene to the next gene on the same contig (by start).

    Needs columns locus_tag, contig, start, end. Returns a copy sorted by (contig, start) with
      next_locus_tag : next gene on the contig (NaN for the last gene)
      gap_to_next    : next.start - this.end - 1  (bp strictly between, 1-based inclusive coords;
                       NEGATIVE = overlap length; NaN for the last gene; no circular wrap).
    This is NOT gene_neighbors.bp_gap, which is the distance to the ANCHOR gene (and is clamped
    at 0 for overlaps).
    Example: cynA end 354660, cynB start 354691 -> 354691 - 354660 - 1 = 30.
    """
    g = genes_df.copy()
    g["start"] = pd.to_numeric(g["start"])
    g["end"] = pd.to_numeric(g["end"])
    g = g.sort_values(["contig", "start", "end", "locus_tag"]).reset_index(drop=True)
    nxt_start = g.groupby("contig")["start"].shift(-1)
    g["next_locus_tag"] = g.groupby("contig")["locus_tag"].shift(-1)
    g["gap_to_next"] = nxt_start - g["end"] - 1
    return g


def runs(genes_df: pd.DataFrame, max_gap_bp: int, same_strand: bool = True,
         max_interlopers: int = 1) -> pd.DataFrame:
    """Assign contiguous-gene run ids.

    Pass ALL genes of the region (not only transporters): adjacency is judged on the genome.
    Steps (per contig, genes sorted by start):
      1. blocks  = maximal chains where every adjacent gap_to_next <= max_gap_bp (any strand).
      2. same_strand=False -> run = block.
         same_strand=True  -> split each block into consecutive same-strand segments. Two segments
         of the same strand separated by ONE opposite-strand segment of <= max_interlopers genes
         are merged into one run; the interloper genes keep their own run but are flagged
         opposite_strand_in_run=True with inside_run_id = the bracketing run (surfaced, never
         auto-added — e.g. MED4 ureD on − inside the + urease/urt cluster).
    Output columns added: run_id ("run_<first locus_tag>"), run_size, opposite_strand_in_run
    (bool), inside_run_id (NaN unless flagged), plus those of adjacent_gaps.
    Example (toy): + + − + + with gaps <= max_gap -> the four + genes form one run, the − gene is
    flagged inside it.
    """
    g = adjacent_gaps(genes_df)
    run_of = {}
    inside = {}
    for _, cg in g.groupby("contig", sort=False):
        tags = cg["locus_tag"].tolist()
        strands = cg["strand"].tolist()
        gaps = cg["gap_to_next"].tolist()
        # 1. blocks
        blocks, cur = [], [0]
        for i in range(1, len(tags)):
            if gaps[i - 1] <= max_gap_bp:
                cur.append(i)
            else:
                blocks.append(cur)
                cur = [i]
        blocks.append(cur)
        for b in blocks:
            if not same_strand:
                for i in b:
                    run_of[tags[i]] = tags[b[0]]
                continue
            # 2. same-strand segments
            segs = []
            for i in b:
                if segs and strands[segs[-1][-1]] == strands[i]:
                    segs[-1].append(i)
                else:
                    segs.append([i])
            seg_run = list(range(len(segs)))  # union pointer per segment
            for k in range(1, len(segs) - 1):
                s_prev, mid, s_next = segs[k - 1], segs[k], segs[k + 1]
                if (strands[s_prev[0]] == strands[s_next[0]] and len(mid) <= max_interlopers):
                    seg_run[k + 1] = seg_run[k - 1]
                    for i in mid:
                        inside[tags[i]] = k - 1  # resolved to a run id below
            # resolve chained merges (A - x - B - y - C)
            for k in range(len(segs)):
                r = k
                while seg_run[r] != r:
                    r = seg_run[r]
                seg_run[k] = r
            first_tag = {}
            for k, seg in enumerate(segs):
                root = seg_run[k]
                first_tag.setdefault(root, tags[segs[root][0]])
                for i in seg:
                    run_of[tags[i]] = first_tag[root]
            for t, k in list(inside.items()):
                if isinstance(k, int):
                    inside[t] = "run_" + first_tag[seg_run[k]]
    g["run_id"] = "run_" + g["locus_tag"].map(run_of)
    g["run_size"] = g.groupby("run_id")["locus_tag"].transform("count")
    g["opposite_strand_in_run"] = g["locus_tag"].isin(inside.keys())
    g["inside_run_id"] = g["locus_tag"].map(inside)
    return g


def attach_runs(t: pd.DataFrame, runs_indexed: pd.DataFrame) -> pd.DataFrame:
    """Attach run_id / opposite_strand_in_run / gap_to_next from runs() output (indexed by locus_tag).

    A gene absent from the runs table (no coordinates in the KG) is KEPT: run_id "nocoord_<locus>"
    (its own pseudo-run), has_coordinates False, opposite_strand_in_run False, gap_to_next NaN.
    It can still join a system cross-locus by the usual rule, never within a run.
    """
    t = t.copy()
    has = t["locus_tag"].isin(runs_indexed.index)
    t["has_coordinates"] = has
    t["run_id"] = t["locus_tag"].map(runs_indexed["run_id"]).where(has, "nocoord_" + t["locus_tag"])
    t["opposite_strand_in_run"] = t["locus_tag"].map(runs_indexed["opposite_strand_in_run"]).map(to_bool)         .where(has, False)
    t["gap_to_next"] = t["locus_tag"].map(runs_indexed["gap_to_next"])
    for c in ("next_locus_tag", "strand"):   # v1.5: adjacency for group_systems Rule A3
        if c in runs_indexed.columns:
            t[c] = t["locus_tag"].map(runs_indexed[c])
    return t


# --------------------------------------------------------------------------- systems
class _UF:
    def __init__(self, items):
        self.p = {i: i for i in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            ra, rb = sorted((ra, rb))
            self.p[rb] = ra


def _ancestors(tcdb_ids, level):
    return {a for a in (tcdb_ancestor(t, level) for t in parse_list(tcdb_ids)) if a}


def _role_complete(roles: set) -> bool:
    """Complete = a single carrier, OR a 'mixed' gene (fused ATPase + membrane domain; coordinator
    rule 2026-10-07), OR binding + permease + ATPase."""
    return ("single_carrier" in roles or "mixed" in roles
            or {"substrate_binding", "permease", "atpase"} <= roles)


ABC_ROLES = ("substrate_binding", "permease", "atpase")


def group_systems(transporter_df: pd.DataFrame, cross_locus: bool = True,
                  within_run_min_level: int = 3, cross_locus_min_level: int = 3,
                  join_within_run_by_role: bool = True, role_join_min_level: int = 2,
                  return_edges: bool = False, join_adjacent_abc: bool = True,
                  adjacent_max_gap_bp: int = 200):
    """Group transporter genes into systems.

    Input columns: locus_tag, run_id, role (from pfam_role), tcdb_ids (list or " | " string).
    Rule A (within run, TCDB): two genes in the same run join if their TCDB attachments share an
      ancestor at level >= within_run_min_level (default 3 = subfamily, e.g. tcdb:3.A.1.16).
      joined_by label: "tcdb_level3".
    Rule A2 (within run, role; ONLY if join_within_run_by_role=True): after Rule A, two systems in
      the SAME run merge if both consist only of ABC roles (binding/permease/atpase), their role
      sets are DISJOINT (complementary), and they share a TCDB ancestor at level >=
      role_join_min_level (default 2, i.e. the superfamily tcdb:3.A.1 suffices). Repeated until
      stable, pairs visited in sorted order (deterministic). Reason: in real cassettes the ATPase
      often reaches only the superfamily. joined_by label: "role".
      Example: {binding, permease} sharing 3.A.1.7 + an ATPase at tcdb:3.A.1 only, same run -> one.
      A superfamily-only permease beside a system that already has a permease does NOT join.
    Rule A3 (within run, adjacency; v1.5.0, researcher-approved 2026-10-08; ONLY if join_adjacent_abc
      and the input carries strand, next_locus_tag, gap_to_next from runs()): after A2, the systems
      of two IMMEDIATELY adjacent genes a, b (b == next_locus_tag[a]: no intervening gene of the
      genome; gap_to_next[a] <= adjacent_max_gap_bp; same strand; same run) merge, even when their
      role sets overlap, if (i) both systems consist only of ABC roles, OR one consists only of ABC
      roles and the other is a single gene of role 'other' with likely_transporter == "strong";
      (ii) the two systems share a TCDB ancestor at level >= role_join_min_level (superfamily, e.g.
      tcdb:3.A.1); (iii) they are NOT both binding+permease+ATPase complete. Repeated until stable.
      joined_by label "adjacent_abc". Examples: MED4 evrC PMM0978 (second permease) joins evrA/evrB;
      devB PMM0748 (HlyD-family MFP, role 'other', strong, tcdb:3.A.1) joins devC/devA.
      The MFP stays role 'other' (no new role-map role): a 'membrane_fusion' role would change the
      Pfam basis of likely_transporter for every HlyD-family gene, which is a wider change.
    Rule B (cross locus; ONLY if cross_locus=True): two systems in different runs merge if
      (i) they share a TCDB ancestor at level >= cross_locus_min_level, (ii) NEITHER is
      role-complete (binding+permease+ATPase, or a single carrier), and (iii) their role sets
      differ (the union adds a role to at least one of them), and (iv) NEITHER consists only of
      role 'other' genes. A 'mixed' gene counts as role-complete (ii). (iii)/(iv) and the mixed rule
      were added after the pilot showed six fused exporters chained through one 'other' gene (sodX).
      Applied pairwise, then
      transitively (union-find). The dpp case: {dppA,dppB}{dppC}{ddpD} share tcdb:3.A.1.5.
      No cap: every merge is exposed (cross_locus_merged, n_runs, member_runs). Label "cross_locus".
    Output: input columns + system_id ("sys_<min locus_tag>"), cross_locus_merged (bool),
      n_runs, member_runs (sorted run ids "|"-joined), system_roles ("|"-joined sorted),
      joined_by (sorted distinct labels of the joins used in the system; "" = one gene).
    return_edges=True -> (frame, edges) where edges has one row per qualifying pair:
      a, b (locus tags; for role/cross_locus the component roots), label, shared (the shared TCDB
      ancestors, "|"-joined), system_id. Rule-B rows list EVERY qualifying pair, including pairs
      already joined through a third piece, so chaining is visible.
    """
    t = transporter_df.copy().reset_index(drop=True)
    tags = t["locus_tag"].tolist()
    role = dict(zip(t["locus_tag"], t["role"]))
    run = dict(zip(t["locus_tag"], t["run_id"]))
    anc_w = {r.locus_tag: _ancestors(r.tcdb_ids, within_run_min_level) for r in t.itertuples()}
    uf = _UF(tags)
    edges = []  # (gene_a, gene_b, label)
    lab_a = f"tcdb_level{within_run_min_level}"

    def components():
        g = defaultdict(list)
        for x in tags:
            g[uf.find(x)].append(x)
        return dict(sorted(g.items()))

    # Rule A
    for _, rg in t.groupby("run_id"):
        members = sorted(rg["locus_tag"])
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                if anc_w[a] & anc_w[b]:
                    uf.union(a, b)
                    edges.append((a, b, lab_a, "|".join(sorted(anc_w[a] & anc_w[b]))))
    # Rule A2
    if join_within_run_by_role:
        anc_r = {r.locus_tag: _ancestors(r.tcdb_ids, role_join_min_level) for r in t.itertuples()}
        changed = True
        while changed:
            changed = False
            comps = components()
            by_run = defaultdict(list)
            for root, mem in comps.items():
                runs_ = {run[m] for m in mem}
                if len(runs_) == 1:
                    by_run[runs_.pop()].append(root)
            for _, roots in sorted(by_run.items()):
                for i, ra in enumerate(roots):
                    for rb in roots[i + 1:]:
                        rla = {role[m] for m in comps[ra]}
                        rlb = {role[m] for m in comps[rb]}
                        if not (rla <= set(ABC_ROLES) and rlb <= set(ABC_ROLES)) or rla & rlb:
                            continue
                        aa = set().union(*(anc_r[m] for m in comps[ra]))
                        ab = set().union(*(anc_r[m] for m in comps[rb]))
                        if aa & ab:
                            uf.union(ra, rb)
                            edges.append((ra, rb, "role", "|".join(sorted(aa & ab))))
                            changed = True
                            break
                    if changed:
                        break
                if changed:
                    break
    # Rule A3
    adj_cols = {"strand", "next_locus_tag", "gap_to_next"}
    if join_adjacent_abc and adj_cols <= set(t.columns):
        anc_j = {r.locus_tag: _ancestors(r.tcdb_ids, role_join_min_level) for r in t.itertuples()}
        strand = dict(zip(t["locus_tag"], t["strand"]))
        nxt = dict(zip(t["locus_tag"], t["next_locus_tag"]))
        gapn = dict(zip(t["locus_tag"], pd.to_numeric(t["gap_to_next"], errors="coerce")))
        strong = dict(zip(t["locus_tag"], t["likely_transporter"])) if "likely_transporter" in t.columns else {}
        tagset = set(tags)
        pairs = sorted((a, nxt[a]) for a in tags
                       if not _isna(nxt[a]) and nxt[a] in tagset and run[a] == run[nxt[a]]
                       and not _isna(strand[a]) and strand[a] == strand[nxt[a]]
                       and not _isna(gapn[a]) and gapn[a] <= adjacent_max_gap_bp)
        abc = set(ABC_ROLES)
        def strong_other(mem, rl):
            return len(mem) == 1 and rl == {"other"} and strong.get(mem[0]) == "strong"
        # pass 1: ABC + ABC pieces until stable; pass 2: a strong 'other' gene onto an ABC-only system
        # (order-independent: e.g. MIT9313 PMT1573 'other' + PMT1574/PMT1575 permeases)
        for allow_other in (False, True):
            changed = True
            while changed:
                changed = False
                comps = components()
                for a, b in pairs:
                    ra, rb = uf.find(a), uf.find(b)
                    if ra == rb:
                        continue
                    ma, mb = comps[ra], comps[rb]
                    rla, rlb = {role[m] for m in ma}, {role[m] for m in mb}
                    ok = (rla <= abc and rlb <= abc) or (allow_other and (
                        (rla <= abc and strong_other(mb, rlb)) or (rlb <= abc and strong_other(ma, rla))))
                    if not ok or (abc <= rla and abc <= rlb):
                        continue
                    sh = set().union(*(anc_j[m] for m in ma)) & set().union(*(anc_j[m] for m in mb))
                    if not sh:
                        continue
                    uf.union(ra, rb)
                    edges.append((ra, rb, "adjacent_abc", "|".join(sorted(sh))))
                    changed = True
                    break
    # Rule B
    if cross_locus:
        anc_x = {r.locus_tag: _ancestors(r.tcdb_ids, cross_locus_min_level) for r in t.itertuples()}
        sysinfo = []
        for root, mem in components().items():
            sysinfo.append((root, {role[m] for m in mem}, set().union(*(anc_x[m] for m in mem)),
                            {run[m] for m in mem}))
        for i, (ra, rolea, anca, runsa) in enumerate(sysinfo):
            for rb, roleb, ancb, runsb in sysinfo[i + 1:]:
                if runsa & runsb or not (anca & ancb):
                    continue
                if _role_complete(rolea) or _role_complete(roleb):
                    continue
                if rolea <= {"other"} or roleb <= {"other"}:
                    continue  # all-'other' pieces never join cross-locus (sodX / cbiQ chains)
                union = rolea | roleb
                if union == rolea and union == roleb:
                    continue
                uf.union(ra, rb)
                edges.append((ra, rb, "cross_locus", "|".join(sorted(anca & ancb))))
    roots = {x: uf.find(x) for x in tags}
    members = defaultdict(list)
    for x, r in roots.items():
        members[r].append(x)
    labels = defaultdict(set)
    for a, _, lab, _sh in edges:
        labels[uf.find(a)].add(lab)
    t["system_id"] = t["locus_tag"].map(lambda x: "sys_" + min(members[roots[x]]))
    t["cross_locus_merged"] = t["locus_tag"].map(lambda x: "cross_locus" in labels[roots[x]])
    t["joined_by"] = t["locus_tag"].map(lambda x: "|".join(sorted(labels[roots[x]])))
    t["n_runs"] = t.groupby("system_id")["run_id"].transform("nunique")
    t["member_runs"] = t.groupby("system_id")["run_id"].transform(lambda s: "|".join(sorted(set(s))))
    t["system_roles"] = t.groupby("system_id")["role"].transform(lambda s: "|".join(sorted(set(s))))
    if not return_edges:
        return t
    e = pd.DataFrame(edges, columns=["a", "b", "label", "shared"])
    e["system_id"] = e["a"].map(lambda x: "sys_" + min(members[roots[x]]))
    return t, e


# --------------------------------------------------------------------------- neighbours
def _has_role_pfam(pfam_ids, role_map=None) -> bool:
    return pfam_role(pfam_ids, role_map) in TRANSPORTER_ROLES + ("mixed",)


def recruited_by(row, role_map: dict | None = None) -> str | None:
    """Why a neighbour qualifies as a transporter-like gene: "pfam", "ko", "pfam+ko" or None.

    pfam = a Pfam in PFAM_ROLE_MAP (`pfam_ids`); ko = truthy `brite_transporter` (the gene's KO
    sits in the BRITE transporters tree; computed upstream, passed as data).
    """
    p = _has_role_pfam(_get(row, "pfam_ids"), role_map)
    k = to_bool(_get(row, "brite_transporter"))
    if p and k:
        return "pfam+ko"
    if p:
        return "pfam"
    if k:
        return "ko"
    return None


def classify_neighbour(row, role_map: dict | None = None) -> str:
    """Classify a genome neighbour of a system (proposal §3.2 step 2; pilot step 4).

    Row fields: pfam_ids, brite_transporter (bool-ish), tcdb_ids, is_linked_enzyme (bool-ish; set
    in step 5 against the system's substrates), is_enzyme_candidate (bool-ish: has EC or KEGG
    metabolism-arm reactions), has_coordinates (bool-ish; absent/NaN -> True).
    Precedence:
      1. has_coordinates False        -> "no_coordinates" (never dropped; position approximate)
      1b. member_of_system non-empty  -> "other_system" (candidate is a member of another system)
      2. has any TCDB call            -> "tcdb_transporter"
      3. recruited_by(row) not None   -> "missing_subunit" (role Pfam or BRITE KO, no TCDB)
      4. to_bool(is_linked_enzyme)    -> "linked_enzyme"   (attached, never pooled; step 5)
      5. to_bool(is_enzyme_candidate) -> "enzyme_candidate"
      6. otherwise                    -> "context"
    Example: Pfam PF00005, no TCDB, brite "False" -> "missing_subunit".
    """
    hc = _get(row, "has_coordinates")
    if not _isna(hc) and not to_bool(hc):
        return "no_coordinates"
    mos = _get(row, "member_of_system")
    if not _isna(mos) and str(mos).strip():
        return "other_system"
    if parse_list(_get(row, "tcdb_ids")):
        return "tcdb_transporter"
    if recruited_by(row, role_map) is not None:
        return "missing_subunit"
    if to_bool(_get(row, "is_linked_enzyme")):
        return "linked_enzyme"
    if to_bool(_get(row, "is_enzyme_candidate")):
        return "enzyme_candidate"
    return "context"


def neighbour_candidates(genome_runs: pd.DataFrame, members_df: pd.DataFrame, window: int) -> pd.DataFrame:
    """Genes within +-window genes (genome order, same contig) of any member of each system.

    genome_runs: ALL genes with coordinates, runs() output (locus_tag, contig, start, end, strand,
      run_id, opposite_strand_in_run, inside_run_id). members_df: locus_tag, system_id.
    One row per (system_id, candidate); members of that system are excluded. Fields:
      nearest_member  = member with the smallest |rank difference| (ties: smaller bp gap, then tag)
      rank_offset     = candidate index - nearest member index (signed; + = downstream by start)
      gap_to_nearest_member = bp strictly between the two genes (cand after member:
                        cand.start - member.end - 1; before: member.start - cand.end - 1;
                        negative = overlap). NOT gene_neighbors.bp_gap.
      same_strand     = candidate strand == nearest member strand
      in_system_run   = candidate run_id is one of the system members' runs
      opposite_strand_interloper = candidate flagged opposite_strand_in_run AND its inside_run_id is
                        one of the system members' runs
    Example (toy): member g4 (510-600 +), candidate g3 (420-500 -) one gene upstream -> rank -1, gap 9.
    """
    g = genome_runs.copy()
    g["start"] = pd.to_numeric(g["start"]); g["end"] = pd.to_numeric(g["end"])
    g = g.sort_values(["contig", "start", "end", "locus_tag"]).reset_index(drop=True)
    g["_i"] = g.groupby("contig").cumcount()
    gi = g.set_index("locus_tag")
    by_contig = {c: cg.reset_index(drop=True) for c, cg in g.groupby("contig")}
    rows = []
    for sid, ms in members_df.groupby("system_id"):
        mem = [m for m in ms["locus_tag"] if m in gi.index]
        mem_set = set(ms["locus_tag"])
        sys_runs = {gi.loc[m, "run_id"] for m in mem}
        best = {}
        for m in mem:
            mr = gi.loc[m]
            cg = by_contig[mr["contig"]]
            lo, hi = max(0, mr["_i"] - window), min(len(cg) - 1, mr["_i"] + window)
            for _, c in cg.iloc[lo:hi + 1].iterrows():
                if c["locus_tag"] in mem_set:
                    continue
                rank = int(c["_i"] - mr["_i"])
                gap = int(c["start"] - mr["end"] - 1) if rank > 0 else int(mr["start"] - c["end"] - 1)
                key = (abs(rank), gap, m)
                if c["locus_tag"] not in best or key < best[c["locus_tag"]][0]:
                    best[c["locus_tag"]] = (key, m, rank, gap, c)
        for cand, (_, m, rank, gap, c) in sorted(best.items()):
            rows.append({
                "system_id": sid, "candidate": cand, "nearest_member": m, "rank_offset": rank,
                "gap_to_nearest_member": gap, "candidate_strand": c["strand"],
                "same_strand": c["strand"] == gi.loc[m, "strand"],
                "candidate_run_id": c["run_id"], "in_system_run": c["run_id"] in sys_runs,
                "opposite_strand_interloper": to_bool(c["opposite_strand_in_run"])
                and c["inside_run_id"] in sys_runs,
            })
    return pd.DataFrame(rows)


def _tag_split(tag: str):
    import re
    m = re.fullmatch(r"(.*?)(\d+)", str(tag))
    return (m.group(1), int(m.group(2))) if m else (None, None)


def no_coordinate_candidates(members_df: pd.DataFrame, no_coord_tags, window: int) -> pd.DataFrame:
    """Neighbour candidates among genes WITHOUT coordinates, placed by locus-tag number (approximate).

    A gene without coordinates cannot be ranked by position. Rule: same alphabetic tag prefix and
    |tag number - member tag number| <= window -> candidate of that member's system, with
    tag_distance = that difference (nearest member by smallest distance, ties by tag).
    Example: member PMM0005, no-coordinate PMM0007, window 2 -> candidate, tag_distance 2.
    Caveat: locus-tag numbering only approximates gene order.
    """
    nc = [(t, *_tag_split(t)) for t in no_coord_tags]
    rows = []
    for sid, ms in members_df.groupby("system_id"):
        mem = set(ms["locus_tag"])
        for t, pre, num in nc:
            if t in mem or num is None:
                continue
            best = None
            for m in sorted(mem):
                mp, mn = _tag_split(m)
                if mp == pre and mn is not None and abs(num - mn) <= window:
                    if best is None or abs(num - mn) < best[1]:
                        best = (m, abs(num - mn))
            if best:
                rows.append({"system_id": sid, "candidate": t, "nearest_member": best[0],
                             "tag_distance": best[1]})
    return pd.DataFrame(rows, columns=["system_id", "candidate", "nearest_member", "tag_distance"])


# --------------------------------------------------------------------------- category values
#: Written category values that mean "nothing applies". Chosen so they survive pd.read_csv with
#: default NA handling: "n/a" and "" are in pandas' default NA set and would read back as NaN.
NOT_ELIGIBLE = "not_eligible"   # strict-variant can_use columns: row not eligible for co-location
NO_BASIS = "none"               # match_basis / link_basis: no gene / singleton group


# --------------------------------------------------------------------------- metabolite equivalence
def _norm_id(x):
    if _isna(x):
        return None
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s or None


def _norm_name(x):
    import re
    return None if _isna(x) else re.sub(r"\s+", " ", str(x).strip().lower()) or None


def equiv_groups(xref: pd.DataFrame) -> pd.DataFrame:
    """Group Metabolite nodes that denote the same compound.

    Input columns: metabolite_id, name, chebi_id, mnxm_id (optional kegg_compound_id; else derived
    from a kegg.compound: prefix). chebi_id may arrive as float (13845.0) -> normalised to "13845".
    Pass 1 (id): union nodes sharing kegg_compound_id, chebi_id or mnxm_id.
    Pass 2 (name_soft): union groups sharing the normalised name (lower-case, collapsed spaces).
    Output adds name_norm, equiv_group (min metabolite_id of the group), link_basis:
      "none" (singleton), "id" (only id links), "name_soft" (only name links), "id|name_soft" (both).
    Example: kegg.compound:C00244 "Nitrate" (ChEBI 25545) and chebi:14654 "nitrate" share no id ->
             one group via the name, link_basis "name_soft".
    """
    x = xref.copy().reset_index(drop=True)
    if "kegg_compound_id" not in x:
        x["kegg_compound_id"] = x["metabolite_id"].map(
            lambda m: m.split(":", 1)[1] if str(m).startswith("kegg.compound:") else None)
    for c in ("kegg_compound_id", "chebi_id", "mnxm_id"):
        x[c] = x[c].map(_norm_id) if c in x else None
    x["name_norm"] = x["name"].map(_norm_name)
    ids = x["metabolite_id"].tolist()
    uf = _UF(ids)
    used = defaultdict(set)
    pending = []
    for c in ("kegg_compound_id", "chebi_id", "mnxm_id"):
        for _, g in x.dropna(subset=[c]).groupby(c):
            m = sorted(g["metabolite_id"])
            for o in m[1:]:
                pending.append((m[0], o, "id"))
    for _, g in x.dropna(subset=["name_norm"]).groupby("name_norm"):
        m = sorted(g["metabolite_id"])
        for o in m[1:]:
            pending.append((m[0], o, "name_soft"))
    for a, b, lab in pending:
        if lab == "name_soft" and uf.find(a) == uf.find(b):
            continue  # already linked by an id: the name adds nothing
        uf.union(a, b)
        used[(a, b)].add(lab)
    labs = defaultdict(set)
    for (a, _b), ls in used.items():
        labs[uf.find(a)] |= ls
    root = {m: uf.find(m) for m in ids}
    members = defaultdict(list)
    for m, r in root.items():
        members[r].append(m)
    x["equiv_group"] = x["metabolite_id"].map(lambda m: min(members[root[m]]))
    x["link_basis"] = x["metabolite_id"].map(lambda m: "|".join(sorted(labs.get(root[m], set()))) or NO_BASIS)
    x["equiv_group_size"] = x["metabolite_id"].map(lambda m: len(members[root[m]]))
    return x


def genes_by_group(metab_df: pd.DataFrame, xref: pd.DataFrame) -> dict:
    """{equiv_group: {locus_tag: {metabolite_ids}}} for metabolism-arm rows (locus_tag, metabolite_id).

    The group comes from xref (metabolite_id -> equiv_group); an id absent from xref is its own group.
    Rows with evidence_source != "metabolism" are ignored when that column is present.
    """
    m = metab_df
    if "evidence_source" in m.columns:
        m = m[m["evidence_source"] == "metabolism"]
    grp = dict(zip(xref["metabolite_id"], xref["equiv_group"]))
    out = defaultdict(lambda: defaultdict(set))
    for lt, mid in zip(m["locus_tag"], m["metabolite_id"]):
        out[grp.get(mid, mid)][lt].add(mid)
    return {g: dict(v) for g, v in out.items()}


def can_use_equiv(substrate_id: str, xref_by_id: pd.DataFrame, gbg: dict, window_loci, run_loci) -> dict:
    """can_use computed two ways on the substrate's equivalence group (never the raw id).

    xref_by_id: xref indexed by metabolite_id with equiv_group, link_basis. gbg: genes_by_group().
    G = genes with a metabolism-arm reaction on any member of the substrate's group.
      can_use_window: G ∩ window_loci (enzyme candidates within +-window of the system) -> "co-located";
                      else G non-empty -> "elsewhere in genome"; else "no".
      can_use_run:    same with run_loci (enzyme candidates inside the system's same-strand run).
    match_basis: "none" (no gene), "exact" (some gene reacts with this very id), else the group's
      link_basis ("id" / "name_soft" / "id|name_soft").
    Example: chebi:14654 (transport-side nitrate) matches a C00244 enzyme only via name_soft.
    """
    if substrate_id in xref_by_id.index:
        grp = xref_by_id.loc[substrate_id, "equiv_group"]
        lb = xref_by_id.loc[substrate_id, "link_basis"]
        lb = NO_BASIS if _isna(lb) or not str(lb) else str(lb)
    else:
        grp, lb = substrate_id, NO_BASIS
    genes = gbg.get(grp, {})
    G = set(genes)

    def call(loci):
        hit = G & set(loci)
        return ("co-located" if hit else "elsewhere in genome" if G else "no"), "|".join(sorted(hit))

    w, wl = call(window_loci)
    r, rl = call(run_loci)
    if not G:
        basis = NO_BASIS
    elif any(substrate_id in ids for ids in genes.values()):
        basis = "exact"
    else:
        basis = lb
    return {"equiv_group": grp, "can_use_window": w, "linked_enzyme_loci_window": wl,
            "can_use_run": r, "linked_enzyme_loci_run": rl,
            "genome_enzyme_loci": "|".join(sorted(G)), "match_basis": basis}


# --------------------------------------------------------------------------- currency metabolites
#: Currency metabolites: id -> (name, source). Docs minimal-8 (docs://analysis/metabolites, the
#: CURRENCY list in workflow d: H2O, CO2, ATP, ADP, AMP, Pi, PPi, NAD(P)(H) = 11 KEGG ids) plus the
#: coordinator's extension H+, CoA, FAD, GTP, GDP (2026-10-07). Glu/Gln deliberately NOT included
#: (docs call them borderline; they are N-flux signals here).
CURRENCY_METABOLITES: dict[str, tuple[str, str]] = {
    "kegg.compound:C00001": ("H2O", "docs_min8"),
    "kegg.compound:C00011": ("CO2", "docs_min8"),
    "kegg.compound:C00002": ("ATP", "docs_min8"),
    "kegg.compound:C00008": ("ADP", "docs_min8"),
    "kegg.compound:C00020": ("AMP", "docs_min8"),
    "kegg.compound:C00009": ("Orthophosphate", "docs_min8"),
    "kegg.compound:C00013": ("Diphosphate", "docs_min8"),
    "kegg.compound:C00003": ("NAD+", "docs_min8"),
    "kegg.compound:C00004": ("NADH", "docs_min8"),
    "kegg.compound:C00005": ("NADPH", "docs_min8"),
    "kegg.compound:C00006": ("NADP+", "docs_min8"),
    "kegg.compound:C00080": ("H+", "extension_2026-10-07"),
    "kegg.compound:C00010": ("CoA", "extension_2026-10-07"),
    "kegg.compound:C00016": ("FAD", "extension_2026-10-07"),
    "kegg.compound:C00044": ("GTP", "extension_2026-10-07"),
    "kegg.compound:C00035": ("GDP", "extension_2026-10-07"),
}


def currency_groups(xref: pd.DataFrame, currency=None) -> set:
    """Equivalence groups containing any currency id (an id absent from xref is its own group)."""
    cur = CURRENCY_METABOLITES if currency is None else currency
    grp = dict(zip(xref["metabolite_id"], xref["equiv_group"]))
    return {grp.get(c, c) for c in cur}


def add_ms_variant(t: pd.DataFrame) -> pd.DataFrame:
    """Add can_use_window_ms / can_use_run_ms / linked_enzyme_loci_{window,run}_ms.

    Eligible row (API review C2) = substrate_depth == "most_specific" AND the gene's
    transport_substrate_resolution == "resolved" AND NOT is_lumping (row family is a lumping family,
    see lumping_families) AND NOT is_currency. Eligible rows copy can_use_window / can_use_run and
    their linked loci; other rows get "not_eligible" and "" loci, so co-location (and linked enzymes) can only
    come from specific, non-currency substrate calls.
    """
    t = t.copy()
    elig = ((t["substrate_depth"] == "most_specific")
            & (t["transport_substrate_resolution"] == "resolved")
            & ~t["is_lumping"].map(to_bool)
            & ~t["is_currency"].map(to_bool))
    for d in ("window", "run"):
        t[f"can_use_{d}_ms"] = t[f"can_use_{d}"].where(elig, NOT_ELIGIBLE)
        t[f"linked_enzyme_loci_{d}_ms"] = t[f"linked_enzyme_loci_{d}"].fillna("").where(elig, "")
    return t


def lumping_families(term_details: pd.DataFrame, threshold: int, required_ids=None) -> set:
    """TCDB families treated as lumping: level_kind == "tc_family" AND metabolite_count >= threshold.

    term_details: ontology_term_details rows (term_id, level_kind, metabolite_count).
    required_ids: every family id that must be classifiable (e.g. all families in the substrate
    table). If any is absent from term_details, or has a missing / non-numeric metabolite_count,
    raise ValueError: a family is never silently treated as non-lumping.
    Example: tcdb:3.A.1 (tc_family, 554 substrates) with threshold 100 -> lumping; tcdb:3.A.1.5
    (tc_subfamily) never.
    """
    d = term_details
    mc = pd.to_numeric(d["metabolite_count"], errors="coerce")
    if required_ids is not None:
        have = dict(zip(d["term_id"], mc))
        missing = sorted(set(required_ids) - set(have))
        nan = sorted(i for i in set(required_ids) & set(have) if pd.isna(have[i]))
        if missing or nan:
            raise ValueError(f"lumping coverage: missing {missing[:10]}, no numeric metabolite_count {nan[:10]}")
    return set(d.loc[(d["level_kind"] == "tc_family") & (mc >= threshold), "term_id"])


def n_status(elements, formula) -> str:
    """"contains_N" if 'N' is among the element symbols; "no_formula" if no formula / no elements;
    else "no_N". Exact symbol match ("Na" is not "N")."""
    els = parse_list(elements)
    if not els:
        return "no_formula" if _isna(formula) or not str(formula).strip() else (
            "contains_N" if "N" in _hill_symbols(str(formula)) else "no_N")
    return "contains_N" if "N" in els else "no_N"


def _hill_symbols(formula: str) -> set:
    import re
    return set(re.findall(r"[A-Z][a-z]?", formula))


def no_coordinate_placeability(members_df: pd.DataFrame, no_coord_tags, window: int) -> pd.DataFrame:
    """Per gene without coordinates: can it be placed near any system member by locus-tag number?

    placement_status: "placed" (same prefix and |tag number difference| <= window for some member),
    "prefix_shared_not_within_window" (prefix shared with a member, none within window), or
    "unplaceable" (no member shares its prefix). Nothing is dropped.
    """
    mem = [(_tag_split(t)) for t in members_df["locus_tag"]]
    rows = []
    for t in no_coord_tags:
        pre, num = _tag_split(t)
        same = [mn for mp, mn in mem if mp == pre and mn is not None and pre is not None]
        dist = min((abs(num - mn) for mn in same), default=None) if num is not None else None
        status = ("unplaceable" if not same else
                  "placed" if dist is not None and dist <= window else "prefix_shared_not_within_window")
        rows.append({"locus_tag": t, "tag_prefix": pre, "shares_prefix_with_member": bool(same),
                     "nearest_member_tag_distance": dist, "placement_status": status})
    return pd.DataFrame(rows)


def expectation_check(rows: pd.DataFrame, expected_usable: bool,
                      defs=("can_use_window", "can_use_run", "can_use_window_ms", "can_use_run_ms")) -> dict:
    """Per-strain expectation check for one substrate group (replaces MED4's fixed EN1 label).

    expected_usable comes from the strain's own genome (any gene with a metabolism-arm reaction on
    the group). Per definition column present in rows: observed value counts and pass, where
    considered values exclude "not_eligible" (NaN is also treated as not considered); pass = all
    considered == "no" if not expected_usable, else
    none considered == "no"; pass None if nothing is considered (not evaluable).
    """
    out = {}
    for c in defs:
        if c not in rows.columns:
            continue
        obs = rows[c].fillna(NOT_ELIGIBLE).value_counts().to_dict()
        cons = rows[c].fillna(NOT_ELIGIBLE)
        cons = cons[cons != NOT_ELIGIBLE]
        if cons.empty:
            ok = None
        elif expected_usable:
            ok = bool((cons != "no").all())
        else:
            ok = bool((cons == "no").all())
        out[c] = {"observed": {k: int(v) for k, v in obs.items()}, "pass": ok}
    return out


# --------------------------------------------------------------------------- substrates
def can_use(substrate_id: str, metabolism_genes_df: pd.DataFrame, system_neighbour_loci) -> str:
    """Can the strain use this substrate metabolically, and is the enzyme by the system?

    metabolism_genes_df: rows (locus_tag, metabolite_id[, evidence_source]) for the strain, e.g.
      metabolites_by_gene / genes_by_metabolite output. Rows with evidence_source != "metabolism"
      are IGNORED (a transport row is not use).
    system_neighbour_loci: system members + linked-enzyme neighbours (set/list/" | " string).
    Rule: G = genes with a metabolism row for substrate_id (exact canonical id match).
      G ∩ loci non-empty -> "co-located"; G non-empty -> "elsewhere in genome"; else "no".
    Example: cyanate with cynS in the cyn neighbourhood -> "co-located".
    Caveat: "involved in a reaction" is undirected (KEGG); a pass for ammonia/amino acids is
    trivial for any genome.
    """
    m = metabolism_genes_df
    if "evidence_source" in m.columns:
        m = m[m["evidence_source"] == "metabolism"]
    genes = set(m.loc[m["metabolite_id"] == substrate_id, "locus_tag"])
    loci = set(parse_list(system_neighbour_loci)) if not isinstance(system_neighbour_loci, (set, frozenset)) \
        else set(system_neighbour_loci)
    if genes & loci:
        return "co-located"
    if genes:
        return "elsewhere in genome"
    return "no"


def likely_transporter_basis(row, role_map: dict | None = None) -> str:
    """Which criteria make a gene a plausible transporter, "|"-joined in the order pfam|ko|cyanorak|tcdb.

    pfam = a role Pfam (role_map, default PFAM_ROLE_MAP); ko = truthy brite_transporter;
    cyanorak = a curated Cyanorak transport role (an id in row["cyanorak_roles"] starting
    "cyanorak.role:Q"; researcher decision 2026-10-08); tcdb = any TCDB attachment whose class is in
    TCDB_TRANSPORTER_CLASSES (1, 2, 3). "" = none.
    """
    out = []
    if _has_role_pfam(_get(row, "pfam_ids"), role_map):
        out.append("pfam")
    if to_bool(_get(row, "brite_transporter")):
        out.append("ko")
    if any(str(r).startswith("cyanorak.role:Q") for r in parse_list(_get(row, "cyanorak_roles"))):
        out.append("cyanorak")
    if any(_tcdb_class(t) in TCDB_TRANSPORTER_CLASSES for t in parse_list(_get(row, "tcdb_ids"))):
        out.append("tcdb")
    return "|".join(out)


def likely_transporter(row, role_map: dict | None = None) -> str:
    """Three-valued plausibility that a gene is a transporter (coordinator rule, 2026-10-07).

      "strong"    = a transporter-role Pfam (role_map) OR (a BRITE transporters-tree KO AND a TCDB
                    class 1-3 attachment) OR (a curated Cyanorak transport (Q.*) role AND a TCDB class 1-3
                    attachment): the KO and Cyanorak bases only UPGRADE a catalogue-listed gene
                    (tcdb_only -> strong), never none -> strong (researcher decisions 2026-10-08: Cyanorak
                    v1.3, KO v1.4; e.g. glutathione S-transferases with a BRITE KO and no TCDB -> none)
      "tcdb_only" = neither of those, but >= 1 TCDB attachment in class 1, 2 or 3
      "none"      = otherwise (e.g. only class 4/5/8/9 attachments, or nothing)
    Never thresholded on tcdb_evidence_score; report that beside it via tcdb_transporter_evidence.
    Known limit: PF00005-carrying non-transport ABC ATPases come out "strong"; review via
    likely_transporter_basis + product.
    Example: fadD-like (Pfam PF00501, tcdb:2.A.x + tcdb:4.C.x, no BRITE) -> "tcdb_only".
    """
    basis = likely_transporter_basis(row, role_map).split("|")
    if "pfam" in basis or ("tcdb" in basis and ("ko" in basis or "cyanorak" in basis)):
        return "strong"
    if "tcdb" in basis:
        return "tcdb_only"
    return "none"


def tcdb_transporter_evidence(tcdb_rows: pd.DataFrame) -> dict:
    """Evidence of ONE gene's TCDB attachments in transporter classes 1-3 (no threshold).

    tcdb_rows: that gene's TCDB rows (term_id, evidence_score, source_agreement), e.g. from
    gene_ontology_terms(ontology='tcdb', verbose=True).
    Returns tcdb_c123_max_score (max evidence_score over class 1-3 rows; None if none) and
    tcdb_c123_source_agreement (sorted distinct values over those rows, "|"-joined; "" if none).
    Example: rows 2.A.1.1.1 (0.0, single_source) + 4.C.1.1 (0.6, both_sources)
             -> {max 0.0, "single_source"}.
    """
    r = tcdb_rows[tcdb_rows["term_id"].map(lambda t: _tcdb_class(str(t)) in TCDB_TRANSPORTER_CLASSES)]
    sc = pd.to_numeric(r["evidence_score"], errors="coerce")
    return {
        "tcdb_c123_max_score": float(sc.max()) if sc.notna().any() else None,
        "tcdb_c123_source_agreement": "|".join(sorted(set(r["source_agreement"].dropna().astype(str)))),
    }


# --------------------------------------------------------------------------- evidence
def evidence_profile(system_rows: pd.DataFrame) -> dict:
    """Annotation-evidence profile of ONE system (columns, not a filter; proposal §3.2 step 4).

    system_rows: one row per gene × TCDB attachment (gene_ontology_terms tcdb verbose fields:
      locus_tag, role, term_id, evidence, evidence_score, source_agreement, pfam_support);
      a recruited gene with no TCDB call appears as one row with NaN TCDB fields.
    Returns:
      n_genes, n_genes_with_tcdb,
      tcdb_depth_max       = max level over all attachments,
      tcdb_depth_min_gene  = min over TCDB genes of that gene's deepest level (the weakest member),
      evidence             = sorted distinct evidence values, "|"-joined,
      n_homology_genes / n_family_inferred_genes = genes with >= 1 row of that evidence,
      max_tcdb_evidence_score,
      source_agreement, pfam_support = sorted distinct values "|"-joined,
      n_pfam_corroborated_genes = genes with >= 1 pfam_support == "corroborated" row,
      roles, has_binding, has_permease, has_atpase, has_single_carrier,
      role_complete = (binding and permease and atpase) or single carrier or a 'mixed' gene.
    Example (toy cyn): 4 genes, 3 with TCDB, depth 4/4, family_inferred, max 0.8, complete.
    """
    r = system_rows.copy()
    has_t = r["term_id"].notna() if "term_id" in r.columns else pd.Series(False, index=r.index)
    t = r[has_t].copy()
    t["_lvl"] = t["term_id"].map(tcdb_level)
    roles = {x for x in r["role"].dropna()}

    def distinct(col):
        return "|".join(sorted(set(t[col].dropna().astype(str)))) if col in t.columns else ""

    def n_genes_where(col, val):
        return int(t.loc[t[col] == val, "locus_tag"].nunique()) if col in t.columns else 0

    score = pd.to_numeric(t.get("evidence_score"), errors="coerce") if len(t) else pd.Series(dtype=float)
    return {
        "n_genes": int(r["locus_tag"].nunique()),
        "n_genes_with_tcdb": int(t["locus_tag"].nunique()),
        "tcdb_depth_max": int(t["_lvl"].max()) if len(t) else None,
        "tcdb_depth_min_gene": int(t.groupby("locus_tag")["_lvl"].max().min()) if len(t) else None,
        "evidence": distinct("evidence"),
        "n_homology_genes": n_genes_where("evidence", "homology"),
        "n_family_inferred_genes": n_genes_where("evidence", "family_inferred"),
        "max_tcdb_evidence_score": float(score.max()) if score.notna().any() else None,
        "source_agreement": distinct("source_agreement"),
        "pfam_support": distinct("pfam_support"),
        "n_pfam_corroborated_genes": n_genes_where("pfam_support", "corroborated"),
        "roles": "|".join(sorted(roles)),
        "has_binding": "substrate_binding" in roles,
        "has_permease": "permease" in roles,
        "has_atpase": "atpase" in roles,
        "has_single_carrier": "single_carrier" in roles,
        "role_complete": _role_complete(roles),
    }


# --------------------------------------------------------------------------- decide-gate build (2026-10-08)
TRANSPORT_ROLE_PREFIX = "cyanorak.role:Q"
ORGANIC_N_CLASSES = ("amino acids", "peptides", "polyamines", "nucleobases/nucleosides", "osmolytes", "amines",
                     "amino sugars")
UNCLASSIFIED_N = "unclassified N"
UNCLASSIFIED_NO_FORMULA = "unclassified (no formula)"


#: Allow-list for ubiquitous substrate groups (ubiquity >= threshold, e.g. ammonia, L-glutamate):
#: only these assimilation enzymes can function-link on them (researcher decision 2026-10-08).
#: EC 6.3.1.2 glutamine synthetase (glnA); EC 1.4.7.1 ferredoxin-dependent glutamate synthase (glsF/GOGAT).
#: Checked in the KG: MED4 PMM0920 ec:6.3.1.2; PMM1512 ec:1.4.7.1 (+ ec:1.4.1.13).
UBIQUITOUS_ALLOWLIST_EC = ("6.3.1.2", "1.4.7.1")


def function_links(system_roles: set, carried_groups: set, gene_groups: dict, gene_roles: dict,
                   members: set, q_prefix: str = TRANSPORT_ROLE_PREFIX, ubiquity: dict | None = None,
                   threshold: int | None = None, gene_ecs: dict | None = None,
                   allow_ecs=UBIQUITOUS_ALLOWLIST_EC) -> list[dict]:
    """Function-linked enzymes of one system (any distance; decide gate 2026-10-08).

    A gene (not a system member) is linked for a carried substrate group if (a) it has a
    metabolism-arm reaction on that group (gene_groups: locus -> set of groups) and (b) it shares at
    least one Cyanorak role with the system (union of members' roles) OUTSIDE the transport branch
    (role ids not starting with q_prefix). Callers pass only carried groups that come from
    non-lumping, non-currency rows. Returns dicts: equiv_group, locus_tag, shared_role_ids ("|").
    Example: amt1 (E.4, Q.4) + glnA (E.4) reacting with ammonia -> linked via E.4; pncC (B.11) not.
    Ubiquitous groups (ubiquity[group] >= threshold, when both are given): only genes carrying an
    allow-listed EC (allow_ecs; gene_ecs: locus -> {"ec:x.y.z.w"}) link; link_breadth records
    "ubiquitous_allowlisted" for those and "specific" otherwise.
    """
    sys_nonq = {r for r in system_roles if not str(r).startswith(q_prefix)}
    allow = {str(e).replace("ec:", "") for e in allow_ecs}
    out = []
    for lt in sorted(gene_groups):
        if lt in members:
            continue
        shared = sys_nonq & set(gene_roles.get(lt, set()))
        if not shared:
            continue
        for g in sorted(set(gene_groups[lt]) & set(carried_groups)):
            breadth = "specific"
            if ubiquity is not None and threshold is not None and ubiquity.get(g, 0) >= threshold:
                ecs = {str(e).replace("ec:", "") for e in (gene_ecs or {}).get(lt, set())}
                if not ecs & allow:
                    continue
                breadth = "ubiquitous_allowlisted"
            out.append({"equiv_group": g, "locus_tag": lt, "shared_role_ids": "|".join(sorted(shared)),
                        "link_breadth": breadth})
    return out


def neighbour_links(carried_groups: set, window_loci: set, gene_groups: dict, ubiquity: dict,
                    threshold: int) -> list[dict]:
    """Neighbour-linked enzymes: window enzymes (+-8, either strand; window_loci) with a reaction on a
    carried group, excluding ubiquitous groups (ubiquity[group] = genes of the strain with a
    metabolism-arm reaction on it; excluded when >= threshold). Returns dicts equiv_group, locus_tag.
    Example: amt1's neighbour pncC reacts with ammonia (36 genes >= 30) -> not linked.
    """
    out = []
    for lt in sorted(window_loci):
        for g in sorted(set(gene_groups.get(lt, set())) & set(carried_groups)):
            if ubiquity.get(g, 0) >= threshold:
                continue
            out.append({"equiv_group": g, "locus_tag": lt})
    return out


def transport_class(member_roles: dict, role_names: dict, q_prefix: str = TRANSPORT_ROLE_PREFIX):
    """Curated transport class of a system: union of members' Cyanorak Q.* role ids and names,
    each "|"-joined in id order; ("none", "none") if no member has a Q role."""
    ids = sorted({r for v in member_roles.values() for r in v if str(r).startswith(q_prefix)})
    if not ids:
        return NO_BASIS, NO_BASIS
    return "|".join(ids), "|".join(str(role_names.get(i, i)) for i in ids)


CATALOGUE_ONLY_REASON = "catalogue-only (TCDB hit, no domain/KO/curated support)"
TRANSPORTER_CANDIDATE_TIERS = ("High", "Medium")


def is_transporter_candidate(tier) -> bool:
    """True for tier High or Medium (system_is_transporter_candidate column of the link tables)."""
    return str(tier) in TRANSPORTER_CANDIDATE_TIERS


def system_tier(strong: bool, tcdb_only: bool, role_complete: bool, member_resolutions,
                c123_max_score, curated_q: bool = False) -> tuple[str, str]:
    """Tier of one system (decide gate 2026-10-08). Returns (tier, reason).

    member_resolutions: transport_substrate_resolution of members that have TCDB calls.
    Order of rules:
      Low    if every TCDB member is family_inferred (superfamily-only);
      Low    if the system's max class 1-3 TCDB score is 0 (score-0-only: the attachments that make
             it a transporter carry no corroboration);
      High   if strong AND role_complete AND resolved;
      Medium if strong (incomplete, or complete without any TCDB resolution);
      Low    "catalogue-only (TCDB hit, no domain/KO/curated support)" if no member is strong but some
             member is tcdb_only (v1.4, researcher decision 2026-10-08; was Medium when resolved);
      not_transporter if no member is strong or tcdb_only.
    Mixed member resolutions (resolved + family_inferred) count as resolved; the reason says "mixed".
    curated_q (a member is strong through a Cyanorak Q.* role + TCDB): the score-0-only rule does NOT apply
    (researcher decision 2026-10-08; e.g. focA), and since v1.6.0 neither does the superfamily-only rule (the
    system then follows the strong rules: Medium, since family_inferred is not "resolved"). Catalogue-only
    (no strong member) is never lifted.
    """
    res = {r for r in member_resolutions if isinstance(r, str) and r}
    sf_note = ""
    if res and res == {"family_inferred"}:
        if not curated_q:
            return "Low", "superfamily-only (all TCDB members family_inferred)"
        # v1.6 (researcher decision 2026-10-08): a curated Cyanorak transport role lifts superfamily-only
        sf_note = " [superfamily-only overridden by curated Cyanorak transport role]"
    if (not curated_q and c123_max_score is not None and not _isna(c123_max_score)
            and float(c123_max_score) == 0.0):
        return "Low", "score-0-only (max class 1-3 TCDB score 0)"
    if curated_q and c123_max_score is not None and not _isna(c123_max_score) and float(c123_max_score) == 0.0:
        note0 = " [score-0-only overridden by curated Cyanorak transport role]"
    else:
        note0 = ""
    resolved = "resolved" in res
    note = (" (mixed member resolutions)" if len(res) > 1 else "") + sf_note + note0
    if strong and role_complete and resolved:
        return "High", "strong + role-complete + resolved" + note
    if strong:
        why = "strong, role-incomplete" if not role_complete else "strong, complete, no TCDB resolution"
        return "Medium", why + note
    if tcdb_only:
        return "Low", CATALOGUE_ONLY_REASON + note
    return "not_transporter", "no member is strong or tcdb_only"


_AA = ("alanine|arginine|asparagine|aspartate|aspartic acid|cysteine|glutamate|glutamic acid|glutamine|glycine|"
       "histidine|isoleucine|leucine|lysine|methionine|phenylalanine|proline|serine|threonine|tryptophan|"
       "tyrosine|valine|ornithine|citrulline|homoserine|beta-alanine|4-aminobutanoate|4-aminobutyrate|"
       "gamma-aminobutyrate|selenocysteine|homocysteine|amino acid|amino acids")
#: Ordered compound-class rules on lower-cased metabolite names (first match wins; any member name of
#: the equivalence group can match). Anchored patterns, never free substrings (except "peptide"), so
#: S-adenosyl-L-methionine or thiamin compounds are not pulled into nucleosides or amino acids.
#: Tuple: (class, rule id, regex, analogue flag).
COMPOUND_RULES: list[tuple[str, str, str, bool]] = [
    ("nitrite", "nitrite_exact", r"^(nitrite|nitrous acid)$", False),
    ("nitrate", "nitrate_exact", r"^(nitrate|nitric acid)$", False),
    ("cyanate", "cyanate_exact", r"^(cyanate|cyanic acid|isocyanate)$", False),
    ("urea", "urea_exact", r"^urea$", False),
    ("urea", "urea_analogue", r"^[a-z0-9,\-]*urea$", True),
    ("ammonium", "ammonium_exact", r"^(ammonia|ammonium|nh3|nh4\+|ammonium ion)$", False),
    # v1.4: only the primary methyl/ethyl amines are ammonium analogues (Amt substrates); quaternary
    # ammoniums (tetramethyl-/tetraethylammonium) get no class; di-/tri-alkylamines go to "amines"
    ("ammonium", "ammonium_analogue",
     r"^(methyl|ethyl)(amine|ammonium)$|^ammonium ion derivative$|^alkylamine$", True),
    ("amines", "amine_name",
     r"^(ethanolamine|propylamine|butylamine|isobutylamine|isoamylamine|pentylamine|hexylamine|phenethylamine|"
     r"2-phenylethylamine|phenylethylamine|tyramine|tryptamine|histamine|dopamine|serotonin|octopamine|"
     r"ethylenediamine|amine|amines|primary amine|aliphatic amine|aromatic amine|"
     r"dimethylamine|trimethylamine|diethylamine|triethylamine)$", False),
    ("osmolytes", "osmolyte_name",
     r"^(glycine betaine|betaine|choline|l-carnitine|carnitine|ectoine|hydroxyectoine|taurine|proline betaine|"
     r"stachydrine|trimethylamine n-oxide|homarine|sarcosine|n,n-dimethylglycine|dimethylglycine|hypotaurine)$"
     r"|betaine$|carnitine$|ectoine$|trimethylammonio", False),
    ("polyamines", "polyamine_name",
     r"^(putrescine|spermidine|spermine|cadaverine|agmatine|norspermidine|1,3-diaminopropane|polyamine|polyamines|"
     r"(sym-)?homospermidine)$",
     False),
    ("peptides", "peptide_name",
     r"peptide|^glutathione$|^(l-)?(alanyl|glycyl|leucyl|prolyl|glutamyl|gamma-glutamyl|aspartyl|lysyl|valyl|"
     r"seryl|threonyl|phenylalanyl|tyrosyl|histidyl|arginyl|methionyl|cysteinyl|isoleucyl|asparaginyl|"
     r"glutaminyl|tryptophyl)-|^(bradykinin|bacitracin( [a-z0-9]+)?|microcin( [a-z0-9]+)?)$", False),
    ("peptides", "peptide_aa3_chain",
     r"^(ala|arg|asn|asp|cys|gln|glu|gly|his|ile|leu|lys|met|phe|pro|ser|thr|trp|tyr|val)"
     r"(-(ala|arg|asn|asp|cys|gln|glu|gly|his|ile|leu|lys|met|phe|pro|ser|thr|trp|tyr|val))+$", False),
    ("nucleobases/nucleosides", "nucleo_name",
     r"^(adenine|guanine|cytosine|thymine|uracil|xanthine|hypoxanthine|purine|pyrimidine|purines|pyrimidines|"
     r"nucleoside|nucleosides|nucleobase|nucleobases|adenosine|guanosine|cytidine|uridine|thymidine|inosine|"
     r"xanthosine|(2'-)?deoxy(adenosine|guanosine|cytidine|uridine|inosine)|5-methylcytosine|"
     r"an? (purine|pyrimidine) nucleobase|5-fluorouridine)$", False),
    ("amino sugars", "amino_sugar_name",
     r"^(n-(acetyl|glycoloyl)-?)?((alpha|beta)-)?(d-)?(glucosamine|galactosamine|mannosamine|neuraminate|"
     r"neuraminic acid|muramate|muramic acid)$|^(n,n'-diacetyl)?chitobiose$|^lacto-n-biose$|^sialic acid$|"
     r"^n-acetyl-beta-d-glucosaminyl-\(1->4\)-n-acetyl-(aldehydo-)?d-glucosamine$", False),
    ("amino acids", "amino_acid_name", r"^((l|d|dl)-)?(" + _AA + r")$", False),
    ("amino acids", "amino_acid_generic",
     r"^(an? )?((l-)?alpha-)?amino acids?$|^polar amino acids?$|^amino acid\(|^branched-chain amino acids?$", False),
    ("amino acids", "amino_acid_extra",
     r"^((l|d|dl)-)?(cystine|homoarginine|dopa|selenomethionine|selenocystine|s-methyl-(l-)?methionine|"
     r"s-methylmethionine)$|^((trans|cis)-)?(4-|3-)?hydroxy-?(l-)?proline$", False),
]


def compound_class(names, n_status=None) -> tuple[str, str, bool]:
    """Compound class of a substrate group from its member names (COMPOUND_RULES, first match wins).
    Returns (class, rule_matched, analogue_flag). No match -> ("unclassified N", "no_rule", False), or
    ("unclassified (no formula)", "no_rule", False) when n_status is given and every member is
    no_formula (researcher decision C). The KG has no ChEBI/KEGG class hierarchy on Metabolite nodes
    (checked in kg_schema), so this layer is name-based; see layered_class for the other layers."""
    import re
    ns = [str(n).strip().lower() for n in names if not _isna(n) and str(n).strip()]
    for cls, rule, pat, analogue in COMPOUND_RULES:
        if any(re.search(pat, n) for n in ns):
            return cls, rule, analogue
    st = {str(x) for x in (n_status or []) if not _isna(x) and str(x)}
    if st and st <= {"no_formula"}:
        return UNCLASSIFIED_NO_FORMULA, "no_rule", False
    return UNCLASSIFIED_N, "no_rule", False


def can_use_applicable(compound_cls: str) -> bool:
    """False for organic N classes (the can_use check has no teeth there; decide gate 2026-10-08)."""
    return compound_cls not in ORGANIC_N_CLASSES



# --------------------------------------------------------------------------- layered compound classifier (D)
_PW_IDS = {
    "amino acids": {"00220", "00250", "00260", "00270", "00280", "00290", "00300", "00310", "00330", "00340",
                    "00350", "00360", "00380", "00400", "00410", "00450", "00470", "01230"},
    "nucleobases/nucleosides": {"00230", "00240"},
    "peptides": {"00480"},
    "osmolytes": {"00430"},
    "cofactors/vitamins": {"00730", "00740", "00750", "00760", "00770", "00780", "00785", "00790", "00670",
                           "00860", "00130"},
}
_PW_XENO = (r"antibiotic|polyketide|xenobiotic|drug metabolism|degradation of aromatic|benzoate|toluene|xylene|"
            r"chloro|nitrotoluene|atrazine|caprolactam|dioxin|naphthalene|aminobenzoate|styrene|ethylbenzene|"
            r"bisphenol|steroid degradation|carbapenem|monobactam|penicillin|cephalosporin|streptomycin|neomycin|"
            r"novobiocin|vancomycin|tetracycline|ansamycin|enediyne|macrolide|staurosporine|prodigiosin|"
            r"phenazine|aflatoxin|acarbose|biosynthesis of siderophore")
_PW_POLYAMINE = r"polyamine|spermidine|putrescine"


def pathway_class(pathway_id, pathway_name) -> tuple:
    """Class implied by one KEGG pathway (layer 2), or (None, reason).

    Global / overview maps (ko011xx, ko012xx except ko01230 "Biosynthesis of amino acids") -> None.
    Then by KEGG map number (_PW_IDS), then by name: polyamine words -> polyamines; antibiotic /
    polyketide / xenobiotic-degradation / drug-metabolism words -> xenobiotic. Everything else -> None
    ("unmapped"). The resulting map is written per run as a reviewable CSV.
    """
    import re
    num = str(pathway_id).split("ko")[-1].split(":")[-1][-5:]
    nm = "" if _isna(pathway_name) else str(pathway_name).lower()
    if num.startswith(("011", "012")) and num != "01230":
        return None, "global_map"
    for cls, ids in _PW_IDS.items():
        if num in ids:
            return cls, f"id:{num}"
    if re.search(_PW_POLYAMINE, nm):
        return "polyamines", "name:polyamine"
    if re.search(_PW_XENO, nm):
        return "xenobiotic", "name:xenobiotic"
    return None, "unmapped"


def pathway_vote(pathway_ids, pmap: dict) -> tuple:
    """Majority vote of a compound group's pathways (layer 2).

    pmap: pathway id -> class or None. Only mapped (non-None) pathways vote. Returns (class, votes,
    tied): class if one class holds > 50% of the votes; otherwise None with tied = the classes sharing
    the top count (when there is a tie). No mapped pathway -> (None, {}, []).
    """
    votes: dict = {}
    for pid in pathway_ids:
        c = pmap.get(pid)
        if c:
            votes[c] = votes.get(c, 0) + 1
    if not votes:
        return None, {}, []
    tot = sum(votes.values())
    top = max(votes.values())
    best = [c for c, v in votes.items() if v == top]
    if len(best) == 1 and top * 2 > tot:
        return best[0], votes, []
    return None, votes, (sorted(best) if len(best) > 1 else [])


_FAM_SIDEROPHORE = r"siderophore|iron[- ]chelate|ferric[- ]?(hydroxamate|siderophore|chelate)|ferrichrome|enterobactin|catecholate"
_FAM_EFFLUX = r"efflux|multidrug|drug|antibiotic|toxin|xenobiotic|resistance-nodulation|antimicrobial"


def family_context_class(family_name, go_names, use_go: bool = True) -> tuple:
    """Class implied by the TCDB family carrying a row (layer 3; a property of the ROW).

    Siderophore words in the family name (or, if use_go, its GO link names) -> "siderophore"; else
    efflux / drug / multidrug / antibiotic / toxin words -> "xenobiotic (efflux family)"; else None.
    Callers pass use_go=False for lumping families (their GO links summarise hundreds of members).
    Returns (class or None, matched text).
    """
    import re
    texts = [("" if _isna(family_name) else str(family_name))]
    if use_go:
        texts += [str(g) for g in (go_names or []) if not _isna(g)]
    for cls, pat in (("siderophore", _FAM_SIDEROPHORE), ("xenobiotic (efflux family)", _FAM_EFFLUX)):
        for t in texts:
            m = re.search(pat, t, flags=re.IGNORECASE)
            if m:
                return cls, m.group(0)
    return None, ""


def group_family_class(row_classes) -> str | None:
    """A group's layer-3 class: the rows' family-context class only if ALL rows agree (none missing)."""
    rc = list(row_classes)
    if not rc or any(_isna(c) or c is None for c in rc):
        return None
    u = set(rc)
    return u.pop() if len(u) == 1 else None


CLASS_CAVEAT = "best effort: names only; KG has no chemical categories"

#: Known false-positive transporter calls (researcher decision 2026-10-08, v1.4): keyed by product name so
#: the flag is organism-agnostic. Ferritin carries TCDB 1.A.155 + Cyanorak Q.4 in the KG (iron storage).
KNOWN_FALSE_POSITIVE_PRODUCTS = {
    "ferritin": r"^ferritin$",
    # v1.5 (researcher decision 2026-10-08): BRITE-KO + TCDB 1.A.12 listings of soluble GSTs
    "glutathione S-transferase": r"^glutathione s-transferase(,.*)?$",
    # sodX PMM1295: the product string itself names the protease (checked in p2_med4_gene_roles.csv)
    "sodX (Ni-SOD maturation protease)": r"^nickel-type superoxide dismutase maturation protease$",
    # v1.6.1: MAPEG (membrane-associated proteins in eicosanoid and glutathione metabolism); MIT9313 PMT1025
    "MAPEG": r"\bmapeg\b|eicosanoid/glutathione metabolism",
}


def known_false_positive(products, gene_names=None) -> tuple:
    """(flag, reason) for a system from its members' products (KNOWN_FALSE_POSITIVE_PRODUCTS, whole-name,
    case-insensitive). gene_names is accepted for the record only. Reason "none" when not flagged.
    Example: ["ferritin"] -> (True, "known false positive: ferritin (product)")."""
    import re
    hits = sorted({k for pr in (products or []) if not _isna(pr)
                   for k, pat in KNOWN_FALSE_POSITIVE_PRODUCTS.items() if re.search(pat, str(pr).strip().lower())})
    if hits:
        return True, "known false positive: " + ", ".join(hits) + " (product)"
    return False, NO_BASIS


# --------------------------------------------------------------------------- RefSeq fragments (v1.4)
FRAGMENT_MAX_GAP_BP = 100
GENERIC_PRODUCTS = {"hypothetical protein", "conserved hypothetical protein", "uncharacterized protein",
                    "unknown", "putative protein", ""}
_RS_TAG = r"_RS\d+$"
_OLD_TAG = r"^PM[A-Z0-9]*_?\d{4,}$"   # PMM0001, PMT0001, PMN2A_0001


def is_refseq_only(locus_tag, aliases=None) -> bool:
    """True if locus_tag is a RefSeq-only tag (*_RS<digits>) and no alias is a PMx-style old locus tag."""
    import re
    if not re.search(_RS_TAG, str(locus_tag)):
        return False
    return not any(re.match(_OLD_TAG, str(a)) for a in (aliases or []))


def refseq_fragments(coords: pd.DataFrame, aliases: dict | None = None,
                     max_gap: int = FRAGMENT_MAX_GAP_BP) -> pd.DataFrame:
    """RefSeq-only genes that overlap or abut (gap <= max_gap bp; negative = overlap) a same-contig,
    same-strand gene with the same product name (case-insensitive; generic products such as
    "hypothetical protein" never match). coords: locus_tag, product, contig, start, end, strand.
    aliases: locus_tag -> identifiers (KG all_identifiers). The parent is the closest such gene that is
    NOT itself RefSeq-only (two adjacent RefSeq-only copies, e.g. MIT9313 CCRG-2 RiPP tandems, are not
    fragments of each other). Returns locus_tag, fragment_of, gap_bp, product.
    Example: NATL2A PMN2A_RS10340 (nirA, 162 bp) 41 bp after PMN2A_1298 (nirA) -> fragment_of PMN2A_1298.
    """
    aliases = aliases or {}
    c = coords.dropna(subset=["start", "end"]).copy()
    c["pnorm"] = c["product"].map(lambda x: "" if _isna(x) else str(x).strip().lower())
    out = []
    for r in c.itertuples():
        if not is_refseq_only(r.locus_tag, aliases.get(r.locus_tag)) or r.pnorm in GENERIC_PRODUCTS:
            continue
        cand = c[(c.locus_tag != r.locus_tag) & (c.contig == r.contig) & (c.strand == r.strand) & (c.pnorm == r.pnorm)]
        best = None
        for q in cand.itertuples():
            gap = int(max(q.start, r.start) - min(q.end, r.end) - 1)
            if gap > max_gap or is_refseq_only(q.locus_tag, aliases.get(q.locus_tag)):
                continue
            key = (abs(gap), q.locus_tag)
            if best is None or key < best[0]:
                best = (key, q.locus_tag, gap)
        if best:
            out.append({"locus_tag": r.locus_tag, "fragment_of": best[1], "gap_bp": best[2], "product": r.product})
    return pd.DataFrame(out, columns=["locus_tag", "fragment_of", "gap_bp", "product"])


def link_counts(link_df: pd.DataFrame, fragments) -> dict:
    """Distinct linked loci per system_id, not counting fragment loci (rows are kept elsewhere)."""
    frag = set(fragments or [])
    return {s: int(g.loc[~g.locus_tag.isin(frag), "locus_tag"].nunique()) for s, g in link_df.groupby("system_id")}


def name_class_with_context(n_status, name_res, pathway_res, family_cls) -> dict:
    """Compound class of a substrate group = NAME RULES ONLY (researcher decision 2026-10-08, v1.3).

    name_res: compound_class output (rule "no_rule" = no match). Pathway votes (pathway_vote output)
    and the carrying-family context (group_family_class output) are reported as CONTEXT columns and
    never assign a class (the earlier layers misassigned e.g. thyroxine -> amino acids, GDP-mannose ->
    xenobiotic). Unmatched groups: "unclassified (no formula)" if every member is no_formula, else
    "unclassified N". Returns compound_class, class_source ("name" / "none"), pathway_context,
    family_context ("none" when empty), class_caveat.
    """
    ncls, nrule, _ = name_res
    _, pvotes, _ = pathway_res
    pctx = ",".join(f"{k}:{v}" for k, v in sorted((pvotes or {}).items())) or NO_BASIS
    fctx = family_cls or NO_BASIS
    if ncls and nrule != "no_rule":
        cls, src = ncls, "name"
    else:
        st = {str(x) for x in (n_status or []) if not _isna(x) and str(x)}
        cls = UNCLASSIFIED_NO_FORMULA if st and st <= {"no_formula"} else UNCLASSIFIED_N
        src = "none"
    return {"compound_class": cls, "class_source": src, "pathway_context": pctx, "family_context": fctx,
            "class_caveat": CLASS_CAVEAT}



# --------------------------------------------------------------------------- v1.6: dedicated vs broad listing
#: Per N compound class: (product regex, gene-name regex anchored at the start of the gene name, curated
#: Cyanorak Q roles that correspond). Researcher decision 2026-10-08. Q.4 (cations) is deliberately NOT
#: mapped to ammonium (ktrA / nhaS carry Q.4). Reviewable as p18_class_keyword_map.csv.
CLASS_KEYWORDS: dict[str, tuple] = {
    # class: (product regex, product exclusion regex, gene-name regex (anchored at start), corresponding Q roles)
    # v1.6.1: word boundaries / exclusions (cyanophycin, cyanocobalamin, nitrate/sulfonate, histidine kinase,
    # OsmC, glutamine amidotransferase, gltX/gltA/gltB)
    "ammonium": (r"\bammonium\b", r"", r"amt", ()),
    "urea": (r"\burea\b", r"", r"urt", ()),
    "cyanate": (r"\bcyanate\b", r"", r"cyn", ()),
    "nitrite": (r"\bnitrite\b", r"", r"foca|nirc", ()),
    "nitrate": (r"\bnitrate\b", r"nitrate/sulfonate", r"nrt|nar", ()),
    "amino acids": (r"\bamino acids?\b|\bglutamate\b|\bglutamine\b|\bproline\b|branched-chain|polar amino|\barginine\b|"
                    r"\blysine\b|\bhistidine\b", r"amidotransferase|histidine kinase", r"nat[a-h]|aap|glt[spi-l]",
                    ("Q.1",)),
    "peptides": (r"peptide", r"", r"dpp|opp", ("Q.1",)),
    "amines": (r"", r"", r"", ("Q.1",)),
    "polyamines": (r"spermidine|putrescine|polyamine", r"", r"pot", ("Q.1",)),
    "osmolytes": (r"betaine|\bosmo(?!c\b)|\bcholine\b|ectoine|glucosylglycerol", r"", r"pro[vwx]|ggt", ()),
    "nucleobases/nucleosides": (r"nucleoside|purine|pyrimidine|uracil|xanthine", r"", r"", ("Q.5",)),
    "amino sugars": (r"acetylglucosamine|chitobiose|glucosamine", r"", r"", ()),
}

#: v1.6.1 efflux annotation (context flag on systems; no tier effect)
EFFLUX_PRODUCT = r"\b(efflux|exporter|export|multidrug|drug resistance|rnd|mate)\b|\bdeva[- ]type\b"
EFFLUX_GENE = r"^(dev[abc]|evr[abc]|tolc|acra|mdta|ccma|ycf38)$"


def efflux_annotated(products, gene_names=None) -> bool:
    """True if a member product matches EFFLUX_PRODUCT (case-insensitive, word-bounded) or a member gene name
    matches EFFLUX_GENE. Example: ccmA 'ABC-type multidrug transport system...' -> True; ycf38 by gene name."""
    import re
    for pr in products or []:
        if not _isna(pr) and re.search(EFFLUX_PRODUCT, str(pr).lower()):
            return True
    for g in gene_names or []:
        if not _isna(g) and re.match(EFFLUX_GENE, str(g).strip().lower()):
            return True
    return False


def class_keyword_table() -> pd.DataFrame:
    return pd.DataFrame([{"compound_class": c, "product_regex": p, "product_exclude_regex": x,
                          "gene_name_regex": ("^(" + g + ")") if g else "", "cyanorak_q_roles": "|".join(q)}
                         for c, (p, x, g, q) in CLASS_KEYWORDS.items()])


def listing_basis(compound_cls, gene_names, products, q_roles=(), efflux: bool = False) -> tuple:
    """("dedicated" | "broad listing", detail) for one system and one N compound class.

    dedicated if (i) a member's product matches the class product regex and not its exclusion regex, or a
    member's gene name starts with the class gene-name pattern (case-insensitive), or (ii) a member carries a
    curated Cyanorak Q role that corresponds to the class (Q.1 -> amino acids, peptides, amines, polyamines;
    Q.5 -> nucleobases/nucleosides) AND the system is not efflux-annotated (v1.6.1: a Q-role-only call on an
    efflux-annotated system is "broad listing", detail "Q.1 only, efflux-annotated"). Otherwise "broad listing".
    """
    import re
    pr, px, gr, qs = CLASS_KEYWORDS.get(compound_cls, ("", "", "", ()))
    hits = []
    names = list(gene_names) + [None] * max(0, len(products) - len(gene_names))
    for nm, prod in zip(names, products):
        if gr and not _isna(nm) and re.match(r"^(?:" + gr + ")", str(nm).strip().lower()):
            hits.append(f"gene name {nm}")
        if pr and not _isna(prod):
            pl = str(prod).lower()
            if re.search(pr, pl) and not (px and re.search(px, pl)):
                hits.append(f"product '{prod}'")
    qn = {str(q).replace("cyanorak.role:", "") for q in q_roles if not _isna(q) and str(q)}
    qhits = [f"Cyanorak {q}" for q in sorted(qn & set(qs))]
    if hits:
        return "dedicated", "; ".join(dict.fromkeys(hits + qhits))
    if qhits:
        if efflux:
            return "broad listing", f"{'/'.join(q.split()[-1] for q in qhits)} only, efflux-annotated"
        return "dedicated", "; ".join(qhits)
    return "broad listing", NO_BASIS


def dedicated_basis(detail) -> str:
    """'keyword' if the detail has a gene-name / product hit, 'Q-role only' if only Cyanorak hits, else 'none'."""
    d = str(detail)
    if "gene name " in d or "product '" in d:
        return "keyword"
    if d.startswith("Cyanorak "):
        return "Q-role only"
    return "none"


def substrate_breadth(rows: pd.DataFrame) -> dict:
    """system_id -> (distinct equiv_groups at most_specific depth, non-lumping, non-currency;
    of those, the N-containing ones (n_status contains_N))."""
    r = rows[(rows.substrate_depth == "most_specific") & ~rows.is_lumping.map(to_bool) & ~rows.is_currency.map(to_bool)]
    out = {}
    for sid, g in r.groupby("system_id"):
        out[sid] = (int(g.equiv_group.nunique()),
                    int(g.loc[g.n_status.astype(str).str.contains("contains_N"), "equiv_group"].nunique()))
    return out

"""Diff step-4 neighbour classes, v0.6 (p4_v0.6_archive/) -> v0.7 (current). Writes p4_class_diff_v0.6_to_v0.7.csv
and p4_pilot_changed_rows.csv. Usage (from the pilot dir): ../../../../../.venv/Scripts/python.exe ../../scripts/p4c_diff_step4.py
"""
import pandas as pd

k = ["system_id", "candidate"]
b = pd.read_csv("p4_v0.6_archive/p4_med4_neighbour_candidates.csv")[k + ["neighbour_class", "role"]]
a = pd.read_csv("p4_med4_neighbour_candidates.csv")
m = b.merge(a[k + ["candidate_name", "candidate_product", "neighbour_class", "role", "role_hint_unverified",
                   "other_system_id"]], on=k, suffixes=("_before", "_after"), how="outer", indicator=True)
assert (m["_merge"] == "both").all(), "row sets differ"
ch = m[(m.neighbour_class_before != m.neighbour_class_after) | (m.role_before != m.role_after)]
ch.drop(columns="_merge").to_csv("p4_class_diff_v0.6_to_v0.7.csv", index=False)
print(pd.crosstab(m.neighbour_class_before, m.neighbour_class_after).to_string())
print(ch.drop_duplicates("candidate")[["candidate", "candidate_name", "neighbour_class_before", "neighbour_class_after",
                                       "role_before", "role_after", "role_hint_unverified"]]
      .query("neighbour_class_before != 'tcdb_transporter'").to_string())
pb = pd.read_csv("p4_v0.6_archive/p4_pilot_neighbours.csv")[["case"] + k + ["neighbour_class", "role"]]
pa = pd.read_csv("p4_pilot_neighbours.csv")
pm = pb.merge(pa[["case"] + k + ["candidate_name", "neighbour_class", "role", "other_system_id", "role_hint_unverified"]],
              on=["case"] + k, suffixes=("_before", "_after"))
pc = pm[(pm.neighbour_class_before != pm.neighbour_class_after) | (pm.role_before != pm.role_after)]
pc.to_csv("p4_pilot_changed_rows.csv", index=False)
pd.set_option("display.width", 250)
print(pc.to_string(index=False))

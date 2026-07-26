import csv, statistics, re
from collections import defaultdict

def compound_class(substrate, family=''):
    s=(substrate+' '+family).lower()
    if any(k in s for k in ['fucose','maltose','sugar','carbohydrate','glucose','hexose','pentose','glycoside','xylose','porter','mfs-sugar']): return 'sugars/carbohydrate'
    if any(k in s for k in ['citrate','dicarboxylate','tricarboxylate','lactate','acetate','gluconate','slc13','trap','malate','succinate','organic-acid','gntp']): return 'organic acids'
    if 'fatty' in s: return 'fatty acids'
    if any(k in s for k in ['peptide','dipeptide','oligopeptide','nickel','pot ']): return 'peptides'
    if any(k in s for k in ['amino acid','polar amino','branched-chain','apc','glutamine','arginine','lysine','histidine']): return 'amino acids'
    if any(k in s for k in ['nucleoside','nucleobase','purine','xanthine','uracil','ncs']): return 'nucleosides/bases'
    if any(k in s for k in ['betaine','choline','carnitine','bcct','osmoprotectant']): return 'osmolytes'
    if 'glycerol' in s: return 'glycerol'
    if any(k in s for k in ['benzoate','aromatic','phenylprop','hcat']): return 'aromatics'
    if any(k in s for k in ['iron','ferric','siderophore','phosphate','sulfate','molybd','nitrate','zinc','manganese','potassium','sodium','inorganic','fe3']): return 'inorganic (ref)'
    return 'other/unresolved'

def summarize(rows, pctkey, subkey='substrate', famkey='carrier_family', filt=None):
    by=defaultdict(list)
    for r in rows:
        if filt and not filt(r): continue
        p=r.get(pctkey,'')
        if p in ('','None'): continue
        by[compound_class(r.get(subkey,''), r.get(famkey,''))].append(float(p))
    out={}
    for c,v in by.items(): out[c]=(len(v), round(statistics.median(v),3), sum(1 for x in v if x>=0.9))
    return out

# HOT1A3 full landscape (all scored systems: candidate + control-ABC)
h=list(csv.DictReader(open('data/system_scores_hot1a3_day11.csv')))
print("=== HOT1A3 day-11: compound-class landscape (all scored systems) ===")
print(f"{'class':22s} {'n':>3} {'medPct':>7} {'n_up(>=.9)':>10}  refclasses")
allc=summarize(h,'system_percentile')
refby=defaultdict(set)
for r in h: refby[compound_class(r.get('substrate',''),r.get('carrier_family',''))].add(r['reference_class'])
for c in sorted(allc, key=lambda x:-allc[x][1]):
    n,med,up=allc[c]; print(f"{c:22s} {n:>3} {med:>7} {up:>10}  {','.join(sorted(refby[c]))}")

# candidate-only, cross experiment (module catalogs)
print("\n=== CANDIDATE compound-class median percentile, per experiment ===")
def load(fn,pk='module_percentile'): 
    try: return list(csv.DictReader(open(fn)))
    except: return []
exps={'HOT1A3_d11':('data/module_catalog_hot1a3_day11_v2.csv','module_percentile'),
      'EZ55_400':('data/module_catalog_ez55_400.csv','module_percentile'),
      'EZ55_800':('data/module_catalog_ez55_800.csv','module_percentile')}
classes=['sugars/carbohydrate','organic acids','amino acids','peptides','nucleosides/bases','osmolytes','glycerol','aromatics','fatty acids','other/unresolved']
hdr=f"{'class':22s}"+''.join(f"{e:>12s}" for e in exps)
print(hdr)
tabs={e:summarize([r for r in load(f) if r['reference_class']=='candidate'],pk) for e,(f,pk) in exps.items()}
for c in classes:
    row=f"{c:22s}"
    for e in exps:
        t=tabs[e].get(c); row+= f"{(str(t[1])+'('+str(t[0])+')') if t else '-':>12s}"
    print(row)

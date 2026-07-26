import csv, statistics
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Okabe-Ito colorblind-safe
BLUE='#0072B2'; ORANGE='#E69F00'; SKY='#56B4E9'; VERM='#D55E00'; GREEN='#009E73'; GREY='#8a8a8a'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.titlesize':11,'figure.dpi':140})

def cclass(sub,fam=''):
    s=(sub+' '+fam).lower()
    if any(k in s for k in ['fucose','maltose','sugar','carbohydrate','glucose','hexose','pentose','glycoside','xylose','porter','mfs-sugar']): return 'sugars/carbohydrate'
    if any(k in s for k in ['citrate','dicarboxylate','tricarboxylate','lactate','acetate','gluconate','slc13','trap','malate','succinate','organic-acid','gntp']): return 'organic acids'
    if 'fatty' in s: return 'fatty acids'
    if any(k in s for k in ['peptide','nickel','pot ']): return 'peptides'
    if any(k in s for k in ['amino acid','polar amino','branched-chain','apc']): return 'amino acids'
    if any(k in s for k in ['nucleoside','nucleobase','purine','xanthine','uracil','ncs']): return 'nucleosides/bases'
    if any(k in s for k in ['betaine','choline','carnitine','bcct','osmoprotectant']): return 'osmolytes'
    if 'glycerol' in s: return 'glycerol'
    if any(k in s for k in ['benzoate','aromatic','phenylprop','hcat']): return 'aromatics'
    return 'other'

# ---- Fig A: compound-class landscape (HOT1A3) ----
h=list(csv.DictReader(open('data/system_scores_hot1a3_day11.csv')))
by=defaultdict(list)
for r in h:
    p=r.get('system_percentile','')
    if p not in('','None'): by[cclass(r.get('substrate',''),r.get('carrier_family',''))].append(float(p))
INORG=0.59  # control-ABC reference
med={c:statistics.median(v) for c,v in by.items() if c!='other'}
med['iron (TonB, confound)']=0.757  # reported finding, dropped from scoring
order=sorted(med, key=lambda c:med[c])
vals=[med[c] for c in order]
cols=[VERM if 'iron' in c else (BLUE if med[c]>=INORG else ORANGE) for c in order]
fig,ax=plt.subplots(figsize=(6.4,4.2))
ax.barh(order,vals,color=cols,height=0.62)
ax.axvline(INORG,color=GREY,ls='--',lw=1.2)
ax.text(INORG+0.015,1.0,f'inorganic\nref {INORG:.2f}',color=GREY,fontsize=8,ha='left',va='center')
for i,v in enumerate(vals): ax.text(v+0.008,i,f'{v:.2f}',va='center',fontsize=8,color='#333')
ax.set_xlim(0,1.0); ax.set_xlabel('median up-percentile (coculture vs axenic)')
ax.set_title('Sugars & nucleosides most induced; amino acids not up (HOT1A3 day-11)',fontsize=10)
plt.tight_layout(); plt.savefig('figures/figA_compound_class_landscape.svg',bbox_inches='tight'); plt.close()

# ---- Fig B: cross-experiment reproducibility (candidate class medians) ----
def cand_med(fn):
    rows=[r for r in csv.DictReader(open(fn)) if r['reference_class']=='candidate']
    d=defaultdict(list)
    for r in rows:
        p=r.get('module_percentile','')
        if p not in('','None'): d[cclass(r.get('substrate',''),r.get('carrier_family',''))].append(float(p))
    return {c:statistics.median(v) for c,v in d.items()}
E={'HOT1A3':cand_med('data/module_catalog_hot1a3_day11_v2.csv'),
   'EZ55-400':cand_med('data/module_catalog_ez55_400.csv'),
   'EZ55-800':cand_med('data/module_catalog_ez55_800.csv')}
classes=['sugars/carbohydrate','organic acids','osmolytes','nucleosides/bases']
expc={'HOT1A3':BLUE,'EZ55-400':SKY,'EZ55-800':ORANGE}
import numpy as np
x=np.arange(len(classes)); w=0.26
fig,ax=plt.subplots(figsize=(6.6,3.8))
for i,(e,c) in enumerate(expc.items()):
    vals=[E[e].get(cl,np.nan) for cl in classes]
    ax.bar(x+(i-1)*w,[0 if v!=v else v for v in vals],w,label=e,color=c)
    for j,v in enumerate(vals):
        if v==v: ax.text(x[j]+(i-1)*w,v+0.01,f'{v:.2f}',ha='center',fontsize=7,color='#333')
ax.axhline(0.5,color=GREY,ls=':',lw=1)
ax.set_xticks(x); ax.set_xticklabels([c.replace('/','/\n') for c in classes],fontsize=8)
ax.set_ylim(0,1.05); ax.set_ylabel('candidate class median up-percentile')
ax.set_title('Sugars reproduce across strains (HOT1A3 + EZ55-400)',fontsize=10)
ax.legend(frameon=False,fontsize=8,ncol=3,loc='upper center',bbox_to_anchor=(0.5,-0.18))
plt.tight_layout(); plt.savefig('figures/figB_cross_experiment_classes.svg',bbox_inches='tight'); plt.close()

# ---- Fig C: temporal L-lactate coculture vs axenic ----
t=[r for r in csv.DictReader(open('data/temporal_module_scores.csv')) if r['omics']=='rnaseq' and 'L-lactate' in r['substrate']]
def val(arm,tp):
    for r in t:
        if r['arm']==arm and r['timepoint']==tp: return float(r['pct'])
    return None
xs=[0,1,2,3]; labels=['day 18','day 31','day 60','day 89']
co=[val('coculture',tp) for tp in labels]
# axenic has day18/day31 and a COMBINED 'days 60+89' point -> plot at the day-89 position (honest: axenic catches up late)
ax_=[val('axenic','day 18'),val('axenic','day 31'),None,val('axenic','days 60+89')]
fig,ax=plt.subplots(figsize=(6.1,3.9))
ax.plot(xs,co,'-o',color=BLUE,lw=2,ms=6,label='coculture')
axx=[x for x,y in zip(xs,ax_) if y is not None]; axy=[y for y in ax_ if y is not None]
ax.plot(axx,axy,'--s',color=ORANGE,lw=2,ms=6,label='axenic (60+89 combined)')
ax.axhline(0.9,color=GREY,ls=':',lw=1); ax.text(0,0.915,'≈ q<0.10',color=GREY,fontsize=7)
ax.set_xticks(xs); ax.set_xticklabels(labels); ax.set_ylim(0,1.03)
ax.set_ylabel('L-lactate transporter up-percentile'); ax.set_xlabel('starvation timepoint')
ax.set_title('L-lactate ramps early in coculture (day 31); axenic only at late starvation',fontsize=9.5)
ax.legend(frameon=False,fontsize=9,loc='center right')
plt.tight_layout(); plt.savefig('figures/figC_temporal_lactate.svg',bbox_inches='tight'); plt.close()
print("wrote figA/figB/figC to figures/")

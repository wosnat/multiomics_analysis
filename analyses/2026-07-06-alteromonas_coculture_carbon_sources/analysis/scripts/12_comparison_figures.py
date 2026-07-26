import csv, matplotlib
from collections import defaultdict
matplotlib.use('Agg'); import matplotlib.pyplot as plt
BLUE='#0072B2'; ORANGE='#E69F00'; GREEN='#009E73'; VERM='#D55E00'; PURPLE='#CC79A7'; SKY='#56B4E9'; GREY='#8a8a8a'
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
def cclass(sub,fam=''):
    s=(str(sub)+' '+str(fam)).lower()
    if any(k in s for k in ['fucose','maltose','sugar','carbohydrate','glucose','hexose','glycoside','porter','mfs-sugar','porin']): return 'sugars'
    if any(k in s for k in ['citrate','dicarboxylate','tricarboxylate','lactate','acetate','gluconate','slc13','trap','organic-acid','gntp']): return 'organic acids'
    if 'fatty' in s: return 'fatty acids'
    if any(k in s for k in ['peptide','nickel','pot ']): return 'peptides'
    if any(k in s for k in ['amino acid','polar amino','branched-chain','apc']): return 'amino acids'
    if any(k in s for k in ['nucleoside','nucleobase','purine','xanthine','uracil','ncs']): return 'nucleosides'
    if any(k in s for k in ['betaine','choline','carnitine','bcct']): return 'osmolytes'
    if 'glycerol' in s: return 'glycerol'
    if any(k in s for k in ['benzoate','aromatic','phenylprop','hcat']): return 'aromatics'
    return 'other'
CLCOL={'sugars':BLUE,'organic acids':GREEN,'amino acids':ORANGE,'peptides':PURPLE,'nucleosides':SKY,
       'osmolytes':VERM,'aromatics':'#000000','glycerol':'#999999','fatty acids':'#7B3294','other':'#cccccc'}

# ===== Fig F: RNA-seq vs proteomics (temporal coculture, per module, max over timepoints) =====
t=list(csv.DictReader(open('data/temporal_module_scores.csv')))
def maxpct(omics,arm,sub):
    vs=[float(r['pct']) for r in t if r['omics']==omics and r['arm']==arm and r['substrate']==sub and r['pct'] not in('','None')]
    return max(vs) if vs else None
subs=sorted(set(r['substrate'] for r in t))
pts=[(maxpct('rnaseq','coculture',s), maxpct('proteomics','coculture',s), s) for s in subs]
pts=[(x,y,s) for x,y,s in pts if x is not None and y is not None]
fig,ax=plt.subplots(figsize=(5.6,5.2))
ax.plot([0,1],[0,1],ls=':',color=GREY,lw=1)
for x,y,s in pts:
    ax.scatter(x,y,s=42,color=CLCOL.get(cclass(s),'#ccc'),edgecolor='white',lw=0.5,zorder=3)
ax.axhline(0.9,color=GREY,ls='--',lw=0.7); ax.axvline(0.9,color=GREY,ls='--',lw=0.7)
ax.set_xlim(0,1.03); ax.set_ylim(0,1.03)
ax.set_xlabel('RNA-seq up-percentile (coculture, max timepoint)')
ax.set_ylabel('proteomics up-percentile (coculture, max)')
ax.set_title(f'RNA vs proteomics (coculture temporal): proteomics underpowered —\n0 modules reach q<0.10 in any arm; transcript signal neither confirmed nor refuted (n={len(pts)})',fontsize=8.2)
hand=[plt.Line2D([],[],marker='o',ls='',color=CLCOL[c],label=c) for c in ['sugars','organic acids','amino acids','peptides','nucleosides']]
ax.legend(handles=hand,frameon=False,fontsize=7,loc='lower right')
plt.tight_layout(); plt.savefig('figures/figF_rna_vs_proteomics.svg',bbox_inches='tight'); plt.close()

# ===== Fig G: EZ55 vs HOT1A3 (candidate module up-percentile, by substrate) =====
def cat(fn):
    d={}
    for r in csv.DictReader(open(fn)):
        if r['reference_class']=='candidate' and r.get('module_percentile') not in ('','None'): d[r['substrate']]=float(r['module_percentile'])
    return d
H=cat('data/module_catalog_hot1a3_day11_v2.csv')
E4=cat('data/module_catalog_ez55_400.csv'); E8=cat('data/module_catalog_ez55_800.csv')
Emax={s:max([v for v in (E4.get(s),E8.get(s)) if v is not None]) for s in set(E4)|set(E8)}
both=sorted(set(H)&set(Emax))
fig,ax=plt.subplots(figsize=(5.8,5.2))
ax.plot([0,1],[0,1],ls=':',color=GREY,lw=1)
for s in both:
    ax.scatter(H[s],Emax[s],s=48,color=CLCOL.get(cclass(s),'#ccc'),edgecolor='white',lw=0.5,zorder=3)
    ax.annotate(s[:16],(H[s],Emax[s]),fontsize=6,xytext=(3,3),textcoords='offset points')
ax.axhline(0.9,color=GREY,ls='--',lw=0.7); ax.axvline(0.9,color=GREY,ls='--',lw=0.7)
ax.set_xlim(0,1.03); ax.set_ylim(0,1.03)
ax.set_xlabel('HOT1A3 day-11 up-percentile'); ax.set_ylabel('EZ55 up-percentile (max of 400/800)')
ax.set_title(f'EZ55 vs HOT1A3 — n={len(both)} shared substrates (EZ55 sparse);\nfucose/carb-porin reproduce, carb-MFS/maltose do NOT; 1 organic acid (acetate) anti-correlated',fontsize=7.8)
plt.tight_layout(); plt.savefig('figures/figG_ez55_vs_hot1a3.svg',bbox_inches='tight'); plt.close()
print(f"figF (n={len(pts)} RNA/protein modules), figG (n={len(both)} shared substrates)")

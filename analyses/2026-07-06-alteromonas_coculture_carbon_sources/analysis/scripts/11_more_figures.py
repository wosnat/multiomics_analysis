import csv, statistics
from collections import defaultdict
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
BLUE='#0072B2'; SKY='#56B4E9'; ORANGE='#E69F00'; VERM='#D55E00'; GREEN='#009E73'; PURPLE='#CC79A7'; GREY='#8a8a8a'
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})

def cclass(sub,fam=''):
    s=(str(sub)+' '+str(fam)).lower()
    if any(k in s for k in ['fucose','maltose','sugar','carbohydrate','glucose','hexose','pentose','glycoside','xylose','porter','mfs-sugar','porin']): return 'sugars'
    if any(k in s for k in ['citrate','dicarboxylate','tricarboxylate','lactate','acetate','gluconate','slc13','trap','malate','succinate','organic-acid','gntp']): return 'organic acids'
    if 'fatty' in s: return 'fatty acids'
    if any(k in s for k in ['peptide','nickel','pot ']): return 'peptides'
    if any(k in s for k in ['amino acid','polar amino','branched-chain','apc']): return 'amino acids'
    if any(k in s for k in ['nucleoside','nucleobase','purine','xanthine','uracil','ncs']): return 'nucleosides'
    if any(k in s for k in ['betaine','choline','carnitine','bcct','osmoprotectant']): return 'osmolytes'
    if 'glycerol' in s: return 'glycerol'
    if any(k in s for k in ['benzoate','aromatic','phenylprop','hcat']): return 'aromatics'
    return 'other/unresolved'

# ===== Fig D: candidate transporter landscape (HOT1A3), count by class, single vs multi =====
pl=[r for r in csv.DictReader(open('../methods/data/parts_list_v2.csv')) if 'HOT1A3' in r['organism_name'] and r.get('reference_class')=='candidate']
byclass=defaultdict(lambda:[0,0])  # [single, multi]
seen=set()
for r in pl:
    sid=r['system_id']
    if sid in seen: continue
    seen.add(sid)
    n=int(r['system_size']) if r['system_size'] not in ('','None') else 1
    byclass[cclass(r['substrate_provisional'],r['carrier_family'])][0 if n==1 else 1]+=1
order=sorted(byclass,key=lambda c:-(byclass[c][0]+byclass[c][1]))
sg=[byclass[c][0] for c in order]; mg=[byclass[c][1] for c in order]
fig,ax=plt.subplots(figsize=(6.4,4.0))
ax.barh(order,sg,color=BLUE,label='single-gene',height=0.66)
ax.barh(order,mg,left=sg,color=ORANGE,label='multi-subunit',height=0.66)
for i,c in enumerate(order):
    tot=sg[i]+mg[i]; ax.text(tot+0.1,i,str(tot),va='center',fontsize=8,color='#333')
ax.invert_yaxis(); ax.set_xlabel('candidate transporter systems (HOT1A3)')
ax.set_title('Transporter repertoire by carbon class — amino acids & sugars largest,\nalmost all single-gene',fontsize=9.5)
ax.legend(frameon=False,fontsize=8,loc='lower right')
plt.tight_layout(); plt.savefig('figures/figD_transporter_landscape.svg',bbox_inches='tight'); plt.close()

# ===== Fig E: heatmap modules x experiments (presence|RNA|proteomics), class-ordered, dividers, * = q<0.10 =====
def catmap(fn):  # -> {sub:(pct,q)}
    d={}
    for r in csv.DictReader(open(fn)):
        if r['reference_class']=='candidate' and r.get('module_percentile') not in ('','None'):
            q=r.get('q','')
            d[r['substrate']]=(float(r['module_percentile']), float(q) if q not in ('','None') else None)
    return d
tp=list(csv.DictReader(open('data/temporal_module_scores.csv')))
def tmap(omics,arm,t):  # -> {sub:(pct,q)}
    d={}
    for r in tp:
        if r['omics']==omics and r['arm']==arm and r['timepoint']==t and r.get('pct') not in ('','None'):
            q=r.get('q','')
            d[r['substrate']]=(float(r['pct']), float(q) if q not in ('','None') else None)
    return d
# column groups
presence=[('HOT1A3 d11',catmap('data/module_catalog_hot1a3_day11_v2.csv')),
          ('EZ55-400',catmap('data/module_catalog_ez55_400.csv')),
          ('EZ55-800',catmap('data/module_catalog_ez55_800.csv'))]
def tgroup(omics):
    g=[]
    for arm,short in [('coculture','co'),('axenic','ax')]:
        tps=(['day 18','day 31','day 60','day 89'] if arm=='coculture'
             else (['day 18','day 31','days 60+89'] if omics=='rnaseq' else ['day 18','day 31']))
        for t in tps:
            m=tmap(omics,arm,t)
            if m: g.append((f'{short} {t.replace("days ","d").replace("day ","d")}',m))
    return g
groups=[('presence',presence),('RNA temporal',tgroup('rnaseq')),('proteome temporal',tgroup('proteomics'))]
cols=[]; colmaps=[]; vbounds=[]; glab=[]
for gname,g in groups:
    glab.append((len(cols)+(len(g)-1)/2, gname))
    for lbl,m in g: cols.append(lbl); colmaps.append(m)
    vbounds.append(len(cols)-0.5)
vbounds=vbounds[:-1]
# rows ordered: up-classes first, then within-class by HOT1A3 pct desc
H={s:v[0] for s,v in presence[0][1].items()}
classorder=['sugars','nucleosides','organic acids','osmolytes','aromatics','other/unresolved','peptides','amino acids','fatty acids','glycerol']
allsub=set()
for m in colmaps: allsub|=set(m)
def ckey(s):
    c=cclass(s); return (classorder.index(c) if c in classorder else 99, -H.get(s,-1))
subs=sorted(allsub,key=ckey); rowcl=[cclass(s) for s in subs]
M=np.full((len(subs),len(cols)),np.nan); SIG=np.zeros_like(M,dtype=bool)
for i,s in enumerate(subs):
    for j,m in enumerate(colmaps):
        if s in m:
            M[i,j]=m[s][0]
            if m[s][1] is not None and m[s][1]<0.10: SIG[i,j]=True
fig,ax=plt.subplots(figsize=(11.5,max(5,0.30*len(subs))))
cmap=plt.cm.RdBu_r.copy(); cmap.set_bad('#e8e8e8')
im=ax.imshow(M,aspect='auto',cmap=cmap,vmin=0,vmax=1)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols,rotation=45,ha='right',fontsize=7)
ax.set_yticks(range(len(subs))); ax.set_yticklabels([s[:30] for s in subs],fontsize=6.5)
# significance asterisks
for i in range(len(subs)):
    for j in range(len(cols)):
        if SIG[i,j]: ax.text(j,i,'*',ha='center',va='center',fontsize=9,color='black',fontweight='bold')
# vertical group dividers + group labels
for b in vbounds: ax.axvline(b,color='black',lw=2.2)
for x,g in glab: ax.text(x,-1.6,g,ha='center',va='bottom',fontsize=8.5,fontweight='bold')
# thin dashed coculture|axenic sub-divider within each temporal group
for j in range(1,len(cols)):
    a,b=cols[j-1],cols[j]
    if 'co' in a and 'ax' in b and a.startswith('P')==b.startswith('P'):
        ax.axvline(j-0.5,color='#444',lw=1.0,ls=(0,(4,2)))
# horizontal class dividers + left class labels
start=0
for i in range(1,len(subs)+1):
    if i==len(subs) or rowcl[i]!=rowcl[start]:
        if i<len(subs): ax.axhline(i-0.5,color='black',lw=1.3)
        ax.text(-0.20,(start+i-1)/2,rowcl[start],transform=ax.get_yaxis_transform(),
                ha='right',va='center',fontsize=7.5,fontweight='bold',color='#333',clip_on=False)
        start=i
cb=plt.colorbar(im,ax=ax,fraction=0.018,pad=0.01); cb.set_label('up-percentile',fontsize=8)
ax.set_title('Candidate module up-percentile by class  ·  * = q<0.10  ·  grey = not scored',fontsize=10)
plt.subplots_adjust(left=0.30)
plt.savefig('figures/figE_experiment_substrate_heatmap.svg',bbox_inches='tight'); plt.close()
print(f"figD ({len(order)} classes), figE ({len(subs)} substrates x {len(cols)} cols) written")

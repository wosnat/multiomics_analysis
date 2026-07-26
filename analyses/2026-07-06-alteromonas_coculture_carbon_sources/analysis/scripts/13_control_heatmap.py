import csv, numpy as np, matplotlib
from collections import defaultdict
matplotlib.use('Agg'); import matplotlib.pyplot as plt
GREY='#8a8a8a'
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
rows=list(csv.DictReader(open('data/control_module_scores.csv')))
# same column order/groups as candidate Fig E
COLS=['HOT1A3 d11','EZ55-400','EZ55-800',
      'co d18','co d31','co d60','co d89','ax d18','ax d31','ax d60+89',
      'P co d18','P co d31','P co d60','P co d89','P ax d18','P ax d31']
vbounds=[2.5, 9.5]  # presence|RNA , RNA|proteome
glab=[(1,'presence'),(6,'RNA temporal'),(12.5,'proteome temporal')]
# rows grouped by reference_class, then substrate
refkey={'control-ABC':0,'control-TonB':1,'ambiguous-TonB':2}
cell=defaultdict(dict); rc={}
for r in rows:
    key=(r['reference_class'],r['substrate'])
    lbl=r['experiment_label']
    if r.get('module_percentile') not in ('','None'):
        q=r.get('q',''); cell[key][lbl]=(float(r['module_percentile']), float(q) if q not in('','None') else None)
    rc[key]=r['reference_class']
keys=sorted(cell.keys(), key=lambda k:(refkey.get(k[0],9), k[1]))
M=np.full((len(keys),len(COLS)),np.nan); SIG=np.zeros_like(M,bool)
for i,k in enumerate(keys):
    for j,c in enumerate(COLS):
        if c in cell[k]:
            M[i,j]=cell[k][c][0]
            if cell[k][c][1] is not None and cell[k][c][1]<0.10: SIG[i,j]=True
fig,ax=plt.subplots(figsize=(11.5,max(4,0.30*len(keys))))
cmap=plt.cm.RdBu_r.copy(); cmap.set_bad('#e8e8e8')
im=ax.imshow(M,aspect='auto',cmap=cmap,vmin=0,vmax=1)
ax.set_xticks(range(len(COLS))); ax.set_xticklabels(COLS,rotation=45,ha='right',fontsize=7)
ax.set_yticks(range(len(keys))); ax.set_yticklabels([k[1][:30] for k in keys],fontsize=6.5)
for i in range(len(keys)):
    for j in range(len(COLS)):
        if SIG[i,j]: ax.text(j,i,'*',ha='center',va='center',fontsize=9,fontweight='bold')
for b in vbounds: ax.axvline(b,color='black',lw=2.2)
for x,g in glab: ax.text(x,-1.2,g,ha='center',va='bottom',fontsize=8.5,fontweight='bold')
for j in range(1,len(COLS)):
    a,b=COLS[j-1],COLS[j]
    if 'co' in a and 'ax' in b and a.startswith('P')==b.startswith('P'):
        ax.axvline(j-0.5,color='#444',lw=1.0,ls=(0,(4,2)))
grp=[refkey.get(k[0],9) for k in keys]; start=0
for i in range(1,len(keys)+1):
    if i==len(keys) or grp[i]!=grp[start]:
        if i<len(keys): ax.axhline(i-0.5,color='black',lw=1.3)
        ax.text(-0.22,(start+i-1)/2,keys[start][0],transform=ax.get_yaxis_transform(),
                ha='right',va='center',fontsize=7.5,fontweight='bold',color='#333',clip_on=False)
        start=i
cb=plt.colorbar(im,ax=ax,fraction=0.018,pad=0.01); cb.set_label('up-percentile',fontsize=8)
ax.set_title('CONTROL modules (same scale as candidates)  ·  * = q<0.10  ·  grey = not scored',fontsize=10)
plt.subplots_adjust(left=0.30)
plt.savefig('figures/figE2_control_heatmap.svg',bbox_inches='tight'); plt.close()
print(f"figE2 control heatmap: {len(keys)} control modules x {len(COLS)} cols")

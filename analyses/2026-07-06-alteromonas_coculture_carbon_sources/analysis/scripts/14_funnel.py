import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
plt.rcParams.update({'font.size':10,'figure.dpi':140})
# stages: (count-inside, right-label, right-detail)
stages=[
 (4028, 'HOT1A3 genome', '4028 genes'),
 (684,  'Transporter genes', 'union of BRITE ∪ KEGG-KO ∪ TCDB ∪ annotation'),
 (57,   'Organic-C candidate systems', 'curated: drop regulators/enzymes/exporters, inorganic, TonB'),
 (46,   'Candidate modules scored', 'HOT1A3 day-11 presence contrast'),
 (2,    'Pass q<0.10 (HOT1A3)', 'carbohydrate-MFS, benzoate'),
 (1.2,  'Reproducible class-level signal', 'sugars  (+ organic acids, weaker)'),
]
N=len(stages); mx=np.log10(4028)
def w(c): return 0.10+0.60*(np.log10(max(c,1.2))/mx)   # log-scaled half-width
ws=[w(c) for c,_,_ in stages]
fig,ax=plt.subplots(figsize=(9.4,6.2))
ax.set_xlim(-0.85,2.35); ax.set_ylim(-0.4,N); ax.axis('off')
colors=matplotlib.colormaps['Blues'](np.linspace(0.42,0.9,N))
CX=-0.05  # funnel centre x
for i,(c,lbl,det) in enumerate(stages):
    yt=N-i; yb=N-i-0.84
    wt=ws[i]; wb=ws[i+1] if i+1<N else ws[i]*0.7
    ax.add_patch(Polygon([(CX-wt,yt),(CX+wt,yt),(CX+wb,yb),(CX-wb,yb)],closed=True,
                 facecolor=colors[i],edgecolor='white',lw=1.6))
    yc=(yt+yb)/2
    cnt=f'{int(c)}' if c>=2 else ''
    ax.text(CX,yc,cnt,ha='center',va='center',fontsize=10.5,fontweight='bold',
            color='white' if i>=2 else '#0b2447')
    # right-side label
    ax.text(0.78,yc+0.12,lbl,ha='left',va='center',fontsize=10,fontweight='bold',color='#123')
    ax.text(0.78,yc-0.16,det,ha='left',va='center',fontsize=8,color='#555')
ax.set_title('Analysis funnel — transporter repertoire → candidate carbon classes',fontsize=12,pad=8,loc='left')
ax.text(CX,-0.28,'→ prioritized shortlist for wet-lab growth assays (not named compounds; iron up = confound)',
        ha='center',va='top',fontsize=8.5,color='#555',style='italic')
plt.tight_layout(); plt.savefig('figures/figH_analysis_funnel.svg',bbox_inches='tight'); plt.close()
print("figH funnel written")

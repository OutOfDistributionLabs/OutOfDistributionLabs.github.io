import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42,'font.family':'DejaVu Sans'})
p=Path(__file__).resolve().parent;s=json.loads((p/'results.json').read_text())['summary'];fig,axes=plt.subplots(1,3,figsize=(11.5,3.4))
colors={'broadcast':'#9aa5b1','flat-index':'#4e758e','primary-hierarchy':'#b98b48','guarded-multiview':'#162a3b'}
for ax,scenario in zip(axes,['local','cross-cutting','coverage-gap']):
 for name,color in colors.items():
  rows=[r for r in s if r['workers']==300 and r['scenario']==scenario and r['strategy']==name]
  ax.plot([r['overlap'] for r in rows],[r['mean_candidates']/300*100 for r in rows],marker='o',label=name,color=color,lw=1.6)
 ax.set(title=scenario.replace('-',' ').capitalize(),xlabel='Secondary membership probability',ylim=(0,105),xticks=[0,.25,.5]);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15)
axes[0].set_ylabel('Candidate workers (% of 300)');handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,ncol=4,loc='lower center',frameon=False,fontsize=8);fig.tight_layout(rect=(0,.12,1,1));fig.savefig(p.parent/'figures/routing.pdf',bbox_inches='tight');fig.savefig(p.parent/'figures/routing.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(6,3))
for name,color in colors.items():
 rows=[r for r in s if r['workers']==300 and r['scenario']=='local' and r['strategy']==name]
 ax.plot([r['overlap'] for r in rows],[r['mean_recall']*100 for r in rows],marker='o',label=name,color=color,lw=1.6)
ax.set(xlabel='Secondary membership probability',ylabel='Eligible-worker recall (%)',ylim=(55,103),xticks=[0,.25,.5]);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.legend(frameon=False,fontsize=8,loc='lower left');fig.tight_layout();fig.savefig(p.parent/'figures/recall.pdf',bbox_inches='tight');plt.close(fig)

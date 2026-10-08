"""Generate publication plots/tables from measured files, never invented points."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'ps.fonttype':42,'font.size':10})
def generate(folder):
    p=Path(folder);r=json.loads((p/'results.json').read_text());a=json.loads((p/'analysis.json').read_text());out=p/'figures';out.mkdir(exist_ok=True)
    modes=['scan','flat','graph'];labels=['Lexical scan','Flat BM25','Graph + BM25'];colors=['#647683','#4E758E','#B18A50'];arm=r['arms']['evaluation']
    fig,ax=plt.subplots(figsize=(7,3.1));values=[100*arm[x]['upstream_success_08'] for x in modes];bars=ax.bar(labels,values,color=colors,width=.55)
    ax.set_ylim(0,60);ax.set_ylabel('Top-one similarity success (%)');ax.set_title('480 tasks held out by repository; deterministic retrieval',loc='left',fontsize=11);ax.spines[['top','right']].set_visible(False)
    for bar,val in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,val+1,f'{val:.2f}%',ha='center')
    fig.tight_layout();fig.savefig(out/'success.pdf');fig.savefig(out/'success.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.1));cs=a['comparisons'];names=['Graph − flat','Graph − scan','Flat − scan'];ds=[100*c['difference'] for c in cs]
    for i,c in enumerate(cs):
        lo,hi=[100*x for x in c['repository_cluster_bootstrap_95']];ax.plot([lo,hi],[i,i],color=colors[i],lw=2);ax.scatter([ds[i]],[i],color=colors[i],s=30)
    ax.axvline(0,color='#9aabb7',lw=1,ls='--');ax.set_yticks(range(3),names);ax.invert_yaxis();ax.set_xlabel('Paired success difference (percentage points)');ax.set_title('Exploratory 95% repository-cluster bootstrap intervals',loc='left',fontsize=11);ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(out/'differences.pdf');fig.savefig(out/'differences.png',dpi=180);plt.close(fig)
    rows=[]
    for mode,label in zip(modes,labels):
        x=arm[mode];rows.append(f"{label} & {round(x['upstream_success_08']*x['n'])}/{x['n']} & {100*x['upstream_success_08']:.2f} & {100*x['recall_at_10']:.2f} & {x['query_cpu_ms_mean']:.3f} & {x['build_cpu_ms_per_repo_mean']:.1f} "+chr(92)*2)
    (p/'table.tex').write_text('\n'.join(rows)+'\n')
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('folder');a=p.parse_args();generate(a.folder)

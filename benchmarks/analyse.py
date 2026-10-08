"""Paired descriptive analysis; not a repair/agent-effectiveness test."""
import csv
import json
import math
from pathlib import Path
import random
import statistics

def exact_mcnemar(wins,losses):
    n=wins+losses
    if not n:return 1.0
    return min(1.0,2*sum(math.comb(n,k) for k in range(min(wins,losses)+1))/2**n)
def paired(rows,arm,baseline,draws=10000,seed=20261007):
    tasks={}
    for r in rows:
        if r['split']!='evaluation':continue
        tasks.setdefault(r['task_id'],{'repo':r['repo'],'language':r['language']})[r['arm']]=int(r['upstream_success_08'])
    pairs=list(tasks.values())
    if any(arm not in x or baseline not in x for x in pairs):raise ValueError('Incomplete pair')
    ds=[x[arm]-x[baseline] for x in pairs];wins=sum(d==1 for d in ds);losses=sum(d==-1 for d in ds)
    groups={}
    for x,d in zip(pairs,ds):groups.setdefault(x['repo'],[]).append(d)
    rng=random.Random(seed);repos=sorted(groups);cluster=[];stratified=[]
    for _ in range(draws):
        picked=[rng.choice(repos) for _ in repos];cluster.append(statistics.mean(d for repo in picked for d in groups[repo]))
        stratified.append(statistics.mean(rng.choice(groups[repo]) for repo in repos for _ in groups[repo]))
    def interval(values):
        a=sorted(values);return [a[int(.025*(len(a)-1))],a[int(.975*(len(a)-1))]]
    return {'contrast':arm+' minus '+baseline,'n_tasks':len(ds),'n_repositories':len(groups),'difference':statistics.mean(ds),'wins':wins,'losses':losses,'exact_mcnemar_p_unadjusted_descriptive':exact_mcnemar(wins,losses),'repository_cluster_bootstrap_95':interval(cluster),'repository_stratified_instance_bootstrap_95':interval(stratified),'bootstrap_draws':draws,'seed':seed,'interpretation':'exploratory retrieval contrast; not the preregistered patch-resolution hypothesis'}
def analyse(folder):
    p=Path(folder);rows=list(csv.DictReader((p/'raw-results.csv').open()));results=json.loads((p/'results.json').read_text())
    if len(rows)!=1800 or len({(r['task_id'],r['arm']) for r in rows})!=1800:raise ValueError('Outcome accounting failed')
    comparisons=[paired(rows,'graph','flat'),paired(rows,'graph','scan'),paired(rows,'flat','scan')]
    # Holm on the descriptive three-comparison assay family; different from future H2 confirmatory tests.
    previous=0
    for i,c in enumerate(sorted(comparisons,key=lambda c:c['exact_mcnemar_p_unadjusted_descriptive'])):
        previous=max(previous,min(1,(len(comparisons)-i)*c['exact_mcnemar_p_unadjusted_descriptive']));c['holm_p_descriptive']=previous
    by_language={}
    for lang in sorted({r['language'] for r in rows}):
        by_language[lang]={}
        for arm in ['scan','flat','graph']:
            a=[r for r in rows if r['split']=='evaluation' and r['language']==lang and r['arm']==arm]
            by_language[lang][arm]={'n':len(a),'success':sum(int(r['upstream_success_08']) for r in a)/len(a)}
    a={'scope':'exploratory non-LLM full-repository retrieval','comparisons':comparisons,'by_language':by_language,'hardware_timing_caveat':'Single container, randomized arm build order, per-arm rebuilds but shared OS/interpreter caches; in-process queries exclude MCP IPC, workspace revision hashing and upstream scoring. Builds are per repository, reused for ten tasks. No cloud billing data.'}
    (p/'analysis.json').write_text(json.dumps(a,indent=2)+'\n');return a
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('folder');a=p.parse_args();print(json.dumps(analyse(a.folder),indent=2))

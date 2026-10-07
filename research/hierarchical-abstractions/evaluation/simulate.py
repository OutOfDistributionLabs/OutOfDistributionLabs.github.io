#!/usr/bin/env python3
"""Deterministic capability-routing simulation, not an LLM-agent benchmark."""
import argparse,csv,json,random,statistics
from pathlib import Path
P=Path(__file__).resolve().parent
STRATEGIES=['broadcast','flat-index','primary-hierarchy','guarded-multiview']
def trial(n,overlap,scenario,seed,queries):
    rng=random.Random(seed);primary={};full={};coverage={};modules=16;skills=4
    def add(index,key,i):index.setdefault(key,set()).add(i)
    for i in range(n):
        key=(rng.randrange(modules),rng.randrange(skills));add(primary,key,i);add(full,key,i)
        if rng.random()<overlap:
            other=((key[0]+rng.randrange(1,modules))%modules,rng.randrange(skills));add(full,other,i)
    # Deterministic index-coverage failures; guarded policy falls back to broadcast.
    for m in range(modules):
        for skill in range(skills):coverage[(m,skill)]=not(scenario=='coverage-gap' and rng.random()<.1)
    rows={name:{'candidates':[],'recall':[],'visits':[],'fallbacks':0} for name in STRATEGIES}
    allworkers=set(range(n))
    for q in range(queries):
        if scenario=='cross-cutting':
            skill=rng.randrange(skills);keys={(m,skill) for m in rng.sample(range(modules),4)}
        else:keys={(rng.randrange(modules),rng.randrange(skills))}
        eligible=set().union(*(full.get(key,set()) for key in keys))
        if not eligible:continue  # Recall undefined for empty truth sets; reported count records exclusions.
        primary_candidates=set().union(*(primary.get(key,set()) for key in keys))
        exact=set(eligible)
        guard_fallback=not all(coverage[key] for key in keys)
        candidates={'broadcast':allworkers,'flat-index':exact,'primary-hierarchy':primary_candidates,'guarded-multiview':allworkers if guard_fallback else exact}
        hierarchy_visits=1+len({key[0]//4 for key in keys})+len({key[0] for key in keys})+len(keys)
        for name in STRATEGIES:
            found=candidates[name];rows[name]['candidates'].append(len(found));rows[name]['recall'].append(len(found&eligible)/len(eligible))
            visits=0 if name=='broadcast' else (len(keys) if name=='flat-index' else hierarchy_visits)
            if name=='guarded-multiview':visits+=len(keys);rows[name]['fallbacks']+=int(guard_fallback)
            rows[name]['visits'].append(visits)
    return [dict(workers=n,overlap=overlap,scenario=scenario,seed=seed,strategy=name,eligible_queries=len(v['recall']),mean_candidates=statistics.mean(v['candidates']),mean_recall=statistics.mean(v['recall']),mean_index_visits=statistics.mean(v['visits']),fallback_rate=v['fallbacks']/len(v['recall'])) for name,v in rows.items()]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--queries',type=int,default=300);parser.add_argument('--seeds',type=int,default=20);args=parser.parse_args()
    allrows=[]
    for n in [100,300,1000]:
        for overlap in [0,.25,.5]:
            for scenario in ['local','cross-cutting','coverage-gap']:
                for seed in range(args.seeds):allrows.extend(trial(n,overlap,scenario,seed,args.queries))
    with (P/'raw-results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(allrows[0]),lineterminator='\n');writer.writeheader();writer.writerows(allrows)
    summary=[]
    for n in [100,300,1000]:
        for overlap in [0,.25,.5]:
            for scenario in ['local','cross-cutting','coverage-gap']:
                for strategy in STRATEGIES:
                    rows=[r for r in allrows if (r['workers'],r['overlap'],r['scenario'],r['strategy'])==(n,overlap,scenario,strategy)]
                    record={'workers':n,'overlap':overlap,'scenario':scenario,'strategy':strategy,'seeds':len(rows),'eligible_queries':sum(r['eligible_queries'] for r in rows)}
                    for metric in ['mean_candidates','mean_recall','mean_index_visits','fallback_rate']:
                        values=[r[metric] for r in rows];record[metric]=statistics.mean(values);record[metric+'_sd']=statistics.stdev(values)
                    summary.append(record)
    out={'parameters':{'workers':[100,300,1000],'modules':16,'skills_per_module':4,'secondary_membership_probability':[0,.25,.5],'scenarios':['local','cross-cutting','coverage-gap'],'seeds':list(range(args.seeds)),'queries_per_seed':args.queries,'coverage_gap_probability':.1},'limitations':['Generated capability labels are both input and ground truth.','Logical workers do not execute, call LLMs, edit code or send network messages.','Candidate counts are delivery counts only if one notification is sent to each candidate.','Index visits are structural counts, not runtime latency or token consumption.','Flat-index has complete labels; primary-hierarchy deliberately omits secondary memberships.','Empty eligible sets are excluded from recall; seed means are then averaged equally.','Guarded-multiview knows index coverage perfectly; real detection is an untested assumption.'],'summary':summary}
    (P/'results.json').write_text(json.dumps(out,indent=2)+'\n')
    # Check mechanisms directly, rather than claiming superiority from means.
    assert all(r['mean_recall']==1 for r in allrows if r['strategy']!='primary-hierarchy')
    assert all(r['mean_recall']==1 for r in allrows if r['strategy']=='primary-hierarchy' and r['overlap']==0)
    assert all(r['mean_candidates']<=r['workers'] for r in allrows)
    def get(n,o,sc,st):return next(r for r in summary if (r['workers'],r['overlap'],r['scenario'],r['strategy'])==(n,o,sc,st))
    table=['| N | Secondary membership | Scenario | Strategy | Candidates, mean ± seed SD | Eligible-worker recall | Index visits |','|---:|---:|---|---|---:|---:|---:|']
    for n in [100,300,1000]:
        for scenario in ['local','cross-cutting','coverage-gap']:
            for strategy in STRATEGIES:
                r=get(n,.5,scenario,strategy);table.append(f'| {n} | 0.50 | {scenario} | {strategy} | {r["mean_candidates"]:.2f} ± {r["mean_candidates_sd"]:.2f} | {r["mean_recall"]:.3f} | {r["mean_index_visits"]:.2f} |')
    report='# Synthetic routing evaluation\n\nOut of Distribution Labs · October 7, 2026\n\n## Purpose\n\nIllustrate the consequences of membership completeness and hierarchy overlap; not evaluate language-model reasoning or software correctness. Python standard library; no external data. Run `python simulate.py` from this folder or invoke it by path. Default: 20 seeds (0–19), 300 queries per seed, 100/300/1,000 logical workers, 16 modules × 4 skills, secondary membership probability 0/.25/.5.\n\n## Baselines and stress tests\n\nBroadcast includes every worker. Flat-index unions all known exact-label memberships. Primary-hierarchy traverses a grouped 16-module hierarchy but retains only primary memberships. Guarded-multiview includes secondary memberships and falls back to broadcast when an explicit, perfectly known coverage flag is false. Local requests select one module/skill; cross-cutting requests select four modules with one skill; coverage-gap requests independently mark each label incomplete with probability .1. A flat index with equivalent complete memberships is a deliberately strong baseline: hierarchy should not receive credit for its indexing benefit.\n\n'+ '\n'.join(table)+'\n\n## Interpretation\n\nFlat indexing and complete multi-view hierarchy produce exactly the same candidate sets when no fallback occurs. Overlap causes recall loss only for the primary-only strategy; this ablation demonstrates the cost of missing memberships, not an intrinsic failure of all hierarchies. Perfectly detected coverage gaps restore recall through broadcast and increase the candidate budget sharply. The simulation supports neither a token-savings claim nor improved patch quality.\n\n## Uncertainty and limitations\n\n± values are sample standard deviations of seed-level means, not confidence intervals. Ground truth is generated from the same labels available to the complete index. Empty eligible sets are skipped for recall, and retained query counts are published. Hardware timing, graph building costs, stale state, actual message bytes, parser errors and LLM behavior are not measured. Coverage detection is an oracle in this experiment. Full parameters, all 2,160 seed/strategy rows and aggregate results are in `raw-results.csv` and `results.json`.\n'
    (P/'report.md').write_text(report)
    print('Generated',len(allrows),'seed/strategy records; selected results:')
    for sc in ['local','cross-cutting','coverage-gap']:
        for st in STRATEGIES:
            r=get(300,.5,sc,st);print(sc,st,'candidates',round(r['mean_candidates'],2),'recall',round(r['mean_recall'],3))
if __name__=='__main__':main()

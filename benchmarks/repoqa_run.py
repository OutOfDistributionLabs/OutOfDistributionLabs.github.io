"""Frozen non-LLM full-repository retrieval assay on real RepoQA tasks."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import random
import re
import subprocess
import time
from intuition_engine.core import Engine,stem
from .repoqa_assets import acquire,UpstreamScorer,DATA_SHA256,SOURCE_COMMIT

MODES=['scan','flat','graph']
CONFIG={'setting':'adapted_full_release_repository_non_llm_retrieval','dataset_sha256':DATA_SHA256,'scorer_commit':SOURCE_COMMIT,'max_candidates':10,'response_token_budget':16000,'bm25_k1':1.5,'bm25_b':.75,'graph_weights':{'entity':.8,'file_mean':.1,'module_mean':.05,'call_hint_mean':.05},'development_repositories_per_language':2,'split_rule':'first two repository IDs in lexical order per language are development','order_seed':20261007,'tuning':'none after freeze','primary_assay_endpoint':'upstream closest-needle similarity >= .8 at top one; not software repair success','source_fields_to_index':['content'],'query_fields':['current needle description'],'engine_model_calls':0}
def task_id(lang,repo,index):return hashlib.sha256(f'{lang}:{repo}:{index}'.encode()).hexdigest()[:24]
def write_csv(path,rows):
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def run(cache,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    if (out/'assay-freeze.json').exists():raise ValueError('Do not overwrite a frozen run: choose a new output directory')
    d,register=acquire(cache);scorer=UpstreamScorer(cache);root=Path(__file__).resolve().parents[1]
    code_files=['intuition_engine/core.py','benchmarks/repoqa_run.py','benchmarks/repoqa_assets.py']
    freeze={**CONFIG,'frozen_before_queries':True,'frozen_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'code_sha256':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in code_files},'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'dependencies':{k:importlib.metadata.version(k) for k in ['mcp','tree-sitter','tree-sitter-languages','nltk']}}
    manifest=[]
    for lang,repos in sorted(d.items()):
        for ri,r in enumerate(sorted(repos,key=lambda r:r['repo'])):
            for ni,n in enumerate(r['needles']):manifest.append({'task_id':task_id(lang,r['repo'],ni),'language':lang,'repo':r['repo'],'repository_commit':r['commit_sha'],'needle_ordinal':ni,'split':'development' if ri<2 else 'evaluation'})
    manifest_bytes=(json.dumps(manifest,indent=2)+'\n').encode();(out/'manifest.json').write_bytes(manifest_bytes);freeze['manifest_sha256']=hashlib.sha256(manifest_bytes).hexdigest();(out/'assay-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
    rows=[];builds=[];rng=random.Random(CONFIG['order_seed']);start=time.perf_counter()
    for lang,repos in sorted(d.items()):
        for ri,r in enumerate(sorted(repos,key=lambda r:r['repo'])):
            split='development' if ri<2 else 'evaluation';modes=MODES.copy();rng.shuffle(modes)
            for mode in modes:
                stem.cache_clear();e=Engine(r['content'],mode)
                builds.append({'language':lang,'repo':r['repo'],'split':split,'arm':mode,'build_cpu_ms':e.build_cpu_ms,'build_wall_ms':e.build_wall_ms,'entity_count':len(e.entities),'source_bytes':sum(len(x.encode()) for x in r['content'].values()),'parse_error_files':e.parse_errors,'file_count':len(r['content'])})
                canonical={(x.path,re.sub(r'\s+','',x.code)):x.id for x in e.entities}
                for ni,n in enumerate(r['needles']):
                    advice=e.query(e.snapshot_id,n['description'],max_candidates=10,response_token_budget=16000)
                    ids=[x['entity_id'] for x in advice['candidates']]
                    answer=e.by_id[ids[0]].code if ids else ''
                    outcome=scorer.score(answer,n,r,lang)
                    gold='\n'.join(r['content'][n['path']].split('\n')[n['start_line']:n['end_line']]);target=canonical.get((n['path'],scorer.canonical(gold,lang)))
                    rank=ids.index(target)+1 if target in ids else 0
                    rows.append({'task_id':task_id(lang,r['repo'],ni),'language':lang,'repo':r['repo'],'split':split,'arm':mode,'upstream_success_08':int(outcome['upstream_success_08']),'exact_top1':int(rank==1),'recall_at_10':int(rank>0),'reciprocal_rank_at_10':1/rank if rank else 0,'target_extractable':int(target is not None),'top1_similarity':outcome['best_similarity'],'query_cpu_ms':advice['usage']['query_cpu_ms'],'query_wall_ms':advice['usage']['query_wall_ms'],'response_bytes':advice['usage']['response_bytes'],'candidate_count':len(ids),'status':advice['status']})
            print(f"Measured {lang} {r['repo']} ({split}); {len(rows)} task/arm outcomes",flush=True)
    expected=len(manifest)*len(MODES)
    if len(rows)!=expected:raise ValueError('Missing task outcomes')
    write_csv(out/'raw-results.csv',rows);write_csv(out/'build-results.csv',builds)
    summary={'run_kind':'non_llm_retrieval_assay','tasks':len(manifest),'task_arm_outcomes':len(rows),'evaluation_tasks':sum(x['split']=='evaluation' for x in manifest),'development_tasks':sum(x['split']=='development' for x in manifest),'elapsed_seconds':time.perf_counter()-start,'engine_model_calls':0,'agent_model_calls':0,'agent_repair_trials':0,'arms':{}}
    for split in ['development','evaluation']:
        summary['arms'][split]={}
        for mode in MODES:
            a=[x for x in rows if x['split']==split and x['arm']==mode];b=[x for x in builds if x['split']==split and x['arm']==mode]
            summary['arms'][split][mode]={'n':len(a),'upstream_success_08':sum(x['upstream_success_08'] for x in a)/len(a),'exact_top1':sum(x['exact_top1'] for x in a)/len(a),'recall_at_10':sum(x['recall_at_10'] for x in a)/len(a),'mrr_at_10':sum(x['reciprocal_rank_at_10'] for x in a)/len(a),'target_extractable':sum(x['target_extractable'] for x in a)/len(a),'query_cpu_ms_mean':sum(x['query_cpu_ms'] for x in a)/len(a),'query_wall_ms_mean':sum(x['query_wall_ms'] for x in a)/len(a),'build_cpu_ms_per_repo_mean':sum(x['build_cpu_ms'] for x in b)/len(b),'build_wall_ms_per_repo_mean':sum(x['build_wall_ms'] for x in b)/len(b),'build_cpu_ms_total':sum(x['build_cpu_ms'] for x in b),'query_cpu_ms_total':sum(x['query_cpu_ms'] for x in a),'source_bytes':sum(x['source_bytes'] for x in b),'max_response_bytes':max(x['response_bytes'] for x in a)}
    (out/'results.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.cache,a.output)

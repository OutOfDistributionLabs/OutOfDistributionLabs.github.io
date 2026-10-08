"""Acquire pinned RepoQA inputs and invoke the actual audited upstream evaluator."""
import ast
import gzip
import hashlib
import json
from pathlib import Path
import re
from enum import Enum
import urllib.request
from tree_sitter_languages import get_language, get_parser
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

SOURCE_COMMIT='ae876deb1365dbf5a15b0533723c8ed123eee586'
DATA_VERSION='2024-06-23'
DATA_SHA256='bd3f7cab47283cdeccee20daea31af587b680cf8f9db192ab4da1037730cd6e2'
SOURCES={
 'repoqa_compute_score.py':('repoqa/compute_score.py','f4e9edaec292105272fb8d2f85f1f5b1b02f5caa4bd61a0c1f463a5f612664d8'),
 'repoqa_metric.py':('repoqa/metric.py','e477e85ed621aa540b9fdfe4f3e022f4077447f942d54fbec53b49e990cbbc38'),
 'repoqa_utility.py':('repoqa/utility.py','a8494598171769033bbff34fde155bae75f3cfb34cad62ef43cd0f73c0284e46')}
LICENSE_SHA256='fcc1f77fe5443b21bfc4dfcc3d66f7654f599b91582df771850e5e876986a103'
LICENSE_COMMIT='e3a571033de99d0b9dcaccd25577a75d4b1c70b1'

def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(url,limit=100_000_000):
    with urllib.request.urlopen(url,timeout=60) as r:
        b=r.read(limit+1)
    if len(b)>limit:raise ValueError('Asset exceeds download bound')
    return b

def acquire(cache):
    cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
    data=cache/f'repoqa-{DATA_VERSION}.json'
    url=f'https://github.com/evalplus/repoqa_release/releases/download/{DATA_VERSION}/repoqa-{DATA_VERSION}.json.gz'
    if not data.exists():
        compressed=fetch(url);raw=gzip.decompress(compressed)
        if sha(raw)!=DATA_SHA256:raise ValueError('Dataset SHA256 mismatch')
        data.write_bytes(raw)
    if sha(data.read_bytes())!=DATA_SHA256:raise ValueError('Cached dataset has changed')
    for name,(path,expected) in SOURCES.items():
        p=cache/name
        if not p.exists():p.write_bytes(fetch(f'https://raw.githubusercontent.com/evalplus/repoqa/{SOURCE_COMMIT}/{path}'))
        if sha(p.read_bytes())!=expected:raise ValueError('Upstream evaluator integrity failure')
    lic=cache/'dataset_LICENSE'
    if not lic.exists():lic.write_bytes(fetch(f'https://raw.githubusercontent.com/evalplus/repoqa_release/{LICENSE_COMMIT}/LICENSE'))
    if sha(lic.read_bytes())!=LICENSE_SHA256:raise ValueError('Dataset license integrity failure')
    return json.loads(data.read_text()),{'dataset_version':DATA_VERSION,'dataset_url':url,'dataset_sha256':DATA_SHA256,'dataset_bytes':data.stat().st_size,'scorer_commit':SOURCE_COMMIT,'scorer_files':{k:v[1] for k,v in SOURCES.items()},'release_license':'Apache-2.0','license_commit':LICENSE_COMMIT,'license_sha256':LICENSE_SHA256,'corpus_redistributed':False}

class UpstreamScorer:
    """Load only fixed-hash scoring definitions; do not run repository/module code."""
    def __init__(self,cache):
        ns={'re':re,'get_parser':get_parser,'get_language':get_language,'Enum':Enum,'Tuple':tuple,'Dict':dict,'SmoothingFunction':SmoothingFunction,'sentence_bleu':sentence_bleu}
        for file in ['repoqa_utility.py','repoqa_metric.py','repoqa_compute_score.py']:
            path=Path(cache)/file
            if sha(path.read_bytes())!=SOURCES[file][1]:raise ValueError('Scorer source hash mismatch')
            tree=ast.parse(path.read_text());nodes=[]
            for node in tree.body:
                if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'FUNCTION_QUERY','COMMENT_QUERY'} for t in node.targets):nodes.append(node)
                elif isinstance(node,ast.FunctionDef) and node.name in {'compute_function_similarity','remove_comments','sanitize_output','needle_evaluator'}:nodes.append(node)
                elif isinstance(node,ast.ClassDef) and node.name=='Result':nodes.append(node)
            exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
        self.ns=ns
    def score(self,answer,needle,repo,lang):
        verdict,target,similarity=self.ns['needle_evaluator'](answer,needle['name'],repo,lang,False)
        return {'upstream_success_08':verdict==self.ns['Result'].BEST_MATCH and similarity>=.8,'best_similarity':float(similarity),'best_name':target}
    def canonical(self,code,lang):
        s=self.ns['sanitize_output']('```'+lang+'\n'+code+'\n```',lang)
        return re.sub(r'\s+','',s)

def qualify(cache,output):
    d,register=acquire(cache);scorer=UpstreamScorer(cache);checks=[]
    for lang,repos in d.items():
        repo=repos[0];n=repo['needles'][0];gold='\n'.join(repo['content'][n['path']].split('\n')[n['start_line']:n['end_line']])
        good=scorer.score(gold,n,repo,lang);bad=scorer.score('',n,repo,lang)
        if not good['upstream_success_08'] or bad['upstream_success_08']:raise ValueError('Upstream scorer sanity test failed')
        checks.append({'language':lang,'gold_passes':True,'empty_fails':True,'gold_similarity':good['best_similarity']})
    register.update(language_counts={l:sum(len(r['needles']) for r in rs) for l,rs in d.items()},repositories=sum(len(rs) for rs in d.values()),scorer_sanity_checks=checks,agent_index_fields=['content only'],label_fields_not_passed_to_engine=['needles','functions','dependency','topic'])
    Path(output).write_text(json.dumps(register,indent=2)+'\n');return register
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--cache',required=True);p.add_argument('--output',required=True);a=p.parse_args();print(json.dumps(qualify(a.cache,a.output),indent=2))

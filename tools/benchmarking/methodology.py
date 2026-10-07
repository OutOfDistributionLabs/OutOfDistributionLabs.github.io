#!/usr/bin/env python3
"""Planning/gates only. No model calls, MCP implementation or experimental results."""
import argparse
import hashlib
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

def read(path):
    return json.loads(Path(path).read_text())

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def canonical_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def validate(c, freeze=False):
    if c.get('schema_version') != 1: raise ValueError('Unsupported protocol schema')
    stages=c['stages']
    if not stages or [s['id'] for s in stages]!=list(range(1,len(stages)+1)):
        raise ValueError('Stages must be sequential')
    for s in stages:
        if not 1<=s['depth']<=5 or not s['criteria'] or len(set(s['criteria']))!=len(s['criteria']):
            raise ValueError('Invalid stage depth or criteria')
    if set(c['arms'])!={'A','B','C'}: raise ValueError('Primary plan requires native, flat and full arms')
    if c['primary']['contrast']!=['C','A']:raise ValueError('Specify full/native primary contrast')
    if not 0<c['primary']['target_absolute_effect']<1:raise ValueError('Invalid effect target')
    if not c['seeds'] or len(set(c['seeds']))!=len(c['seeds']):raise ValueError('Nonempty unique seeds required')
    if freeze or c.get('frozen'):
        if not c.get('frozen'):raise ValueError('Protocol is not frozen')
        if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or v<=0 for v in c['budgets'].values()):
            raise ValueError('All resource ceilings must be positive finite numbers')
        if any(not v for v in c['locks'].values()):raise ValueError('All version and manifest locks required')
    return c

def power(effect=.05, discordance=.25, n=500):
    if not 0<effect<1 or not effect<=discordance<=1 or n<1:
        raise ValueError('Need 0 < effect <= discordance <= 1 and n >= 1')
    z=1.959964+.841621
    return {'planning_approximation_only':True,'assumed_discordance':discordance,
            'target_effect':effect,'approx_required_instances':math.ceil(z*z*discordance/effect**2),
            'available_instances':n,'approx_detectable_effect':z*math.sqrt(discordance/n),
            'caveat':'Normal approximation; ignores repository correlation, finite population and exact test power.'}

def schedule(c,manifest):
    if not isinstance(manifest,list) or not manifest:raise ValueError('Nonempty manifest list required')
    ids=[x['instance_id'] for x in manifest]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate instance IDs')
    if any(not x.get('repo') or not x.get('instance_id') for x in manifest):raise ValueError('Each task needs repo and instance_id')
    rng=random.Random(c['seeds'][0]);rows=[]
    groups={repo:[] for repo in sorted({x['repo'] for x in manifest})}
    for x in manifest:groups[x['repo']].append(x)
    for repo,items in groups.items():
        items=sorted(items,key=lambda x:x['instance_id']);rng.shuffle(items)
        for x in items:
            for seed in c['seeds']:
                arms=sorted(c['arms']);rng.shuffle(arms)
                for arm in arms:
                    rows.append({'instance_id':x['instance_id'],'repo':repo,'seed':seed,'arm':arm,
                                 'run_id':f"{canonical_hash(c)[:12]}-{canonical_hash([x['instance_id'],seed,arm])[:16]}",
                                 'fresh_session_required':True})
    return {'draft':not c['frozen'],'protocol_sha256':canonical_hash(c),'manifest_sha256':canonical_hash(manifest),'runs':rows}

def evidence_path(base,path):
    p=(base/path).resolve()
    # Project-local records: copy supporting artifacts into project before attesting.
    if not p.is_relative_to(base.resolve()) or not p.is_file():raise ValueError('Evidence must be an existing project-local file')
    return p

def check_ledger(c,base,records):
    expected=1;parent=None
    for r in records:
        if r['protocol_sha256']!=canonical_hash(c):raise ValueError('Protocol changed: renew reviews in a new versioned ledger')
        if r['parent_record_sha256']!=parent or r['stage']!=expected:raise ValueError('Broken review sequence')
        for path,h in r['artifact_sha256'].items():
            if digest(evidence_path(base,path))!=h:raise ValueError('Reviewed artifact changed: renew affected reviews')
        parent=canonical_hash(r)
        if r['disposition']=='advance':expected+=1
        elif r['disposition']=='stop':raise ValueError('Programme is stopped; create an explicit revised protocol')
    return expected,parent

def record_gate(protocol_path,ledger_path,review):
    base=Path(protocol_path).resolve().parent;c=validate(read(protocol_path))
    ledger=Path(ledger_path);records=read(ledger) if ledger.exists() else []
    expected,parent=check_ledger(c,base,records)
    if expected>len(c['stages']) or review.get('stage')!=expected:raise ValueError('Review must address next unpassed stage')
    stage=c['stages'][expected-1]
    if review.get('disposition') not in ('advance','redo','stop'):raise ValueError('Invalid disposition')
    if not review.get('reviewer') or not review.get('review_role') or not isinstance(review.get('independent'),bool):
        raise ValueError('Identify reviewer, role and independence honestly')
    checks=review.get('checks',{})
    if set(checks)!=set(stage['criteria']):raise ValueError('Every stage criterion must be reviewed')
    paths=review.get('artifacts',[])
    if not paths or len(set(paths))!=len(paths):raise ValueError('Unique supporting artifacts required')
    hashes={p:digest(evidence_path(base,p)) for p in paths}
    for item in checks.values():
        if not isinstance(item.get('pass'),bool) or not item.get('reason') or not item.get('evidence'):
            raise ValueError('Each check requires boolean, reason and evidence')
        if any(p not in hashes for p in item['evidence']):raise ValueError('Check evidence must reference attached artifacts')
    if review['disposition']=='advance':
        if not all(item['pass'] for item in checks.values()):raise ValueError('Failed criteria block advancement')
        if expected>=8:validate(c,freeze=True)
    elif not review.get('remediation'):raise ValueError('Redo/stop requires an explicit remediation or stopping rationale')
    r={**review,'recorded_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),
       'protocol_sha256':canonical_hash(c),'artifact_sha256':hashes,'parent_record_sha256':parent,
       'machine_check_scope':'Sequence, attestations and artifact integrity only; scientific judgments are reviewer attestations.'}
    ledger.parent.mkdir(parents=True,exist_ok=True)
    temporary=ledger.with_suffix(ledger.suffix+'.tmp');temporary.write_text(json.dumps(records+[r],indent=2)+'\n');temporary.replace(ledger)
    return r

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--protocol',type=Path,required=True)
    sub=p.add_subparsers(dest='command',required=True)
    v=sub.add_parser('validate');v.add_argument('--confirmatory',action='store_true')
    sub.add_parser('plan')
    z=sub.add_parser('power');z.add_argument('--effect',type=float,default=.05);z.add_argument('--discordance',type=float,default=.25);z.add_argument('--n',type=int,default=500)
    s=sub.add_parser('schedule');s.add_argument('--manifest',type=Path,required=True);s.add_argument('--output',type=Path,required=True)
    g=sub.add_parser('gate');g.add_argument('--review',type=Path,required=True);g.add_argument('--ledger',type=Path,required=True)
    a=p.parse_args()
    try:
        c=validate(read(a.protocol))
        if a.command=='validate':validate(c,a.confirmatory);result={'valid':True,'frozen':c['frozen'],'scope':'methodology only'}
        elif a.command=='plan':result={'status':c['status'],'stages':c['stages']}
        elif a.command=='power':result=power(a.effect,a.discordance,a.n)
        elif a.command=='schedule':
            result=schedule(c,read(a.manifest));a.output.write_text(json.dumps(result,indent=2)+'\n');result={'runs_planned':len(result['runs']),'output':str(a.output),'draft':result['draft']}
        else:result=record_gate(a.protocol,a.ledger,read(a.review))
        print(json.dumps(result,indent=2))
    except (ValueError,KeyError,TypeError,OSError) as e:p.exit(2,f'Protocol error: {e}\n')
if __name__=='__main__':main()

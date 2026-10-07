#!/usr/bin/env python3
"""Publish research checkpoints and two-minute progress/ntfy heartbeats."""
import argparse, datetime as dt, fcntl, html, json, os, subprocess, sys, time, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2]
PROJECT=Path(__file__).resolve().parent
STATE=PROJECT/'status.json'
URL='https://outofdistributionlabs.github.io/research/hierarchical-abstractions/progress.html'
STEPS=['Scope and research protocol','Primary-source literature review','Formal model and architecture','Reproducible synthetic evaluation','LaTeX manuscript and review','Publication and verification']
def now(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
def read(): return json.loads(STATE.read_text())
def notify(title,message):
    request=urllib.request.Request('https://ntfy.sh/oodlabs',data=message.encode(),headers={'Title':title,'Click':URL,'Tags':'microscope'},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=20) as response:
            if response.status!=200: raise RuntimeError(f'ntfy HTTP {response.status}')
        return True
    except Exception as exc:
        print(f'Notification failed: {exc}',file=sys.stderr);return False

def render(s):
    stamp=dt.datetime.fromisoformat(s['updated_at']).astimezone(ZoneInfo('America/Los_Angeles')).strftime('%b %d, %Y · %H:%M %Z')
    items=[]
    for i,label in enumerate(STEPS):
        state='Complete' if i<s['step'] else ('In progress' if i==s['step'] else 'Planned')
        items.append(f'<li><span class="number">{i+1:02}</span><span>{html.escape(label)}</span><small>{state}</small></li>')
    events=''.join(f'<li><time>{html.escape(e["at"])}</time><p>{html.escape(e["summary"])}</p></li>' for e in reversed(s['events']))
    completed=s['step']==len(STEPS)
    links='<a href="research-plan.md">Research protocol</a> <a href="sources.md">Literature map</a> <a href="design.md">Architecture notes</a> <a href="evaluation/report.md">Evaluation</a>'
    links=' '.join(link for link in links.split(' </a>') if False) if False else links
    # Expose only files that exist at this checkpoint.
    resources=[('research-plan.md','Research protocol'),('sources.md','Literature map'),('design.md','Architecture notes'),('evaluation/report.md','Evaluation'),('white-paper.pdf','Read the white paper'),('white-paper.tex','LaTeX source'),('references.bib','Bibliography')]
    links=''.join(f'<a href="{path}">{label}</a>' for path,label in resources if (PROJECT/path).exists())
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#080b0d"><title>Research progress · Out of Distribution Labs</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#080b0d;color:#b4c0cc;font:15px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,Helvetica,sans-serif}main{max-width:1050px;padding:48px 32px 80px;margin:auto}a{color:inherit;text-decoration:none}a:hover{color:#e4bd83}a:focus-visible{outline:2px solid #e4bd83;outline-offset:4px}.brand{font-size:22px;line-height:1.3;letter-spacing:.04em;opacity:.7}.amber{color:#e4bd83}.labs{display:block}nav{display:flex;justify-content:space-between;gap:24px;align-items:start}.back{font-size:12px;min-height:44px;padding:8px 0}h1{font-size:clamp(28px,5vw,48px);line-height:1.2;font-weight:400;max-width:800px;margin:64px 0 24px}h2{font-size:18px;font-weight:400;margin:40px 0 16px}.meta{color:#8d9eaa;font-size:12px}.lead{max-width:720px}.progress{height:2px;background:#23303a;margin:32px 0}.progress span{display:block;height:100%;background:#e4bd83}ol{list-style:none;padding:0;margin:0}.steps li{display:grid;grid-template-columns:32px 1fr auto;gap:16px;padding:18px 0;border-top:1px solid #b1c6d51c}.number,small{font-size:12px;color:#8d9eaa}.resources{display:flex;flex-wrap:wrap;gap:16px 28px}.resources a{min-height:44px;padding:8px 0;color:#e4bd83}.events li{border-top:1px solid #b1c6d51c;padding:16px 0}.events time{font-size:11px;color:#8d9eaa}.events p{margin:6px 0}.note{font-size:12px;color:#8d9eaa;max-width:760px}@media(max-width:600px){main{padding:24px 24px 56px}h1{margin-top:48px}.steps li{grid-template-columns:24px 1fr}.steps small{grid-column:2}.brand{font-size:18px}}
</style></head><body><main><nav><a class="brand" href="../../">Out <span class="amber">of</span> Distribution<span class="labs">Labs</span></a><a class="back" href="../../">Home ↗</a></nav><h1>Hierarchical abstractions as a basis for ontology graphs</h1>'''
    page+=f'<p class="lead">A research white paper on shared, typed knowledge for hundreds of micro-agents.</p><p class="meta">{("Published · research complete" if completed else "Research in progress")} · {s["step"]}/6 steps complete · Updated {stamp}</p><div class="progress"><span style="width:{s["step"]/6*100:.1f}%"></span></div><p>{html.escape(s["summary"])}</p><h2>Research process</h2><ol class="steps">'+''.join(items)+'</ol><h2>Research materials</h2><div class="resources">'+links+'</div><h2>Checkpoint log</h2><ol class="events">'+events+'</ol><p class="note">Primary-source review, a proposed architecture, and explicitly synthetic evaluation. This project does not claim a deployment with hundreds of language-model agents. Checkpoints are published after each step; two-minute heartbeats refresh this page and notify the oodlabs ntfy topic while the process is running.</p></main></body></html>'
    (PROJECT/'progress.html').write_text(page)
def save(s):
    STATE.write_text(json.dumps(s,indent=2)+'\n');render(s)
def publish(message,checkpoint=False):
    files=['research/hierarchical-abstractions/status.json','research/hierarchical-abstractions/progress.html']
    if checkpoint: files=['index.html','research/hierarchical-abstractions']
    subprocess.run(['git','add','--',*files],cwd=ROOT,check=True)
    if subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode==0:return
    subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
    subprocess.run(['git','commit','-m',message],cwd=ROOT,check=True)
    subprocess.run(['git','-c','credential.helper=!gh auth git-credential','push','origin','main'],cwd=ROOT,check=True)
def update(kind,summary=None,step=None):
    with open('/tmp/oodlabs-research-publish.lock','w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        s=read()
        if kind=='heartbeat' and s['step']>=len(STEPS):return False
        if step is not None:
            if step!=s['step']+1:raise ValueError('Complete steps in sequence')
            s['step']=step
        s['updated_at']=now()
        if summary:s['summary']=summary;s['events'].append({'at':s['updated_at'],'summary':summary})
        save(s)
        publish('Research heartbeat: hierarchical abstractions' if kind=='heartbeat' else f'Research step {s["step"]}: {s["summary"][:90]}',checkpoint=kind!='heartbeat')
        label='Research complete' if s['step']==6 else f'Research {s["step"]}/6'
        if not notify('OOD Labs · '+label,('Heartbeat: ' if kind=='heartbeat' else 'Checkpoint: ')+s['summary']+'\n'+URL):
            raise RuntimeError('Published, but ntfy delivery failed; see stderr')
        return True

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['begin','heartbeat','step','notify']);parser.add_argument('--summary');parser.add_argument('--step',type=int);parser.add_argument('--interval',type=int,default=120);args=parser.parse_args()
    if args.command=='begin':
        s={'title':'Hierarchical abstractions as a basis for ontology graphs','step':0,'updated_at':now(),'summary':'Research protocol defined. Starting the primary-source literature review.','events':[]};s['events'].append({'at':s['updated_at'],'summary':s['summary']});save(s);update('checkpoint')
        log=open('/tmp/oodlabs-research-heartbeat.log','a')
        process=subprocess.Popen([sys.executable,__file__,'heartbeat','--interval',str(args.interval)],stdout=log,stderr=log,start_new_session=True)
        Path('/tmp/oodlabs-research-heartbeat.pid').write_text(str(process.pid));print(f'Heartbeat PID {process.pid}',flush=True)
    elif args.command=='heartbeat':
        while True:
            time.sleep(args.interval)
            try:
                if not update('heartbeat'):break
            except Exception as exc:
                print(f'{now()} Heartbeat error: {exc}',file=sys.stderr,flush=True)
                notify('OOD Labs · publishing error',str(exc)+'\n'+URL)
    elif args.command=='step':update('checkpoint',args.summary,args.step)
    else:
        if not notify('OOD Labs · research',args.summary or read()['summary']):raise RuntimeError('ntfy delivery failed')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Config-driven OOD Labs research publishing. Python standard library only."""
import argparse, datetime as dt, fcntl, html, json, os, signal, subprocess, sys, time, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2]
DEFAULT_STEPS=['Scope and research protocol','Primary-source literature review','Formal model and architecture','Reproducible evaluation','Manuscript and review','Publication and verification']
def now():return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
def project_path(name):
    path=(ROOT/'research'/name).resolve()
    if not path.is_relative_to(ROOT/'research') or path==ROOT/'research':raise ValueError('Project must be inside research/')
    return path

def load(project):return json.loads((project/'research.json').read_text()),json.loads((project/'status.json').read_text())
def notify(config,title,message):
    topic=config.get('ntfy_topic')
    if not topic:return True
    request=urllib.request.Request('https://ntfy.sh/'+topic,data=message.encode(),headers={'Title':title,'Click':config['progress_url'],'Tags':'microscope'},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=20) as response:
            if response.status!=200:raise RuntimeError(f'ntfy HTTP {response.status}')
        return True
    except Exception as exc:print(f'Notification failed: {exc}',file=sys.stderr,flush=True);return False

def render(project,c,s):
    e=html.escape;steps=c['steps'];done=s['step']==len(steps)
    stamp=dt.datetime.fromisoformat(s['updated_at']).astimezone(ZoneInfo(c.get('timezone','America/Los_Angeles'))).strftime('%b %d, %Y · %H:%M %Z')
    items=[]
    for i,label in enumerate(steps):
        state='Complete' if i<s['step'] else ('In progress' if i==s['step'] and s['running'] else 'Planned')
        items.append(f'<li><span class="number">{i+1:02}</span><span>{e(label)}</span><small>{state}</small></li>')
    events=''.join(f'<li><time>{e(event["at"])}</time><p>{e(event["summary"])}</p></li>' for event in reversed(s['events']))
    resources=''.join(f'<a href="{e(item["path"],quote=True)}">{e(item["label"])}</a>' for item in c['resources'] if (project/item['path']).is_file())
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#080b0d"><title>Research progress · Out of Distribution Labs</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#080b0d;color:#b4c0cc;font:15px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,Helvetica,sans-serif}main{max-width:1050px;padding:48px 32px 80px;margin:auto}a{color:inherit;text-decoration:none}a:hover{color:#e4bd83}a:focus-visible{outline:2px solid #e4bd83;outline-offset:4px}.brand{font-size:22px;line-height:1.3;letter-spacing:.04em;opacity:.7}.amber{color:#e4bd83}.labs{display:block}nav{display:flex;justify-content:space-between;gap:24px;align-items:start}.back{font-size:12px;min-height:44px;padding:8px 0}h1{font-size:clamp(28px,5vw,48px);line-height:1.2;font-weight:400;max-width:800px;margin:64px 0 24px}h2{font-size:18px;font-weight:400;margin:40px 0 16px}.meta{color:#8d9eaa;font-size:12px}.lead{max-width:720px}.progress{height:2px;background:#23303a;margin:32px 0}.progress span{display:block;height:100%;background:#e4bd83}ol{list-style:none;padding:0;margin:0}.steps li{display:grid;grid-template-columns:32px 1fr auto;gap:16px;padding:18px 0;border-top:1px solid #b1c6d51c}.number,small{font-size:12px;color:#8d9eaa}.resources{display:flex;flex-wrap:wrap;gap:16px 28px}.resources a{min-height:44px;padding:8px 0;color:#e4bd83}.events li{border-top:1px solid #b1c6d51c;padding:16px 0}.events time{font-size:11px;color:#8d9eaa}.events p{margin:6px 0}.note{font-size:12px;color:#8d9eaa;max-width:760px}@media(max-width:600px){main{padding:24px 24px 56px}h1{margin-top:48px}.steps li{grid-template-columns:24px 1fr}.steps small{grid-column:2}.brand{font-size:18px}}
</style></head><body><main><nav><a class="brand" href="../../">Out <span class="amber">of</span> Distribution<span class="labs">Labs</span></a><a class="back" href="../../">Home ↗</a></nav>'''
    phase='Published · research complete' if done else ('Research in progress' if s['running'] else 'Paused')
    page+=f'<h1>{e(c["title"])}</h1><p class="lead">{e(c["subtitle"])}</p><p class="meta">{phase} · {s["step"]}/{len(steps)} steps complete · Updated {stamp}</p><div class="progress"><span style="width:{s["step"]/len(steps)*100:.1f}%"></span></div><p>{e(s["summary"])}</p><h2>Research process</h2><ol class="steps">'+''.join(items)+'</ol><h2>Research materials</h2><div class="resources">'+resources+'</div><h2>Checkpoint log</h2><ol class="events">'+events+f'</ol><p class="note">{e(c["evidence_note"])}</p><p class="note"><a href="../PROCESS.md">Reusable research process</a></p></main></body></html>'
    (project/'progress.html').write_text(page)
def save(project,c,s):
    target=project/'status.json';temporary=project/'status.json.tmp';temporary.write_text(json.dumps(s,indent=2)+'\n');temporary.replace(target);render(project,c,s)
def git(*args,check=True):return subprocess.run(['git',*args],cwd=ROOT,check=check)
def publish(c,paths,message):
    git('add','--',*paths)
    if git('diff','--cached','--quiet','--',*paths,check=False).returncode==0:return
    git('diff','--cached','--check','--',*paths)
    # --only prevents unrelated staged files entering a research commit.
    git('commit','--only','-m',message,'--',*paths)
    git('-c','credential.helper=!gh auth git-credential','push',c.get('remote','origin'),c.get('branch','main'))
def lock():
    handle=open('/tmp/oodlabs-research-publish.lock','w');fcntl.flock(handle,fcntl.LOCK_EX);return handle

def update(project,kind,summary=None,step=None,extra=()):
    with lock():
        c,s=load(project)
        if kind=='heartbeat' and (not s['running'] or s['step']>=len(c['steps'])):return False
        if step is not None:
            if step!=s['step']+1 or step>len(c['steps']):raise ValueError('Complete steps in sequence')
            s['step']=step
        if kind=='pause':s['running']=False
        if kind=='resume':s['running']=True
        if s['step']==len(c['steps']):s['running']=False
        s['updated_at']=now()
        if summary:s['summary']=summary;s['events'].append({'at':s['updated_at'],'summary':summary})
        save(project,c,s)
        relative=str(project.relative_to(ROOT))
        paths=[relative+'/status.json',relative+'/progress.html'] if kind=='heartbeat' else [relative]
        for value in extra:
            resolved=(ROOT/value).resolve()
            if not resolved.is_relative_to(ROOT):raise ValueError('Extra files must be in repository')
            paths.append(str(resolved.relative_to(ROOT)))
        message=f'Research heartbeat: {c["id"]}' if kind=='heartbeat' else f'Research {c["id"]} step {s["step"]}: {s["summary"][:72]}'
        publish(c,paths,message)
        label='Research complete' if s['step']==len(c['steps']) else f'Research {s["step"]}/{len(c["steps"])}'
        if not notify(c,'OOD Labs · '+label,('Heartbeat: ' if kind=='heartbeat' else 'Checkpoint: ')+s['summary']+'\n'+c['progress_url']):raise RuntimeError('Published, but ntfy delivery failed')
        return True

def heartbeat(project,interval):
    while True:
        time.sleep(interval)
        try:
            if not update(project,'heartbeat'):break
        except Exception as exc:
            print(f'{now()} Heartbeat error: {exc}',file=sys.stderr,flush=True)
            c,_=load(project);notify(c,'OOD Labs · publishing error',str(exc)+'\n'+c['progress_url'])
def spawn(project):
    pidpath=Path('/tmp')/('oodlabs-research-'+project.name+'.pid')
    if pidpath.exists():
        try:os.kill(int(pidpath.read_text()),0);print('Heartbeat already running');return
        except (ProcessLookupError,ValueError):pass
    c,_=load(project);log=open('/tmp/oodlabs-research-'+project.name+'.log','a')
    process=subprocess.Popen([sys.executable,__file__,'--project',project.name,'heartbeat','--interval',str(c.get('heartbeat_seconds',120))],stdout=log,stderr=log,start_new_session=True)
    pidpath.write_text(str(process.pid));print(f'Heartbeat PID {process.pid}',flush=True)
def initialize(project,title,topic):
    if (project/'research.json').exists():raise ValueError('Project already configured')
    project.mkdir(parents=True,exist_ok=True)
    c={'id':project.name,'title':title,'subtitle':'A research white paper by Out of Distribution Labs.','steps':DEFAULT_STEPS,'timezone':'America/Los_Angeles','ntfy_topic':topic,'heartbeat_seconds':120,'remote':'origin','branch':'main','progress_url':f'https://outofdistributionlabs.github.io/research/{project.name}/progress.html','evidence_note':'A structured primary-source review. Proposals and evaluation results are explicitly distinguished from prior work.','resources':[{'path':p,'label':label} for p,label in [('research-plan.md','Research protocol'),('sources.md','Literature map'),('design.md','Theory and architecture'),('evaluation/report.md','Evaluation'),('white-paper.pdf','Read the white paper'),('white-paper.tex','LaTeX source'),('references.bib','Bibliography')]]}
    (project/'research.json').write_text(json.dumps(c,indent=2)+'\n')
    (project/'research-plan.md').write_text((ROOT/'tools/research/protocol-template.md').read_text().replace('{{TITLE}}',title))
    (project/'.gitignore').write_text('*.aux\n*.bbl\n*.blg\n*.fdb_latexmk\n*.fls\n*.log\n*.out\n*.toc\n__pycache__/\n')
    s={'step':0,'running':False,'updated_at':now(),'summary':'Protocol draft created; scope confirmation and research have not started.','events':[]};save(project,c,s)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--project',required=True);parser.add_argument('command',choices=['init','start','heartbeat','step','pause','render','notify']);parser.add_argument('--title');parser.add_argument('--topic',default='oodlabs');parser.add_argument('--summary');parser.add_argument('--step',type=int);parser.add_argument('--interval',type=int,default=120);parser.add_argument('--extra',action='append',default=[]);args=parser.parse_args();project=project_path(args.project)
    if args.command=='init':
        if not args.title:parser.error('init requires --title')
        initialize(project,args.title,args.topic)
    elif args.command=='start':update(project,'resume',args.summary,extra=args.extra);spawn(project)
    elif args.command=='heartbeat':heartbeat(project,args.interval)
    elif args.command=='step':
        if args.step is None or not args.summary:parser.error('step requires --step and --summary')
        update(project,'checkpoint',args.summary,args.step,args.extra)
    elif args.command=='pause':update(project,'pause',args.summary or 'Research paused.',extra=args.extra)
    elif args.command=='render':
        c,s=load(project);render(project,c,s)
    else:
        c,s=load(project)
        if not notify(c,'OOD Labs · research',args.summary or s['summary']):raise RuntimeError('ntfy delivery failed')
if __name__=='__main__':main()

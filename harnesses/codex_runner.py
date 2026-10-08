"""Fresh-session Codex adapter and honest readiness check; no fabricated trial scores."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

def collect_events(text):
    events=[]
    for line in text.splitlines():
        try:events.append(json.loads(line))
        except ValueError:pass
    return events

def readiness(output):
    with tempfile.TemporaryDirectory(prefix='ood-codex-readiness-') as work:
        command=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','-C',work,'--json','Reply READY only. Do not use tools.']
        begin=time.perf_counter()
        try:r=subprocess.run(command,capture_output=True,text=True,timeout=60);events=collect_events(r.stdout);exit_code=r.returncode
        except subprocess.TimeoutExpired:events=[];exit_code=124
    completed=any(e.get('type')=='turn.completed' for e in events)
    errors=[e.get('message') or e.get('error',{}).get('message') for e in events if e.get('type') in {'error','turn.failed'}]
    result={'kind':'fresh_codex_readiness_not_benchmark','cli_version':subprocess.check_output(['codex','--version'],text=True).strip(),'ready':exit_code==0 and completed,'exit_code':exit_code,'elapsed_seconds':time.perf_counter()-begin,'errors':errors,'provider_cost_usd':None,'mcp_agent_calls':0,'benchmark_attempts':0,'credential_values_recorded':False}
    Path(output).write_text(json.dumps(result,indent=2)+'\n');return result

def command(workspace,model,arm,python=sys.executable):
    if arm not in {'A','B','C'}:raise ValueError('Unknown arm')
    result=['codex','exec','--ignore-user-config','--ephemeral','--json','--sandbox','workspace-write','-C',str(workspace),'--model',model]
    if arm!='A':
        result += ['-c','mcp_servers.intuition.command='+json.dumps(python),'-c','mcp_servers.intuition.args='+json.dumps(['-m','intuition_engine.server','--root',str(workspace),'--mode','flat' if arm=='B' else 'graph'])]
    return result

def run(task,workspace,model,arm,output,wall_seconds,isolation_receipt):
    allowed={'instance_id','problem_statement','repo','base_commit'}
    if set(task)!=allowed:raise ValueError('Only permitted task fields may reach the agent')
    receipt=json.loads(Path(isolation_receipt).read_text())
    checks=['fresh_workspace','hidden_assets_not_visible','network_scoped','no_prior_arm_memory']
    if any(receipt.get(k) is not True for k in checks):raise ValueError('External sandbox qualification receipt required')
    out=Path(output)
    if out.exists():raise ValueError('Use a fresh output directory for every run')
    out.mkdir(parents=True)
    prompt='Solve this repository issue. Use available repository tools and the intuition tools if useful. Do not seek benchmark reference solutions.\n\n'+task['problem_statement']
    begin=time.perf_counter()
    try:
        result=subprocess.run(command(workspace,model,arm)+[prompt],capture_output=True,text=True,timeout=wall_seconds)
        stdout=result.stdout;returncode=result.returncode;stopped='completed' if returncode==0 else 'error'
    except subprocess.TimeoutExpired as e:
        stdout=e.stdout.decode() if isinstance(e.stdout,bytes) else e.stdout or '';returncode=124;stopped='wall_timeout'
    events=collect_events(stdout)
    tokens=[e.get('usage',{}) for e in events if e.get('type')=='turn.completed']
    tools=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='mcp_tool_call']
    # Costs remain null without a qualified billing meter; this cannot satisfy confirmatory cost gates.
    record={'instance_id':task['instance_id'],'arm':arm,'model_id':model,'exit_code':returncode,'stopping_reason':stopped,'wall_seconds':time.perf_counter()-begin,'token_usage_events':tokens,'mcp_tool_calls':len(tools),'provider_cost_usd':None,'confirmatory_accounting_qualified':False,'independent_grading_pending':True}
    (out/'events.jsonl').write_text(stdout);(out/'run.json').write_text(json.dumps(record,indent=2)+'\n')
    patch=subprocess.run(['git','diff','--no-ext-diff'],cwd=workspace,capture_output=True,text=True,check=True).stdout;(out/'model.patch').write_text(patch)
    return record

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('readiness');q.add_argument('--output',required=True)
    q=sub.add_parser('run');q.add_argument('--task',required=True);q.add_argument('--workspace',required=True);q.add_argument('--model',required=True);q.add_argument('--arm',choices=['A','B','C'],required=True);q.add_argument('--output',required=True);q.add_argument('--wall-seconds',type=int,default=300);q.add_argument('--isolation-receipt',required=True)
    a=p.parse_args()
    if a.action=='readiness':r=readiness(a.output)
    else:r=run(json.loads(Path(a.task).read_text()),a.workspace,a.model,a.arm,a.output,a.wall_seconds,a.isolation_receipt)
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()

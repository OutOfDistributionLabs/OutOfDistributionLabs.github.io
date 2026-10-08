"""Fresh, isolated Codex/MCP feasibility adapter for FeatureBench lv1.

Never run this in an evaluator container. Gold and task metadata remain host-only;
only the masked repository and public problem statement reach inference.
"""
import argparse,hashlib,json,logging,os,shlex,socket,subprocess,time
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
MODEL='gpt-6.1-sol'

def prepare_network():
    from featurebench.infer.network import AgentNetworkIsolation,ApiEndpoint
    net=AgentNetworkIsolation('codex',MODEL,{'OPENAI_BASE_URL':'https://chatgpt.com'})
    net.endpoints=(ApiEndpoint('chatgpt.com',443),ApiEndpoint('auth.openai.com',443))
    net.start();up=urlsplit(os.environ.get('HTTPS_PROXY') or os.environ['HTTP_PROXY'])
    net.proxy.upstream_proxy=(up.hostname,up.port or 8080)
    return net

def run(row,image,arm,output,wall_seconds=300):
    import docker
    from featurebench.infer.container import ContainerManager
    from featurebench.infer.runtime import RuntimeHandler
    from featurebench.infer.models import TaskInstance
    if arm not in {'A','B','C'}:raise ValueError('Invalid arm')
    out=Path(output);out.mkdir(parents=True,exist_ok=False);log=out/'trusted-setup.log'
    cm=ContainerManager();net=prepare_network();container=None
    credential_home=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
    ca=Path('/etc/ssl/certs/ca-certificates.crt')
    volumes=net.docker_volume()|{str(ca):{'bind':'/run/ood-ca.pem','mode':'ro'},'/opt/codex/bin/codex':{'bind':'/usr/local/bin/codex','mode':'ro'},str(credential_home/'auth.json'):{'bind':'/tmp/ood-codex-home/auth.json','mode':'rw'}}
    env={k:os.environ[k] for k in ['HTTP_PROXY','HTTPS_PROXY','NO_PROXY'] if k in os.environ}
    env.update({'SSL_CERT_FILE':'/run/ood-ca.pem','REQUESTS_CA_BUNDLE':'/run/ood-ca.pem','PIP_CERT':'/run/ood-ca.pem','CODEX_HOME':'/tmp/ood-codex-home','PYTHONPATH':'/installed-agent/engine'})
    begin=time.perf_counter()
    try:
        host=urlsplit(env.get('HTTPS_PROXY') or env['HTTP_PROXY']).hostname
        container=cm.client.containers.run(image,['tail','-f','/dev/null'],detach=True,working_dir='/testbed',volumes=volumes,environment=env,extra_hosts={host:socket.gethostbyname(host)},cap_drop=['ALL'],security_opt=['no-new-privileges:true'],labels={'oodlabs.study':'featurebench-contract-pilot','oodlabs.arm':arm})
        cm.exec_command(container,'mkdir -p /installed-agent/engine /agent-logs; touch /installed-agent/setup-env.sh',log_file=log)
        task=TaskInstance.from_dict(row)
        if not RuntimeHandler(cm)._initialize_level1(container,task,log,white_box=False):raise RuntimeError('Official source masking failed')
        cm.copy_to_container(container,ROOT/'intuition_engine','/installed-agent/engine/intuition_engine')
        install='timeout -k 10 180s /opt/miniconda3/envs/testbed/bin/python -m venv /installed-agent/venv && timeout -k 10 180s /installed-agent/venv/bin/pip install mcp==1.29.0 tree-sitter==0.21.3 tree-sitter-languages==1.10.2 nltk==3.9.1'
        rc,_=cm.exec_command(container,install,log_file=log,timeout=180)
        if rc:raise RuntimeError('Isolated engine dependencies failed')
        # Docker owns the network boundary; Codex's internal sandbox is not relied upon.
        if not net.isolate(container,cm,log):raise RuntimeError('API-only isolation failed')
        check="test ! -e /root/my_repo && test ! -e /var/run/docker.sock && test ! -e /tmp/mask.patch && test ! -e /tmp/test_patch.diff"
        rc,_=cm.exec_command(container,check,log_file=log)
        if rc:raise RuntimeError('Hidden asset boundary failed')
        hidden=list(row.get('FAIL_TO_PASS') or [])
        for path in hidden:
            rc,_=cm.exec_command(container,'test ! -e '+shlex.quote('/testbed/'+path.removeprefix('/testbed/')),log_file=log)
            if rc:raise RuntimeError('F2P file visible')
        probe="source /installed-agent/setup-env.sh; /opt/miniconda3/envs/testbed/bin/python -c "+shlex.quote("import urllib.request,urllib.error\ntry: urllib.request.urlopen('https://huggingface.co',timeout=5);raise SystemExit(2)\nexcept urllib.error.URLError as e: raise SystemExit(0 if '403' in str(e) else 3)")
        rc,_=cm.exec_command(container,probe,log_file=log,timeout=15)
        if rc:raise RuntimeError('Non-model network denial probe failed')
        container.reload();receipt={'fresh_container':True,'hidden_assets_not_visible':True,'no_docker_socket':True,'non_model_download_denied':True,'attached_networks':list(container.attrs['NetworkSettings']['Networks']),'auth_file_content_recorded':False}
        (out/'isolation.json').write_text(json.dumps(receipt,indent=2)+'\n')
        # Verify actual pinned CLI/model availability within isolated environment, before task.
        setup='source /installed-agent/setup-env.sh; source /opt/miniconda3/etc/profile.d/conda.sh; conda activate testbed; export PYTHONPATH=/installed-agent/engine; '
        args=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--json','--sandbox','danger-full-access','--model',MODEL,'-c','model_reasoning_effort="medium"','-C','/testbed']
        if arm!='A':
            args+=['-c','mcp_servers.intuition.command="/installed-agent/venv/bin/python"','-c','mcp_servers.intuition.args='+json.dumps(['-m','intuition_engine.server','--root','/testbed','--mode','flat' if arm=='B' else 'graph'])]
        prompt='Implement the feature described below in this repository. Preserve existing behavior. Use available repository tools and, if exposed, the intuition tools to inform decisions. Do not seek external reference solutions.\n\n'+row['problem_statement']
        cmd=setup+'timeout -k 10 '+str(wall_seconds)+'s '+shlex.join(args+[prompt])+' > /agent-logs/events.jsonl 2>/agent-logs/codex-stderr.log'
        agent_begin=time.perf_counter();rc,_=cm.exec_command(container,cmd,log_file=log,timeout=wall_seconds+30);agent_wall=time.perf_counter()-agent_begin
        for name in ['events.jsonl','codex-stderr.log']:cm.copy_from_container(container,'/agent-logs/'+name,out/name)
        events=[]
        for line in (out/'events.jsonl').read_text().splitlines():
            try:events.append(json.loads(line))
            except ValueError:pass
        rc_patch,patch=cm.exec_command(container,'cd /testbed && git add -N . && git diff --no-ext-diff --binary',timeout=60)
        if rc_patch:raise RuntimeError('Patch capture failed')
        (out/'model.patch').write_text(patch)
        calls=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='mcp_tool_call']
        record={'instance_id':row['instance_id'],'arm':arm,'model':MODEL,'reasoning_effort':'medium','cli_version':subprocess.check_output(['codex','--version'],text=True).strip(),'wall_ceiling_seconds':wall_seconds,'agent_wall_seconds':agent_wall,'setup_and_agent_wall_seconds':time.perf_counter()-begin,'exit_code':rc,'turn_completed':any(e.get('type')=='turn.completed' for e in events),'usage':[e.get('usage') for e in events if e.get('type')=='turn.completed'],'mcp_calls':len(calls),'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'provider_cost_usd':None,'confirmatory_qualified':False}
        (out/'run.json').write_text(json.dumps(record,indent=2)+'\n');return record
    finally:
        if container is not None:container.remove(force=True)
        net.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('--task',required=True);p.add_argument('--image',required=True);p.add_argument('--arm',required=True,choices=['A','B','C']);p.add_argument('--output',required=True);a=p.parse_args();logging.basicConfig(level=logging.INFO);r=run(json.loads(Path(a.task).read_text()),a.image,a.arm,a.output);print(json.dumps(r,indent=2))
if __name__=='__main__':main()

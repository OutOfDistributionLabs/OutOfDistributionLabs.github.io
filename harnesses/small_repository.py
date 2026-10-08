"""Bounded Docker sessions for source-only class generation and hidden grading.

No evaluator/host socket is mounted into inference. This adapter is a feasibility
adaptation; it does not claim official RepoClassBench environment/leaderboard parity.
"""
import hashlib,io,json,logging,os,shlex,shutil,socket,subprocess,tarfile,threading,time
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
MODEL='gpt-6.1-sol'
REQUIREMENTS=['mcp==1.29.0','tree-sitter==0.21.3','tree-sitter-languages==1.10.2','nltk==3.9.1','pytest==7.4.4','pytest-json-report==1.5.0','numpy==1.26.4','urllib3==1.26.20','chardet==5.2.0','charset-normalizer==3.4.2','idna==3.10','certifi==2025.1.31','pytest-httpbin==2.1.0','httpbin==0.10.2','Flask==2.2.5','Werkzeug==2.2.3','pytest-mock==3.14.0','six==1.17.0']

def docker_client():
 import docker
 return docker.DockerClient(base_url='unix:///var/run/docker.sock',timeout=120)
def put(container,name,data):
 b=io.BytesIO()
 with tarfile.open(fileobj=b,mode='w') as t:
  e=tarfile.TarInfo(Path(name).name);e.size=len(data);t.addfile(e,io.BytesIO(data))
 container.exec_run(['mkdir','-p',str(Path(name).parent)]);container.put_archive(str(Path(name).parent),b.getvalue())
def get(container,name):
 stream,_=container.get_archive(name);b=io.BytesIO(b''.join(stream))
 with tarfile.open(fileobj=b) as t:return t.extractfile(t.getmembers()[0]).read()
def execute(container,args,seconds=120,workdir='/work',environment=None):
 result=[];error=[]
 def job():
  try:result.append(container.exec_run(args,workdir=workdir,environment=environment or {},demux=False))
  except Exception as e:error.append(e)
 th=threading.Thread(target=job,daemon=True);th.start();th.join(seconds)
 if th.is_alive():container.kill();return 124,b'Host watchdog timed out; container killed.'
 if error:raise error[0]
 return result[0].exit_code,result[0].output

def setup_environment():
 env={k:os.environ[k] for k in ['HTTP_PROXY','HTTPS_PROXY','NO_PROXY'] if k in os.environ}
 env.update({k.lower():v for k,v in list(env.items())})
 env.update({'SSL_CERT_FILE':'/etc/ssl/certs/ca-certificates.crt','REQUESTS_CA_BUNDLE':'/etc/ssl/certs/ca-certificates.crt','PIP_CERT':'/etc/ssl/certs/ca-certificates.crt'})
 host=urlsplit(env.get('HTTPS_PROXY') or env['HTTP_PROXY']).hostname
 return env,{host:socket.gethostbyname(host)}

def prepare_runtime(base,output):
 client=docker_client();env,hosts=setup_environment();c=None
 try:
  c=client.containers.run(base,['tail','-f','/dev/null'],detach=True,working_dir='/work',environment=env,extra_hosts=hosts,volumes={'/etc/ssl/certs/ca-certificates.crt':{'bind':'/etc/ssl/certs/ca-certificates.crt','mode':'ro'}},labels={'oodlabs.study':'repoclassbench-small-pilot','oodlabs.kind':'setup'})
  rc,out=execute(c,['bash','-lc','apt-get update && apt-get install -y --no-install-recommends git ripgrep'],seconds=180)
  if rc:raise RuntimeError('Search tooling installation failed: '+out.decode(errors='replace')[-1000:])
  put(c,'/tmp/requirements.txt',('\n'.join(REQUIREMENTS)+'\n').encode())
  rc,out=execute(c,['python','-m','pip','install','--no-cache-dir','-r','/tmp/requirements.txt'],seconds=180)
  if rc:raise RuntimeError('Runtime dependency installation failed: '+out.decode(errors='replace')[-1000:])
  for p in (ROOT/'intuition_engine').glob('*.py'):put(c,'/engine/intuition_engine/'+p.name,p.read_bytes())
  rc,freeze=execute(c,['python','-m','pip','freeze'])
  if rc:raise RuntimeError('Runtime inventory failed')
  image=c.commit(repository='ood-small-repository-runtime',tag='v1',conf={'Env':['PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin','PYTHONPATH=/engine'],'Cmd':['tail','-f','/dev/null'],'WorkingDir':'/work'})
  # Docker commit inherits bind-mount volume declarations and proxy variables.
  # Sanitize the saved image config before reloading; no credentials are present.
  saved=io.BytesIO(b''.join(client.api.get_image(image.id)));clean=io.BytesIO()
  with tarfile.open(fileobj=saved) as archive:
   manifest=json.load(archive.extractfile('manifest.json'));name=manifest[0]['Config'];config=json.load(archive.extractfile(name));config['config']['Volumes']=None;config['config']['Env']=['PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin','PYTHONPATH=/engine'];manifest[0]['RepoTags']=['ood-small-repository-runtime:v2']
   with tarfile.open(fileobj=clean,mode='w') as target:
    for member in archive:
     data=json.dumps(config).encode() if member.name==name else json.dumps(manifest).encode() if member.name=='manifest.json' else None
     if data is not None:member.size=len(data);target.addfile(member,io.BytesIO(data))
     else:target.addfile(member,archive.extractfile(member) if member.isfile() else None)
  client.images.load(clean.getvalue());image=client.images.get('ood-small-repository-runtime:v2')
  record={'base':base,'image_id':image.id,'image_bytes':image.attrs['Size'],'requirements':REQUIREMENTS,'installed_inventory':freeze.decode(),'auth_or_evaluator_files_in_image':False}
  Path(output).write_text(json.dumps(record,indent=2)+'\n');return record
 finally:
  if c:c.remove(force=True)

def tree_hash(folder):
 h=hashlib.sha256()
 for p in sorted(Path(folder).rglob('*')):
  if p.is_file():
   if p.is_symlink():raise ValueError('Symlinks not permitted in benchmark view')
   h.update(p.relative_to(folder).as_posix().encode()+b'\0'+p.read_bytes()+b'\0')
 return h.hexdigest()
def masked_view(row,originals,output):
 original=Path(originals)/row['repo_metadata']['issue_id'];out=Path(output);out.mkdir(parents=True,exist_ok=False)
 relative=Path(row['file']).relative_to(row['repo_metadata']['issue_id']);target=original/relative;body=row['ground_truth_class_body'];text=target.read_text()
 if text.count(body)!=1:raise ValueError('Reference class not uniquely present in pinned source')
 for p in original.rglob('*'):
  if not p.is_file():continue
  parts=p.relative_to(original).parts
  if any(x=='.git' or x=='__pycache__' or x.lower().startswith('test') for x in parts) or p.suffix in {'.pyc','.pyo'}:continue
  if p.is_symlink():raise ValueError('Source symlink rejected')
  dest=out/p.relative_to(original);dest.parent.mkdir(parents=True,exist_ok=True)
  content=(text.replace(body,'# <MSR CLASS PLACEHOLDER>') if p==target else p.read_text(errors='replace')) if p.suffix=='.py' else None
  if content is not None:
   if body in content:raise ValueError('Reference implementation still visible')
   dest.write_text(content)
  else:dest.write_bytes(p.read_bytes())
 return {'view':str(out),'source_sha256':tree_hash(out),'target':relative.as_posix(),'tests_hidden':True,'reference_body_removed':True,'retained_imports_deviation':True}

def grade(row,originals,answer,image,output):
 out=Path(output);out.mkdir(parents=True,exist_ok=False);work=out/'workspace';original=Path(originals)/row['repo_metadata']['issue_id'];shutil.copytree(original,work)
 for p in list(work.rglob('__pycache__')):
  if p.is_dir():shutil.rmtree(p)
 for p in list(work.rglob('*.pyc')):p.unlink()
 for item in [work,*work.rglob('*')]:item.chmod(0o755 if item.is_dir() else 0o644)
 relative=Path(row['file']).relative_to(row['repo_metadata']['issue_id']);target=work/relative;text=target.read_text();body=row['ground_truth_class_body']
 if text.count(body)!=1:raise ValueError('Reference class mismatch in evaluator')
 target.write_text(text.replace(body,answer));client=docker_client();c=None;begin=time.perf_counter()
 try:
  c=client.containers.run(image,detach=True,network_mode='none',working_dir='/work',cap_drop=['ALL'],security_opt=['no-new-privileges:true'],volumes={str(work.resolve()):{'bind':'/work','mode':'rw'}},environment={'PYTHONPATH':'/work'},labels={'oodlabs.study':'repoclassbench-small-pilot','oodlabs.kind':'grading'})
  expected=row['evaluation_metadata']['test_directives']
  if not expected:raise ValueError('Cannot grade an empty expected-test set')
  rc,log=execute(c,['python','-m','pytest',*expected,'--json-report','--json-report-file=/tmp/report.json','--tb=short','--continue-on-collection-errors'],seconds=120)
  (out/'pytest.log').write_bytes(log)
  try:report=json.loads(get(c,'/tmp/report.json'))
  except Exception as e:raise RuntimeError('Missing pytest report: '+log.decode(errors='replace')[-600:]) from e
  outcomes={x['nodeid']:x['outcome'] for x in report.get('tests',[])}
  passed=[x for x in expected if outcomes.get(x)=='passed'];failed=[x for x in expected if outcomes.get(x)!='passed']
  result={'task_id':row['task_id'],'resolved':len(passed)==len(expected),'passed':len(passed),'required':len(expected),'missing_or_failed':len(failed),'pytest_exit_code':rc,'wall_seconds':time.perf_counter()-begin,'grading_rule':'All official expected test IDs must appear as passed; missing/skipped/error count as failure. Adapted runtime, no linter feedback.'}
  (out/'grade.json').write_text(json.dumps(result,indent=2)+'\n');return result
 finally:
  if c:c.remove(force=True)

def infer(row,view,image,arm,output,wall_seconds=300,probe_only=False):
 from featurebench.infer.network import AgentNetworkIsolation,ApiEndpoint
 from featurebench.infer.container import ContainerManager
 out=Path(output);out.mkdir(parents=True,exist_ok=False);client=docker_client();net=AgentNetworkIsolation('codex',MODEL,{'OPENAI_BASE_URL':'https://chatgpt.com'});net.endpoints=(ApiEndpoint('chatgpt.com',443),ApiEndpoint('auth.openai.com',443));net.start();up=urlsplit(os.environ.get('HTTPS_PROXY') or os.environ['HTTP_PROXY']);net.proxy.upstream_proxy=(up.hostname,up.port or 8080);c=None
 home=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')));volumes=net.docker_volume()|{str(Path(view).resolve()):{'bind':'/work','mode':'ro'},'/opt/codex/bin/codex':{'bind':'/usr/local/bin/codex','mode':'ro'},str(home/'auth.json'):{'bind':'/tmp/codex-home/auth.json','mode':'rw'},'/etc/ssl/certs/ca-certificates.crt':{'bind':'/etc/ssl/certs/ca-certificates.crt','mode':'ro'}}
 begin=time.perf_counter()
 try:
  c=client.containers.run(image,detach=True,working_dir='/work',volumes=volumes,cap_add=['DAC_OVERRIDE'],environment={'CODEX_HOME':'/tmp/codex-home','SSL_CERT_FILE':'/etc/ssl/certs/ca-certificates.crt','PYTHONPATH':'/engine'},cap_drop=['ALL'],security_opt=['no-new-privileges:true'],labels={'oodlabs.study':'repoclassbench-small-pilot','oodlabs.arm':arm})
  put(c,'/installed-agent/setup-env.sh',b'');c.exec_run(['mkdir','-p','/agent-logs','/answer'])
  if not net.isolate(c,ContainerManager(),out/'isolation-setup.log'):raise RuntimeError('API-only network setup failed')
  rc,probe=execute(c,['bash','-lc',"source /installed-agent/setup-env.sh; python -c \"import urllib.request,urllib.error; urllib.request.urlopen('https://huggingface.co',timeout=5)\""],seconds=10)
  if b'403' not in probe:raise RuntimeError('Benchmark download denial not demonstrated')
  c.reload();receipt={'source_sha256':tree_hash(view),'networks':list(c.attrs['NetworkSettings']['Networks']),'benchmark_download_denied':True,'hidden_tests_and_answer_not_mounted':True,'docker_socket_not_mounted':True,'workspace_readonly':True}
  if receipt['networks']:raise RuntimeError('Unrestricted network still attached')
  (out/'isolation.json').write_text(json.dumps(receipt,indent=2)+'\n')
  relative=Path(row['file']).relative_to(row['repo_metadata']['issue_id']).as_posix()
  prompt=f"Implement the class {row['class_name']} for {relative}. The repository under /work is read-only and the target class is missing. Inspect dependencies with repository tools and, if available, intuition tools. Write only the Python class definition (and imports it needs) to /answer/class.py; this file replaces the class placeholder. Do not edit repository files. Do not seek external reference solutions.\n\n"+row['detailed_description']
  if probe_only:prompt='This is a readiness check, not a benchmark attempt. Do not implement the missing class. If intuition MCP tools are available, call intuition_status once. Write READY to /answer/class.py and reply READY.'
  args=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--json','--sandbox','danger-full-access','--model',MODEL,'-c','model_reasoning_effort="medium"','-C','/work']
  if arm!='A':args+=['-c','mcp_servers.intuition.command="/usr/local/bin/python"','-c','mcp_servers.intuition.args='+json.dumps(['-m','intuition_engine.server','--root','/work','--mode','flat' if arm=='B' else 'graph'])]
  cmd='source /installed-agent/setup-env.sh; timeout -k 10 '+str(wall_seconds)+'s '+shlex.join(args+[prompt])+' > /agent-logs/events.jsonl 2>/agent-logs/stderr.log'
  start=time.perf_counter();rc,raw=execute(c,['bash','-lc',cmd],seconds=wall_seconds+30);elapsed=time.perf_counter()-start
  events_raw=get(c,'/agent-logs/events.jsonl');(out/'events.jsonl').write_bytes(events_raw);(out/'stderr.log').write_bytes(get(c,'/agent-logs/stderr.log'));events=[]
  for line in events_raw.decode(errors='replace').splitlines():
   try:events.append(json.loads(line))
   except ValueError:pass
  try:answer=get(c,'/answer/class.py').decode()
  except Exception:answer=''
  (out/'answer.py').write_text(answer)
  errors=[e.get('message') or e.get('error') for e in events if e.get('type') in {'error','turn.failed'}]
  result={'task_id':row['task_id'],'arm':arm,'model':MODEL,'reasoning_effort':'medium','exit_code':rc,'turn_completed':any(e.get('type')=='turn.completed' for e in events),'usage':[e.get('usage') for e in events if e.get('type')=='turn.completed'],'mcp_calls':sum(e.get('type')=='item.completed' and e.get('item',{}).get('type')=='mcp_tool_call' for e in events),'wall_seconds':elapsed,'wall_ceiling_seconds':wall_seconds,'errors':errors,'source_sha256':receipt['source_sha256'],'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),'provider_cost_usd':None}
  (out/'run.json').write_text(json.dumps(result,indent=2)+'\n');return result,answer
 finally:
  if c:c.remove(force=True)
  net.close()

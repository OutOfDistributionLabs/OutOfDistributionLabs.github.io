"""Pinned FeatureBench asset selection and filesystem-preserving VFS image import.

Gold/task data stays evaluator-only. Flattening changes image identity, not source
filesystem contents; disclose derived-image qualification rather than leaderboard parity.
Requires crane (go-containerregistry) and a running Docker daemon.
"""
import argparse,json,subprocess,sys
from pathlib import Path

def flatten(source,tag,crane,output,drop_caches=False):
    digest=subprocess.check_output([crane,'digest',source],text=True).strip()
    pinned=source.split('@')[0]+'@'+digest
    config=json.loads(subprocess.check_output([crane,'config',pinned],text=True))
    changes=[];c=config.get('config',{})
    for entry in c.get('Env') or []:changes+=['--change','ENV '+entry]
    for key,directive in [('WorkingDir','WORKDIR'),('User','USER')]:
        if c.get(key):changes+=['--change',directive+' '+c[key]]
    for key in ['Entrypoint','Cmd']:
        if c.get(key):changes+=['--change',key.upper()+' '+json.dumps(c[key])]
    export=subprocess.Popen([crane,'export',pinned,'-'],stdout=subprocess.PIPE)
    filtered=None
    stream=export.stdout
    if drop_caches:
        filtered=subprocess.Popen([sys.executable,'-m','benchmarks.featurebench_filter','--stats',str(output)+'.filter.json'],stdin=export.stdout,stdout=subprocess.PIPE)
        export.stdout.close();stream=filtered.stdout
    try:
        imported=subprocess.run(['docker','--host=unix:///var/run/docker.sock','import',*changes,'-',tag],stdin=stream,capture_output=True,text=True)
        stream.close();filter_code=filtered.wait() if filtered else 0;export_code=export.wait()
        if export_code or filter_code or imported.returncode:raise RuntimeError('Image export/import failed: '+imported.stderr[-1000:])
    finally:
        if export.poll() is None:export.terminate();export.wait()
    record={'source':source,'source_digest':digest,'derived_tag':tag,'derived_image_id':imported.stdout.strip(),'source_image_config':config,'derivation':'crane export merged filesystem streamed to single-layer docker import; Env/User/WorkingDir/Entrypoint/Cmd retained','cache_filter':drop_caches,'qualification':'Source image layers were flattened to fit VFS storage. Official gold/empty scoring still required; not identity-equivalent leaderboard infrastructure.'}
    Path(output).write_text(json.dumps(record,indent=2)+'\n');return record

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--tag',required=True);p.add_argument('--crane',default='crane');p.add_argument('--output',required=True);p.add_argument('--drop-caches',action='store_true');a=p.parse_args();r=flatten(a.source,a.tag,a.crane,a.output,a.drop_caches);print(json.dumps({k:r[k] for k in ['source_digest','derived_tag','derived_image_id']},indent=2))
if __name__=='__main__':main()

"""Run unchanged official FeatureBench grading on pinned evaluator-only instances.

This entry point never supplies reference data to an agent. Image names may be
replaced by a provenance-recorded flattened image; report that deviation.
"""
import argparse,json,hashlib,shutil
from pathlib import Path

def evaluate(row,patch,output,image,timeout=600):
    import pandas as pd
    import docker
    client=docker.from_env();image_bytes=client.images.get(image).attrs['Size']
    needed=(2*image_bytes if client.info()['Driver']=='vfs' else 0)+2_000_000_000
    if shutil.disk_usage('/workspace').free<needed:raise RuntimeError('Insufficient storage for evaluator VFS copies; scoring not attempted')
    from featurebench.harness.run_evaluation import run_instance
    instance=dict(row);instance['level']=int(row['instance_id'].rsplit('lv',1)[-1]);instance['image_name']=image
    return run_instance(pd.Series(instance),{'instance_id':row['instance_id'],'model_patch':patch,'n_attempt':1},Path(output),timeout=timeout)

def qualify(rows,output,images):
    from featurebench.harness.utils import preprocess_hf_patch
    out=Path(output);out.mkdir(parents=True,exist_ok=True);records=[]
    for row in rows:
        for control in ['gold','empty']:
            patch=preprocess_hf_patch(row['patch'],row['FAIL_TO_PASS']) if control=='gold' else ''
            try:result=evaluate(row,patch,out/control,images[row['repo']])
            except Exception as e:result={'completed':False,'resolved':None,'error':str(e)}
            valid=not result.get('error') or (control=='empty' and 'Empty patch' in str(result.get('error')))
            records.append({'instance_id':row['instance_id'],'control':control,'completed':result.get('completed',False),'resolved':result.get('resolved',False) if valid else None,'classification':'qualified_control' if valid else 'infrastructure_invalid','error':result.get('error'),'report':result.get('report'),'patch_sha256':hashlib.sha256(patch.encode()).hexdigest()})
            (out/'qualification-results.json').write_text(json.dumps(records,indent=2)+'\n')
    return records

def main():
    p=argparse.ArgumentParser();p.add_argument('--tasks',required=True);p.add_argument('--images',required=True);p.add_argument('--output',required=True);a=p.parse_args();r=qualify(json.loads(Path(a.tasks).read_text()),a.output,json.loads(Path(a.images).read_text()));print(json.dumps([{k:x[k] for k in ['instance_id','control','completed','resolved','error']} for x in r],indent=2))
if __name__=='__main__':main()

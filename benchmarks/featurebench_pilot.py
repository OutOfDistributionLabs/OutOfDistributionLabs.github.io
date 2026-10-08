"""Frozen feasibility schedule; failed qualification never becomes an agent score.

Run per repository serially to fit VFS storage. Results are not SOTA claims and
small development task counts cannot establish effectiveness.
"""
import argparse,hashlib,json,random,time
from pathlib import Path

def validate_controls(task,qualification):
    controls=[x for x in json.loads(Path(qualification).read_text()) if x['instance_id']==task['instance_id']]
    if not any(x['control']=='gold' and x.get('classification')=='qualified_control' and x.get('resolved') is True for x in controls):raise ValueError('Official gold qualification required before inference')
    if not any(x['control']=='empty' and x.get('classification')=='qualified_control' and x.get('resolved') is False for x in controls):raise ValueError('Official negative control qualification required before inference')

def run(task,image,output,qualification,seed=20261007):
    from harnesses.featurebench_container import run as infer
    from benchmarks.featurebench_qualify import evaluate
    validate_controls(task,qualification)
    out=Path(output);out.mkdir(parents=True,exist_ok=False);arms=['A','B','C'];random.Random(seed).shuffle(arms)
    records=[]
    for arm in arms:
        try:
            inference=infer(task,image,arm,out/arm)
            patch=(out/arm/'model.patch').read_text()
            grade=evaluate(task,patch,out/'grading'/arm,image)
            record={'arm':arm,'inference':inference,'grade':grade,'classification':'infrastructure_invalid' if grade.get('error') and 'Empty patch' not in str(grade['error']) else 'graded_development_attempt'}
        except Exception as e:
            record={'arm':arm,'classification':'infrastructure_invalid','error':str(e)}
        records.append(record);(out/'results.json').write_text(json.dumps(records,indent=2)+'\n')
        # Stop an infeasible model/runtime rather than spending remaining trials.
        if record['classification']=='infrastructure_invalid':break
    return records

def main():
    p=argparse.ArgumentParser();p.add_argument('--task',required=True);p.add_argument('--image',required=True);p.add_argument('--output',required=True);p.add_argument('--qualification',required=True);p.add_argument('--seed',type=int,default=20261007);a=p.parse_args();print(json.dumps(run(json.loads(Path(a.task).read_text()),a.image,a.output,a.qualification,a.seed),indent=2))
if __name__=='__main__':main()

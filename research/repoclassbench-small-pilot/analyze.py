"""Descriptive analysis of the six preselected cells; never fills missing outcomes."""
import json
from pathlib import Path

def analyze(records):
    if len(records)!=6:raise ValueError('All six scored cells required')
    seen=set(); summary={}
    for r in records:
        run,grade=r['run'],r['grade'];key=(run['task_id'],run['arm'])
        if key in seen or not run['turn_completed'] or grade['resolved'] is None:raise ValueError('Invalid or duplicate cell')
        seen.add(key)
    for arm in ['A','B','C']:
        rows=[r for r in records if r['run']['arm']==arm]
        if len(rows)!=2:raise ValueError('Incomplete arm')
        summary[arm]={'resolved':sum(r['grade']['resolved'] for r in rows),'tasks':2,'inference_seconds':sum(r['run']['wall_seconds'] for r in rows),'input_tokens':sum(u.get('input_tokens',0) for r in rows for u in r['run']['usage']),'cached_input_tokens':sum(u.get('cached_input_tokens',0) for r in rows for u in r['run']['usage']),'output_tokens':sum(u.get('output_tokens',0) for r in rows for u in r['run']['usage']),'logged_tool_operations':sum(r['run']['mcp_calls'] for r in rows),'provider_cost_usd':None}
    by_task={task:{r['run']['arm']:r for r in records if r['run']['task_id']==task} for task,_ in seen}
    for task,arms in by_task.items():
        if set(arms)!=set('ABC') or len({r['run']['source_sha256'] for r in arms.values()})!=1:raise ValueError('Task source parity violated')
    return {'arms':summary,'graph_minus_native_resolution':sum(a['C']['grade']['resolved']-a['A']['grade']['resolved'] for a in by_task.values())/2,'graph_minus_flat_resolution':sum(a['C']['grade']['resolved']-a['B']['grade']['resolved'] for a in by_task.values())/2,'inference_accounting_scope':'Valid scored cells only. Setup, readiness and interrupted attempt excluded; unknown interrupted token spend and provider price prevent total-cost claims.','powered_or_representative':False}

if __name__=='__main__':
    p=Path(__file__).parent
    print(json.dumps(analyze(json.loads((p/'evaluation/results.json').read_text())),indent=2))

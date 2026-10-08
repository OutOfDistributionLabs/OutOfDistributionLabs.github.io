"""Six real dataset stdio probes; no LLM and no effectiveness inference."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import tempfile
import time
from intuition_engine.core import safe_path,snapshot
from benchmarks.repoqa_assets import acquire
from .mcp_client import consult
async def run(cache,output):
    data,_=acquire(cache);rows=[]
    for lang,repos in sorted(data.items()):
        repo=sorted(repos,key=lambda r:r['repo'])[0];query=repo['needles'][0]['description']
        for mode in ['flat','graph']:
            with tempfile.TemporaryDirectory(prefix='ood-mcp-task-') as folder:
                root=Path(folder)
                for path,text in repo['content'].items():
                    p=root/safe_path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
                t=time.perf_counter();r=await consult(root,query,mode,10);elapsed=time.perf_counter()-t
                parity=r['status']['snapshot_id']==snapshot(repo['content'])
                if not parity:raise ValueError('MCP corpus parity failed for '+lang+' '+repo['repo'])
                rows.append({'language':lang,'repo':repo['repo'],'mode':mode,'kind':'real_mcp_client_probe_not_agent_trial','snapshot_parity':parity,'tool_count':len(r['tools']),'candidate_count':len(r['advice']['candidates']),'query_status':r['advice']['status'],'response_bytes':r['advice']['usage']['response_bytes'],'query_cpu_ms':r['advice']['usage']['query_cpu_ms'],'elapsed_including_server_start_seconds':elapsed,'engine_model_calls':0,'query_sha256':hashlib.sha256(query.encode()).hexdigest()})
            print(lang,mode,'MCP round trip passed',flush=True)
    result={'actual_mcp_query_calls':len(rows),'languages':6,'arms':2,'llm_calls':0,'agent_effectiveness_claim':False,'probes':rows};Path(output).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',required=True);p.add_argument('--output',required=True);a=p.parse_args();asyncio.run(run(a.cache,a.output))

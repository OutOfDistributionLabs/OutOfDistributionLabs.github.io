"""Real stdio MCP client, reusable by a harness; not an LLM effectiveness run."""
import argparse
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def unpack(r):
    if r.isError:raise RuntimeError(r.content[0].text)
    return r.structuredContent or json.loads(r.content[0].text)
async def consult(root,query,mode='graph',max_candidates=8):
    params=StdioServerParameters(command=sys.executable,args=['-m','intuition_engine.server','--root',str(root),'--mode',mode])
    async with stdio_client(params) as (reader,writer):
        async with ClientSession(reader,writer) as session:
            await session.initialize();tools=await session.list_tools()
            status=unpack(await session.call_tool('intuition_status',{}))
            advice=unpack(await session.call_tool('intuition_query',{'snapshot_id':status['snapshot_id'],'query':query,'max_candidates':max_candidates,'response_token_budget':16000}))
            return {'kind':'actual_mcp_client_call_not_llm_trial','tools':[t.name for t in tools.tools],'status':status,'advice':advice}
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--query',required=True);p.add_argument('--mode',default='graph',choices=['scan','flat','graph']);a=p.parse_args();print(json.dumps(asyncio.run(consult(a.root,a.query,a.mode)),indent=2))
if __name__=='__main__':main()

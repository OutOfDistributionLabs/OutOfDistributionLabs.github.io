"""Portable shell adapter to the real stdio MCP; no direct Engine calls."""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    p = argparse.ArgumentParser()
    p.add_argument('operation', choices=['status', 'query', 'evidence'])
    p.add_argument('value', nargs='?', default='')
    a = p.parse_args()
    mode = os.environ['INTUITION_MODE']
    params = StdioServerParameters(command=sys.executable, args=[
        '-m', 'intuition_engine.server', '--root', '/work', '--mode', mode], env={'PYTHONPATH': '/engine'})
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            status = await session.call_tool('intuition_status', {})
            decoded = status.structuredContent or json.loads(status.content[0].text)
            args = {} if a.operation == 'status' else {'snapshot_id': decoded['snapshot_id']}
            if a.operation == 'query': args['query'] = a.value
            if a.operation == 'evidence': args['evidence_ids'] = json.loads(a.value)
            result = status if a.operation == 'status' else await session.call_tool('intuition_' + a.operation, args)
            payload = result.structuredContent or json.loads(result.content[0].text)
            with Path('/agent-logs/mcp-calls.jsonl').open('a') as log:
                log.write(json.dumps({'tool': 'intuition_' + a.operation, 'mode': mode, 'is_error': result.isError, 'snapshot_id': decoded['snapshot_id']}) + '\n')
            print(json.dumps(payload))
            if result.isError: raise SystemExit(1)

if __name__ == '__main__': asyncio.run(run())

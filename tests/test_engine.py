import asyncio
import json
from pathlib import Path
import sys
import tempfile
import unittest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from intuition_engine.core import Engine, read_workspace

def decode(r):
    if r.structuredContent:return r.structuredContent
    return json.loads(r.content[0].text)
class EngineTests(unittest.TestCase):
    def test_language_adapters_and_no_oracle(self):
        cases={'x.py':'def work(x):\n return x\n','x.cpp':'int work(int x){return x;}','x.java':'class A { int work(int x){return x;} }','x.ts':'function work(x: number){return x;}','x.rs':'fn work(x:i32)->i32 {x}','x.go':'package a\nfunc work(x int) int {return x}'}
        for p,c in cases.items():
            e=Engine({p:c});self.assertTrue(e.entities,p);self.assertIsNone(e.query(e.snapshot_id,'work')['coverage']['calibrated_probability'])
    def test_flat_graph_same_corpus_and_evidence(self):
        content={'math.py':'def calculate_value(x):\n return x+1\n','other.py':'def unrelated(z):\n return z\n'}
        flat=Engine(content,'flat');graph=Engine(content,'graph')
        self.assertEqual(flat.snapshot_id,graph.snapshot_id);self.assertEqual(set(flat.by_id),set(graph.by_id))
        for e in [flat,graph]:
            r=e.query(e.snapshot_id,'calculate value');i=r['candidates'][0]['entity_id'];self.assertEqual(e.evidence(e.snapshot_id,[i])['evidence'][0]['path'],'math.py')
    def test_snapshot_change_and_forged_evidence(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'a.py';p.write_text('def x():\n return 1\n');e=Engine(read_workspace(t),root=t)
            with self.assertRaises(ValueError):e.evidence(e.snapshot_id,['forged'])
            p.write_text('def x():\n return 2\n');self.assertEqual(e.query(e.snapshot_id,'x')['status'],'stale_snapshot')
    def test_escape_and_budgets(self):
        with self.assertRaises(ValueError):Engine({'../answer.py':'pass'})
        with tempfile.TemporaryDirectory() as t,tempfile.TemporaryDirectory() as out:
            p=Path(out)/'secret.py';p.write_text('pass');(Path(t)/'escape.py').symlink_to(p)
            with self.assertRaises(ValueError):read_workspace(t)
        e=Engine({'a.py':'\n'.join(f'def value_{i}():\n return {i}' for i in range(100))})
        r=e.query(e.snapshot_id,'value',max_candidates=50,response_token_budget=1024)
        self.assertLessEqual(len(json.dumps(r,ensure_ascii=False).encode()),1024)
        self.assertEqual(r['usage']['response_bytes'],len(json.dumps(r,ensure_ascii=False).encode()))
        with self.assertRaises(ValueError):e.query(e.snapshot_id,'value',max_candidates=100)
        with self.assertRaises(ValueError):e.query(e.snapshot_id,'value',response_token_budget=0)
    def test_actual_stdio_mcp_round_trip(self):
        async def check(root):
            parameters=StdioServerParameters(command=sys.executable,args=['-m','intuition_engine.server','--root',root,'--mode','graph'])
            async with stdio_client(parameters) as (read,write):
                async with ClientSession(read,write) as session:
                    await session.initialize();tools=await session.list_tools()
                    self.assertEqual({t.name for t in tools.tools},{'intuition_status','intuition_query','intuition_evidence'})
                    s=decode(await session.call_tool('intuition_status',{}))
                    r=decode(await session.call_tool('intuition_query',{'snapshot_id':s['snapshot_id'],'query':'calculate value'}))
                    self.assertFalse(r.get('isError',False));self.assertTrue(r['candidates'])
                    q=decode(await session.call_tool('intuition_evidence',{'snapshot_id':s['snapshot_id'],'evidence_ids':[r['candidates'][0]['entity_id']]}));self.assertIn('calculate_value',q['evidence'][0]['source'])
                    invalid=await session.call_tool('intuition_query',{'snapshot_id':s['snapshot_id'],'query':'x','max_candidates':999});self.assertTrue(invalid.isError)
        with tempfile.TemporaryDirectory() as root:
            (Path(root)/'a.py').write_text('def calculate_value(x):\n return x+1\n');asyncio.run(check(root))
if __name__=='__main__':unittest.main()

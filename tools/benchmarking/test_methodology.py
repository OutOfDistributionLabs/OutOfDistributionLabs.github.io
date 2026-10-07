"""Meaningful gate/integrity/planning tests; no real benchmark outcomes."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('ood_methodology',Path(__file__).with_name('methodology.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=Path(__file__).resolve().parents[2]
class MethodologyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
        self.c=m.read(ROOT/'research/intuition-engine-benchmarking/protocol.json')
        self.path=self.base/'protocol.json';self.path.write_text(json.dumps(self.c));self.ledger=self.base/'gates.json'
        (self.base/'scope.md').write_text('Fixture evidence, not a scientific result.')
    def review(self,stage=1,disposition='advance'):
        return {'stage':stage,'disposition':disposition,'reviewer':'test fixture','review_role':'author self-review','independent':False,'artifacts':['scope.md'],'checks':{k:{'pass':True,'reason':'Fixture assertion','evidence':['scope.md']} for k in self.c['stages'][stage-1]['criteria']}}
    def test_unfrozen_or_incomplete_protocol_blocks_confirmation(self):
        with self.assertRaises(ValueError):m.validate(self.c,True)
        self.c['frozen']=True
        with self.assertRaises(ValueError):m.validate(self.c)
    def test_failed_check_cannot_advance_and_redo_can_be_retried(self):
        r=self.review();next(iter(r['checks'].values()))['pass']=False
        with self.assertRaises(ValueError):m.record_gate(self.path,self.ledger,r)
        self.assertFalse(self.ledger.exists())
        r['disposition']='redo';r['remediation']='Repair fixture'
        m.record_gate(self.path,self.ledger,r)
        m.record_gate(self.path,self.ledger,self.review())
        self.assertEqual(len(m.read(self.ledger)),2)
    def test_skipped_stage_and_evidence_mutation_block_advance(self):
        with self.assertRaises(ValueError):m.record_gate(self.path,self.ledger,self.review(2))
        m.record_gate(self.path,self.ledger,self.review())
        (self.base/'scope.md').write_text('Changed evidence')
        with self.assertRaises(ValueError):m.record_gate(self.path,self.ledger,self.review(2))
    def test_protocol_change_and_path_escape_block_gate(self):
        r=self.review();r['artifacts']=['../outside.txt']
        with self.assertRaises(ValueError):m.record_gate(self.path,self.ledger,r)
        m.record_gate(self.path,self.ledger,self.review())
        c=copy.deepcopy(self.c);c['primary']['target_absolute_effect']=.06;self.path.write_text(json.dumps(c))
        with self.assertRaises(ValueError):m.record_gate(self.path,self.ledger,self.review(2))
    def test_schedule_pairs_each_task_and_seed_without_claiming_run(self):
        tasks=[{'instance_id':'fixture-1','repo':'one'},{'instance_id':'fixture-2','repo':'two'}]
        a=m.schedule(self.c,tasks);self.assertEqual(a['runs'],m.schedule(self.c,list(reversed(tasks)))['runs'])
        self.assertTrue(a['draft']);self.assertEqual(len(a['runs']),6)
        self.assertEqual(len({r['run_id'] for r in a['runs']}),6)
        for t in tasks:self.assertEqual({r['arm'] for r in a['runs'] if r['instance_id']==t['instance_id']},{'A','B','C'})
        with self.assertRaises(ValueError):m.schedule(self.c,[tasks[0],tasks[0]])
    def test_power_is_labelled_approximation_and_validated(self):
        self.assertEqual(m.power()['approx_required_instances'],785)
        self.assertTrue(m.power()['planning_approximation_only'])
        with self.assertRaises(ValueError):m.power(effect=.3,discordance=.1)
if __name__=='__main__':unittest.main()

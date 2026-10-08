import json,tempfile,unittest
from pathlib import Path
from benchmarks.featurebench_pilot import validate_controls
class QualificationGateTests(unittest.TestCase):
 def check(self,rows):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'controls.json';p.write_text(json.dumps(rows));validate_controls({'instance_id':'task'},p)
 def test_upstream_completed_error_never_admits_agents(self):
  with self.assertRaises(ValueError):self.check([{'instance_id':'task','control':'gold','upstream_completed_flag':True,'classification':'infrastructure_invalid','resolved':False}])
 def test_gold_without_negative_control_never_admits_agents(self):
  with self.assertRaises(ValueError):self.check([{'instance_id':'task','control':'gold','classification':'qualified_control','resolved':True}])
 def test_both_valid_controls_admit_next_gate(self):
  self.check([{'instance_id':'task','control':c,'classification':'qualified_control','resolved':r} for c,r in [('gold',True),('empty',False)]])
if __name__=='__main__':unittest.main()

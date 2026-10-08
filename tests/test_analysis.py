import unittest
from benchmarks.analyse import exact_mcnemar,paired
class AnalysisTests(unittest.TestCase):
    def test_exact_pair_test(self):
        self.assertEqual(exact_mcnemar(0,0),1);self.assertEqual(exact_mcnemar(11,10),1)
        self.assertAlmostEqual(exact_mcnemar(5,0),.0625)
    def test_pair_accounting_and_missing_arm(self):
        # Synthetic unit-test fixtures, never used as research measurements.
        rows=[{'task_id':'fixture','repo':'fixture-repo','language':'fixture','split':'evaluation','arm':'flat','upstream_success_08':'0'},{'task_id':'fixture','repo':'fixture-repo','language':'fixture','split':'evaluation','arm':'graph','upstream_success_08':'1'}]
        r=paired(rows,'graph','flat',draws=20);self.assertEqual(r['wins'],1);self.assertEqual(r['difference'],1)
        with self.assertRaises(ValueError):paired(rows[:1],'graph','flat',draws=20)
if __name__=='__main__':unittest.main()

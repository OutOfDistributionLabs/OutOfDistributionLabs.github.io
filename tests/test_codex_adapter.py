import tempfile
import unittest
from harnesses.codex_runner import command,run
class CodexAdapterTests(unittest.TestCase):
    def test_fresh_session_and_treatment_config(self):
        a=command('/task','fixed-model','A');b=command('/task','fixed-model','B');c=command('/task','fixed-model','C')
        self.assertIn('--ephemeral',a);self.assertIn('--ignore-user-config',a)
        self.assertFalse(any('mcp_servers' in x for x in a));self.assertTrue(any('"flat"' in x for x in b));self.assertTrue(any('"graph"' in x for x in c))
    def test_hidden_fields_cannot_be_submitted(self):
        with self.assertRaises(ValueError):run({'instance_id':'fixture','problem_statement':'x','repo':'r','base_commit':'b','gold_patch':'secret'},'/task','fixed-model','A','/tmp/never-created',10,'missing-receipt')
if __name__=='__main__':unittest.main()

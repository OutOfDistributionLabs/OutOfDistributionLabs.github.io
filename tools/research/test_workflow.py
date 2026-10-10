"""Exercise publishing isolation and rollback against a temporary local git remote."""
import importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('run.py'));runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
class Workflow(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'repo';self.root.mkdir();self.oldroot=runner.ROOT;runner.ROOT=self.root
  def cmd(*args):return subprocess.run(args,cwd=self.root,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  self.cmd=cmd;cmd('git','init','-b','main');cmd('git','config','user.name','Test');cmd('git','config','user.email','test@example.invalid')
  (self.root/'base').write_text('base');cmd('git','add','base');cmd('git','commit','-m','base')
  remote=Path(self.tmp.name)/'remote.git';cmd('git','init','--bare',str(remote));cmd('git','remote','add','origin',str(remote));cmd('git','push','origin','main')
  (self.root/'tools/research').mkdir(parents=True);(self.root/'tools/research/protocol-template.md').write_text('# {{TITLE}}')
  self.project=runner.project_path('test-project');runner.initialize(self.project,'Test title','');self.notify=runner.notify;runner.notify=lambda *args:True
 def tearDown(self):runner.ROOT=self.oldroot;runner.notify=self.notify;self.tmp.cleanup()
 def test_checkpoint_isolation_heartbeat_and_completion(self):
  unrelated=self.root/'unrelated.txt';unrelated.write_text('private work');self.cmd('git','add','unrelated.txt')
  runner.update(self.project,'resume','Started');runner.update(self.project,'checkpoint','Protocol complete',1)
  tracked=subprocess.check_output(['git','ls-tree','--name-only','HEAD'],cwd=self.root,text=True);self.assertNotIn('unrelated.txt',tracked)
  staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=self.root,text=True);self.assertIn('unrelated.txt',staged)
  (self.project/'white-paper.pdf').write_text('unfinished');runner.update(self.project,'heartbeat');self.assertNotIn('Read the white paper',(self.project/'progress.html').read_text())
  for step in range(2,7):runner.update(self.project,'checkpoint',f'Step {step}',step)
  self.assertFalse(runner.update(self.project,'heartbeat'));self.assertFalse(runner.load(self.project)[1]['running'])
  with self.assertRaises(ValueError):runner.update(self.project,'resume')
 def test_parent_hub_updates_and_is_published_with_task(self):
  import shutil
  for name in ['build_hub.py','hub-template.html']:
   shutil.copy(Path(__file__).with_name(name),self.root/'tools/research'/name)
  parent=self.root/'research/programme';parent.mkdir()
  (parent/'project.json').write_text(json.dumps({'title':'Programme','description':'Description','papers':[],'tasks':[{'id':'test-project','title':'Task','description':'Protocol','complete_label':'Complete'}]}))
  c,s=runner.load(self.project);c['parent_project']='programme';runner.save(self.project,c,s)
  (self.project/'research.json').write_text(json.dumps(c))
  runner.update(self.project,'checkpoint','Protocol complete',1)
  page=(parent/'index.html').read_text();self.assertIn('1/6 steps',page)
  self.assertIn('../programme/',(self.project/'progress.html').read_text())
  tracked=subprocess.check_output(['git','show','HEAD:research/programme/index.html'],cwd=self.root,text=True)
  self.assertIn('1/6 steps',tracked)
 def test_failed_publish_rolls_back_step(self):
  runner.update(self.project,'resume');original=runner.publish
  try:
   runner.publish=lambda *args:(_ for _ in ()).throw(RuntimeError('validation failed'))
   with self.assertRaises(RuntimeError):runner.update(self.project,'checkpoint','Not published',1)
   self.assertEqual(runner.load(self.project)[1]['step'],0)
  finally:runner.publish=original
 def test_independent_notification_cadence(self):
  c,_=runner.load(self.project);c.update(notification_seconds=300,notify_on_checkpoint=False,notify_on_complete=True)
  calls=[];runner.notify=lambda *args:calls.append(args) or True
  clock=runner.Path('/tmp')/('oodlabs-research-'+self.project.name+'-notification.json');clock.unlink(missing_ok=True)
  try:
   with patch.object(runner.time,'time',return_value=1000):runner.notify_scheduled(self.project,c,'t','m','resume')
   with patch.object(runner.time,'time',return_value=1060):runner.notify_scheduled(self.project,c,'t','m','heartbeat')
   self.assertEqual(len(calls),0)
   with patch.object(runner.time,'time',return_value=1300):runner.notify_scheduled(self.project,c,'t','m','heartbeat')
   self.assertEqual(len(calls),1)
   with patch.object(runner.time,'time',return_value=1301):runner.notify_scheduled(self.project,c,'t','m','checkpoint')
   self.assertEqual(len(calls),1)
   with patch.object(runner.time,'time',return_value=1302):runner.notify_scheduled(self.project,c,'t','m','checkpoint',complete=True)
   self.assertEqual(len(calls),2)
  finally:clock.unlink(missing_ok=True)
 def test_invalid_slug_and_sequence(self):
  with self.assertRaises(ValueError):runner.project_path('../escape')
  with self.assertRaises(ValueError):runner.update(self.project,'checkpoint','Skipped step',2)
 def test_error_notifications_use_configured_interval(self):
  c,_=runner.load(self.project);c.update(notification_seconds=300,notify_on_checkpoint=False,notify_on_error=False)
  calls=[];runner.notify=lambda *args:calls.append(args) or True
  clock=runner.Path('/tmp')/('oodlabs-research-'+self.project.name+'-notification.json');clock.unlink(missing_ok=True)
  try:
   for stamp in [1000,1060,1300]:
    with patch.object(runner.time,'time',return_value=stamp):runner.notify_scheduled(self.project,c,'error','failed','error')
   self.assertEqual(len(calls),1)
   c['notify_on_error']=True
   with patch.object(runner.time,'time',return_value=1301):runner.notify_scheduled(self.project,c,'error','failed','error')
   self.assertEqual(len(calls),2)
  finally:clock.unlink(missing_ok=True)
 def test_disk_full_does_not_leave_partial_status(self):
  c,s=runner.load(self.project);original=(self.project/'status.json').read_text();write=runner.Path.write_text
  def fail(path,*args,**kwargs):
   if path.name=='status.json.tmp':
    write(path,'partial');raise OSError('no space left on device')
   return write(path,*args,**kwargs)
  with patch.object(runner.Path,'write_text',fail),self.assertRaises(OSError):runner.save(self.project,c,s)
  self.assertFalse((self.project/'status.json.tmp').exists())
  self.assertEqual((self.project/'status.json').read_text(),original)
if __name__=='__main__':unittest.main()

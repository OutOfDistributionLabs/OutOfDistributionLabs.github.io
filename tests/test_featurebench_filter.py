import io,json,tarfile,tempfile,unittest
from pathlib import Path
from benchmarks.featurebench_filter import filter_stream
class CacheFilterTests(unittest.TestCase):
    def archive(self,link=None):
        b=io.BytesIO()
        with tarfile.open(fileobj=b,mode='w') as t:
            for name,text in [('opt/miniconda3/pkgs/cache','cached'),('opt/miniconda3/envs/testbed/code.py','active'),('root/my_repo/source.py','source')]:
                info=tarfile.TarInfo(name);info.size=len(text);t.addfile(info,io.BytesIO(text.encode()))
            if link:
                info=tarfile.TarInfo('usr/bin/broken');info.type=link;info.linkname='/opt/miniconda3/pkgs/cache' if link==tarfile.SYMTYPE else 'opt/miniconda3/pkgs/cache';t.addfile(info)
        b.seek(0);return b
    def test_active_environment_and_source_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            out=io.BytesIO();filter_stream(self.archive(),out,Path(d)/'stats.json');out.seek(0)
            with tarfile.open(fileobj=out) as t:
                self.assertEqual(t.extractfile('opt/miniconda3/envs/testbed/code.py').read(),b'active');self.assertEqual(t.extractfile('root/my_repo/source.py').read(),b'source');self.assertNotIn('opt/miniconda3/pkgs/cache',t.getnames())
    def test_hardlink_payload_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            out=io.BytesIO();filter_stream(self.archive(tarfile.LNKTYPE),out,Path(d)/'stats.json');out.seek(0)
            with tarfile.open(fileobj=out) as t:self.assertEqual(t.extractfile('usr/bin/broken').read(),b'cached')
    def test_symlink_to_removed_cache_rejected(self):
        with tempfile.TemporaryDirectory() as d,self.assertRaises(ValueError):filter_stream(self.archive(tarfile.SYMTYPE),io.BytesIO(),Path(d)/'stats.json')
if __name__=='__main__':unittest.main()

"""Streaming cache-only removal for storage-constrained derived images.

Fail closed if a retained hard link points into a removed directory. Never remove
active environments, source files or tests. This is a disclosed infrastructure
adaptation that must pass unchanged official reference grading before inference.
"""
import argparse,json,posixpath,sys,tarfile
from collections import Counter
from pathlib import Path
EXCLUDED=('opt/miniconda3/pkgs','root/.cache','root/my_repo/.git')
def normalized(name):
    name=posixpath.normpath(name).removeprefix('./').lstrip('/')
    if name=='..' or name.startswith('../'):raise ValueError('Unsafe source image member')
    return name

def excluded(name):
    return any(name==p or name.startswith(p+'/') for p in EXCLUDED)

def filter_stream(source,target,stats_path):
    sizes=Counter();removed=Counter();members=0
    with tarfile.open(fileobj=source,mode='r|') as src,tarfile.open(fileobj=target,mode='w|',format=tarfile.PAX_FORMAT) as dst:
        for entry in src:
            name=normalized(entry.name);prefix='/'.join(name.split('/')[:3]);sizes[prefix]+=entry.size;members+=1
            if excluded(name):removed[prefix]+=entry.size;continue
            if entry.islnk() and excluded(normalized(entry.linkname)):
                raise ValueError('Retained hard link points into excluded cache: '+name)
            if entry.issym():
                linked=entry.linkname if entry.linkname.startswith('/') else posixpath.join(posixpath.dirname(name),entry.linkname)
                if excluded(normalized(linked)):raise ValueError('Retained symlink points into excluded cache: '+name)
            dst.addfile(entry,src.extractfile(entry) if entry.isfile() else None)
    Path(stats_path).write_text(json.dumps({'excluded_prefixes':EXCLUDED,'members_seen':members,'source_regular_bytes':sum(sizes.values()),'removed_regular_bytes':sum(removed.values()),'largest_source_prefixes':sizes.most_common(20),'removed_prefixes':removed.most_common()},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stats',required=True);a=p.parse_args();filter_stream(sys.stdin.buffer,sys.stdout.buffer,a.stats)

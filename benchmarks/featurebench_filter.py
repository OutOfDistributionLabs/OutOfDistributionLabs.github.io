"""Streaming cache removal, preserving retained hard-link payloads and aliases.

Cached payloads spool to hashed temporary paths only. Retained symlinks into a
removed cache fail closed. Qualify the result with the official reference scorer.
"""
import argparse,copy,hashlib,json,posixpath,shutil,sys,tarfile,tempfile
from collections import Counter
from pathlib import Path
EXCLUDED=('opt/miniconda3/pkgs','root/.cache','root/my_repo/.git')
def normalized(name):
    name=posixpath.normpath(name).removeprefix('./').lstrip('/')
    if name=='..' or name.startswith('../'):raise ValueError('Unsafe source image member')
    return name

def excluded(name):return any(name==p or name.startswith(p+'/') for p in EXCLUDED)

def filter_stream(source,target,stats_path):
    sizes=Counter();removed=Counter();members=0;cached={};redirect={};materialized={};restored=[];spooled=0
    with tempfile.TemporaryDirectory(prefix='ood-image-cache-') as work,tarfile.open(fileobj=source,mode='r|') as src,tarfile.open(fileobj=target,mode='w|',format=tarfile.PAX_FORMAT) as dst:
        for entry in src:
            name=normalized(entry.name);prefix='/'.join(name.split('/')[:3]);sizes[prefix]+=entry.size;members+=1
            if excluded(name):
                removed[prefix]+=entry.size
                if entry.isfile():
                    spooled+=entry.size
                    if spooled>12_000_000_000:raise ValueError('Cache spool budget exceeded')
                    path=Path(work)/hashlib.sha256(name.encode()).hexdigest()
                    with path.open('wb') as f:shutil.copyfileobj(src.extractfile(entry),f)
                    cached[name]=path
                elif entry.islnk():redirect[name]=normalized(entry.linkname)
                continue
            if entry.issym():
                linked=entry.linkname if entry.linkname.startswith('/') else posixpath.join(posixpath.dirname(name),entry.linkname)
                if excluded(normalized(linked)):raise ValueError('Retained symlink points into excluded cache: '+name)
            if entry.islnk() and excluded(normalized(entry.linkname)):
                linked=normalized(entry.linkname);seen=set()
                while linked in redirect:
                    if linked in seen:raise ValueError('Cache hard-link cycle')
                    seen.add(linked);linked=redirect[linked]
                if linked in materialized:
                    entry=copy.copy(entry);entry.linkname=materialized[linked];dst.addfile(entry);continue
                if linked in cached:
                    entry=copy.copy(entry);entry.type=tarfile.REGTYPE;entry.linkname='';entry.size=cached[linked].stat().st_size
                    with cached[linked].open('rb') as f:dst.addfile(entry,f)
                    materialized[linked]=name;restored.append(name);continue
                if not excluded(linked):
                    entry=copy.copy(entry);entry.linkname=linked;dst.addfile(entry);continue
                raise ValueError('Retained link has no verified cached payload: '+name)
            dst.addfile(entry,src.extractfile(entry) if entry.isfile() else None)
    Path(stats_path).write_text(json.dumps({'excluded_prefixes':EXCLUDED,'members_seen':members,'source_regular_bytes':sum(sizes.values()),'removed_regular_bytes':sum(removed.values()),'cache_spool_bytes':spooled,'restored_hardlink_payloads':restored,'largest_source_prefixes':sizes.most_common(20),'removed_prefixes':removed.most_common()},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stats',required=True);a=p.parse_args();filter_stream(sys.stdin.buffer,sys.stdout.buffer,a.stats)

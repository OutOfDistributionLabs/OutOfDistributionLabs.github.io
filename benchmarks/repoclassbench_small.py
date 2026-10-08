"""Execute frozen paired class-generation pilot; private assets stay outside repo."""
import argparse
import hashlib
import json
from pathlib import Path
from harnesses.small_repository import infer, grade, ROOT

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--rows', required=True)
    p.add_argument('--originals', required=True)
    p.add_argument('--views', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    project = ROOT / 'research/repoclassbench-small-pilot'
    freeze = json.loads((project / 'freeze.json').read_text())
    for name, expected in freeze['artifacts'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen implementation changed: ' + name)
    controls = json.loads((project / 'qualification.json').read_text())
    if len(controls) != 4 or any(r['resolved'] != (r['control'] == 'gold') for r in controls):
        raise ValueError('Reference and empty controls did not qualify')
    readiness = json.loads((project / 'readiness.json').read_text())
    if not readiness['turn_completed'] or readiness['mcp_calls'] < 1:
        raise ValueError('Actual MCP readiness not demonstrated')
    rows = json.loads(Path(a.rows).read_text())
    image = json.loads((project / 'runtime.json').read_text())['image_id']
    output = Path(a.output)
    output.mkdir(parents=True, exist_ok=False)
    records = []
    for entry in freeze['schedule']:
        i, arm = entry['task_ordinal'], entry['arm']
        task = output / f'{i}-{arm}'
        run, answer = infer(rows[i], Path(a.views) / str(i), image, arm,
                            task / 'inference', freeze['wall_seconds'])
        result = grade(rows[i], a.originals, answer, image, task / 'grading')
        record = {'run': run, 'grade': result}
        records.append(record)
        (output / 'results.json').write_text(json.dumps(records, indent=2) + '\n')
        print(json.dumps(record), flush=True)

if __name__ == '__main__': main()

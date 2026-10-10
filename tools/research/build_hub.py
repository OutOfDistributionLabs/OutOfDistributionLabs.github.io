#!/usr/bin/env python3
"""Build a programme hub from its curated papers and existing task status files."""
import argparse
import html
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def build(slug):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug):
        raise ValueError('Use a project slug')
    folder = ROOT / 'research' / slug
    project = json.loads((folder / 'project.json').read_text())
    esc = html.escape
    arrow = '<svg aria-hidden="true" viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor"><path d="M3 9 9 3M3 3h6v6"/></svg>'
    papers = []
    for paper in project['papers']:
        task = paper['task']
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', task):
            raise ValueError('Invalid publication task slug')
        for name in ['white-paper.pdf', 'progress.html']:
            if not (ROOT / 'research' / task / name).is_file():
                raise ValueError('Missing publication: ' + task + '/' + name)
        papers.append(f'''<li class="paper"><div><p class="meta">{esc(paper['meta'])}</p><h3>{esc(paper['title'])}</h3><p class="description">{esc(paper['summary'])}</p></div><div class="links"><a href="../{esc(task)}/white-paper.pdf" target="_blank" rel="noopener" aria-label="Read {esc(paper['title'])}, PDF in a new tab">White paper {arrow}</a><a href="../{esc(task)}/progress.html">Progress</a></div></li>''')
    tasks = []
    completed = 0
    running = 0
    paused = 0
    for task in project['tasks']:
        task_id = task['id']
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', task_id):
            raise ValueError('Invalid task slug')
        source = ROOT / 'research' / task_id
        config = json.loads((source / 'research.json').read_text())
        state = json.loads((source / 'status.json').read_text())
        total = len(config['steps'])
        done = state['step'] == total
        completed += done
        running += state['running'] and not done
        paused += not done and not state['running']
        label = task['complete_label'] if done else 'In progress' if state['running'] else 'Paused'
        kind = 'complete' if done else 'active' if state['running'] else 'paused'
        tasks.append(f'''<li class="task" data-task="{esc(task_id)}" data-total="{total}" data-done-label="{esc(task['complete_label'])}" data-step="{state['step']}" data-running="{str(state['running']).lower()}"><div><h3><a href="../{esc(task_id)}/progress.html">{esc(task['title'])}{arrow}</a></h3><p class="description">{esc(task['description'])}</p></div><div class="task-status"><span class="state {kind}">{esc(label)}</span><span class="steps">{state['step']}/{total} steps</span></div><div class="track" role="progressbar" aria-label="{esc(task['title'])} progress" aria-valuemin="0" aria-valuemax="{total}" aria-valuenow="{state['step']}"><span style="width:{state['step']/total*100:.2f}%"></span></div></li>''')
    template = (ROOT / 'tools/research/hub-template.html').read_text()
    replacements = {'TITLE': esc(project['title']), 'DESCRIPTION': esc(project['description']), 'PAPERS': '\n'.join(papers), 'TASKS': '\n'.join(tasks), 'COUNTS': f'{completed} complete · {paused} paused' + (f' · {running} active' if running else ''), 'ACTIVITY': 'Research in progress' if running else 'No active runs', 'PAPERCOUNT': str(len(papers))}
    for key, value in replacements.items():
        template = template.replace('{{' + key + '}}', value)
    (folder / 'index.html').write_text(template)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--project', required=True)
    build(p.parse_args().project)

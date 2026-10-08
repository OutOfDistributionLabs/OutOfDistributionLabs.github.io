# Out of Distribution Labs research process

The reusable runner lives in [`tools/research/run.py`](../tools/research/run.py). It needs Python 3.9+ (standard library), git, and an authenticated GitHub CLI (`gh`). LaTeX compilation is a separate research step. A project is one folder under `research/`; its `research.json` configures title, steps, topic, interval, public URL, publishing remote/branch and resource links.

## New project

Run commands from the repository root:

```sh
python tools/research/run.py --project project-slug init --title 'Research title' --topic oodlabs
# Confirm direction and fill in research/project-slug/research-plan.md.
# Add a link to research/project-slug/progress.html in index.html.
python tools/research/run.py --project project-slug start --summary 'Scope confirmed; beginning research.' --extra index.html
```

`init` prepares a draft, without committing or sending notifications. `start` publishes the first checkpoint and starts a detached, project-specific heartbeat. Repeating `start` reuses a running heartbeat. The runner is a workspace process, not a cloud scheduler: it runs while the workspace is alive. For an unattended research job, invoke it from a persistent machine or scheduled workflow with the required GitHub/ntfy access; publishing a status page alone does not perform research.

## Work one step at a time

```sh
python tools/research/run.py --project project-slug step --step 1 --summary 'Protocol complete; reviewing primary sources.'
python tools/research/run.py --project project-slug step --step 2 --summary 'Literature review complete; developing theory.'
# Continue sequentially through the configured steps; add --extra PATH for shared files.
python tools/research/run.py --project project-slug step --step 6 --summary 'Paper and supporting materials published and verified.' --extra index.html
```

A step updates status and the public HTML page, stages project artifacts, commits, pushes to the configured branch and follows the configured notification policy at `https://ntfy.sh/TOPIC`. New projects default to a 60-second page heartbeat and a separate 300-second ntfy interval. Configure `heartbeat_seconds`, `notification_seconds`, `notify_on_checkpoint` (default false) and `notify_on_complete` (default true) in `research.json`; restart an already-running daemon after changing the page interval. Page heartbeats publish only `status.json` and `progress.html`; it does not publish unfinished manuscript files. Complete every configured step in order. There is no artificial waiting period between steps.

Use `pause` to publish a paused state and stop the next heartbeat; `start` resumes. `render` regenerates HTML without publishing. `notify --summary TEXT` sends only a notification. Heartbeat logs and process IDs are in `/tmp/oodlabs-research-PROJECT.log` and `.pid`. A shared git lock serializes publishing across projects. `git commit --only` excludes unrelated staged files; old design prototypes are not published. Validation/commit failures restore the prior checkpoint. Push failures leave the local commit available for a retry (`start` republishes the current project) and are logged/notified; an ntfy failure is reported separately from a successful push. Progress pages are static and publicly accessible. Configure project URLs when the deployment domain changes.

## Research quality gates

Use [`protocol-template.md`](../tools/research/protocol-template.md) for scope and evidence rules. The normal stages are protocol, primary-source review, theoretical synthesis, evaluation, manuscript, publication. Customize the steps for the problem, keeping literature review before claims and writing. A theoretical paper may prioritize proofs and counterexamples; an empirical paper needs reproducible experiments, suitable baselines and uncertainty estimates. Always distinguish proposals, derived consequences, observations and hypotheses. Keep exact source versions and the search cutoff. No fabricated references, unsupported novelty claims, or simulated-agent results presented as real multi-agent deployments.

The existing `hierarchical-abstractions` project is a worked example. Its paper branding uses the lab's sans-serif wordmark, blue-black ink and restrained champagne/amber accents; its LaTeX source can serve as a starting point for later papers once complete.

Run `python tools/research/test_workflow.py` to exercise checkpoint isolation, sequential steps, rollback, completed-project behavior and unpublished-link filtering against a temporary local git remote.

## Branded manuscript template

Copy `tools/research/white-paper-template.tex` to the project folder as `white-paper.tex`. Edit title, subtitle, short title, date, paper identifier and evidence status; then supply the reviewed content and verified bibliography. It uses the lab's sans-serif wordmark, dark blue-black cover, restrained amber accent and plain mathematical typesetting. The two-line wordmark uses a shared left edge, and the particle graphic spans the full dark cover band. Inspect the compiled cover when the title changes: layout is a design choice, not automatically fitted.

## Agent-engine benchmarking

Use [benchmark-process.md](../tools/research/benchmark-process.md) for the reusable 12-stage experimental programme, workload depth, substeps and mandatory sentinel gates. The local Python planning and gate scaffold is [tools/benchmarking/methodology.py](../tools/benchmarking/methodology.py); the [intuition-engine methodology](intuition-engine-benchmarking/README.md) is the first worked protocol. Planning completion does not imply engine or benchmark completion.

Runtime errors use the same `notification_seconds` interval by default; `notify_on_error: true` opts into immediate error notices. Page cadence remains independent. Failed status writes remove their temporary file and preserve the previous status.

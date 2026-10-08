# Intuition engine: executable development study

Out of Distribution Labs · development version 0.1.0

[Read the white paper](white-paper.pdf) · [Measured results](report.md) · [Qualification](qualification.md) · [Full methodology](../intuition-engine-benchmarking/research-plan.md)

This project contains a working MCP and a real-data deterministic retrieval study. It does **not** contain successful Codex/Claude/Antigravity or hundred-agent repair trials. Fresh Codex authentication fails before inference; monetary accounting is unqualified. That blocker and the graph prototype's near-null/negative retrieval result are preserved rather than replaced with simulated agent scores.

## Install and use the MCP

From repository root, Python 3.10+:

```sh
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m intuition_engine.server --root /absolute/path/to/repository --mode graph
```

The server uses stdio for MCP protocol messages; keep it in a client-managed process. It exposes `intuition_status`, `intuition_query` and `intuition_evidence`. A client queries the current snapshot, asks for source candidates, and optionally fetches evidence IDs. It never edits code. `flat` mode is the matched BM25 control. `scan` supplies the simple deterministic scan control.

Common MCP client configuration (adapt the Python executable/root to your machine):

```json
{
  "mcpServers": {
    "intuition": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "intuition_engine.server", "--root", "/absolute/path/to/task-repository", "--mode", "graph"]
    }
  }
}
```

Codex uses its own configuration shape:

```toml
[mcp_servers.intuition]
command = "/absolute/path/to/.venv/bin/python"
args = ["-m", "intuition_engine.server", "--root", "/absolute/path/to/task-repository", "--mode", "graph"]
```

Only point the server at the permitted task source workspace. Do not mount evaluator storage/reference answers. It checks revision changes and rejects stale advice; restart/reindex through the controller after edits. Call-name links are heuristic hints, not sound runtime-call proofs. Ranking scores are not correctness probabilities. Response budget fields currently use conservative UTF-8 byte ceilings, not exact model tokenization. There is no automatic globally correct abstraction or proof-checking facility.

An actual client call:

```sh
.venv/bin/python -m harnesses.mcp_client --root /path/to/repo --query 'Where is retry idempotency enforced?' --mode graph
```

This is a transport/advice call, not an LLM effectiveness experiment. Twelve dataset-based stdio probes and separate fixture tests passed; other harnesses still need adapter conformance and measured adoption.

## Reproduce the frozen assay

The existing results use engine/scoring code hashes in `evaluation/assay-freeze.json` (git commit `495a6bc` at freeze). Later analysis/plot/report commits do not change that ranking. The artifact includes the exact dataset hash, dependencies, limits and fixed weights. Do not overwrite the published run directory.

```sh
.venv/bin/python -m benchmarks.repoqa_assets --cache /tmp/repoqa-assets --output /tmp/asset-register.json
.venv/bin/python -m benchmarks.repoqa_run --cache /tmp/repoqa-assets --output /tmp/repoqa-run-new
.venv/bin/python -m benchmarks.analyse /tmp/repoqa-run-new
# Plotting dependency is optional:
.venv/bin/pip install matplotlib
.venv/bin/python -m benchmarks.figures /tmp/repoqa-run-new
.venv/bin/python -m harnesses.mcp_probe --cache /tmp/repoqa-assets --output /tmp/mcp-probes.json
```

Dataset/scorer downloads are fixed-hash checked. Corpus source is never executed. Release-license and original repository licensing still apply; no source-code corpus is republished here. Exact task ranks should reproduce under locked code/dependencies; timing will vary with hardware and caches. This is full-repository non-LLM retrieval, not official RepoQA long-context model performance.

## Checks and agent readiness

```sh
.venv/bin/python -m unittest discover -s tests -v
python tools/research/test_workflow.py
python tools/benchmarking/test_methodology.py
.venv/bin/python -m harnesses.codex_runner readiness --output /tmp/codex-readiness.json
```

The Codex runner constructs fresh ephemeral A/B/C sessions and rejects forbidden task fields. A benchmark run additionally requires a separately checked isolation receipt. It captures token events and patches but leaves provider cost null without a real billing meter; it cannot qualify a confirmatory equal-cost study merely by accepting command-line inputs. Authentication, official repair scoring, aggregate budget enforcement, full cost accounting and actual agent-issued MCP calls are open gates. See the method for symmetric failure policies and power limits.

## Build the paper

```sh
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error research/intuition-engine-pilot/white-paper.tex
```

The final section contains the measured results. Tables/plots derive from JSON/CSV measurements; the LaTeX result rows are an inline copy of generated `evaluation/table.tex` to avoid input/alignment macro issues.

## Configurable activity updates

In research.json: `heartbeat_seconds: 60`, `notification_seconds: 300`, `notify_on_checkpoint: false`, `notify_on_complete: true`. The shared research runner publishes page activity each minute, sends periodic ntfy every five minutes, and sends a completion notice. Completed work stops its daemon. Timers run only while the workspace is alive.

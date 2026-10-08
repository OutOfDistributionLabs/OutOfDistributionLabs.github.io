# Measured development study results

Out of Distribution Labs · Real benchmark data; no LLM repair trials

## Held-out repository retrieval

The frozen assay evaluated 600 RepoQA release cases (six languages, 60 repositories), with 120 development tasks and 480 evaluation tasks separated by repository. All 1,800 task/arm outcomes are retained. The input is full release repository code, not the official 16K-context model prompt. A deterministic ranker returns a function; the exact upstream scorer determines closest-needle match and similarity >= .8. This is an adapted assay, not a leaderboard score or software-correctness result.

| Arm | Successful / 480 | Success | Canonical code/path recall@10 | Mean query CPU ms | Mean build CPU ms/repository |
|---|---:|---:|---:|---:|---:|
| Lexical scan | 221 | 46.04% | 73.75% | 8.988 | 285.4 |
| Flat BM25 | 183 | 38.13% | 72.08% | 1.746 | 304.5 |
| Graph + BM25 | 184 | 38.33% | 72.29% | 3.076 | 314.3 |

## Paired interpretation

Graph beats flat on 11 tasks and loses on 10: a net one task, +0.21 percentage points. The exploratory repository-cluster 95% bootstrap interval is [-1.67, +1.88] points (10,000 draws, seed 20261007); the exact paired McNemar p-value is 1.00. There is no evidence of a retrieval advantage for this frozen graph prototype. This is not a proof that all abstraction graphs are useless.

Graph trails the lexical scan by 7.71 points. The scan is a deliberately simple matched-corpus retrieval control, not a Codex agent. Scanning is slower per query, illustrating a quality/latency tradeoff. Graph's mean query CPU is 1.76 times flat's and its repository-build CPU is about 3.2% higher. Hierarchical pooling and call-name hints did not earn their extra query work here. Do not claim engine token savings or patch-resolution gains.

The graph/exact-code diagnostic succeeds on 185 evaluation cases, while upstream similarity succeeds on 184; those are different metrics. Canonical code/path matching ignores whitespace and uses parser extraction, while upstream scorer compares the selected answer against the ten curated needle functions, including ambiguity/threshold effects. Neither metric validates behavior. All evaluation targets were extractable; one development target was not. Unsupported/parser-error signals and all timing rows are retained.

## Costs and transport

The full three-arm assay ran in about 79 seconds in one container. Indexes were rebuilt per arm/repository and reused for ten queries; stem caches were cleared, but OS/interpreter caches were shared and arm order randomized. Query CPU/wall measures are in-process: they exclude scorer execution, MCP IPC, model inference and workspace revision hashing. Build cost is reported separately, not silently amortized away. Source bytes total about 55.2 MB; the complete dataset metadata/code file is 71.5 MB. These are local timing observations, not provider billing or general hardware throughput.

Twelve real stdio MCP query probes (flat and graph, one development repository per language) passed discovery, query and exact source-snapshot parity. Fixture tests also passed source retrieval, invalid-argument handling, stale revision and forged evidence rejection. Direct MCP client calls demonstrate transport/corpus parity, not autonomous agent adoption or an agent quality improvement. The assay itself called deterministic rankers in-process, so transport-probe timings must not be mixed into its latency figures.

## Scientific sentinel

Advance to publishing this limited result. Redo the engine design before a larger effectiveness claim; preserve the frozen null/negative study and use a new development/freeze cycle for changes. Do not rerun the same holdout until it looks favourable. Original primary patch-resolution hypothesis remains untested. Codex readiness fails because CLI authentication cannot refresh, and monetary accounting remains unqualified. No Claude Code/Antigravity or hundred-agent comparison was performed.

## Reproduction artifacts

`evaluation/assay-freeze.json`: pre-query source hashes, weights, split rule and dependencies. `manifest.json`: all task IDs and repository commits. `raw-results.csv`: 1,800 rows. `build-results.csv`: 180 rebuilds. `results.json` and `analysis.json`: aggregates and paired analysis. Figures and tables derive from those measured files. No benchmark source-code corpus or credentials are committed.

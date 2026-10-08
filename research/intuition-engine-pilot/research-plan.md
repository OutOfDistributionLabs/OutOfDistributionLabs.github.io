# Intuition engine implementation and development pilot

Out of Distribution Labs · October 7, 2026 (Pacific)

Follow the [methodology](../intuition-engine-benchmarking/research-plan.md) and reusable 12-stage sentinel programme. This continuation implements an engine and real MCP, qualifies actual benchmark assets, and executes available bounded development assays. Engine implementation and a non-LLM assay do not complete the primary patch-resolution hypothesis.

## Scope and endpoint

Primary future study: independent Codex native/flat/full arms on official SWE-bench repair tasks, total-budget matched. This environment's fresh Codex CLI smoke test currently fails before inference because its access token cannot be refreshed. Do not use the interactive conversation as a substitute control, invent costs, or label direct Python MCP calls as a Codex experiment.

Available first assay: real RepoQA description-to-function retrieval with deterministic lexical and graph-assisted rankers, source corpus matched, evaluator labels isolated from indexes. Initially qualify all five language adapters; unsupported language tasks are disclosed. Report candidate recall/ranking and upstream similarity score where validated; this is an adapted non-LLM retrieval assay, not official model leaderboard performance or software repair evidence.

## Development freeze

First acquire and hash a fixed RepoQA release; identify all task/repository/language IDs; reserve development tasks before any tuning. Freeze retrieval settings before reporting held-out descriptive results. Native no-index linear lexical scanning, BM25 plus symbol matching, and graph-assisted BM25 use the same documents and query; same candidate cap, no label-informed graph. Native scanning is a deterministic retrieval baseline, explicitly distinct from a native Codex agent. Count build/query wall and CPU time, corpus size and MCP calls. No statistical claim of agent benefit follows from this assay.

## Sentinels

1 qualification: task license/version, real corpus, answer boundary, evaluator sanity checks and resources. 2 implementation: actual MCP initialize/list/call round trip, stale revision/path-escape/unsupported-language tests and common flat/full API. 3 harness: fresh-run isolation and complete accounting; Codex auth failure blocks agent trials. 4 available assay: all predeclared task IDs scored, fair source access, null outcomes retained. 5 review: distinguish retrieval from repair, service round trip from agent call, and unknown dollar cost from zero. 6 publication: sanitised reproducible code, hashes, full results and blockers.

Publish at each checkpoint; page heartbeat every 60 seconds; ntfy every 300 seconds to oodlabs, with checkpoint notices disabled and a completion notice enabled. A blocked scientific gate prevents its dependent claims, while independent implementation and properly qualified assays may proceed.

## Final deliverable

A branded LaTeX white paper following the reusable cover template, with problem/thesis, existing work, method, MCP/harness architecture, threats to validity and reproducibility, followed by measured results at the end. Use only real traces and dataset-derived measurements; retain null results. Include full machine-readable outcomes and scorer checks. No Codex/Claude repair results are claimed if authentication prevents their execution.

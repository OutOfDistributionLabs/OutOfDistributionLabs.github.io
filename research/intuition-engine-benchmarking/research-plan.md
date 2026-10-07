# Intuition engine: experimental protocol

Out of Distribution Labs · October 7, 2026 · Planning protocol v0.1 (not frozen)

## Problem statement

Software agents spend scarce context, tool calls and inference budget deciding which repository evidence matters, how components interact, and when a local hypothesis requires wider inspection. Can a revision-scoped abstraction graph improve these decisions enough to improve independently graded software outcomes, after accounting for its construction and consultation costs?

The earlier paper's synthetic simulation established no advantage over a complete flat index. This programme tests real task outcomes and the incremental contribution of typed, evidence-grounded abstraction. It does not assume that hierarchy, more agents, or an MCP interface is beneficial.

## Proposed thesis and falsifiers

**Primary hypothesis H1:** on a frozen, repository-stratified SWE-bench Verified comparison with one specified model/harness and equal total resource ceilings, engine assistance increases the official resolved fraction relative to the native harness. A practically meaningful target is +5 absolute percentage points. Evidence of improvement requires the lower bound of the predeclared 95% paired interval above zero; achieving the +5-point target is a separate descriptive requirement, not implied by statistical significance. The target is an experimental design choice, not a predicted result.

**Mechanism hypothesis H2:** with identical source corpus, token allowance and a common tool interface, the full engine beats BM25 plus symbol lookup on RepoQA function retrieval and on the software repair task. If native-tool improvement disappears against this baseline, attribute it to tool/index availability rather than hierarchy. H2 comparisons are secondary and multiplicity-adjusted; they cannot rescue a failed H1.

**Exploratory efficiency hypothesis H3:** the engine lowers end-to-end monetary cost by at least 20% while resolution remains within a predeclared 3-point non-inferiority margin. This requires a separate appropriately powered study; do not infer non-inferiority from a nonsignificant success difference. Report cost/success curves even if no inferential claim is possible. Margins must be justified and locked before confirmatory data.

**Qualitative mechanism question Q1:** do evidence trails enable agents to find missed cross-module dependencies, reject stale claims, and recover from low coverage? Score blinded traces using a fixed rubric (correct dependency discovery, evidence-grounding, justified broadening, harmful advice, recovery). Two independent reviewers label a repository-stratified sample; report agreement and adjudication. Without independent reviewers this remains a single-reviewer descriptive audit, not reliable causal validation.

Negative results are valid: no improvement, excessive overhead, or worse repair success reject the claimed benefit within this model/harness/benchmark. Tool correctness without task gains is not success for H1. Improvements from altered prompts or unequal extra model calls do not isolate the engine.

## Task ladder and sequence

1. RepoQA SNF: low-cost mechanism assay with the upstream 0.8 threshold and official evaluator. Preserve an official unchanged full-context baseline. A repository-tool variant exposes only the supplied task context, with the same context universe across arms; label this variant explicitly, never submit it as an unchanged official leaderboard result. Target function and correctness fields are evaluator-only.
2. SWE-bench Verified: primary repair benchmark, official held-out grading; issues and base revision are agent input. Pre-existing repository tests may be run normally. Gold patches, benchmark test patches, grading scripts and reference solutions are outside the agent sandbox.
3. SWE-bench Pro: independent long-horizon replication only after engineering and budget feasibility. The upstream audit currently reports V2 as default; pin the explicit release/config, do not silently combine V1/V2 or Verified/Pro scores.
4. CrossCodeEval: optional context-selection assay; it evaluates cross-file completion, not repair or multi-agent coordination. Raw-corpus availability must pass audit before promising a graph-building comparison. Reference-assisted retrieval is not an admissible treatment input.

Do not jump directly from a retrieval gain to a repair claim. Do not claim hundreds of agent performance from single-agent results. Multi-agent concurrency is a later separate factorial experiment holding aggregate budget fixed.

## Treatment arms and estimands

| Arm | Harness support | Purpose |
|---|---|---|
| A native | Native repository tools; no engine endpoint | Real deployment baseline |
| B flat | Native tools + common MCP endpoint implementing BM25 and deterministic symbol lookup | Strong indexing/tool baseline |
| C full | Native tools + same endpoint implementing typed multi-view graph, evidence paths and measured coverage-based broadening | Full engine treatment |
| D ablated | Same as C with selected graph/admission/coverage mechanism disabled | Mechanism isolation, after pilot |

For B/C/D, tool names, response schema, response token cap, initial instructions and permissible data are identical. A has the same harness instructions with the unavailable tool excluded; document the unavoidable interface difference. Log actual consultation rate. Primary deployment effect is intention-to-treat C minus A, including tasks where the agent ignores the engine or it fails. Mechanism effect is C minus B. Per-consultation analysis is exploratory because consultation is selected by task/agent behavior.

D variants, one at a time: flatten all abstraction edges while preserving candidate entities and evidence; disable broadening; remove revision/evidence admission; replace structured views with token-matched summaries. Some arms can produce unsafe proposals; run only inside isolated benchmarks. An oracle-localization arm, if used for an upper bound, is distinctly evaluator-assisted and excluded from fair comparisons.

## Information and cost controls

Freeze model identifier (not only a moving alias), harness version, prompts, tools, sampling settings, engine commit, parser/retriever versions, benchmark release, instance IDs, image digests and scorer. Agent-visible snapshots contain only permitted issue/context and base-revision code; no git future history, remote task discussions, reference patches, grading assets or prior arm traces. Disable network during the agent phase except narrowly routed inference if needed. Evaluator runs separately in a fresh sandbox after the patch is sealed. Persist hashes and a field allowlist rather than giving engines complete benchmark records.

Primary budget: same maximum monetary spend, wall clock and agent/model tool allowance per instance; count engine model inference against the same spend ceiling. Record input/output/cache token counts with provider pricing version, engine CPU/RAM, serialized bytes, indexing and query times. Do not call CPU milliseconds and model dollars interchangeable. The budget vector includes a fixed CPU/RAM allowance; report its costs separately where pricing is unavailable. Use cold per-task construction as the primary accounting. Warm repository reuse is a separate amortized analysis with disclosed reuse factor, storage and invalidation policy. No hidden free preprocessing or cached cross-task labels.

Pilot proposes actual numeric ceilings based on resource measurements; protocol.json deliberately leaves them unset. A confirmatory freeze must reject missing ceilings. Compare matched maximum ceilings, report actual usage and budget-exceeded outcomes. Cost curves at multiple fixed ceilings are secondary. A cheaper failed run is not automatically better.

## Pairing, splits and execution

Audit every eligible instance before sampling. Separate pilot/development and confirmation by repository where feasible; publish the exact mapping and overlaps. The 500-item Verified universe limits clean repository-disjoint tests. If pilot tasks consume part of that universe, report the reduced untouched confirmation size; never tune on outcomes and then silently count those tasks as held out. If full 500 is retained for confirmation, develop on a separately audited, repository-disjoint dataset or declare the overlap limitation before freezing.

Use a deterministic seeded manifest with all inclusions/exclusions and reasons. Pair arms on the same instance and replicate index. Randomize/interleave arm order within repository blocks to reduce provider and infrastructure drift. Fresh process, working directory, graph store, conversation and evaluator run ID per arm. Check reproducibility, not deterministic model behavior; when API seeds are unsupported, record that fact. Repeats share an instance: do not treat them as new independent tasks.

First harness is an isolated Codex CLI runner, if it can expose stable model configuration, MCP access, logs and cost accounting. The current interactive conversation is suitable for a plumbing demonstration but not an unbiased paired run: it already knows prior reasoning and cannot be reset by asking it to forget. Never let the same conversation solve C then A. Benchmark subprocesses require independent fresh sessions. A standalone script speaking MCP is a client integration check, not a Codex effectiveness experiment.

## Metrics and statistical analysis

Primary endpoint: official binary resolved outcome per eligible instance for C and A at the locked primary ceiling, one locked primary attempt each. Record an attempted run failing through engine/agent timeout as unresolved in intention-to-treat. Infrastructure failures unrelated to arm are retried with a predeclared symmetric policy (one retry, same configuration); report both raw and final rates and exclusions. A failure of the treatment service itself stays in the treatment outcome. Never exclude cases because the patch fails.

Calculate paired absolute resolution difference, discordant counts (C-only success/A-only success), exact two-sided McNemar test, and 95% paired bootstrap interval stratified by repository, resampling instances within repository with published seed and 10,000 draws. This primary interval conditions on the benchmark repository mix. Separately bootstrap whole repositories as a sensitivity analysis; few repositories make that estimate unstable. Cross-repository generalization claims require independent repository replication, not just an instance-level interval.

If repeated primary attempts are later selected, specify their aggregation before freeze: instance-level mean success, with all attempts of an instance kept together in resampling, replaces—not supplements opportunistically—the single-attempt primary. Pass@k is a separate budget-k endpoint, not pass@1. Use Holm adjustment for the fixed secondary H2 family (RepoQA C/B and repair C/B); subgroup and ablation discoveries are exploratory unless independently preregistered. Report language/repository/task-size strata without selecting a winning subset as the primary result.

Secondary endpoints: end-to-end dollars and elapsed time distributions, tokens, CPU/RAM, official RepoQA success, evidence retrieval recall@k/MRR if independent relevance labels exist, valid evidence citation rate, invalid/stale reference rate, coverage-warning calibration, engine query count and consultation fraction. Gold patch file overlap is only an imperfect post-run localization proxy, never truth for all relevant evidence or a training input. Warning calibration needs held-out labels, never the previous simulation's perfect coverage oracle.

## Power and decision limits

A rough paired normal approximation is n ≈ (1.96 + 0.842)^2 q / d², where q is the discordant probability and d the absolute effect. For q=.25 and d=.05 this is about 785 independent instances; 500 would have a rough minimum detectable effect of 6.3 points. These are planning approximations ignoring finite population and repository correlation. Estimate discordance from development-only pilots, simulate the exact predeclared analysis, and freeze the sample/budget before confirmation. Repository clustering and benchmark-size limits can reduce power further.

If the available untouched set is too small, predeclare an estimation study with wide intervals or expand using a separate benchmark; do not pool incompatible scores to manufacture sample size. Null result with a wide interval is inconclusive, not proof of equivalence. Predefine endpoint and sample size; no repeated significance checking or post-hoc margin changes.

## Ethical/reproducibility and reporting boundaries

Public benchmark exposure/model training contamination is a threat even when our engine sees only permitted inputs. Record model release, task age and contamination checks; stronger claims need newer/private tasks later. Existing licenses, task access terms, images and upstream scorer feasibility must be audited before execution. No unreviewed benchmark code runs on the host; isolate tasks. Keep credentials out of traces and public artifacts. Publish manifests, protocol diffs, scorer/image/engine versions, sanitised trajectories, costs and all arms including null results.

The finished report should state the exact intervention and limits: useful retrieval, successful repair, cost efficiency and transferable harness integration are distinct claims. It should not claim certified semantic soundness from AST relations or a learned confidence score.

## Programme and sentinels

See ../../tools/research/benchmark-process.md for the reusable 12-stage programme, workload depth, substeps, and explicit redo/advance gates. Every stage emits an artifact and a sentinel evidence record. Planning acceptance allows implementation; only measured later gates allow experiments or effectiveness conclusions.

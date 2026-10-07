# Intuition engine benchmarking methodology

Out of Distribution Labs · Planning protocol v0.1

Read [the experimental protocol](research-plan.md), [existing benchmark audit](benchmarks.md), [proposed MCP contract](engine-contract.md), [reusable 12-stage programme](../../tools/research/benchmark-process.md), and [sentinel review](sentinel-review.md). [Public progress](https://outofdistributionlabs.github.io/research/intuition-engine-benchmarking/progress.html).

This phase specifies the research and creates executable planning/gate infrastructure. **No engine implementation, MCP calls or measured agent results yet.** The experimental programme is held at benchmark qualification; the completed public planning project is not a completed benchmark study.

## Local Python entry point

From repository root, Python 3.10+ (standard library):

```sh
python research/intuition-engine-benchmarking/methodology.py validate
python research/intuition-engine-benchmarking/methodology.py plan
python research/intuition-engine-benchmarking/methodology.py power --effect .05 --discordance .25 --n 500
python tools/benchmarking/test_methodology.py
# Expected to exit 2 until the real study is frozen and all ceilings/locks exist:
python research/intuition-engine-benchmarking/methodology.py validate --confirmatory
```

For another project, copy/customize protocol.json, then use:

```sh
python tools/benchmarking/methodology.py --protocol research/PROJECT/protocol.json plan
```

A task manifest is a JSON list of `{"instance_id":"actual-id","repo":"owner/repo"}` records, built from audited real benchmark data. Schedule creation does not execute agents:

```sh
python research/intuition-engine-benchmarking/methodology.py schedule --manifest /path/to/manifest.json --output /path/to/schedule.json
```

The schedule includes one A/B/C run per instance/seed in randomized order within repository blocks. Its run IDs distinguish arms, but an executor must namespace them with a unique execution ID on every actual launch to avoid upstream evaluator cache reuse. More configured seeds are repeated attempts, not independent task sample size. Do not repurpose these repeats as extra confirmatory evidence without updating/fixing the analysis before freeze.

## Sentinel records

Examples of real author self-reviews are scope-review.json and qualification-review.json. A gate input must list every criterion in that stage, boolean verdict, reason and project-local evidence artifacts; reviewer identity/role/independence; disposition and remediation for redo/stop. Attached files are hashed. Review files are immutable once recorded; version changes require renewed reviews and a new ledger, retaining the old history.

```sh
python research/intuition-engine-benchmarking/methodology.py gate --review research/intuition-engine-benchmarking/next-review.json --ledger research/intuition-engine-benchmarking/programme-gates.json
```

The current next stage is **02 Benchmark qualification**. It cannot advance merely because the MCP design is written. Never rerun the already-recorded stage-01 review against the current ledger. When the protocol is frozen, create a versioned ledger for that exact protocol and renew prior attestations. Confirmation gates require a frozen protocol and complete budget/version locks.

## Next implementation deliverables

1. Audited benchmark manifests and permitted-agent-field export, reference scorer smoke test and resource report.
2. Versioned package for flat and full engines, official SDK stdio MCP server and real MCP client round-trip tests.
3. Isolated Codex CLI adapter, unique working trees/stores, complete spend telemetry and independent grading.
4. Development-only A/B/C pilot; then power/budget freeze, untouched confirmation, ablations and cross-harness replication.

These are acceptance-gated work items, not existing capabilities. Preserve all negative results. The primary claim is patch-resolution improvement; retrieval, transport interoperability and finite graph checks alone do not establish it.

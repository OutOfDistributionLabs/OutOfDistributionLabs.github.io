# Existing benchmark audit

Out of Distribution Labs · inspected October 7, 2026 · primary project documentation, evaluator source where noted; benchmark data and images have not yet been acquired or executed.

| Problem | Existing benchmark | Selection | What an engine can help with | What it cannot establish |
|---|---|---|---|---|
| Issue → correct repository patch | [SWE-bench Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified), 500 curated tasks | Main outcome study | Code/evidence localization; dependencies; targeted test suggestions; revision-aware state | Production correctness, unseen repository generalization, hundred-agent scaling |
| Description → relevant function | [RepoQA SNF](https://github.com/evalplus/repoqa), 500 cases: five languages × ten repos × ten functions | First mechanism assay | Semantic code localization, compact evidence and abstention/broadening | Correct patches or functional equivalence; evaluator uses syntactic similarity |
| Long-horizon issue → patch | [SWE-bench Pro](https://github.com/scaleapi/SWE-bench_Pro-os) | Independent replication candidate | Cross-file dependencies and longer decision chains | Same population as Verified; comparable score without matching release/protocol |
| Cross-file code completion | [CrossCodeEval](https://github.com/amazon-science/cceval) | Optional secondary assay | Selecting dependency context under token limits | End-to-end software repair or harness decision quality |

## Exact source audit and version traps

### SWE-bench

Inspected [README at 02e7a74](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/README.md) and the [evaluation guide](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/docs/guides/evaluation.md). README identifies Verified's 500 tasks and a Docker-based evaluator. Current source documents CLI changes and result caching by run_id/instance_id; use a unique evaluation ID for every arm/attempt/patch to avoid stale reuse. Pin package/CLI version and validate commands against that version, rather than copying old white-paper commands. Guide resource requirements are substantial; local image pulls and reference-score checks remain future work. Lite is useful development material but is not assumed disjoint from Verified. Audit actual IDs and repository overlap before assigning splits.

### RepoQA

Inspected [README at ae876de](https://github.com/evalplus/repoqa/blob/ae876deb1365dbf5a15b0533723c8ed123eee586/README.md) and [compute_score.py](https://github.com/evalplus/repoqa/blob/ae876deb1365dbf5a15b0533723c8ed123eee586/repoqa/compute_score.py). SNF requires the returned function to be the closest syntactic match among candidates and exceed the score threshold (documented default .8). Preserve the upstream score rather than inventing a correctness judge. The official input is a prepared dependency-ordered long context, not unrestricted full repository access. A tool-based arm must be restricted to the same supplied context and documented as an adapted setting. Validate parser/language coverage before comparison. Code identity/canonical-ID metrics are supplementary to upstream scoring, not a replacement. Comments-cleaning and context tokenization flags must match across arms.

### SWE-bench Pro

Inspected [README at 66f9276](https://github.com/scaleapi/SWE-bench_Pro-os/blob/66f92766bba642462d4bbe5479e83f91f9211862/README.md) and [V2 README](https://github.com/scaleapi/SWE-bench_Pro-os/blob/66f92766bba642462d4bbe5479e83f91f9211862/v2/README.md). The observed main README describes a 642-task, 11-repository V2 default and a legacy 731-task V1 configuration, with Harbor task packages and public images for V2. These are upstream claims, not our validation. Pin explicit config and dataset revision: a floating `load_dataset(..., split='test')` can silently change the study. Task bundles include reference solutions/verifiers, so mounted agent views must exclude them. Locked-protocol tooling and fresh-sandbox regrading are useful models for contamination controls. Audit asset access, image digests, release date and licenses at acquisition; results are pending.

### CrossCodeEval

Inspected [README at 40c68d2](https://github.com/amazon-science/cceval/blob/40c68d2b7ca2a8eae95d901ac80e6a540a84a53d/README.md). It ships baseline/retrieval/reference-assisted settings and instructs users to contact authors for raw data. The graph engine needs a comparable permitted corpus; precomputed reference-assisted contexts leak privileged information if used as a fair treatment input. Because raw repository availability has not been established, this is conditional rather than the first benchmark. README identifies Apache-2.0 for the project; separate underlying repository/data licensing still needs audit.

## MCP primary references

Inspected [MCP tools specification, 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) and [Python SDK README at 91941ed](https://github.com/modelcontextprotocol/python-sdk/blob/91941ed4d3985d59def99e090baa3f880c626cc8/README.md). The server will use the official SDK, tool discovery and structured schemas; transport interoperability is an engineering check, not an effectiveness result. Pin the installed SDK version in implementation; installed SDK existence alone does not validate a client connection or an agent's ability to call it.

## Search/selection record

Targeted search families: executable repository repair; cross-file semantic localization; context selection; MCP tool interoperability. Candidate primary repositories were fetched directly and compared against their stated task/evaluation setup. The guessed SWE-bench/SWE-QA README returned 404; it was not treated as verified evidence or selected. This is a focused benchmark audit, not an exhaustive survey. No external email was sent and no dataset was downloaded in this planning phase.

## Acquisition sentinel (future, must pass before trials)

Record immutable dataset revision and manifest checksum; permitted agent fields; licenses; image digests; official scorer version; pilot/confirmation task and repository overlaps; baseline/reference evaluation smoke test in an evaluator-only sandbox; required disk/CPU/network availability. Failed asset or scorer checks block trials. Reference success is evidence of a functioning evaluator, not an engine score.

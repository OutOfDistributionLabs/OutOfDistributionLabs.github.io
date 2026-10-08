# Small RepoClassBench MCP pilot

Out of Distribution Labs · October 7, 2026 (Pacific)

Replace the storage-blocked FeatureBench feasibility pilot with two smaller class-generation tasks requiring repository context. Pin RepoClassBench source/data and repository archive; retain FeatureBench failures rather than rewriting them. Task selection is in manifest, before agent outcomes.

Three arms: native Codex; same harness plus flat MCP; same harness plus graph-reranking MCP. `gpt-6.1-sol`, medium effort, pinned CLI, one fresh attempt each, 300-second wall ceiling. Randomized arm order seed 20261007 + task ordinal. Same public description, masked source, tool response cap and runtime. Six scheduled runs maximum. No new paid API credentials.

Adaptations: lightweight Python 3.11 environment replaces per-task Conda setup; retain source imports during class masking; hide all repository tests and Git history from agent, instead of offering iterative hidden-test feedback; judge the exact required test IDs with the official all-required-tests-pass rule. Linter feedback and full benchmark environment are not reproduced. Qualify gold and empty behavior before inference. Report every deviation and infrastructure failure.

This tests tool integration and functional outcomes for an existing prototype. The richer contract/invariant engine remains proposed. Two development tasks cannot establish a five-point effect, SOTA improvement, hundred-agent usefulness or benchmark-wide reliability. Unknown dollar cost is null, not zero. Preserve raw traces privately; publish only sanitized summaries.

Separate evaluator containers hold hidden tests/reference metadata; inference containers expose only masked source/public description and installed engine. No host evaluator or Docker socket mount. API-only network proxy prevents benchmark/reference downloads. Actual MCP calls, input/output/cached tokens, source snapshot hashes, deadline and result are recorded.

Every stage has an author self-review sentinel. Pages update every 60 seconds while active; ntfy uses 300 seconds, independently configurable.

Transport adaptation: Codex native MCP registration did not demonstrate tool use in readiness checks. Both tool arms therefore expose the same portable shell adapter, which starts the actual stdio MCP and makes SDK calls. Consultation of status and at least one query is instructed; native does not receive those instructions. This evaluates the complete tool-plus-instruction treatment, not the isolated effect of graph structure. Tool calls are independently logged. Only graph versus flat holds those instructions constant.

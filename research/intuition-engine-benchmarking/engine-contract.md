# Proposed intuition engine MCP contract

Design only; no server or effectiveness result exists in this project yet.

## Minimum intervention

An evidence-grounded repository adviser answers: **where should the agent inspect next, and why might a local view be insufficient?** It supplies ranked file/symbol evidence and typed dependency paths, with observed coverage limitations. The agent decides whether to follow it and uses its existing edit/test tools. It does not autonomously apply patches, allocate unbounded workers, certify correctness, or obtain hidden grading feedback.

## Internal representation

- Entity IDs include repository snapshot hash, path and source span; node kinds: file, module, symbol and supported contract/evidence records.
- Edge types distinguish contains, imports, calls (statically resolved only), implements, supports and abstracts. Unresolved dynamic dispatch/imports remain marked unknown rather than invented.
- Abstraction records include source member IDs, extraction method, revision and explicitly stated questions they are useful for; this is a heuristic retrieval view, not a mathematically certified Galois connection.
- Evidence paths connect returned recommendations to source snippets. Generated explanations are candidate claims and do not become accepted facts through fluent wording.
- Coverage estimates use parser success, unresolved edges, supported language count, corpus coverage and score disagreement. They are operational signals requiring calibration, not perfect knowledge of missing relevance. Low coverage broadens search or returns abstention within a fixed budget.
- Begin with lexical and deterministic structural features; do not add an engine-side LLM before measuring this version. Later generated summaries are a new costed, preregistered treatment.

Use language adapters with tree-sitter or audited parsers. A Python-only AST prototype may support Python development but cannot be called a five-language RepoQA engine. Full-language confirmation waits for parser coverage or freezes an explicitly narrowed task population.

## Tool surface shared by flat and full arms

MVP local stdio transport via the official Python MCP SDK. A later Streamable HTTP service is a deployment extension, not a prerequisite for local evaluation.

`intuition_query` input:

```json
{
  "snapshot_id": "sha256:...",
  "intent": "locate",
  "query": "Where is the retry idempotency behavior implemented?",
  "focus_ids": [],
  "max_candidates": 8,
  "response_token_budget": 2000
}
```

Allowed intents: `locate`, `explain_dependency`, `suggest_tests`, `broaden`. Enforce finite bounds and input schema. Both B and C accept the same fields; flat intent responses use lexical/symbol matching without graph reasoning, and state that limitation. Policy/config mode is set by the experiment controller outside the agent prompt; the API does not expose evaluator data.

Output schema:

```json
{
  "schema_version": "1",
  "snapshot_id": "sha256:...",
  "status": "ok",
  "candidates": [{"entity_id": "...", "path": "...", "span": [10, 25], "score": 0.6,
                  "evidence_ids": ["..."], "reason": "...", "relation_path": []}],
  "coverage": {"signals": ["unresolved_dynamic_calls"], "calibrated_probability": null},
  "recommended_action": "inspect",
  "abstention_reason": null,
  "usage": {"index_cpu_ms": 0, "query_cpu_ms": 0, "response_bytes": 0,
            "engine_model_input_tokens": 0, "engine_model_output_tokens": 0}
}
```

Numbers above illustrate schema, not measurements. Scores are ranking scores, not correctness probabilities. A missing calibrated model means probability is null. Status variants: `ok`, `insufficient_evidence`, `stale_snapshot`, `unsupported_language`, `budget_exceeded`. Empty results are admissible; errors are logged and count in deployment effects. Deterministic evidence IDs permit a bounded `intuition_evidence(snapshot_id, evidence_ids)` tool with the same response cap in B/C. A read-only `intuition_status()` reports snapshot and parser capabilities. Index creation/invalidation is controller-owned and fully costed, not a model-visible source of benchmark labels.

## Revision and side effects

On agent edits, compute a new working-tree snapshot or mark the old advice stale until reindexing. Invalidation of affected dependency neighborhoods is measured against full rebuild correctness. The MCP server sees a whitelisted task workspace only; reject paths escaping it and never mount evaluator storage. No cross-arm graph store, memory, semantic cache or transcript sharing. Preserve deterministic query logs and schema version.

## Harness adapter contract (future)

Inputs: task ID, permitted problem statement/context, snapshot checkout, arm configuration, fixed model/harness, seed/attempt index, resource ceilings. Outputs: sealed patch/function answer, structured trace, token/cost/cache report, MCP events, stopping reason. Evaluator annotates success afterward in separate storage. Identical runner schema works for Codex, Claude Code and other clients; differing capabilities are recorded and tested before use. Test tool discovery and at least one real agent-issued call; direct Python calls alone are plumbing checks.

## Implementation acceptance

Round-trip protocol test with a real MCP client; deterministic source localization fixture; language unsupported case; path escape and evidence-forgery rejection; stale snapshot after edit; response cap and graceful budget exhaustion; flat/full arms receive same corpus; telemetry matches independent accounting; no hidden fields; engine-off arm starts without the endpoint. Full implementation belongs to programme stage 05, after this methodology is reviewed.

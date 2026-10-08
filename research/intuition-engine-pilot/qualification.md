# Qualification sentinel

Out of Distribution Labs · author self-review · October 7, 2026 (Pacific)

## Advance: bounded non-LLM retrieval assay

Acquired the real RepoQA 2024-06-23 release. Its decompressed SHA256 is `bd3f7cab47283cdeccee20daea31af587b680cf8f9db192ab4da1037730cd6e2`, 71,510,991 bytes. Contrary to the project's README description of 500 cases/five languages, this release actually contains **600 cases across 60 repositories and six languages**, including Go. Each language contributes 100 cases. We evaluate this explicit release rather than silently discarding or miscounting Go.

The release repository's Apache-2.0 license is pinned by commit and hash. Underlying code remains third-party material: no dataset/source-code snippets are republished. Only code to fetch the existing release, manifests, measurements and IDs are included. Source extraction executes no repository code.

The actual upstream scoring definitions (pinned `ae876deb...`) are loaded after SHA256 verification, with only the audited scoring functions, parser query constants and enum selected from their AST. It is the upstream needle evaluator, not a new LLM judge. Six-language gold-answer and empty-answer sanity checks passed; exact scores and source hashes are in asset-register.json. Official outcome requires closest-needle identity and similarity >= .8.

**Adapted setting:** full release repository corpus, deterministic retrieval, no LLM and no official long-context prompt construction. This is not an official RepoQA leaderboard submission. Raw `content` is the only benchmark field passed into engine construction. Target identities, target code/spans, curated dependency/function lists and descriptions of other tasks are excluded from the index. Only the current query description is supplied at query time. Scoring uses labels afterward. The trusted deterministic ranker runs in-process; this is a code-level information boundary, not a hardened sandbox claim for an untrusted LLM.

Freeze before outcomes: same extracted entities, query and max ten candidates for scan/flat/graph; conservative 16,000-byte response allowance; no extra model calls. Lexical sort selects two development repositories per language (120 tasks), leaving eight per language (480 tasks) as a repository-disjoint descriptive evaluation. No hyperparameter tuning on those results; weights and tokenization are declared before running. Corpus/index construction and query CPU/wall time are measured. The original patch-resolution hypothesis remains untested.

## Hold: isolated Codex/repair experiments

Codex CLI version `0.159.0-alpha.3` was launched with a fresh ephemeral session, user config disabled, empty workspace and a no-tools readiness prompt. It failed before a completed turn: “Your access token could not be refreshed because you have since logged out or signed in to another account. Please sign in again.” No credential values were read or published. Authentication readiness is absent; native/flat/full Codex trials cannot be honestly reported.

Docker daemon 28.4.0 is available, but this does not establish SWE-bench image/scorer qualification, inference credentials, a priced model, or hidden-test isolation. This phase does not run unqualified benchmark repair code. Disk available at inspection was about 30 GB, below some upstream full-suite recommendations. The Codex adapter must additionally pass isolated actual tool calls and cost accounting before repair claims; unknown provider spend must never be labelled zero.

## Cadence

Project research.json controls page heartbeat 60 seconds, notification interval 300 seconds, checkpoint notifications false, completion notification true. Existing completed projects are not restarted. The periodic process runs only while the workspace is alive.

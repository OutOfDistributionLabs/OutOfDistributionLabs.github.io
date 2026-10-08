# Intuition engine: implementation and benchmark pilot

Out of Distribution Labs

## Scope confirmation
- Primary question and falsifiable hypotheses:
- Intended audience, domain and decision this work should inform:
- Theoretical, empirical or implementation emphasis:
- Authors, claims of novelty and known constraints:

## Review protocol
Record search date, exact query families, databases and inclusion/exclusion criteria. Prioritize primary sources; mark preprints, inaccessible full texts and version changes. This is a structured narrative review unless a reproducible systematic-review protocol is explicitly implemented. Maintain `sources.md` with citation, mechanism, relevance, limitation and access depth.

## Work sequence
1. Confirm scope, questions, evidence standards and outputs.
2. Read prior work; build a source/claim matrix; identify disagreements and gaps.
3. Develop definitions, propositions, proofs/counterexamples and/or architecture. Label established results versus proposals.
4. Evaluate appropriate claims. For theory, proofs and counterexamples are primary; use simulations only where useful. Report assumptions, baselines, seeds, raw data and limitations. Never fabricate an experiment or interpret simulated workers as deployed LLM agents.
5. Write and compile branded LaTeX. Audit citations, figures, tables, derivations, typography and epistemic status.
6. Publish PDF, source, bibliography and supporting artifacts. Check mobile progress page, links, repository push and deployment. Mark complete only after verification.

## Checkpoint rules
Each completed step must produce reviewable artifacts before `run.py step`. The runner updates progress, commits only project/explicit paths, pushes and sends ntfy. A background heartbeat publishes timestamp-only status updates and ntfy every two minutes while running. Pause the runner when work stops; completion stops it automatically. Heartbeats indicate an active runner, not proof that research is advancing.

## Evidence and claim ledger
For each substantive claim record its status: established result (source), proposed definition, derived proposition (proof), empirical result (reproduction), or hypothesis (test). Record alternatives and failure cases. Distinguish software checks from scientific validation. Clearly state unresolved assumptions.

## Artifacts
`research.json`, `status.json`, `progress.html`, `research-plan.md`, `sources.md`, `design.md`, optional `evaluation/`, `white-paper.tex`, `references.bib`, `white-paper.pdf`. Link the project from the homepage Research overlay.

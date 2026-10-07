# Research protocol

**Out of Distribution Labs · October 7, 2026**

## Working question
Can explicit, hierarchical abstractions provide a shared ontology graph that lets hundreds of narrow agents retrieve the right knowledge, coordinate changes, and preserve provenance without conflating relatedness with logical entailment?

## Working scope
Unless the project owner specifies otherwise, emphasize a formal architecture with implementable contracts; use research and knowledge synthesis as the running domain; author the white paper as Out of Distribution Labs. Micro-agents means bounded, specialized workers, not independently trained models. Do not assume that adding agents improves reasoning.

## Process and deliverables
1. Protocol: define questions, inclusion criteria, evidence categories and publication automation.
2. Literature: inspect primary papers and standards on abstraction, ontologies, graph retrieval, multi-agent coordination and distributed state; record what each source supports and what it does not.
3. Synthesis: develop a typed, polyhierarchical graph; formalize abstraction/refinement, provenance, coordination, schema governance and out-of-distribution handling. Explicitly distinguish the proposal from established results.
4. Evaluation: run a reproducible Python simulation at 100, 300 and 1,000 logical workers, with baselines and hierarchy-overlap stress tests. Measure candidate routing and coordination counts; avoid claiming LLM accuracy or production performance.
5. Manuscript: create branded LaTeX, verified bibliography, architecture figure, measured plots, limitations and an implementation/evaluation roadmap; compile the PDF and inspect it.
6. Publication: add PDF/source links to Research and the progress page; verify links, mobile layout, repository push and Pages deployment.

Every step updates `progress.html` and `status.json`, commits and pushes. `researchctl.py` also refreshes the progress timestamp and sends a notification every 120 seconds while active. Step notifications include the public progress URL. The heartbeat terminates after the final step. ntfy topic: `oodlabs` on ntfy.sh; messages contain only public research progress.

## Search and inclusion protocol
Search primary publisher/author pages, arXiv, ACL Anthology, OpenReview, W3C and official distributed-systems papers. Query families: (i) abstract interpretation / state abstraction / formal concept analysis, (ii) ontology hierarchy / OntoClean / OWL profiles / SKOS / SHACL / provenance, (iii) hierarchical GraphRAG / graph memory, (iv) multi-agent blackboard / contract net / LLM coordination, (v) CRDT / distributed consistency / knowledge conflict.

Include works that explain a mechanism or evaluation directly relevant to one of those families. Prefer original research, standards and authoritative specifications. Label preprints; distinguish conceptual proposals, formal results and empirical measurements. Exclude marketing claims, uncited benchmarks, and material that treats arbitrary embedding clusters as a verified ontology. This is a structured narrative review, not an exhaustive systematic review or a claim of literature completeness.

## Research questions
- Which abstraction relations are sound, which are task-dependent, and which must be reversible through evidence?
- How can multiple abstraction hierarchies coexist without `is-a`, `part-of` and causal edges becoming interchangeable?
- What execution and update contracts can many agents share?
- What does hierarchy improve in a controlled routing model, and where does it fail?
- How should unfamiliar evidence, schema mismatch and disagreement trigger refinement or abstention?

## Evidence and claim discipline
For each cited source record title, authors, publication/year, URL, relevant mechanism and limitation. All manuscript claims must be tagged conceptually as prior work, proposal, derivation, or our synthetic result. Do not describe the simulation as a deployed 100–1,000-agent LLM experiment. Report random seeds, raw results, configuration and baseline assumptions. State that provenance records attribution, not truth, and that OWL's open-world semantics differs from application validation.

## Publication artifacts
`progress.html`, `sources.md`, `design.md`, `evaluation/`, `white-paper.tex`, `references.bib`, `white-paper.pdf`, and the notification/publishing script. The homepage Research overlay links to this project without changing its visual composition.

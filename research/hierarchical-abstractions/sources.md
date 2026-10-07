# Primary-source literature map

Out of Distribution Labs · reviewed October 7, 2026. **22 sources.** Structured narrative review; no completeness or systematic-review claim. Exact arXiv versions are pinned. Full text was inspected where the access-depth field says so; failed/scanned access is recorded rather than represented as a full reading.

## Synthesis

The evidence supports a separation of semantic abstraction, information organization, retrieval and coordination. Software contracts and abstract interpretation provide stronger foundations than visual resemblance between graphs. Safe distributed accumulation requires a separate semantic admission policy. Agent frameworks and graph retrieval are useful mechanisms, not proofs that an ontology improves a hundred-agent coding workflow.

## Source/claim matrix

### cousot1977 — Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints
**Patrick Cousot and Radhia Cousot · 1977 · Foundational theory**

Primary source: https://cs.nyu.edu/~pcousot/COUSOTpapers/POPL77.shtml

Mechanism: Ordered abstract domains connect simplified program properties to concrete semantics; abstraction must preserve soundness, not merely resemblance.

Boundary: Applies when a concrete semantics and sound abstraction operators are supplied; arbitrary LLM summaries do not inherit these guarantees.

Access: Author summary and original bibliographic entry inspected. Venue/version: POPL.

### ganter1999 — Formal Concept Analysis: Mathematical Foundations
**Bernhard Ganter and Rudolf Wille · 1999 · Foundational theory**

Primary source: https://doi.org/10.1007/978-3-642-59830-2

Mechanism: Object-attribute contexts induce extents, intents and a concept lattice, supporting non-tree hierarchies.

Boundary: A lattice reflects the supplied incidence relation; it does not establish that observed attributes are correct or causally meaningful.

Access: Publisher description and metadata inspected; book not read in full. Venue/version: Springer.

### parnas1972 — On the Criteria To Be Used in Decomposing Systems into Modules
**David L. Parnas · 1972 · Software foundations**

Primary source: https://doi.org/10.1145/361598.361623

Mechanism: Module boundaries should be understood as design decisions rather than assumed to coincide with an execution sequence.

Boundary: A source-tree decomposition is not by itself an ontology or a scheduling proof.

Access: Publisher abstract/metadata and university bibliographic page inspected; attempted full-text URL returned 403. Venue/version: Communications of the ACM.

### liskov1994 — A Behavioral Notion of Subtyping
**Barbara H. Liskov and Jeannette M. Wing · 1994 · Software foundations**

Primary source: https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf

Mechanism: Behavioral subtyping constrains properties, specifications, invariants and histories; identical method names are insufficient.

Boundary: Ontology subsumption alone is not a proof of behavioral substitutability.

Access: Full paper inspected, especially introduction and specification conditions. Venue/version: ACM Transactions on Programming Languages and Systems.

### hoare1969 — An Axiomatic Basis for Computer Programming
**C. A. R. Hoare · 1969 · Software foundations**

Primary source: https://www.cs.cmu.edu/~crary/819-f09/Hoare69.pdf

Mechanism: Pre/postcondition reasoning provides a basis for explicit obligations on agent-produced program changes.

Boundary: A passing finite test set is not a universal program proof; termination needs a separate obligation.

Access: Scanned PDF and indexed primary-source passage inspected; local text extraction unusable. Venue/version: Communications of the ACM.

### ontoclean2009 — An Overview of OntoClean
**Nicola Guarino and Christopher A. Welty · 2009 · Ontology methodology**

Primary source: https://www.loa-cnr.it/Papers/GuarinoWeltyOntoCleanv3.pdf

Mechanism: Identity, rigidity and unity constrain taxonomic modeling; roles and stable kinds require different treatment.

Boundary: Metaproperties require domain judgment; this is not an automatic validator of arbitrary source-code concepts.

Access: Revised chapter full text inspected; original 2004 and revised 2009 author pages checked. Venue/version: Handbook on Ontologies, second edition.

### modularity2008 — Modular Reuse of Ontologies: Theory and Practice
**Bernardo Cuenca Grau and Ian Horrocks and Yevgeny Kazakov and Ulrike Sattler · 2008 · Ontology theory**

Primary source: https://www.cs.ox.ac.uk/oucl/work/yevgeny.kazakov/publications/journ/CueHorKazSat08Modularity_JAIR.pdf

Mechanism: Conservative extension and locality-based modules formalize safe vocabulary reuse.

Boundary: General conservative-extension problems can be undecidable in expressive settings; a neighborhood is not automatically a logical module.

Access: Full paper inspected, especially definitions and computability qualifications. Venue/version: Journal of Artificial Intelligence Research.

### owl2012 — OWL 2 Web Ontology Language Profiles (Second Edition)
**{World Wide Web Consortium} · 2012 · Normative standard**

Primary source: https://www.w3.org/TR/2012/REC-owl2-profiles-20121211/

Mechanism: EL, QL and RL trade expressive features for specific computational properties.

Boundary: Profile-specific complexity bounds do not imply low end-to-end latency; profiles are not interchangeable.

Access: Full text or normative specification inspected. Venue/version: None.

### semantics2012 — OWL 2 Web Ontology Language Direct Semantics (Second Edition)
**{World Wide Web Consortium} · 2012 · Normative standard**

Primary source: https://www.w3.org/TR/2012/REC-owl2-direct-semantics-20121211/

Mechanism: Model-theoretic entailment and consistency define the logical interpretation of OWL ontologies.

Boundary: Open-world reasoning must not be mistaken for application-level completeness or validation.

Access: Full text or normative specification inspected. Venue/version: None.

### skos2009 — SKOS Simple Knowledge Organization System Reference
**{World Wide Web Consortium} · 2009 · Normative standard**

Primary source: https://www.w3.org/TR/2009/REC-skos-reference-20090818/

Mechanism: Broader/narrower concepts and mapping relations support knowledge organization without asserting class equivalence.

Boundary: skos:broader is not declared transitive; broaderTransitive is separate, and broader does not mean OWL subclass.

Access: Full text or normative specification inspected. Venue/version: None.

### shacl2017 — Shapes Constraint Language (SHACL)
**{World Wide Web Consortium} · 2017 · Normative standard**

Primary source: https://www.w3.org/TR/2017/REC-shacl-20170720/

Mechanism: Shape validation checks a data graph against declared constraints.

Boundary: Conformance is validation under selected shapes, not proof of real-world truth or arbitrary logical consistency.

Access: Full text or normative specification inspected. Venue/version: None.

### prov2013 — PROV-O: The PROV Ontology
**{World Wide Web Consortium} · 2013 · Normative standard**

Primary source: https://www.w3.org/TR/2013/REC-prov-o-20130430/

Mechanism: Entities, activities, agents and derivation relations support interoperable provenance.

Boundary: Provenance records origin and process, not reliability, independence or truth.

Access: Full text or normative specification inspected. Venue/version: None.

### smith1980 — The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver
**Reid G. Smith · 1980 · Coordination foundations**

Primary source: https://ieeexplore.ieee.org/document/1675516

Mechanism: Task announcement, bidding and award separate task allocation from problem solving.

Boundary: A allocation protocol does not make worker outputs semantically correct.

Access: Publisher metadata and original-paper bibliographic record inspected; no complete IEEE full text. Venue/version: IEEE Transactions on Computers.

### nii1986 — Blackboard Systems: The Blackboard Model of Problem Solving and the Evolution of Blackboard Architectures
**H. Penny Nii · 1986 · Coordination foundations**

Primary source: https://doi.org/10.1609/aimag.v7i2.537

Mechanism: Shared structured problem state can coordinate specialized knowledge sources.

Boundary: Modern provenance and ontology governance are additional design obligations.

Access: Publisher abstract and bibliographic metadata inspected. Venue/version: AI Magazine.

### crdt2011 — Conflict-free Replicated Data Types
**Marc Shapiro and Nuno Pregui{\c c}a and Carlos Baquero and Marek Zawirski · 2011 · Distributed-state theory**

Primary source: https://inria.hal.science/inria-00609399v2

Mechanism: Join-semilattice state, monotone updates and eventual delivery support replica convergence.

Boundary: Convergence of records does not imply consistency of their logical interpretation.

Access: Full INRIA report RR-7687 inspected, including convergence assumptions. Venue/version: INRIA research report RR-7687.

### graphrag2024 — From Local to Global: A Graph RAG Approach to Query-Focused Summarization
**Darren Edge and Ha Trinh and Newman Cheng and Joshua Bradley and Alex Chao and Apurva Mody and Steven Truitt and Dasha Metropolitansky and Robert Osazuwa Ness and Jonathan Larson · 2024 · Graph retrieval preprint**

Primary source: https://arxiv.org/abs/2404.16130v2

Mechanism: Hierarchical community detection and summaries support global, query-focused summarization.

Boundary: Community membership is topical structure, not a certified subclass relation.

Access: Version 2 full HTML inspected; revised February 19, 2025. Venue/version: arXiv:2404.16130v2.

### hipporag2024 — HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models
**Bernal Jim{\'e}nez Guti{\'e}rrez and Yiheng Shu and Yu Gu and Michihiro Yasunaga and Yu Su · 2024 · Peer-reviewed graph retrieval**

Primary source: https://proceedings.neurips.cc/paper_files/paper/2024/hash/6ddc001d07ca4f319af96a3024f6dbd1-Abstract-Conference.html

Mechanism: Knowledge graphs and Personalized PageRank integrate evidence across retrieved passages.

Boundary: Associative relevance scores are not entailment or calibrated confidence.

Access: Full NeurIPS paper inspected. Venue/version: Advances in Neural Information Processing Systems 37.

### autogen2023 — AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation
**Qingyun Wu and Gagan Bansal and Jieyu Zhang and Yiran Wu and Beibin Li and Erkang Zhu and Li Jiang and Xiaoyun Zhang and Shaokun Zhang and Jiale Liu and Ahmed Hassan Awadallah and Ryen W. White and Doug Burger and Chi Wang · 2023 · Agent framework preprint**

Primary source: https://arxiv.org/abs/2308.08155v2

Mechanism: Customizable conversable agents combine language models, tools and human interaction.

Boundary: Conversation orchestration does not establish ontology consistency or favorable scaling.

Access: Version 2 full HTML inspected; cited version is the 2023 preprint. Venue/version: arXiv:2308.08155v2.

### mast2025 — Why Do Multi-Agent LLM Systems Fail?
**Mert Cemri and Melissa Z. Pan and Shuyi Yang and Lakshya A. Agrawal and Bhavya Chopra and Rishabh Tiwari and Kurt Keutzer and Aditya Parameswaran and Dan Klein and Kannan Ramchandran and Matei Zaharia and Joseph E. Gonzalez and Ion Stoica · 2025 · Failure-analysis preprint**

Primary source: https://arxiv.org/abs/2503.13657v3

Mechanism: MAST distinguishes specification/design, inter-agent alignment, and verification/termination failures.

Boundary: A failure taxonomy is diagnostic, not a guarantee that a proposed ontology removes those failures.

Access: Version 3 full HTML inspected; revised October 26, 2025. Venue/version: arXiv:2503.13657v3.

### scaling2025 — Towards a Science of Scaling Agent Systems
**Yubin Kim and Ken Gu and Chanwoo Park and Chunjong Park and Samuel Schmidgall and A. Ali Heydari and Yao Yan and Zhihan Zhang and Yuchen Zhuang and Yun Liu and Mark Malhotra and Paul Pu Liang and Hae Won Park and Yuzhe Yang and Xuhai Xu and Yilun Du and Shwetak Patel and Tim Althoff and Daniel McDuff and Xin Liu · 2025 · Agent-scaling preprint**

Primary source: https://arxiv.org/abs/2512.08296v3

Mechanism: Controlled comparisons report task-dependent coordination effects and limitations of adding agents.

Boundary: These benchmark configurations do not establish the behavior of hundreds of agents using the proposed graph.

Access: Version 3 full HTML inspected; revised April 8, 2026. Venue/version: arXiv:2512.08296v3 (2026 revision).

### sweagent2024 — SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering
**John Yang and Carlos E. Jimenez and Alexander Wettig and Kilian Lieret and Shunyu Yao and Karthik Narasimhan and Ofir Press · 2024 · Peer-reviewed software agents**

Primary source: https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html

Mechanism: Agent-computer interfaces expose repository navigation, editing and test execution as useful bounded actions.

Boundary: Single-system benchmark results do not validate this ontology-based multi-agent architecture.

Access: Full NeurIPS paper inspected. Venue/version: Advances in Neural Information Processing Systems 37.

### swebench2024 — SWE-bench: Can Language Models Resolve Real-World GitHub Issues?
**Carlos E. Jimenez and John Yang and Alexander Wettig and Shunyu Yao and Kexin Pei and Ofir Press and Karthik Narasimhan · 2024 · Peer-reviewed software benchmark**

Primary source: https://openreview.net/forum?id=VTF8yNQM66

Mechanism: Repository-level issue resolution evaluated through executable tests offers a future testbed.

Boundary: Test-defined success is not comprehensive semantic correctness; contamination and task selection require controls.

Access: Original primary-paper abstract and indexed ICLR paper inspected. Venue/version: International Conference on Learning Representations.

## Exact query families used

- Cousot Cousot 1977 abstract interpretation unified lattice model static analysis original paper
- Guarino Welty OntoClean overview ontology taxonomies rigidity identity unity
- Formal concept analysis Ganter Wille 1999 concept lattice Springer
- W3C OWL 2 profiles EL QL RL recommendation 2012
- W3C SKOS reference broader transitive hierarchical mapping 2009
- W3C SHACL recommendation 2017 PROV O 2013
- Ontology modularity conservative extension description logics 2007 2008 paper
- Parnas 1972 criteria used decomposing systems modules original paper
- Liskov Wing 1994 behavioral notion subtyping original paper
- Hoare axiomatic basis computer programming 1969 paper
- Multi agent systems contract net protocol blackboard Hearsay II original paper
- Shapiro Preguica Baquero Zawirski conflict free replicated data types 2011 INRIA
- From Local to Global Graph RAG query focused summarization 2404.16130
- HippoRAG NeurIPS 2024 knowledge graph personalized PageRank paper
- AutoGen enabling next gen LLM applications multi agent conversation 2308.08155
- Why Do Multi-Agent LLM Systems Fail 2025 MAST paper
- Towards a Science of Scaling Agent Systems 2025 arxiv
- SWE agent agent computer interfaces software engineering 2405.15793
- SWE bench can language models resolve real world github issues ICLR 2024
- 2026 ontology graph software engineering multi agent abstraction

## Screening notes

State-abstraction MDP work and CodeOntology were searched as adjacent areas but not relied on for propositions because the inspected material was insufficient to support a precise claim in this scope. Broader source-code knowledge graphs, ontology learning and agent memory are not exhaustively covered. Full copyrighted texts were inspected in temporary local storage and are not redistributed. Citation records and our own annotations are published. No quantitative results from prior papers are pooled or presented as directly comparable to our simulation.

# Formal synthesis and architecture

Out of Distribution Labs · theoretical proposal · October 7, 2026

## Thesis and epistemic status

An ontology graph can provide a shared semantic interface for micro-agents when its abstraction edges state preservation obligations, its claims retain provenance and revision scope, and its execution protocol keeps conjecture separate from admitted facts. A hierarchy is useful infrastructure, not evidence that adding agents improves software correctness. The propositions below are elementary consequences of stated assumptions; no mathematical novelty is claimed. The architectural synthesis is a proposal, not an evaluated production system.

## 1. Four structures, four meanings

1. **Semantic abstraction:** an ordered family of representations with interpretation maps and specified preservation properties.
2. **Ontology:** a typed vocabulary and axioms about kinds, instances, properties and relations.
3. **Retrieval organization:** communities, summaries, embeddings and indexes that select candidate evidence.
4. **Coordination:** task dependencies, capabilities, leases and admissible effects.

They may share identifiers and graph storage, but their edges are not interchangeable. `subClassOf`, `partOf`, `calls`, `dependsOn`, `summarizes`, `derivedFrom` and `assignedTo` must retain different types and inference rules. An embedding cluster does not become a superclass because it has a parent.

## 2. Concrete software worlds and abstract domains

Fix a repository revision r, environment e and specification version v. Let X_(r,e,v) be possible concrete software states/traces, including code and execution behavior. A concrete knowledge state is S in C = P(X), ordered by inclusion. More inclusion means less precision: more worlds remain possible. An abstract domain A has an order ≤_A and monotone maps alpha: C→A and gamma: A→C with alpha(S)≤a iff S⊆gamma(a). This Galois connection gives S⊆gamma(alpha(S)). A sound abstract transformer F# over-approximates a concrete F when F(gamma(a))⊆gamma(F#(a)). These guarantees require supplied semantics; an LLM-written description has no such guarantee merely because it is shorter.

For composable domains A0,A1,A2 with Galois connections (alpha01,gamma10) and (alpha12,gamma21), composition is a Galois connection because alpha12(alpha01(x))≤z iff alpha01(x)≤gamma21(z) iff x≤gamma10(gamma21(z)). This is the **composition proposition**. It justifies only registered, compatible abstraction paths. A diagram of code→module→service→business goal does not meet its premises automatically.

**Example:** intervals abstract concrete integer values; alpha({2,4})=[2,4]. The interval is not a claim that 3 was observed. A resource-effect domain records “may acquire lock” rather than “always acquires lock.” An `AuthService` class is an ontology classification, while a service-level trace abstraction is a semantic map. Store the distinction explicitly.

## 3. Task-relative sufficiency and a necessary lower bound

For a set Q of Boolean predicates on concrete worlds, define x~_Q y iff every q in Q has q(x)=q(y). An abstraction h:X→Z is **Q-sufficient** if every q factors through h: there exists q-bar with q=q-bar∘h. It need not form a Galois connection to be task-sufficient.

**Separation proposition:** If q(x)≠q(y) for some q in Q, any Q-sufficient h must have h(x)≠h(y). Proof: otherwise q-bar(h(x))=q-bar(h(y)), contradicting the difference. Thus collapsing distinct states across the question boundary loses necessary information. An abstraction cannot simultaneously be arbitrarily compact and preserve every possible question.

**Software counterexample:** two cache implementations return identical outputs under single-threaded tests; one invalidates atomically and one permits stale reads during a race. A summary that erases interleaving is insufficient for the question “can a reader observe stale data after invalidation?” Passing tests supports only the tested conditions, not a universally valid superclass contract.

For a finite dataset, the quotient X/~_Q is the coarsest partition sufficient for Q. Defining it does not make it computable over arbitrary program traces. Maintain multiple views for different Q, and refine a view when a counterexample separates worlds it previously identified.

## 4. Typed, contextual, polyhierarchical graph

Let G_r=(V,E,tau,kappa,P) be a graph snapshot at revision r. tau gives node/edge sorts. kappa assigns context (revision, environment, specification, viewpoint). P records provenance links. Logical content T_r is a separately admitted set of axioms. Candidate assertions are reified claim records and do not enter T_r by mere insertion into V.

Suggested node sorts: Artifact (file, symbol, patch, build), Concept (logical class), Requirement, Contract, Observation (test outcome, static-analysis report), Claim, Task, AgentCapability and Context. Predicate signatures specify allowed source/target sorts and inference behavior. Keep taxonomy a finite DAG after collapsing declared equivalent classes; general graph relations may be cyclic. Acyclicity is a chosen application invariant, not a claim that every ontology or SKOS graph must be acyclic.

Polyhierarchy supports a function both as part of `PaymentService` and as an instance of `IdempotentOperation`, while its security viewpoint concerns credentials. `partOf` is not `subClassOf`; changing a module boundary is not retyping the function. Pin identifiers to repository revision and stable symbol identity; preserve rename/move lineage as claims rather than blindly equating every path.

## 5. Certificates and inference boundaries

Every promoted abstraction edge should carry: source/target domain, context, abstraction/refinement maps or a weaker declared relationship, preserved question family Q, witness or proof obligation, validation method, source hashes, and expiry/invalidation rules. “Proof-backed,” “validated on selected tests,” and “unverified summary” are different evidence statuses.

A class implication A⊆B preserves universal properties of B when applied to A, under the same interpretation/context. It does not transfer arbitrary existential claims to A; B can have one verified instance while A has none. It also does not justify service behavior from object classification. Behavioral substitutability requires preconditions, postconditions, invariants and relevant history constraints (Liskov/Wing), not just compatible names.

OWL's open-world semantics supports entailment, while SHACL checks selected data constraints. A minimum-count shape can fail even though the absent edge is not logically false under OWL. PROV records derivation, not truth. Use separate registries for ontology conformance, semantic validity, empirical validation and access authorization.

## 6. Coordination and distributed admission

Worker contract a=(role,read_signature,write_scope,tools,preconditions,output_shapes,verification_policy,budget). A worker reads an immutable snapshot, selects relevant concepts, expands to grounded artifacts, runs a bounded action and proposes a delta with evidence. A deterministic admission pipeline checks authorization, schema, revision preconditions and semantic conflicts before publishing a new accepted snapshot. Textual consensus is not proof.

Use append-only candidate claim records and provenance as replicated sets; use a controlled accepted projection for non-monotone choices, identity merges and schema edits. An observed-remove/tombstone design can retract visibility without pretending that deletion erases history. Never assert that arbitrary ontology merges are safe CRDT operations.

**Merge counterexample:** T0 declares A and B disjoint. Delta1 asserts A(a); Delta2 asserts B(a). Each extension of T0 is satisfiable in isolation, but their union is not. Both records can converge correctly as data while the interpreted theory becomes inconsistent. Therefore convergent storage and semantically safe admission are independent obligations.

If workers read overlapping sets and write shared symbols, snapshot validation must include relevant read dependencies, not only identical file writes. Schema extensions can change entailments outside an edited region. Conservative extension over signature Sigma would preserve all old Sigma entailments, but a full test may be undecidable in expressive logics. Use restricted fragments, locality modules, bounded regression query suites and explicit scope limits.

### Restricted safe parallel extension

If T1=T∪Delta1 and T2=T∪Delta2 are each model-conservative extensions of T on the same domains, their private signatures are disjoint, and each delta mentions only its own private vocabulary plus T's signature, then their union is model-conservative over T. Every base model has two expansions; combine their disjoint private interpretations while leaving the shared base interpretation fixed. Each delta still sees its original expansion, so both hold. This elementary proposition is a sufficient condition, not a claim that ordinary agent edits satisfy it. Overlapping identities, contract updates and arbitrary instance assertions require stronger governance.

## 7. Scaling and routing claims

A complete directed all-to-all notification graph contains N(N−1) edges. If a declared routing policy sends each update to at most k workers, directed deliveries per update are ≤k. This is an arithmetic bound on a policy, not a general theorem that ontology use turns coordination into O(Nk), since indexing, selection, validation, graph maintenance and data replication have their own costs.

For balanced routing views, selected buckets contain approximately N*b/B workers when N workers are distributed across B buckets and b buckets are selected. This assumption fails under skew, overlap, cross-module concerns and broad tasks. A flat inverted index with the same membership often has the same candidate count. Evaluate hierarchy against it, not merely against a weak broadcast baseline.

## 8. Out-of-distribution handling

OOD includes an unfamiliar API, unseen relation, unrepresented effect, stale revision, incompatible environment, or evidence that contradicts a contract. Novel embeddings alone do not calibrate OOD confidence. Distinguish “outside current schema,” “unsupported inference,” “low evidence coverage” and “logical conflict.” Suspend only affected accepted claims, retain witnesses, and propose a scoped refinement. Require an evidence-driven split rather than immediately introducing a global superclass.

## 9. Running workflow

A request to make retry behavior safe under concurrent payment processing produces: requirement nodes, call/effect analysis, revision-scoped behavior claims, a counterexample task, proposed patch, test/static-analysis observations, admission decision and new snapshot. Parser, contract, security, test, patch and review micro-agents own different capabilities. They may reason through the same ontology but act through separate authorization scopes. Hundreds of worker records can exist while only a small bounded cohort executes a task.

## 10. What the simulation can test

The supporting simulation will compare broadcast, a flat inverted index, a single-view hierarchy and a guarded multi-view hierarchy on known software-capability labels. It will record candidate size, recall of eligible logical workers, structural routing operations and modeled—not measured—per-worker delivery cost. Stress cross-cutting capabilities and random requests spanning modules. Ground truth uses generated labels; no LLM, code patch success, retrieval semantics or wall-clock deployment throughput is evaluated.

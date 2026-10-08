# Runtime qualification outcome

Out of Distribution Labs · October 7, 2026 (Pacific)

**No FeatureBench agent attempts ran. No valid task scores were produced.**

| Check | Outcome | Interpretation |
|---|---|---|
| Fresh pinned Codex/model readiness | Passed | Authentication works; not a benchmark trial. |
| Dataset/source pinning | Passed | Fast v1.1 has 100 rows; manifest selects two lv1 instances before agent outcomes. |
| Original multilayer image pulls | Cancelled | VFS cumulative copies exceeded most of the 32 GB workspace. |
| Full flattened Metaflow image | Imported, then removed | 17.7 GB merged filesystem; not enough room for working VFS copies. |
| Cache-only filter, first attempt | Rejected | A retained conda hard link depended on removed cached payload. Partial derived image removed. |
| Revised compact import | Imported, then removed | 13.6 GB; 4.08 GB of cache/history removed, with required hard-link bytes/aliases retained. Unqualified runtime. |
| Official reference patch | Infrastructure invalid | Container creation failed with `no space left on device`; tests never ran. |
| Official empty patch | Infrastructure invalid | Container creation failed; not evidence that the scorer passed its negative-control check. |
| Astropy control qualification | Not attempted | Kept in the manifest; not replaced or counted as failed software behavior. |
| Native/flat/graph agent comparison | Not attempted | Qualification sentinel holds inference. |

The official harness emits completed=true/resolved=false on its infrastructure error reports. Our normalized records retain those raw flags but set task resolution to **null**, because no tests executed. A disk failure is not an unresolved feature score.

Docker VFS can require the image plus init and writable filesystem copies. The revised preflight reserves two additional image-size copies and a safety margin before either evaluator or agent creation. Container cloning exhausted the disk despite a successful import. Cleanup removed all registered task images/containers; ordinary Docker inventory is now empty, although roughly 19 GB remains occupied in the filesystem. We did not modify daemon-managed orphan directories or restart the managed daemon. Environment recovery is appropriate before retrying.

To resume, provide a fresh workspace with **128 GB storage for serial derived-image preparation/evaluation**, or a supported Docker setup using a copy-on-write driver such as overlay2. This is a capacity recommendation, not a guarantee about every future benchmark. Keep the same task manifest and one-attempt protocol; rerun gold/empty qualification from clean output directories. Do not run agents until gold passes, negative controls behave correctly, and hidden-asset/network probes pass.

The adapter and orchestrator are implemented and syntax-checked, but their full container/MCP/inference path remains untested. Current unit checks cover filter payload preservation, unsafe-link rejection and publisher behavior. Unknown provider cost remains null. The contract-reasoning engine is still proposed; the planned pilot compares the existing lexical MCP as a feasibility baseline.

# Measured outcomes

All six planned scored cells completed. One initial native attempt was interrupted by an account usage limit and retried unchanged after the user requested another try. It is excluded from solution scoring; its trace remains registered.

| Task | Native | Flat MCP | Graph MCP |
|---|---:|---:|---:|
| Pydicom Sequence | 10/13; fail | 10/13; fail | 10/13; fail |
| Requests rEQueSt | 44/44; pass | 44/44; pass | 44/44; pass |

Each arm resolves 1/2. Both paired resolution contrasts are zero. There is no measured success improvement in this pilot.

| Arm | Inference seconds, sum | Input tokens | Cached input | Output tokens | Logged adapter operations |
|---|---:|---:|---:|---:|---:|
| A | 90.00 | 213202 | 176384 | 3327 | 0 |
| B | 108.53 | 192451 | 158848 | 3822 | 6 |
| C | 109.26 | 191729 | 169088 | 3503 | 6 |

A native; B flat; C graph. Each tool cell consulted status, query and evidence. The operation log counts requested operations (three per cell); each query/evidence SDK invocation additionally calls status to obtain a snapshot, so three logged operations involve five MCP tool requests. All call responses succeeded. These adapter operations are not direct native CLI MCP events.

All Pydicom failures concern exact exception message wording; the requested exception types were raised. This is an incidental contract-compatibility failure, not evidence of deep cross-module reasoning inadequacy. Required tests remain scored unchanged.

The valid-run totals exclude setup, readiness probes and the quota-interrupted attempt. Its spend is unknown. Provider price is unknown; cost is null, not zero. Cached counters are retained; input counts can accumulate across turns. These are descriptive timings, not significant efficiency effects.

Two convenience-selected tasks, one model, one attempt per cell and adapted environments cannot establish current SOTA weakness, population improvement or hundred-agent benefit. The next study should select substantive dependency/invariant failures before confirmatory benchmarking.

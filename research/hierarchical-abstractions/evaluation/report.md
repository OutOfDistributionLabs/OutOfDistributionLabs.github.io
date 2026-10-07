# Synthetic routing evaluation

Out of Distribution Labs · October 7, 2026

## Purpose

Illustrate the consequences of membership completeness and hierarchy overlap; not evaluate language-model reasoning or software correctness. Python standard library; no external data. Run `python simulate.py` from this folder or invoke it by path. Default: 20 seeds (0–19), 300 queries per seed, 100/300/1,000 logical workers, 16 modules × 4 skills, secondary membership probability 0/.25/.5.

## Baselines and stress tests

Broadcast includes every worker. Flat-index unions all known exact-label memberships. Primary-hierarchy traverses a grouped 16-module hierarchy but retains only primary memberships. Guarded-multiview includes secondary memberships and falls back to broadcast when an explicit, perfectly known coverage flag is false. Local requests select one module/skill; cross-cutting requests select four modules with one skill; coverage-gap requests independently mark each label incomplete with probability .1. A flat index with equivalent complete memberships is a deliberately strong baseline: hierarchy should not receive credit for its indexing benefit.

| N | Secondary membership | Scenario | Strategy | Candidates, mean ± seed SD | Eligible-worker recall | Index visits |
|---:|---:|---|---|---:|---:|---:|
| 100 | 0.50 | local | broadcast | 100.00 ± 0.00 | 1.000 | 0.00 |
| 100 | 0.50 | local | flat-index | 2.67 ± 0.16 | 1.000 | 1.00 |
| 100 | 0.50 | local | primary-hierarchy | 1.76 ± 0.11 | 0.658 | 4.00 |
| 100 | 0.50 | local | guarded-multiview | 2.67 ± 0.16 | 1.000 | 5.00 |
| 100 | 0.50 | cross-cutting | broadcast | 100.00 ± 0.00 | 1.000 | 0.00 |
| 100 | 0.50 | cross-cutting | flat-index | 9.28 ± 0.31 | 1.000 | 4.00 |
| 100 | 0.50 | cross-cutting | primary-hierarchy | 6.31 ± 0.14 | 0.680 | 11.91 |
| 100 | 0.50 | cross-cutting | guarded-multiview | 9.28 ± 0.31 | 1.000 | 15.91 |
| 100 | 0.50 | coverage-gap | broadcast | 100.00 ± 0.00 | 1.000 | 0.00 |
| 100 | 0.50 | coverage-gap | flat-index | 2.64 ± 0.12 | 1.000 | 1.00 |
| 100 | 0.50 | coverage-gap | primary-hierarchy | 1.75 ± 0.09 | 0.663 | 4.00 |
| 100 | 0.50 | coverage-gap | guarded-multiview | 11.95 ± 3.98 | 1.000 | 5.00 |
| 300 | 0.50 | local | broadcast | 300.00 ± 0.00 | 1.000 | 0.00 |
| 300 | 0.50 | local | flat-index | 7.07 ± 0.17 | 1.000 | 1.00 |
| 300 | 0.50 | local | primary-hierarchy | 4.69 ± 0.13 | 0.664 | 4.00 |
| 300 | 0.50 | local | guarded-multiview | 7.07 ± 0.17 | 1.000 | 5.00 |
| 300 | 0.50 | cross-cutting | broadcast | 300.00 ± 0.00 | 1.000 | 0.00 |
| 300 | 0.50 | cross-cutting | flat-index | 27.73 ± 0.59 | 1.000 | 4.00 |
| 300 | 0.50 | cross-cutting | primary-hierarchy | 18.80 ± 0.21 | 0.678 | 11.91 |
| 300 | 0.50 | cross-cutting | guarded-multiview | 27.73 ± 0.59 | 1.000 | 15.91 |
| 300 | 0.50 | coverage-gap | broadcast | 300.00 ± 0.00 | 1.000 | 0.00 |
| 300 | 0.50 | coverage-gap | flat-index | 7.03 ± 0.18 | 1.000 | 1.00 |
| 300 | 0.50 | coverage-gap | primary-hierarchy | 4.67 ± 0.14 | 0.663 | 4.00 |
| 300 | 0.50 | coverage-gap | guarded-multiview | 38.71 ± 12.31 | 1.000 | 5.00 |
| 1000 | 0.50 | local | broadcast | 1000.00 ± 0.00 | 1.000 | 0.00 |
| 1000 | 0.50 | local | flat-index | 23.63 ± 0.45 | 1.000 | 1.00 |
| 1000 | 0.50 | local | primary-hierarchy | 15.73 ± 0.15 | 0.666 | 4.00 |
| 1000 | 0.50 | local | guarded-multiview | 23.63 ± 0.45 | 1.000 | 5.00 |
| 1000 | 0.50 | cross-cutting | broadcast | 1000.00 ± 0.00 | 1.000 | 0.00 |
| 1000 | 0.50 | cross-cutting | flat-index | 92.67 ± 0.92 | 1.000 | 4.00 |
| 1000 | 0.50 | cross-cutting | primary-hierarchy | 62.65 ± 0.56 | 0.676 | 11.92 |
| 1000 | 0.50 | cross-cutting | guarded-multiview | 92.67 ± 0.92 | 1.000 | 15.92 |
| 1000 | 0.50 | coverage-gap | broadcast | 1000.00 ± 0.00 | 1.000 | 0.00 |
| 1000 | 0.50 | coverage-gap | flat-index | 23.56 ± 0.42 | 1.000 | 1.00 |
| 1000 | 0.50 | coverage-gap | primary-hierarchy | 15.67 ± 0.21 | 0.664 | 4.00 |
| 1000 | 0.50 | coverage-gap | guarded-multiview | 132.09 ± 44.80 | 1.000 | 5.00 |

## Interpretation

Flat indexing and complete multi-view hierarchy produce exactly the same candidate sets when no fallback occurs. Overlap causes recall loss only for the primary-only strategy; this ablation demonstrates the cost of missing memberships, not an intrinsic failure of all hierarchies. Perfectly detected coverage gaps restore recall through broadcast and increase the candidate budget sharply. The simulation supports neither a token-savings claim nor improved patch quality.

## Uncertainty and limitations

± values are sample standard deviations of seed-level means, not confidence intervals. Ground truth is generated from the same labels available to the complete index. Empty eligible sets are skipped for recall, and retained query counts are published. Hardware timing, graph building costs, stale state, actual message bytes, parser errors and LLM behavior are not measured. Coverage detection is an oracle in this experiment. Full parameters, all 2,160 seed/strategy rows and aggregate results are in `raw-results.csv` and `results.json`.

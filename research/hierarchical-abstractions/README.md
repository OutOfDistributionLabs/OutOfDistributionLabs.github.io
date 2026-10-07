# Hierarchical abstractions as a basis for ontology graphs

**Out of Distribution Labs · White paper 01 · Version 1.0 · October 7, 2026**

Theoretical foundations for ontology graphs shared by hundreds of software-engineering micro-agents. The paper separates semantic abstraction, ontological classification, retrieval and coordination, and develops contextual domains, question-relative sufficiency, typed claims and controlled admission. It includes three elementary propositions, software/distributed-merge counterexamples, a proposed architecture, finite checks and a reproducible routing simulation. It does not claim mathematical novelty or a production hundred-agent LLM deployment.

- [White paper PDF](white-paper.pdf)
- [Progress and checkpoint history](progress.html)
- [LaTeX source](white-paper.tex) and [verified bibliography](references.bib)
- [Research protocol](research-plan.md), [22-source literature map](sources.md), [source register](source-register.json), [formal design notes](design.md)
- [Synthetic evaluation](evaluation/report.md), [raw data](evaluation/raw-results.csv), [aggregate data](evaluation/results.json), [finite checks](evaluation/formal-checks.json)
- [Reusable process](../PROCESS.md), shared runner and templates in `tools/research/` at repository root

## Reproduce

From this directory:

```sh
python evaluation/simulate.py
python evaluation/check_formal.py
python evaluation/plot.py
latexmk -pdf -interaction=nonstopmode -halt-on-error white-paper.tex
```

Simulation/checking need Python 3.9+ and its standard library. Plotting needs Matplotlib. The manuscript needs a TeX Live installation containing pdfLaTeX, BibTeX, latexmk, Helvetica/Latin Modern fonts, natbib, TikZ, booktabs, tabularx, titlesec, enumitem, fancyhdr, microtype and xurl. Parameters and seeds are fixed in the scripts and published JSON. Source metadata records exact arXiv versions and primary URLs; copyright-protected source texts are not redistributed.

The simulation reports generated-label candidate routing, not model accuracy, tokens, wall-clock throughput or software correctness. Complete flat indexing is a strong baseline and matches complete hierarchy without fallback. Omitted memberships reduce recall; oracle coverage guards restore it by expanding the cohort. Finite checks instantiate the stated definitions but do not replace the general proofs.

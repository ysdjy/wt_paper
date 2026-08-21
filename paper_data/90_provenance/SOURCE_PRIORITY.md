
# Source priority

1. Later dedicated authoritative audits override older summaries and plot exports. Fig.4 uses only `figures/fig4_ablation/AUTHORITATIVE_A1_A6.csv`.
2. `final_statistical_evidence/` is authoritative for PHM2010 D1 bootstrap/common-universe and D1/D2/D3 transfer results.
3. Dataset-specific final exports: NASA `nasa_dcpsr_results_stageaware_opt` original split; Mendeley `FINAL_REPORT`, `04_overall_comparison`, `05_generalization`, `06_ablation`, and `07_semantic_consistency`.
4. Audited figure manifests are source indexes; data are copied from the manifest's original source path.

Git tracking is provenance metadata, not an authority criterion: local ignored final files are allowed but recorded as `git_tracked=false`.

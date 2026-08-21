
# Manuscript → canonical data map

The third cross-machine dataset's formal name is "Multivariate time series data of milling processes with varying tool wear and machine tools" (short name MTW-CM), hosted on Mendeley Data. `03_MENDELEY_CROSS_MACHINE` below is a retained folder path only.

| Manuscript item | Claim/Table/Figure | Canonical data file | Status |
|---|---|---|---|
| New Fig.1 | D1 final 9-method evidence | `07_figure_ready/fig1/` | MAPPED |
| New Fig.2 | D1/D2/D3 robustness | `07_figure_ready/fig2/` | MAPPED |
| New Fig.3 | PHM/NASA/MTW-CM cross-dataset effects | `07_figure_ready/fig3/` | MAPPED |
| New Fig.4 / current Table 12 replacement | A1-A6 ablation | `01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv` | MAPPED_WITH_CORRECTION |
| New Fig.5 | lifecycle q/probability/hidden representation | `07_figure_ready/fig5/` | MAPPED |
| `投稿版20260709` Table 8 | legacy B1-B12 main table | `01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv` for current 9-method replacement | REQUIRES_MANUSCRIPT_UPDATE |
| `投稿版20260709` Tables 9-10 | older D1/D2/S1/S2 protocol | no current canonical replacement for S1/S2 | UNRESOLVED/LEGACY_PROTOCOL |
| `投稿版20260709` Table 11 | NASA N1-N4 | `02_NASA/task_level_results.csv` | MAPPED; verify manuscript values against original split |
| `投稿版20260709` Table 12 | stale A1-A6 values | `01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv` | STALE; MUST UPDATE |
| `投稿版20260709` Tables 13-14 | q and wear semantics | `01_PHM2010/04_semantics/` and `07_figure_ready/fig5/` | MIXED/REQUIRES_UPDATE |

The PDF and DOCX versions contain the same stale Table 12 and Table 13 values as `main.tex`; images/PDF were not used to transcribe numbers. Manuscript-only synchronization items (MS-001..MS-003) are tracked separately in `90_provenance/MANUSCRIPT_SYNC_STATUS.csv`, not in `90_provenance/UNRESOLVED_ITEMS.csv`.

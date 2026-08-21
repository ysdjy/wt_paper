# Figure Report

## Workflow and export contract

- Nature Figure skill used: `nature-figure`
- Backend: Python only (`matplotlib`, `pandas`, `numpy`, `scipy`)
- Archetypes: quantitative grid (Figs. 1, 2, 4); schematic-led mixed composite (Fig. 3); asymmetric mixed-modality figure with a ternary hero panel (Fig. 5)
- Final width: approximately 183 mm (7.2 in) for a full-width two-column layout
- Export: editable SVG, Type-42-font PDF, and 600-dpi PNG
- Typography: Arial/Helvetica/DejaVu Sans fallback, 7–9 pt effective journal sizing
- Image integrity: no photographic panels, crops, local contrast changes, or synthetic observations

## Core conclusions and evidence hierarchy

### Figure 1

Core conclusion: on the D1 common universe, DC-PSR maintains near-backbone discrimination while reducing probability-sequence roughness. The forest plot is the primary statistical evidence; the Pareto map and controlled paired comparison provide trade-off and mechanism context. Comparable parameter counts were incomplete, so marker area is deliberately not used.

### Figure 2

Core conclusion: competitive position changes across unseen target conditions and must be read task by task rather than through a pooled mean. Colors encode within-task relative scores, never absolute Accuracy. All D1/D2/D3 results and unfavorable cells are retained.

### Figure 3

Core conclusion: degradation-consistent inference preserves some middle-state and smoothness benefits as domain shift increases, but absolute discrimination gains are not universal. NASA Accuracy is slightly negative relative to the backbone; D2-M and D3-M negative Accuracy deltas remain visible. Cross-dataset uncertainty structures differ (NASA original N1–N4 versus cross-machine five-seed means), so the heatmap is descriptive and controlled, not a pooled significance analysis.

### Figure 4

Core conclusion: ordered inference gives the strongest smoothing but sacrifices discrimination, whereas final fusion partially restores discrimination for a balanced configuration. A2 (Raw+Fine) and A3 (Raw+Prior) are parallel variants rather than nested sequential additions; therefore path-node effects are shown against A1, not interpreted as isolated adjacent causal increments.

### Figure 5

Core conclusion: the real C6 lifecycle outputs form an ordered trajectory in probability space and retain continuous wear semantics. The PCA panel uses existing real 64-dimensional hidden representations and deterministic SVD only; it does not retrain the network or fit a label-driven embedding.

## Unified visual system

The fixed method palette and markers requested in the task are defined once in `scripts/common.py`. DC-PSR is always vermillion (`#D55E00`) with a circle; the shared Multi-task TCN-GRU backbone is deep blue (`#0072B2`) with a diamond. Signed effects use a zero-centered muted-blue/near-white/vermillion map. Relative high-is-good scores use deep navy/teal/pale gold.

## Reproducibility

All figure-level derived tables are saved in `plot_data/`. Each figure has its own script, and the complete package is rebuilt from the project root with:

```bash
python nature_figures/scripts/make_all_figures.py
```

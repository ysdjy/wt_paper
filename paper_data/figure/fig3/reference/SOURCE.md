# Reference mockup provenance

- `reference_mockup.png` ← `figures/fig4_ablation/matlab/fig4_ablation_refined_matlab.png` —
  the **primary** style reference: MATLAB-rendered, bottom-centered panel captions already, dual
  y-axis bar+line combo panels, "A6 accuracy restored" / "A5 strongest smoothing" callout-annotation
  style, muted navy/teal/gold palette with a highlighted A5/A6 background band.
- `reference_mockup_alt_original.png` ← `nature_figures/fig4_ablation/fig4_ablation.png` — earlier
  Python-only draft of the same figure, kept as a secondary reference for the "mechanism evidence
  path" flow-chain panel idea (Raw→+Fine→+Prior→Mixture→Ordered→Final boxes).

**Style-only reference.** Learn: panel captions below each panel, dual-axis bar+line combination,
highlighted-region annotation callouts, muted diverging heatmap coloring, flow-chain mechanism
panel.

**Do not reuse**: any Smooth/Acc/M-F1 value, the specific "0.0236 / 0.0136 / 0.0188" numbers, or
the "A5 strongest smoothing" / "A6 accuracy restored" specific deltas shown here — these must be
recomputed from `paper_data/07_figure_ready/fig4/A1_A6_absolute.csv` exactly as v1 already does
(the actual, verified numbers are close in shape but not in these exact digits; see
`../plot_fig3.py`'s validation section for the authoritative values).

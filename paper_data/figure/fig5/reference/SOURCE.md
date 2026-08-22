# Reference mockup provenance

`reference_mockup_partial_panel_d_only.png` ← `figures/fig5_semantics_refined/fig5_semantics_refined.png`.
Only **panel (d)** (the PCA scatter, "Shared latent degradation manifold") is relevant style
reference for final fig5 (表示几何) — the other panels (a,b,c,e) belong to final fig4's subject
matter. This project has **no existing mockup** for the 3D stage-probability-surface /
confidence-surface panels that final fig5 also needs (per the task brief and
`DCPSR_Chapter4_CN_Detailed.docx` §4.6) — those panels are designed fresh, reusing the muted
navy/teal/gold palette and bottom-caption convention established across the other 4 figures for
visual consistency, and drawing general 3D-aesthetic cues from
`../fig3/reference/reference_mockup.png` (the MATLAB-rendered fig3 mockup) rather than copying any
specific existing 3D panel.

**Style-only reference.** Learn from panel (d): dashed connector line threading through the point
cloud in life-order, marker-shape-by-stage + continuous-color-by-q dual encoding, bottom-centered
caption.

**Do not reuse**: the specific PC1/PC2 point positions, variance-explained percentages, or point
count/shape shown here — recompute from `paper_data/07_figure_ready/fig5/hidden_representation.csv`
exactly as v1 already does (single PCA fit reused across panels, via
`_shared/data_utils.py::pca_2d`).

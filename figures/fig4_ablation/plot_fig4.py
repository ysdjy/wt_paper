"""Backward-compatible entry point for the refined audited Fig. 4.

The retired heatmap workflow has been removed. Running this file delegates to
``plot_fig4_ablation_refined.py`` and therefore uses the authoritative summary
and the inference-only lifecycle trajectory exports.
"""

from plot_fig4_ablation_refined import main


if __name__ == "__main__":
    main()

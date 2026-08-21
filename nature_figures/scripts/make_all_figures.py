from __future__ import annotations

import matplotlib.pyplot as plt

from common import OUT, apply_style
import fig1_overall_performance
import fig2_cross_condition
import fig3_cross_dataset
import fig4_ablation
import fig5_semantics
from generate_docs import write_docs
from qc_figures import run_qc


FIGURES = [
    ("Fig. 1  Overall performance", OUT / "fig1_overall_performance/fig1_overall_performance.png"),
    ("Fig. 2  Cross-condition robustness", OUT / "fig2_cross_condition/fig2_cross_condition.png"),
    ("Fig. 3  Cross-dataset evidence", OUT / "fig3_cross_dataset/fig3_cross_dataset.png"),
    ("Fig. 4  Ablation and mechanism", OUT / "fig4_ablation/fig4_ablation.png"),
    ("Fig. 5  Degradation semantics", OUT / "fig5_semantics/fig5_semantics.png"),
]


def make_contact_sheet() -> None:
    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), facecolor="white")
    axes = axes.ravel()
    for ax, (title, path) in zip(axes, FIGURES):
        image = plt.imread(path)
        ax.imshow(image)
        ax.set_title(title, loc="left", fontsize=11, pad=5)
        ax.axis("off")
    axes[-1].axis("off")
    fig.subplots_adjust(left=0.02, right=0.99, top=0.97, bottom=0.02, wspace=0.05, hspace=0.12)
    path = OUT / "previews/all_figures_contact_sheet.png"
    fig.savefig(path, dpi=220, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def main() -> None:
    fig1_overall_performance.main()
    fig2_cross_condition.main()
    fig3_cross_dataset.main()
    fig4_ablation.main()
    fig5_semantics.main()
    write_docs()
    make_contact_sheet()
    ok, issues = run_qc()
    if not ok:
        raise SystemExit("Figure QC failed: " + "; ".join(issues))


if __name__ == "__main__":
    main()

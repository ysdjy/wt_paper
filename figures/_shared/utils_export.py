"""Submission-ready export helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def export_figure(fig, output_stem: Path, *, dpi: int = 600) -> list[Path]:
    """Save editable SVG, Type-42 PDF, and a high-resolution PNG preview."""
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    outputs = []
    for suffix in ("svg", "pdf", "png"):
        target = output_stem.with_suffix(f".{suffix}")
        kwargs = {"bbox_inches": "tight", "pad_inches": 0.04}
        if suffix == "png":
            kwargs.update(dpi=dpi, metadata={"Software": "Python/matplotlib", "Description": f"{dpi} dpi preview"})
        fig.savefig(target, **kwargs)
        outputs.append(target)
    plt.close(fig)
    return outputs

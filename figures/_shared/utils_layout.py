"""Layout helpers enforcing centered below-panel captions."""

from __future__ import annotations

from collections.abc import Iterable


def add_panel_caption(fig, anchors, label: str, text: str, *, pad: float = 0.010, fontsize: float = 6.8):
    """Place ``(a) description`` below the full rendered axis/tick/label extent."""
    if not isinstance(anchors, Iterable) or hasattr(anchors, "get_position"):
        anchors = [anchors]
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = [ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted()) for ax in anchors]
    x0 = min(box.x0 for box in boxes)
    x1 = max(box.x1 for box in boxes)
    y0 = min(box.y0 for box in boxes)
    return fig.text(
        (x0 + x1) / 2,
        y0 - min(pad, 0.012),
        f"({label}) {text}",
        ha="center",
        va="top",
        fontsize=fontsize,
        color="#252525",
        linespacing=1.05,
    )


def quiet_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def hide_axis_frame(ax) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

"""Stable visual semantics shared by all Chapter 4 figures."""

DC_PSR = "#0B6174"
BACKBONE = "#6E7C8B"
BASELINE_DARK = "#44515E"
BASELINE_MID = "#8793A0"
BASELINE_LIGHT = "#C9D0D6"
GOLD = "#D9A441"
ORANGE = "#D55E00"
NEGATIVE = "#4C78A8"
POSITIVE = "#D55E00"
NEAR_WHITE = "#F7F7F7"
TEXT = "#252525"
GRID = "#E8E8E8"

STAGE_COLORS = {
    "early": "#315A7D",
    "middle": "#D9A441",
    "late": "#D55E00",
}

METHOD_ORDER = [
    "DC-PSR",
    "Multi-task TCN-GRU",
    "TCN-GRU",
    "RF",
    "HTT-Net",
    "Multi-source Attention",
    "MTF-AViTK",
    "Dynamic GIN + TGP",
    "DP2Net-adapted",
]

METHOD_COLORS = {
    "DC-PSR": DC_PSR,
    "Multi-task TCN-GRU": BACKBONE,
    "TCN-GRU": "#A3AFBA",
    "RF": "#4D4D4D",
    "HTT-Net": "#8C7AA9",
    "Multi-source Attention": "#C49A3A",
    "MTF-AViTK": "#5E9587",
    "Dynamic GIN + TGP": "#8B6F83",
    "DP2Net-adapted": "#8B8B58",
}

METHOD_MARKERS = {
    "DC-PSR": "o",
    "Multi-task TCN-GRU": "D",
    "TCN-GRU": "^",
    "RF": "s",
    "HTT-Net": "h",
    "Multi-source Attention": "p",
    "MTF-AViTK": "v",
    "Dynamic GIN + TGP": "X",
    "DP2Net-adapted": "*",
}

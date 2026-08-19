# -*- coding: utf-8 -*-
r"""
Shared condition-relative Early/Middle/Late stage-label utility for this
baseline's Unified Protocols B-S (C1->C6, native single-source) and B-D1
(pooled C1+C4->C6, "DP2Net-adapted") comparisons against DC-PSR.

READ-ONLY with respect to the main DC-PSR codebase: only *imports*
`代码/main_experiment_3_fgds_psi_optimized.py` as a library (never edits
it), the same pattern used by every other baseline in this project
(baselines/htt_net, baselines/mtf_avitk, baselines/multi_source_attention).
Reusing the exact same `define_condition_relative_stages` /
`split_grouped_lifecycle` functions guarantees this baseline's Unified
Protocol stage labels are byte-for-byte identical to every other baseline
(task instructions #13/#66: "must directly reuse the current DC-PSR
evaluation definition, not redefine it").

VB convention: VB = max(flute_1, flute_2, flute_3) per run -- this
project's confirmed real-data convention. This is DIFFERENT from DP2Net's
own Protocol-A 4-stage scheme, which paper-natively uses
mean(flute_1,2,3) for its Stage-IV (failure) threshold -- see
PAPER_SPEC.md sec 2 and preprocessing.py::assign_paper_native_4stage.
Only Protocol B (Unified, 3-class E/M/L) uses this module.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # .../论文
ARCHIVE_DIR = PROJECT_ROOT / "archive"
CODE_DIR = PROJECT_ROOT / "代码"

os.environ.setdefault(
    "FGDS_RUN_DIR",
    str(Path(tempfile.gettempdir()) / "dp2net_dcpsr_base_import_cache"),
)

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))
import main_experiment_3_fgds_psi_optimized as dcpsr_base  # noqa: E402

STAGE_NAMES = dcpsr_base.STAGE_NAMES
STAGE_TO_ID = dcpsr_base.STAGE_TO_ID
ID_TO_STAGE = dcpsr_base.ID_TO_STAGE


def load_vb_table(conditions=("C1", "C4", "C6")) -> pd.DataFrame:
    rows = []
    for cond in conditions:
        cond_lower = cond.lower()
        wear_path = ARCHIVE_DIR / cond_lower / f"{cond_lower}_wear.csv"
        wdf = pd.read_csv(wear_path)
        wdf.columns = [str(c).strip() for c in wdf.columns]
        vb = wdf[["flute_1", "flute_2", "flute_3"]].max(axis=1)
        for cut, v in zip(wdf["cut"].astype(int), vb):
            rows.append({"condition": cond, "run_id": int(cut), "VB": float(v)})
    return pd.DataFrame(rows)


def get_condition_relative_labels(conditions=("C1", "C4", "C6")) -> pd.DataFrame:
    df = load_vb_table(conditions)
    labeled, _thresholds = dcpsr_base.define_condition_relative_stages(df)
    return labeled


def get_unified_split(conditions=("C1", "C4", "C6")):
    """Pooled-source split (train=C1+C4 internal val, test=C6) -- used for
    Protocol B-D1 ("DP2Net-adapted, pooled source")."""
    labeled = get_condition_relative_labels(conditions)
    return dcpsr_base.split_grouped_lifecycle(labeled)


def get_single_source_split(source="C1", target="C6"):
    """Native single-source split (train/val=source only, test=target) --
    used for Protocol B-S, preserving DP2Net's own SSDG character while
    using DC-PSR's unified E/M/L labels. 70/30 train/val within source,
    per the paper's own Sec 4.2 split ratio."""
    labeled = get_condition_relative_labels((source, target))
    src = labeled[labeled["condition"] == source].sort_values("run_id").reset_index(drop=True)
    tgt = labeled[labeled["condition"] == target].sort_values("run_id").reset_index(drop=True)
    val_idx = []
    for st in STAGE_NAMES:
        gs = src[src["stage"] == st].sort_values("run_id")
        if len(gs) == 0:
            continue
        n = max(1, int(round(len(gs) * 0.30)))
        n = min(n, max(len(gs) - 1, 1))
        start = max(0, (len(gs) - n) // 2)
        val_idx.extend(gs.iloc[start:start + n].index.tolist())
    val_idx = sorted(set(val_idx))
    val_df = src.loc[val_idx].copy()
    train_df = src.drop(index=val_idx).copy()
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), tgt


if __name__ == "__main__":
    labeled = get_condition_relative_labels()
    print(labeled.groupby(["condition", "stage"]).size())
    tr, va, te = get_unified_split()
    print(f"B-D1: train={len(tr)} val={len(va)} test={len(te)}")
    tr2, va2, te2 = get_single_source_split("C1", "C6")
    print(f"B-S (C1->C6): train={len(tr2)} val={len(va2)} test={len(te2)}")

# -*- coding: utf-8 -*-
r"""
Shared condition-relative Early/Middle/Late stage-label utility for this
baseline's Unified Protocol B (DC-PSR C1+C4 -> C6 comparison).

This module is READ-ONLY with respect to the main DC-PSR codebase: it only
*imports* `代码/main_experiment_3_fgds_psi_optimized.py` as a library
(never edits it), the same pattern used by `baselines/htt_net/train.py`
and `baselines/mtf_avitk/data/label_utils.py`. Reusing the exact same
`define_condition_relative_stages` / `split_grouped_lifecycle` functions
guarantees this baseline's Unified Protocol B stage labels and
train/val/test split are byte-for-byte identical to every other baseline
in the unified comparison (per task instructions #13/#38: "must directly
reuse the current DC-PSR evaluation definition, not redefine it").

VB convention: VB = max(flute_1, flute_2, flute_3) per run -- this
project's confirmed real-data convention (see
baselines/htt_net/README.md and baselines/mtf_avitk/data/label_utils.py).

Only used for Protocol B (Unified). Protocol A (original-paper sanity
reproduction) uses Dynamic GIN + TGP's own fixed cut-index thresholds
(Initial 1-50 / Normal 51-210 / Severe 211-315, first 300 passes only)
instead -- see preprocessing.py.
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
    str(Path(tempfile.gettempdir()) / "dynamic_gin_tgp_dcpsr_base_import_cache"),
)

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))
import main_experiment_3_fgds_psi_optimized as dcpsr_base  # noqa: E402

STAGE_NAMES = dcpsr_base.STAGE_NAMES
STAGE_TO_ID = dcpsr_base.STAGE_TO_ID
ID_TO_STAGE = dcpsr_base.ID_TO_STAGE


def load_vb_table(conditions=("C1", "C4", "C6")) -> pd.DataFrame:
    """Build a (condition, run_id, VB) table straight from the raw PHM2010
    wear CSVs in archive/, using VB = max(flute_1, flute_2, flute_3)."""
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
    """Authoritative condition-relative stage labels: columns include
    condition, run_id, VB, VB_smooth, q_true, rate_norm, stage, stage_id,
    fine_state_true. Identical logic/thresholds to every other DC-PSR
    baseline (computed per-condition)."""
    df = load_vb_table(conditions)
    labeled, _thresholds = dcpsr_base.define_condition_relative_stages(df)
    return labeled


def get_unified_split(conditions=("C1", "C4", "C6")):
    """Train/val/test split reused byte-for-byte from
    dcpsr_base.split_grouped_lifecycle: stage-stratified internal
    validation carved out of C1+C4, C6 held out entirely as test.
    Returns (train_df, val_df, test_df)."""
    labeled = get_condition_relative_labels(conditions)
    return dcpsr_base.split_grouped_lifecycle(labeled)


if __name__ == "__main__":
    labeled = get_condition_relative_labels()
    print(labeled.groupby(["condition", "stage"]).size())
    tr, va, te = get_unified_split()
    print(f"train={len(tr)} val={len(va)} test={len(te)}")

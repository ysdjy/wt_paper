# -*- coding: utf-8 -*-
r"""
Runs the existing, UNMODIFIED `代码/7.4对比实验.py` (B1-B12 comparison
experiment) against the reconstructed feature file
(`baselines/htt_net/data/run_level_features_all.csv`) built from raw
PHM2010 signals, so that HTT-Net's numbers (also computed on this same
reconstructed file, see ../train.py) can be compared to B1-B12 on an
apples-to-apples basis.

This does NOT edit `代码/7.4对比实验.py`. It works by:
  1. Importing `main_experiment_3_fgds_psi_optimized` ourselves first and
     overriding its `FEATURE_FILE` attribute -- when 7.4对比实验.py later
     does its own `import main_experiment_3_fgds_psi_optimized as base`,
     Python reuses the already-imported module from sys.modules (does not
     re-execute it), so our override is preserved.
  2. Setting COMPARISON_RECHECK_DIR before loading 7.4对比实验.py so its
     own output directories point into this project's outputs/ tree
     instead of the (nonexistent on this machine) wangting Desktop path.
  3. Loading 7.4对比实验.py via importlib (its filename is not a valid
     Python identifier) and calling its main() explicitly.

IMPORTANT CAVEAT (repeated from build_run_level_features.py and
../README.md): the feature set used here is a reconstruction from raw
signals, not the manuscript's original (now-missing) run_level_features_all
.csv. These B1-B12 numbers are only valid for comparison against HTT-Net's
numbers computed on the same reconstructed file -- they should NOT be
assumed to match whatever B1-B12 numbers already appear in the manuscript
draft.

Usage:
    python run_b1_b12_recheck.py
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[2]
CODE_DIR = PROJECT_ROOT / "代码"
FEATURE_FILE = THIS_DIR / "run_level_features_all.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "htt_net" / "B1_B12_recheck_on_reconstructed_features"

if not FEATURE_FILE.exists():
    raise FileNotFoundError(f"Run build_run_level_features.py first -- missing {FEATURE_FILE}")

os.environ.setdefault("FGDS_RUN_DIR", str(Path(tempfile.gettempdir()) / "htt_net_base_import_cache"))
os.environ["COMPARISON_RECHECK_DIR"] = str(OUTPUT_DIR)

sys.path.insert(0, str(CODE_DIR))
import main_experiment_3_fgds_psi_optimized as base  # noqa: E402

base.FEATURE_FILE = FEATURE_FILE
print(f"[recheck] base.FEATURE_FILE overridden to: {base.FEATURE_FILE}")
print(f"[recheck] output dir: {OUTPUT_DIR}")

script_path = CODE_DIR / "7.4对比实验.py"
spec = importlib.util.spec_from_file_location("comparison_recheck_script", script_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["comparison_recheck_script"] = mod
spec.loader.exec_module(mod)

mod.main()

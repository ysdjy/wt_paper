# -*- coding: utf-8 -*-
r"""
Literal reproduction audit -- runs the UNMODIFIED `代码/7.4对比实验.py`
main() exactly as it was written (sequential B1..B12, ONE base.set_seed()
call at the top of main(), B8->B9->B10->B11->B12 in original order), with
RANDOM_SEED left at its hardcoded default (42) -- no diagnostic runner,
no per-model seed isolation, no protocol changes.

The only patch applied (identical to the already-established pattern in
final_five_seed_sweep/scripts/run_generic_baselines_seed.py, used for the
other 4 seeds of the original sweep) is FEATURE_FILE, because the script's
hardcoded default path (C:\Users\wangting\...) does not exist on this
machine. RANDOM_SEED is NOT touched -- it stays at the script's own
default of 42, i.e. we run exactly `python 7.4对比实验.py` would run.

Output goes to legacy_repro_audit/output/ -- NEVER anywhere under
补充材料/小论文/4_comparison_experiment_recheck/ (the original archived
ground-truth run) or final_five_seed_sweep/ (the frozen 9-method sweep).

Usage:
    python run_legacy_main_seed42.py
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
AUDIT_ROOT = THIS_DIR.parent
PROJECT_ROOT = AUDIT_ROOT.parent
CODE_DIR = PROJECT_ROOT / "代码"
FEATURE_FILE = PROJECT_ROOT / "baselines" / "htt_net" / "data" / "run_level_features_all.csv"
OUTPUT_DIR = AUDIT_ROOT / "output" / "seed42_literal_main"

if not FEATURE_FILE.exists():
    raise FileNotFoundError(f"Authoritative feature file missing: {FEATURE_FILE}")

os.environ.setdefault("FGDS_RUN_DIR", str(Path(tempfile.gettempdir()) / "legacy_repro_audit_base_cache"))
os.environ["COMPARISON_RECHECK_DIR"] = str(OUTPUT_DIR)

sys.path.insert(0, str(CODE_DIR))
import main_experiment_3_fgds_psi_optimized as base  # noqa: E402

base.FEATURE_FILE = FEATURE_FILE
print(f"[legacy audit] base.FEATURE_FILE = {base.FEATURE_FILE}")
print(f"[legacy audit] base.RANDOM_SEED  = {base.RANDOM_SEED}  (untouched, script default)")
print(f"[legacy audit] output dir        = {OUTPUT_DIR}")

script_path = CODE_DIR / "7.4对比实验.py"
mod_name = "legacy_repro_comparison_script_seed42"
spec = importlib.util.spec_from_file_location(mod_name, script_path)
mod = importlib.util.module_from_spec(spec)
sys.modules[mod_name] = mod
spec.loader.exec_module(mod)

mod.main()

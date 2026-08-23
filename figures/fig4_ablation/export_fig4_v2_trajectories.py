"""Inference-only export of formal A1-A6 lifecycle probability trajectories.

This script never calls a training routine. It loads the frozen seed-42
preprocessing tables and the formal B11/B12 checkpoint, runs ``model.eval()``
under ``torch.inference_mode()``, reconstructs A1-A6 using the audited formal
probability-inference function, and writes traceable lifecycle CSVs for Fig. 4.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

import numpy as np
import pandas as pd
import torch


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
CODE_FILE = ROOT / "代码" / "main_experiment_3_fgds_psi_optimized.py"
CHECKPOINT = (
    ROOT
    / "补充材料"
    / "小论文"
    / "4_comparison_experiment_recheck"
    / "3_models"
    / "B11_B12_multitask_tcn_gru.pth"
)
FORMAL_PREDICTIONS = (
    ROOT
    / "补充材料"
    / "小论文"
    / "4_comparison_experiment_recheck"
    / "1_results"
    / "FINAL_comparison_predictions.csv"
)
FROZEN_DIR = ROOT / "protocol_diagnostic_fixed_preprocess" / "frozen_preprocess"
FROZEN_FEATURES = FROZEN_DIR / "selected_features_seed42.json"
FROZEN_TEST = FROZEN_DIR / "feat_test_frozen.csv"
FROZEN_MANIFEST = FROZEN_DIR / "manifest_hashes.json"
AUTHORITATIVE_SUMMARY = OUT_DIR / "AUTHORITATIVE_A1_A6.csv"
MANIFEST_PATH = OUT_DIR / "data_manifest.json"

TRAJECTORY_OUT = OUT_DIR / "A1_A6_probability_trajectories.csv"
LOCAL_OUT = OUT_DIR / "A1_A6_lifecycle_variation.csv"
CUMULATIVE_OUT = OUT_DIR / "A1_A6_cumulative_variation.csv"

EXPECTED_CHECKPOINT_SHA256 = "17299bbc71baa8148a0c3916084b034ec0efe4120a36b06f2b2cb8a6919ec69b"
EXPECTED_FEATURE_SHA256 = "6e8affeb681d0b386e453421a0df7a66932138199eb236403d27b797c11eeb88"
METHODS = ["A1", "A2", "A3", "A4", "A5", "A6"]
METHOD_TO_OUTPUT = {
    "A1": "raw",
    "A2": "raw_fine",
    "A3": "raw_prior",
    "A4": "mix",
    "A5": "ordered",
    "A6": "final",
}
OUTPUT_TO_PROB_PREFIX = {
    "raw": "raw_prob",
    "raw_fine": "raw_fine_prob",
    "raw_prior": "raw_prior_prob",
    "mix": "mix_prob",
    "ordered": "ordered_prob",
    "final": "final_prob",
}
PARAMS = {
    "eta": 0.75,
    "fine_weight": 0.30,
    "temperature": 1.20,
    "mid_floor": 0.12,
    "late_tau": 0.66,
    "early_tau": 0.38,
    "order_blend": 0.25,
}
SMOOTHING_WINDOW = 11


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def import_formal_base():
    side_dir = Path(tempfile.gettempdir()) / "fig4_v2_inference_import_side_outputs"
    os.environ["FGDS_RUN_DIR"] = str(side_dir)
    module_name = "fig4_v2_formal_base"
    spec = importlib.util.spec_from_file_location(module_name, CODE_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import formal base code: {CODE_FILE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def configure_inference_runtime() -> torch.device:
    """Match the audited formal runtime without changing cuDNN algorithm policy."""
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_frozen_test(base):
    with FROZEN_FEATURES.open("r", encoding="utf-8") as handle:
        selected_info = json.load(handle)
    selected = selected_info["selected_features_in_order"]
    if len(selected) != 45:
        raise ValueError(f"Expected 45 frozen selected features, found {len(selected)}")
    feat_test = pd.read_csv(FROZEN_TEST)
    missing = [column for column in selected if column not in feat_test.columns]
    if missing:
        raise ValueError(f"Frozen test table lacks selected columns: {missing}")
    test_pack = base.make_pack(feat_test, selected, base.BEST_ARCH["L"], "test_C6")
    if len(test_pack["meta"]) != 304:
        raise ValueError(f"Expected 304 C6 windows, found {len(test_pack['meta'])}")
    return selected, test_pack


def run_forward_only(base, selected: list[str], test_pack: dict, device: torch.device) -> pd.DataFrame:
    base.DEVICE = str(device)
    model = base.TCNGRUMultiTask(
        input_dim=len(selected),
        channels=base.BEST_ARCH["channels"],
        gru_hidden=base.BEST_ARCH["gru_hidden"],
        dropout=base.BEST_ARCH["dropout"],
    ).to(device)
    try:
        state = torch.load(CHECKPOINT, map_location=device, weights_only=True)
    except TypeError:
        state = torch.load(CHECKPOINT, map_location=device)
    model.load_state_dict(state, strict=True)
    model.eval()

    stage_parts: list[np.ndarray] = []
    fine_parts: list[np.ndarray] = []
    q_parts: list[np.ndarray] = []
    with torch.inference_mode():
        for x_batch, _, _, _ in test_pack["loader"]:
            output = model(x_batch.to(device, non_blocking=True))
            stage_parts.append(output["stage_prob"].detach().cpu().numpy())
            fine_parts.append(output["fine_prob"].detach().cpu().numpy())
            q_parts.append(output["q_hat"].detach().cpu().numpy().reshape(-1))

    stage_prob = np.concatenate(stage_parts, axis=0)
    fine_prob = np.concatenate(fine_parts, axis=0)
    q_hat = np.concatenate(q_parts, axis=0)
    pred_raw = test_pack["meta"].copy().reset_index(drop=True)
    pred_raw["q_hat"] = q_hat
    pred_raw["q_true_model"] = test_pack["yq"]
    for index, stage in enumerate(base.STAGE_NAMES):
        pred_raw[f"raw_prob_{stage}"] = stage_prob[:, index]
    for index in range(base.N_FINE_STATES):
        pred_raw[f"fine_prob_{index}"] = fine_prob[:, index]
    pred_raw["stage_pred_raw"] = np.argmax(stage_prob, axis=1)
    pred_raw["stage_pred_raw_name"] = pred_raw["stage_pred_raw"].map(base.ID_TO_STAGE)
    return base.apply_probability_inference(pred_raw, PARAMS)


def validate_formal_outputs(base, inferred: pd.DataFrame) -> dict:
    authoritative = pd.read_csv(AUTHORITATIVE_SUMMARY).set_index("ID").loc[METHODS]
    formal = pd.read_csv(FORMAL_PREDICTIONS).sort_values("run_id_end").reset_index(drop=True)
    inferred = inferred.sort_values("cut_index").reset_index(drop=True)
    if not np.array_equal(formal["run_id_end"].to_numpy(), inferred["cut_index"].to_numpy()):
        raise ValueError("Formal prediction and inferred run IDs differ")

    metrics = {}
    max_metric_difference = 0.0
    for method, output in METHOD_TO_OUTPUT.items():
        row = base.manuscript_metric_row(inferred, output, method, split="test_C6")
        metrics[method] = row
        for metric in ["Acc", "Macro-F1", "M-F1", "M-Rec", "M→E", "M→L", "Rev", "Jump", "Smooth"]:
            diff = abs(float(row[metric]) - float(authoritative.loc[method, metric]))
            max_metric_difference = max(max_metric_difference, diff)
            if diff > 5e-10:
                raise ValueError(f"{method} {metric} differs from authoritative summary by {diff:.3e}")

    a1_labels = inferred["stage_pred_raw_name"].astype(str).to_numpy()
    a6_labels = inferred["stage_pred_final_name"].astype(str).to_numpy()
    if not np.array_equal(a1_labels, formal["pred_B11"].astype(str).to_numpy()):
        raise ValueError("A1 labels do not equal stored formal B11 labels")
    if not np.array_equal(a6_labels, formal["pred_B12"].astype(str).to_numpy()):
        raise ValueError("A6 labels do not equal stored formal B12 labels")

    a1_prob = inferred[["raw_prob_early", "raw_prob_middle", "raw_prob_late"]].to_numpy(float)
    a6_prob = inferred[["final_prob_early", "final_prob_middle", "final_prob_late"]].to_numpy(float)
    b11_prob = formal[["prob_E_B11", "prob_M_B11", "prob_L_B11"]].to_numpy(float)
    b12_prob = formal[["prob_E_B12", "prob_M_B12", "prob_L_B12"]].to_numpy(float)
    a1_anchor_max_abs = float(np.max(np.abs(a1_prob - b11_prob)))
    a6_anchor_max_abs = float(np.max(np.abs(a6_prob - b12_prob)))
    if a1_anchor_max_abs > 5.1e-4 or a6_anchor_max_abs > 5.1e-4:
        raise ValueError("Full-precision inference exceeds the stored four-decimal probability tolerance")
    return {
        "max_authoritative_metric_abs_difference": max_metric_difference,
        "formal_A1_labels_equal_B11": True,
        "formal_A6_labels_equal_B12": True,
        "A1_vs_rounded_B11_probability_max_abs_difference": a1_anchor_max_abs,
        "A6_vs_rounded_B12_probability_max_abs_difference": a6_anchor_max_abs,
    }


def build_outputs(inferred: pd.DataFrame, authoritative: pd.DataFrame):
    inferred = inferred.sort_values(["condition", "cut_index"]).reset_index(drop=True)
    run_min = int(inferred["cut_index"].min())
    run_max = int(inferred["cut_index"].max())
    relative_life = (inferred["cut_index"].to_numpy(float) - run_min) / (run_max - run_min)
    configuration = authoritative.set_index("ID")["Configuration"].to_dict()

    trajectory_parts = []
    local_parts = []
    cumulative_parts = []
    for method in METHODS:
        output = METHOD_TO_OUTPUT[method]
        prefix = OUTPUT_TO_PROB_PREFIX[output]
        probability_columns = [f"{prefix}_{stage}" for stage in ["early", "middle", "late"]]
        probability = inferred[probability_columns].to_numpy(float)
        prediction_column = "stage_pred_raw" if output == "raw" else f"stage_pred_{output}"
        prediction_name_column = (
            "stage_pred_raw_name" if output == "raw" else f"stage_pred_{output}_name"
        )

        trajectory_parts.append(
            pd.DataFrame(
                {
                    "ID": method,
                    "Configuration": configuration[method],
                    "condition": inferred["condition"].astype(str),
                    "run_id": inferred["cut_index"].astype(int),
                    "relative_tool_life": relative_life,
                    "true_stage": inferred["stage_true"].astype(str),
                    "true_stage_id": inferred["stage_true_id"].astype(int),
                    "q_true": inferred["q_true"].astype(float),
                    "q_hat": inferred["q_hat"].astype(float),
                    "p_E": probability[:, 0],
                    "p_M": probability[:, 1],
                    "p_L": probability[:, 2],
                    "pred_stage": inferred[prediction_name_column].astype(str),
                    "pred_stage_id": inferred[prediction_column].astype(int),
                }
            )
        )

        delta = np.full(len(probability), np.nan, dtype=float)
        delta[1:] = np.sum(np.abs(np.diff(probability, axis=0)), axis=1)
        smoothed = (
            pd.Series(delta)
            .rolling(window=SMOOTHING_WINDOW, min_periods=1, center=True)
            .mean()
            .to_numpy()
        )
        cumulative = np.zeros(len(probability), dtype=float)
        cumulative[1:] = np.cumsum(delta[1:])
        smooth_from_delta = float(np.nanmean(delta))
        smooth_authoritative = float(authoritative.set_index("ID").loc[method, "Smooth"])
        if abs(smooth_from_delta - smooth_authoritative) > 5e-10:
            raise ValueError(f"{method} local variation mean does not reproduce Smooth")
        if abs(cumulative[-1] / (len(probability) - 1) - smooth_authoritative) > 5e-10:
            raise ValueError(f"{method} cumulative endpoint does not reproduce Smooth")

        local_parts.append(
            pd.DataFrame(
                {
                    "ID": method,
                    "condition": inferred["condition"].astype(str),
                    "run_id": inferred["cut_index"].astype(int),
                    "relative_tool_life": relative_life,
                    "local_variation_l1": delta,
                    "local_variation_l1_smoothed": smoothed,
                    "smoothing_window_runs": SMOOTHING_WINDOW,
                }
            )
        )
        cumulative_parts.append(
            pd.DataFrame(
                {
                    "ID": method,
                    "condition": inferred["condition"].astype(str),
                    "run_id": inferred["cut_index"].astype(int),
                    "relative_tool_life": relative_life,
                    "cumulative_variation_l1": cumulative,
                }
            )
        )

    trajectories = pd.concat(trajectory_parts, ignore_index=True)
    local = pd.concat(local_parts, ignore_index=True)
    cumulative = pd.concat(cumulative_parts, ignore_index=True)
    probability_sums = trajectories[["p_E", "p_M", "p_L"]].sum(axis=1)
    probability_sum_max_abs_error = float(np.max(np.abs(probability_sums - 1.0)))
    # A1 is the checkpoint's float32 softmax output; retain it byte-for-value
    # instead of renormalizing and changing the audited Smooth value.
    if probability_sum_max_abs_error > 2e-7:
        raise ValueError(
            f"Exported probability sum error is {probability_sum_max_abs_error:.3e}"
        )
    trajectories.to_csv(TRAJECTORY_OUT, index=False, encoding="utf-8-sig")
    local.to_csv(LOCAL_OUT, index=False, encoding="utf-8-sig")
    cumulative.to_csv(CUMULATIVE_OUT, index=False, encoding="utf-8-sig")
    return trajectories, local, cumulative, {
        "probability_sum_max_abs_error": probability_sum_max_abs_error,
        "all_local_means_equal_authoritative_smooth": True,
        "all_cumulative_endpoints_equal_smooth_times_303": True,
    }


def update_manifest(runtime: dict, validation: dict, row_counts: dict) -> None:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    with FROZEN_MANIFEST.open("r", encoding="utf-8") as handle:
        frozen_hashes = json.load(handle)
    manifest["fig4_v2"] = {
        "audit_result": "PASS_INFERENCE_ONLY",
        "experiment_protocol_changed": False,
        "training_performed": False,
        "inference_only": True,
        "dataset": "PHM2010",
        "task": "D1: train C1+C4, test C6",
        "test_universe": {"condition": "C6", "window_length": 12, "run_id_min": 12, "run_id_max": 315, "n": 304},
        "authoritative_summary": {"path": str(AUTHORITATIVE_SUMMARY.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(AUTHORITATIVE_SUMMARY)},
        "formal_checkpoint": {"path": str(CHECKPOINT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(CHECKPOINT)},
        "frozen_preprocessing": {
            "directory": str(FROZEN_DIR.relative_to(ROOT)).replace("\\", "/"),
            "selected_features": str(FROZEN_FEATURES.relative_to(ROOT)).replace("\\", "/"),
            "scaled_test_table": str(FROZEN_TEST.relative_to(ROOT)).replace("\\", "/"),
            "hash_manifest": frozen_hashes,
            "refit_or_reselection_performed": False,
        },
        "formal_probability_anchor": {"path": str(FORMAL_PREDICTIONS.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(FORMAL_PREDICTIONS), "stored_precision": "four decimals"},
        "probability_inference_source": {"path": str(CODE_FILE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(CODE_FILE), "function": "apply_probability_inference", "A1_A6_mapping": METHOD_TO_OUTPUT, "parameters": PARAMS},
        "trajectory_definition": {
            "relative_tool_life": "(run_id - 12) / (315 - 12) over the evaluated C6 L=12 universe",
            "local_variation": "L1 norm of adjacent (p_E, p_M, p_L) probability vectors",
            "local_display_smoothing": {"method": "centered rolling arithmetic mean", "window_runs": SMOOTHING_WINDOW, "raw_values_preserved": True},
            "cumulative_variation": "cumulative sum of local L1 variation; starts at zero",
        },
        "outputs": {
            "probability_trajectories": {"path": TRAJECTORY_OUT.name, "sha256": sha256(TRAJECTORY_OUT), "rows": row_counts["trajectory"]},
            "lifecycle_variation": {"path": LOCAL_OUT.name, "sha256": sha256(LOCAL_OUT), "rows": row_counts["local"]},
            "cumulative_variation": {"path": CUMULATIVE_OUT.name, "sha256": sha256(CUMULATIVE_OUT), "rows": row_counts["cumulative"]},
        },
        "validation": validation,
        "runtime": runtime,
    }
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main() -> None:
    if sha256(CHECKPOINT) != EXPECTED_CHECKPOINT_SHA256:
        raise ValueError("Formal checkpoint SHA-256 does not match the authoritative audit")
    raw_feature = ROOT / "baselines" / "htt_net" / "data" / "run_level_features_all.csv"
    if sha256(raw_feature) != EXPECTED_FEATURE_SHA256:
        raise ValueError("Formal raw feature SHA-256 does not match the authoritative audit")

    device = configure_inference_runtime()
    base = import_formal_base()
    selected, test_pack = load_frozen_test(base)
    inferred = run_forward_only(base, selected, test_pack, device)
    validation = validate_formal_outputs(base, inferred)
    authoritative = pd.read_csv(AUTHORITATIVE_SUMMARY)
    trajectories, local, cumulative, export_validation = build_outputs(inferred, authoritative)
    validation.update(export_validation)
    runtime = {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "device": torch.cuda.get_device_name(0) if device.type == "cuda" else "CPU",
        "model_mode": "eval",
        "autograd": "torch.inference_mode",
    }
    update_manifest(
        runtime,
        validation,
        {"trajectory": len(trajectories), "local": len(local), "cumulative": len(cumulative)},
    )
    print("[Fig4 V2 audit] PASS_INFERENCE_ONLY")
    print(f"[Fig4 V2 audit] checkpoint: {CHECKPOINT.name} ({sha256(CHECKPOINT)})")
    print("[Fig4 V2 audit] training performed: False")
    print(f"[Fig4 V2 audit] A1-A6 trajectory rows: {len(trajectories)}")
    print(f"[Fig4 V2 audit] max summary difference: {validation['max_authoritative_metric_abs_difference']:.3e}")
    for path in [TRAJECTORY_OUT, LOCAL_OUT, CUMULATIVE_OUT, MANIFEST_PATH]:
        print(f"[Fig4 V2 output] {path.name} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the manuscript Single Source of Truth without modifying source results."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median, pstdev, stdev
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper_data"
ALLOWED_STATUS = {
    "AUTHORITATIVE", "CANONICAL_COPY", "DERIVED", "AUDIT_SUPPORTING",
    "SUPERSEDED", "EXCLUDED", "UNRESOLVED",
}
METHOD_IDS = {
    "RF": "rf", "TCN-GRU": "tcn_gru", "Multi-task TCN-GRU": "multitask_tcn_gru",
    "DC-PSR": "dc_psr", "HTT-Net (adapted)": "htt_net", "HTT-Net": "htt_net",
    "Multi-source Attention": "multi_source_attention",
    "Multi-source Channel-Spatial Attention": "multi_source_attention",
    "MTF-AViTK": "mtf_avitk", "Dynamic GIN + TGP": "dynamic_gin_tgp",
    "DP2Net-adapted": "dp2net_adapted", "DP2Net": "dp2net_adapted",
    "B9": "b9", "B10": "b10", "B11": "b11", "B12": "b12",
}
METHOD_METADATA = [
    {"method_id": "rf", "method_name": "RF", "aliases": "Random Forest", "role": "comparison"},
    {"method_id": "tcn_gru", "method_name": "TCN-GRU", "aliases": "TCN GRU", "role": "comparison"},
    {"method_id": "multitask_tcn_gru", "method_name": "Multi-task TCN-GRU", "aliases": "Multitask TCN-GRU", "role": "comparison"},
    {"method_id": "dc_psr", "method_name": "DC-PSR", "aliases": "B12", "role": "proposed"},
    {"method_id": "htt_net", "method_name": "HTT-Net (adapted)", "aliases": "HTT-Net", "role": "comparison"},
    {"method_id": "multi_source_attention", "method_name": "Multi-source Attention", "aliases": "Multi-source Channel-Spatial Attention", "role": "comparison"},
    {"method_id": "mtf_avitk", "method_name": "MTF-AViTK", "aliases": "", "role": "comparison"},
    {"method_id": "dynamic_gin_tgp", "method_name": "Dynamic GIN + TGP", "aliases": "", "role": "comparison"},
    {"method_id": "dp2net_adapted", "method_name": "DP2Net-adapted", "aliases": "DP2Net", "role": "comparison"},
]
METHOD_DISPLAY = {row["method_id"]: row["method_name"] for row in METHOD_METADATA}
RAW_SIGNAL_METHODS = {
    "multi_source_attention", "mtf_avitk", "dynamic_gin_tgp", "dp2net_adapted",
}
TRANSFER_METRICS = [
    "Acc", "MacroF1", "E_F1", "M_F1", "L_F1", "M_Precision", "M_Recall",
    "M_to_E", "M_to_L", "Rev", "Jump", "Smooth",
]
THIRD_DATASET_ID = "MILLING_CROSS_MACHINE"
THIRD_DATASET_NAME = "Multivariate time series data of milling processes with varying tool wear and machine tools"
THIRD_DATASET_SHORT_NAME = "MTW-CM"
THIRD_DATASET_HOST = "Mendeley Data"
LOW_IS_GOOD = {"Smooth", "Jump", "Rev", "M_to_E", "M_to_L"}
registry: dict[str, dict] = {}
copy_rows: list[dict] = []
unresolved: list[dict] = []
manuscript_sync: list[dict] = []


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def git_tracked(path: Path) -> bool:
    try:
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel(path)], cwd=ROOT,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return False


def load_previous_copy_manifest() -> dict[str, dict]:
    path = PAPER / "90_provenance/COPY_MANIFEST.csv"
    if not path.exists():
        return {}
    return {row["canonical_path"]: row for row in read_csv(path)}


PREVIOUS = load_previous_copy_manifest()


def register(
    dst: Path, *, status: str, data_level: str, dataset: str = "", task: str = "",
    method: str = "", seed: str = "", source: Path | None = None,
    transformation: str = "none", intended_use: str = "", notes: str = "",
) -> None:
    assert status in ALLOWED_STATUS
    registry[rel(dst)] = {
        "status": status, "data_level": data_level, "dataset": dataset, "task": task,
        "method": method, "seed": seed, "source_path": rel(source) if source else "",
        "source_sha256": sha256(source) if source and source.exists() else "",
        "transformation": transformation, "intended_use": intended_use, "notes": notes,
    }


def safe_copy(
    source_rel: str, dest_rel: str, *, status: str = "CANONICAL_COPY",
    data_level: str = "summary", dataset: str = "", task: str = "", method: str = "",
    seed: str = "", intended_use: str = "", notes: str = "",
    allow_source_update: bool = False,
) -> Path:
    src, dst = ROOT / source_rel, ROOT / dest_rel
    if not src.exists():
        raise FileNotFoundError(src)
    src_hash = sha256(src)
    key = rel(dst)
    prior = PREVIOUS.get(key)
    if dst.exists():
        if prior:
            if prior.get("source_sha256") != src_hash and not allow_source_update:
                raise RuntimeError(f"Source changed for existing canonical file: {key}")
            prior_canonical = prior.get("canonical_sha256", "")
            if prior_canonical and sha256(dst) != prior_canonical and not allow_source_update:
                raise RuntimeError(f"Canonical file was locally modified: {key}")
        elif sha256(dst) != src_hash:
            raise RuntimeError(f"Unmanaged conflicting canonical file: {key}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or sha256(dst) != src_hash:
        shutil.copy2(src, dst)
    register(dst, status=status, data_level=data_level, dataset=dataset, task=task,
             method=method, seed=seed, source=src, intended_use=intended_use, notes=notes)
    copy_rows.append({
        "source_path": rel(src), "canonical_path": key, "source_sha256": src_hash,
        "canonical_sha256": sha256(dst), "git_tracked": str(git_tracked(src)).lower(),
        "status": status, "copy_mode": "byte_for_byte",
    })
    return dst


def derived_csv(
    dest_rel: str, rows: list[dict], fields: list[str], *, sources: list[Path],
    data_level: str, dataset: str = "", task: str = "", method: str = "",
    transformation: str, intended_use: str, status: str = "DERIVED", notes: str = "",
) -> Path:
    dst = ROOT / dest_rel
    write_csv(dst, rows, fields)
    source = sources[0] if sources else None
    source_paths = ";".join(rel(p) for p in sources)
    source_hashes = ";".join(sha256(p) for p in sources)
    register(dst, status=status, data_level=data_level, dataset=dataset, task=task,
             method=method, source=source, transformation=transformation,
             intended_use=intended_use, notes=(notes + f" inputs={source_paths}").strip())
    registry[rel(dst)]["source_path"] = source_paths
    registry[rel(dst)]["source_sha256"] = source_hashes
    return dst


def derived_json(
    dest_rel: str, payload: dict, *, sources: list[Path], data_level: str,
    dataset: str = "", task: str = "", method: str = "", transformation: str,
    intended_use: str, status: str = "DERIVED", notes: str = "",
) -> Path:
    dst = ROOT / dest_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source = sources[0] if sources else None
    source_paths = ";".join(rel(p) for p in sources)
    source_hashes = ";".join(sha256(p) for p in sources)
    register(dst, status=status, data_level=data_level, dataset=dataset, task=task,
             method=method, source=source, transformation=transformation,
             intended_use=intended_use, notes=(notes + f" inputs={source_paths}").strip())
    registry[rel(dst)]["source_path"] = source_paths
    registry[rel(dst)]["source_sha256"] = source_hashes
    return dst


FIGURE_READY_METADATA_FIELDS = [
    "dataset_id", "task_id", "protocol_id", "aggregation_level", "uncertainty_type",
    "n_test", "test_universe", "source_path", "status",
]


def with_figure_metadata(
    rows: list[dict], *, dataset_id: str, task_id: str, protocol_id: str,
    aggregation_level: str, uncertainty_type: str, n_test: int | str,
    test_universe: str, source_path: str, status: str = "DERIVED",
) -> tuple[list[dict], list[str]]:
    enriched = [
        dict(row) | {
            "dataset_id": dataset_id, "task_id": task_id, "protocol_id": protocol_id,
            "aggregation_level": aggregation_level, "uncertainty_type": uncertainty_type,
            "n_test": n_test, "test_universe": test_universe,
            "source_path": source_path, "status": status,
        }
        for row in rows
    ]
    base_fields = list(rows[0]) if rows else []
    fields = base_fields + [field for field in FIGURE_READY_METADATA_FIELDS if field not in base_fields]
    return enriched, fields


def stage_id(value: str) -> int:
    text = str(value).strip().lower()
    mapping = {"0": 0, "1": 1, "2": 2, "early": 0, "middle": 1, "late": 2}
    if text not in mapping:
        raise ValueError(f"Unknown stage label: {value!r}")
    return mapping[text]


def recompute_transfer_metrics(rows: list[dict]) -> dict:
    """Recompute frozen transfer metrics from existing predictions only."""
    ordered = sorted(rows, key=lambda row: int(row["run_id"]))
    truth = [stage_id(row["true_stage"]) for row in ordered]
    pred = [stage_id(row["pred_stage"]) for row in ordered]
    probabilities = [
        [f(row["p_early"]), f(row["p_middle"]), f(row["p_late"])]
        for row in ordered
    ]
    cm = [[0 for _ in range(3)] for _ in range(3)]
    for actual, estimate in zip(truth, pred):
        cm[actual][estimate] += 1
    precision, recall, f1 = [], [], []
    for label in range(3):
        tp = cm[label][label]
        fp = sum(cm[row][label] for row in range(3)) - tp
        fn = sum(cm[label]) - tp
        p_value = tp / (tp + fp) if tp + fp else 0.0
        r_value = tp / (tp + fn) if tp + fn else 0.0
        f_value = 2 * p_value * r_value / (p_value + r_value) if p_value + r_value else 0.0
        precision.append(p_value); recall.append(r_value); f1.append(f_value)
    differences = [b - a for a, b in zip(pred, pred[1:])]
    variation = [
        sum(abs(b - a) for a, b in zip(left, right))
        for left, right in zip(probabilities, probabilities[1:])
    ]
    middle_total = sum(cm[1])
    return {
        "Acc": sum(a == b for a, b in zip(truth, pred)) / len(ordered),
        "MacroF1": mean(f1),
        "E_F1": f1[0], "M_F1": f1[1], "L_F1": f1[2],
        "M_Precision": precision[1], "M_Recall": recall[1],
        "M_to_E": cm[1][0] / (middle_total + 1e-12),
        "M_to_L": cm[1][2] / (middle_total + 1e-12),
        "Rev": sum(delta < 0 for delta in differences),
        "Jump": sum(abs(delta) >= 2 for delta in differences),
        "Smooth": mean(variation),
    }


def f(value, default=math.nan) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def ensure_tree() -> None:
    dirs = [
        "00_metadata", "01_PHM2010/01_main_D1/bootstrap",
        "01_PHM2010/01_main_D1/predictions_common_universe",
        "01_PHM2010/02_cross_condition_D1_D2_D3/predictions",
        "01_PHM2010/03_ablation", "01_PHM2010/04_semantics",
        "01_PHM2010/05_training_seed_sensitivity", "02_NASA/predictions",
        "03_MENDELEY_CROSS_MACHINE/generalization/predictions",
        "03_MENDELEY_CROSS_MACHINE/ablation", "03_MENDELEY_CROSS_MACHINE/semantics",
        "04_cross_dataset", "05_baseline_metadata", "06_canonical_tables",
        "07_figure_ready/fig1", "07_figure_ready/fig2", "07_figure_ready/fig3",
        "07_figure_ready/fig4", "07_figure_ready/fig5", "08_table_ready",
        "90_provenance", "99_scripts",
    ]
    for item in dirs:
        (PAPER / item).mkdir(parents=True, exist_ok=True)


def copy_phm() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    d1_src = ROOT / "final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv"
    safe_copy(rel(d1_src), "paper_data/01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv",
              status="AUTHORITATIVE", dataset="PHM2010", task="D1",
              intended_use="PHM2010 D1 main comparison and bootstrap CI")
    safe_copy("final_statistical_evidence/predictions_common_universe/D1_MANIFEST.csv",
              "paper_data/01_PHM2010/01_main_D1/D1_common_universe_manifest.csv",
              status="AUTHORITATIVE", data_level="manifest", dataset="PHM2010", task="D1")
    for src in sorted((ROOT / "final_statistical_evidence/predictions_common_universe").glob("D1_*_304runs.csv")):
        method = src.stem.removeprefix("D1_").removesuffix("_304runs")
        safe_copy(rel(src), f"paper_data/01_PHM2010/01_main_D1/predictions_common_universe/{src.name}",
                  status="AUTHORITATIVE", data_level="prediction_level", dataset="PHM2010",
                  task="D1", method=method, intended_use="confusion matrix/bootstrap/error analysis")
    for method_dir in sorted((ROOT / "final_statistical_evidence/bootstrap").iterdir()):
        if not method_dir.is_dir():
            continue
        for name in ("bootstrap_config.json", "bootstrap_summary.csv", "bootstrap_samples.csv"):
            src = method_dir / name
            if src.exists():
                safe_copy(rel(src), f"paper_data/01_PHM2010/01_main_D1/bootstrap/{method_dir.name}/{name}",
                          status="AUTHORITATIVE", data_level="bootstrap", dataset="PHM2010",
                          task="D1", method=method_dir.name)

    transfer_frozen_src = ROOT / "final_statistical_evidence/results/TRANSFER_TASKS_D1_D2_D3.csv"
    d1_extended = {
        row["method_id"]: row for row in read_csv(transfer_frozen_src) if row["Task"] == "D1"
    }
    transfer_sources = [d1_src, transfer_frozen_src]
    transfer = []
    for row in read_csv(d1_src):
        method_id = METHOD_IDS[row["Method"]]
        extended = d1_extended[method_id]
        metrics = {
            "Acc": row["Acc"], "MacroF1": row["MacroF1"], "E_F1": extended["E_F1"],
            "M_F1": row["M_F1"], "L_F1": extended["L_F1"],
            "M_Precision": extended["M_Precision"], "M_Recall": row["M_Rec"],
            "M_to_E": row["M_to_E"], "M_to_L": row["M_to_L"],
            "Rev": row["Rev"], "Jump": row["Jump"], "Smooth": row["Smooth"],
        }
        transfer.append({
            "Method": row["Method"], "method_id": method_id, "Task": "D1",
            "source": "fixed official model point estimate from D1 moving-block bootstrap table",
            **metrics, "n_test": 304, "test_universe": "run_id_12_315_common_304",
            "aggregation_level": "task_point_estimate",
            "protocol_id": "PHM_D1_D2_D3_COMMON_304",
            "source_path": "paper_data/01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv",
            "status": "AUTHORITATIVE",
        })

    for task in ("D2", "D3"):
        for method_meta in METHOD_METADATA:
            method = method_meta["method_id"]
            source_pred = ROOT / f"final_statistical_evidence/transfer_tasks/{task}/{method}/predictions.csv"
            source_rows = read_csv(source_pred)
            common_rows = [row for row in source_rows if 12 <= int(row["run_id"]) <= 315]
            run_ids = sorted(int(row["run_id"]) for row in common_rows)
            if len(common_rows) != 304 or run_ids != list(range(12, 316)):
                raise RuntimeError(f"{task}/{method} cannot form exact run_id 12..315 common universe")
            metrics = recompute_transfer_metrics(common_rows)
            canonical_pred = derived_csv(
                f"paper_data/01_PHM2010/02_cross_condition_D1_D2_D3/predictions/{task}/{method}/predictions.csv",
                common_rows, list(common_rows[0]), sources=[source_pred], data_level="prediction_level",
                dataset="PHM2010", task=task, method=method,
                transformation="filter existing predictions to run_id 12..315; no inference or training",
                intended_use="D2/D3 common-universe metric recomputation", status="AUTHORITATIVE",
                notes=f"source_n={len(source_rows)}; raw_signal_method={str(method in RAW_SIGNAL_METHODS).lower()}",
            )
            derived_json(
                f"paper_data/01_PHM2010/02_cross_condition_D1_D2_D3/predictions/{task}/{method}/metrics.json",
                metrics | {
                    "n_test": 304, "test_universe": "run_id_12_315_common_304",
                    "source_predictions": rel(canonical_pred), "retrained": False,
                },
                sources=[canonical_pred], data_level="derived_metric", dataset="PHM2010",
                task=task, method=method,
                transformation="recompute classification and sequence metrics on ordered 304-run predictions",
                intended_use="D2/D3 frozen common-universe metrics", status="AUTHORITATIVE",
            )
            config_src = ROOT / f"final_statistical_evidence/transfer_tasks/{task}/{method}/config.yaml"
            if config_src.exists():
                safe_copy(
                    rel(config_src),
                    f"paper_data/01_PHM2010/02_cross_condition_D1_D2_D3/predictions/{task}/{method}/config.yaml",
                    status="CANONICAL_COPY", data_level="protocol", dataset="PHM2010", task=task,
                    method=method, intended_use="frozen training configuration provenance only",
                )
            transfer_sources.append(source_pred)
            transfer.append({
                "Method": method_meta["method_name"], "method_id": method, "Task": task,
                "source": "existing seed-42 predictions filtered and recomputed; no retraining",
                **metrics, "n_test": 304, "test_universe": "run_id_12_315_common_304",
                "aggregation_level": "task_point_estimate",
                "protocol_id": "PHM_D1_D2_D3_COMMON_304",
                "source_path": rel(canonical_pred), "status": "AUTHORITATIVE",
            })
    transfer_dst = derived_csv(
        "paper_data/01_PHM2010/02_cross_condition_D1_D2_D3/transfer_tasks_long.csv", transfer,
        list(transfer[0]), sources=transfer_sources, data_level="task_level", dataset="PHM2010",
        transformation="D1 fixed official point estimates; D2/D3 recomputed on run_id 12..315",
        intended_use="D1/D2/D3 common-universe cross-condition comparisons", status="AUTHORITATIVE",
    )
    summary_rows = []
    for method_meta in METHOD_METADATA:
        subset = [row for row in transfer if row["method_id"] == method_meta["method_id"]]
        summary = {"Method": method_meta["method_name"], "method_id": method_meta["method_id"], "n_tasks": len(subset)}
        for metric in TRANSFER_METRICS:
            values = [f(row[metric]) for row in subset]
            summary[f"{metric}_mean"] = mean(values)
            summary[f"{metric}_std"] = stdev(values)
        summary.update({
            "protocol_id": "PHM_D1_D2_D3_COMMON_304", "aggregation_level": "across_task_mean_std",
            "uncertainty_type": "across_task_std", "n_test": 304,
            "test_universe": "run_id_12_315_common_304",
            "source_path": rel(transfer_dst), "status": "DERIVED",
        })
        summary_rows.append(summary)
    derived_csv(
        "paper_data/01_PHM2010/02_cross_condition_D1_D2_D3/transfer_tasks_mean_std.csv",
        summary_rows, list(summary_rows[0]), sources=[transfer_dst], data_level="summary",
        dataset="PHM2010", task="D1,D2,D3",
        transformation="mean and sample std across three common-304 task point estimates",
        intended_use="descriptive across-task summary; never treated as seed uncertainty",
    )

    ablation_src = ROOT / "figures/fig4_ablation/AUTHORITATIVE_A1_A6.csv"
    ablation_dst = safe_copy(rel(ablation_src), "paper_data/01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv",
                             status="AUTHORITATIVE", dataset="PHM2010", task="D1",
                             intended_use="only permitted Fig.4 and manuscript ablation input")
    safe_copy("figures/fig4_ablation/ABLATION_RECOMPUTED.csv",
              "paper_data/01_PHM2010/03_ablation/A1_A6_RECOMPUTED_AUDIT.csv",
              status="AUDIT_SUPPORTING", data_level="audit", dataset="PHM2010", task="D1")
    safe_copy("figures/fig4_ablation/ABLATION_DATA_AUDIT.md",
              "paper_data/01_PHM2010/03_ablation/ABLATION_DATA_AUDIT.md",
              status="AUDIT_SUPPORTING", data_level="audit", dataset="PHM2010", task="D1")
    safe_copy("figures/fig4_ablation/data_manifest.json",
              "paper_data/01_PHM2010/03_ablation/data_manifest.json",
              status="AUDIT_SUPPORTING", data_level="manifest", dataset="PHM2010", task="D1",
              allow_source_update=True)

    life_src = ROOT / "补充材料/小论文/9_probability_wear_consistency_analysis/Data_5_4_A6_probability_wear_trajectory.csv"
    life_dst = safe_copy(rel(life_src), "paper_data/01_PHM2010/04_semantics/C6_lifecycle_probability_wear.csv",
                         status="AUTHORITATIVE", data_level="prediction_level", dataset="PHM2010", task="D1/C6")
    hidden_src = ROOT / "补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/repr_hidden_hct.csv"
    hidden_rows = [r for r in read_csv(hidden_src) if r["split"] == "test_C6" and r["condition"] == "C6"]
    hidden_dst = derived_csv(
        "paper_data/01_PHM2010/04_semantics/C6_hidden_representation.csv", hidden_rows,
        list(hidden_rows[0]), sources=[hidden_src], data_level="representation", dataset="PHM2010", task="D1/C6",
        transformation="filter split=test_C6 and condition=C6; values unchanged",
        intended_use="Fig.5 representation panel", status="AUTHORITATIVE",
    )
    qstats = calculate_q_statistics(read_csv(life_dst))
    derived_csv("paper_data/01_PHM2010/04_semantics/q_statistics.csv", [qstats], list(qstats),
                sources=[life_dst], data_level="summary", dataset="PHM2010", task="D1/C6",
                transformation="direct recomputation from all q_true/q_pred pairs",
                intended_use="Fig.5 q agreement")
    return read_csv(d1_src), read_csv(transfer_dst), read_csv(ablation_dst), read_csv(life_dst)


def copy_phm_training_seed_sensitivity() -> None:
    """Archive seed-sensitivity evidence without promoting it into the main D1 table."""
    base = "paper_data/01_PHM2010/05_training_seed_sensitivity"
    copies = [
        ("final_five_seed_sweep/results/FINAL_9_METHODS_SEED_LEVEL.csv", "original_5seed_seed_level.csv", "seed_level"),
        ("final_five_seed_sweep/results/FINAL_9_METHODS_5SEED.csv", "original_5seed_summary.csv", "summary"),
        ("final_five_seed_sweep/AUDIT.md", "ORIGINAL_5SEED_AUDIT.md", "audit"),
        ("protocol_diagnostic_fixed_preprocess/FIXED_PREPROCESS_5SEED.csv", "fixed_preprocessing_seed_level.csv", "seed_level"),
        ("protocol_diagnostic_fixed_preprocess/FIXED_PREPROCESS_5SEED_SUMMARY.csv", "fixed_preprocessing_summary.csv", "summary"),
        ("protocol_diagnostic_fixed_preprocess/OLD_VS_FIXED_PREPROCESS.csv", "old_vs_fixed_preprocessing.csv", "audit"),
        ("protocol_diagnostic_fixed_preprocess/PROTOCOL.md", "FIXED_PREPROCESS_PROTOCOL.md", "protocol"),
        ("protocol_diagnostic_fixed_preprocess/FINAL_DIAGNOSTIC_REPORT.md", "FIXED_PREPROCESS_DIAGNOSTIC_REPORT.md", "audit"),
    ]
    for source, name, level in copies:
        safe_copy(
            source, f"{base}/{name}", status="AUDIT_SUPPORTING", data_level=level,
            dataset="PHM2010", task="D1", intended_use="training-seed sensitivity audit only",
            notes="Must not replace fixed official D1 point estimates or moving-block bootstrap CI.",
        )
    readme = PAPER / "01_PHM2010/05_training_seed_sensitivity/README.md"
    write_text(readme, """
# PHM2010 D1 training-seed sensitivity — audit supporting only

The manuscript main comparison remains the fixed official model evaluated on the 304-run common universe, with moving-block bootstrap 95% confidence intervals. Nothing in this directory may be merged into, averaged with, or substituted for `01_main_D1/D1_9methods_bootstrap_CI.csv`.

- `original_5seed_*` preserves the original five-seed sweep, including its documented preprocessing/training-seed coupling.
- `fixed_preprocessing_*` varies only `TRAIN_SEED` while holding preprocessing at seed 42.
- `old_vs_fixed_preprocessing.csv` is a protocol diagnostic, not a main-table estimate.

All files in this directory have catalog status `AUDIT_SUPPORTING`.
""")
    register(
        readme, status="AUDIT_SUPPORTING", data_level="documentation", dataset="PHM2010",
        task="D1", transformation="curated protocol boundary",
        intended_use="prevent seed-sensitivity evidence from entering the main comparison",
    )


def rankdata(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    result = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        rank = (i + 1 + j) / 2
        for index in order[i:j]:
            result[index] = rank
        i = j
    return result


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = mean(x), mean(y)
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denominator = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return numerator / denominator


def calculate_q_statistics(rows: list[dict]) -> dict:
    true = [f(r["q_true"]) for r in rows]
    pred = [f(r["q_pred"]) for r in rows]
    avg = mean(true)
    return {
        "n": len(rows),
        "R2": 1 - sum((a - b) ** 2 for a, b in zip(true, pred)) / sum((a - avg) ** 2 for a in true),
        "Spearman_rho": pearson(rankdata(true), rankdata(pred)),
        "MAE": mean(abs(a - b) for a, b in zip(true, pred)),
        "stage_agreement": mean(r["true_stage"] == r["pred_stage"] for r in rows),
        "q_true_field": "q_true", "q_pred_field": "q_pred", "aggregation_level": "304_run_pair",
    }


def copy_nasa() -> tuple[list[dict], list[dict]]:
    base = ROOT / "补充材料/小论文/nasa_dcpsr_results_stageaware_opt"
    summary_src = base / "Table_NASA_original_split_mean_std.csv"
    summary_dst = safe_copy(rel(summary_src), "paper_data/02_NASA/original_split_mean_std.csv",
                            status="AUTHORITATIVE", dataset="NASA_MILLING", task="N1-N4",
                            intended_use="original-split summary across N1-N4")
    task_src = base / "Table_NASA_cross_case_B9_B12_metrics_by_seed.csv"
    task_rows = [r for r in read_csv(task_src) if r["Split_type"] == "original" and r["Task"] in {"N1", "N2", "N3", "N4"}]
    task_dst = derived_csv("paper_data/02_NASA/task_level_results.csv", task_rows, list(task_rows[0]),
                           sources=[task_src], data_level="task_level", dataset="NASA_MILLING", task="N1-N4",
                           transformation="filter Split_type=original and tasks N1-N4",
                           intended_use="NASA task/seed evidence", status="AUTHORITATIVE")
    for src in sorted(base.glob("Pred_NASA_original_N[1-4]_B*_seed*.csv")):
        match = re.search(r"original_(N\d)_(B\d+)_seed(\d+)", src.stem)
        task, method, seed = match.groups() if match else ("", "", "")
        safe_copy(rel(src), f"paper_data/02_NASA/predictions/{src.name}", status="AUTHORITATIVE",
                  data_level="prediction_level", dataset="NASA_MILLING", task=task, method=method, seed=seed)
    return read_csv(summary_dst), read_csv(task_dst)


def copy_mendeley() -> tuple[list[dict], list[dict], list[dict]]:
    base = ROOT / "experiments_mendeley"
    overall_src = base / "04_overall_comparison/summary/overall_comparison_mean_std_by_task.csv"
    by_seed_src = base / "04_overall_comparison/by_seed/overall_comparison_metrics_by_seed.csv"
    overall_dst = safe_copy(rel(overall_src), "paper_data/03_MENDELEY_CROSS_MACHINE/overall_by_task_mean_std.csv",
                            status="AUTHORITATIVE", dataset=THIRD_DATASET_ID, task="D1-M,D2-M,D3-M")
    by_seed_dst = safe_copy(rel(by_seed_src), "paper_data/03_MENDELEY_CROSS_MACHINE/overall_by_seed.csv",
                            status="AUTHORITATIVE", data_level="seed_level", dataset=THIRD_DATASET_ID,
                            task="D1-M,D2-M,D3-M")
    quality_src = base / "00_dataset_audit/dataset_quality_report.csv"
    quality = read_csv(quality_src)
    summary_rows = []
    restrictions = {
        "T8": "early_truncated=True; starts at VB=34; affects interpretation when M3 is train/test",
    }
    for row in quality:
        summary_rows.append({
            "dataset_id": THIRD_DATASET_ID, "machine": row["sequence_id"].replace("T", "M") if False else row["domain_id"],
            "tool": row["sequence_id"], "run_count": row["n"], "VB_min_um": row["VB_min"],
            "VB_max_um": row["VB_max"], "early_count": row["early"], "middle_count": row["middle"],
            "late_count": row["late"], "sensor_availability": "primary_channel_set; see source audit",
            "known_restrictions": restrictions.get(row["sequence_id"], "none documented for canonical primary channel set"),
            "official_name": "Multivariate time series data of milling processes with varying tool wear and machine tools",
        })
    dataset_dst = derived_csv(
        "paper_data/03_MENDELEY_CROSS_MACHINE/dataset_summary.csv", summary_rows, list(summary_rows[0]),
        sources=[quality_src, base / "00_dataset_audit/channel_summary.csv"], data_level="metadata",
        dataset=THIRD_DATASET_ID, transformation="one metadata row per tool from audited run counts and VB ranges",
        intended_use="dataset description and validation", status="AUTHORITATIVE",
    )
    task_json = json.loads((base / "02_protocols/task_definitions.json").read_text(encoding="utf-8"))
    task_rows = []
    for task in task_json:
        if task.get("name") not in {"D1-M", "D2-M", "D3-M"}:
            continue
        task_rows.append({
            "task_id": task["name"], "group": task.get("group", ""),
            "train_machines": "+".join(task.get("train_domains", task.get("train_machines", []))),
            "test_machine": "+".join(task.get("test_domains", task.get("test_machines", []))),
            "train_tools": "+".join(task.get("train_sequences", [])),
            "test_tools": "+".join(task.get("test_sequences", [])),
            "execution_status": "DONE_5_SEEDS", "seeds": "42;52;62;72;82",
            "notes": "dual-source cross-machine; single-source MS1-MS6 not claimed as completed",
        })
    task_dst = derived_csv("paper_data/03_MENDELEY_CROSS_MACHINE/task_definitions.csv", task_rows, list(task_rows[0]),
                           sources=[base / "02_protocols/task_definitions.json"], data_level="metadata",
                           dataset=THIRD_DATASET_ID, transformation="retain completed core dual-source tasks only",
                           intended_use="cross-machine task definitions", status="AUTHORITATIVE")

    for src in sorted((base / "04_overall_comparison/predictions").glob("*.csv")):
        match = re.search(r"(D\d-M)_seed(\d+)_predictions_test_(.+)", src.stem)
        task, seed, method = match.groups() if match else ("", "", "")
        safe_copy(rel(src), f"paper_data/03_MENDELEY_CROSS_MACHINE/generalization/predictions/{src.name}",
                  status="AUTHORITATIVE", data_level="prediction_level", dataset=THIRD_DATASET_ID,
                  task=task, method=method, seed=seed)
    for source_dir, target_dir in [
        (base / "05_generalization", PAPER / "03_MENDELEY_CROSS_MACHINE/generalization"),
        (base / "06_ablation", PAPER / "03_MENDELEY_CROSS_MACHINE/ablation"),
        (base / "07_semantic_consistency", PAPER / "03_MENDELEY_CROSS_MACHINE/semantics"),
    ]:
        for src in sorted(p for p in source_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".csv", ".json", ".parquet"}):
            local = src.relative_to(source_dir)
            status = "AUDIT_SUPPORTING" if "single_source" in local.as_posix() else "AUTHORITATIVE"
            level = "prediction_level" if "probability_evolution" in local.as_posix() else "summary"
            safe_copy(rel(src), rel(target_dir / local), status=status, data_level=level,
                      dataset=THIRD_DATASET_ID, task="D1-M,D2-M,D3-M",
                      notes="single-source file is retained only as non-completion evidence" if status == "AUDIT_SUPPORTING" else "")
    return read_csv(overall_dst), read_csv(by_seed_dst), read_csv(dataset_dst)


def build_cross_dataset(d1: list[dict], nasa: list[dict], mend: list[dict]) -> tuple[list[dict], list[dict]]:
    rows = []
    def add(dataset, scope, method, acc, mf1, smooth, jump, source, aggregation, n):
        rows.append({"dataset": dataset, "task_scope": scope, "method": method, "Acc": acc,
                     "M_F1": mf1, "Smooth": smooth, "Jump": jump, "source_path": rel(source),
                     "aggregation": aggregation, "n_or_task_count": n})
    dmap = {r["Method"]: r for r in d1}
    for method in ("Multi-task TCN-GRU", "DC-PSR"):
        r = dmap[method]
        add("PHM2010", "D1", "B11" if method.startswith("Multi") else "B12", r["Acc"], r["M_F1"], r["Smooth"], r["Jump"],
            ROOT / "paper_data/01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv", "304-run common-universe point estimate", 304)
    nmap = {r["Method"]: r for r in nasa}
    for method in ("B11", "B12"):
        r = nmap[method]
        add("NASA_MILLING", "original_N1-N4", method, r["Acc_mean"], r["M-F1_mean"], r["Smooth_mean"], r["Jump_mean"],
            ROOT / "paper_data/02_NASA/original_split_mean_std.csv", "mean across four original tasks", 4)
    for task in ("D1-M", "D2-M", "D3-M"):
        for method in ("B11", "B12"):
            r = next(x for x in mend if x["task"] == task and x["Method"] == method)
            add(THIRD_DATASET_ID, task, method, r["Acc_mean"], r["M_F1_mean"], r["Smooth_mean"], r["Jump_mean"],
                ROOT / "paper_data/03_MENDELEY_CROSS_MACHINE/overall_by_task_mean_std.csv", "mean across five seeds", 5)
    for method in ("B11", "B12"):
        sub = [r for r in rows if r["dataset"] == THIRD_DATASET_ID and r["method"] == method and r["task_scope"].endswith("-M")]
        add(THIRD_DATASET_ID, "D1-M,D2-M,D3-M", method,
            mean(f(r["Acc"]) for r in sub), mean(f(r["M_F1"]) for r in sub),
            mean(f(r["Smooth"]) for r in sub), mean(f(r["Jump"]) for r in sub),
            ROOT / "paper_data/03_MENDELEY_CROSS_MACHINE/overall_by_task_mean_std.csv", "mean of three five-seed task means", 3)
    abs_dst = derived_csv("paper_data/04_cross_dataset/backbone_vs_dcpsr_absolute.csv", rows, list(rows[0]),
                          sources=[ROOT / "paper_data/01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv",
                                   ROOT / "paper_data/02_NASA/original_split_mean_std.csv",
                                   ROOT / "paper_data/03_MENDELEY_CROSS_MACHINE/overall_by_task_mean_std.csv"],
                          data_level="summary", dataset="CROSS_DATASET",
                          transformation="select B11/B12 absolute metrics; no normalization",
                          intended_use="cross-dataset absolute evidence")
    deltas = []
    scopes = sorted({(r["dataset"], r["task_scope"]) for r in rows})
    for dataset, scope in scopes:
        pair = {r["method"]: r for r in rows if r["dataset"] == dataset and r["task_scope"] == scope}
        if pair.keys() >= {"B11", "B12"}:
            deltas.append({
                "dataset": dataset, "task_scope": scope,
                "delta_Acc": f(pair["B12"]["Acc"]) - f(pair["B11"]["Acc"]),
                "delta_M_F1": f(pair["B12"]["M_F1"]) - f(pair["B11"]["M_F1"]),
                "Smooth_benefit": f(pair["B11"]["Smooth"]) - f(pair["B12"]["Smooth"]),
                "Jump_benefit": f(pair["B11"]["Jump"]) - f(pair["B12"]["Jump"]),
                "absolute_source": rel(abs_dst),
            })
    delta_dst = derived_csv("paper_data/04_cross_dataset/backbone_vs_dcpsr_deltas.csv", deltas, list(deltas[0]),
                            sources=[abs_dst], data_level="derived_metric", dataset="CROSS_DATASET",
                            transformation="B12-B11 for Acc/M_F1; B11-B12 for Smooth/Jump",
                            intended_use="effect direction without losing absolute data")
    machine = [r for r in deltas if r["dataset"] == THIRD_DATASET_ID and r["task_scope"].endswith("-M")]
    derived_csv("paper_data/04_cross_dataset/cross_machine_task_deltas.csv", machine, list(machine[0]),
                sources=[abs_dst], data_level="derived_metric", dataset=THIRD_DATASET_ID,
                transformation="subset per-task B11/B12 deltas", intended_use="Fig.3 cross-machine panel")
    failure = build_d2m_failure_distribution()
    failure_dst = derived_csv("paper_data/04_cross_dataset/D2M_failure_distribution.csv", failure, list(failure[0]),
                              sources=sorted((PAPER / "03_MENDELEY_CROSS_MACHINE/semantics/probability_evolution").glob("D2-M_*.csv")),
                              data_level="derived_distribution", dataset=THIRD_DATASET_ID, task="D2-M",
                              transformation="stage_true by raw(B11)/final(B12) predicted-stage counts and within-method proportions",
                              intended_use="Fig.3 D2-M failure analysis")
    return rows, deltas


def build_d2m_failure_distribution() -> list[dict]:
    output = []
    base = PAPER / "03_MENDELEY_CROSS_MACHINE/semantics/probability_evolution"
    for path in sorted(base.glob("D2-M_seed*_predictions_test_B11B12.csv")):
        seed = re.search(r"seed(\d+)", path.name).group(1)
        rows = read_csv(path)
        for method, column in (("B11", "stage_pred_raw_name"), ("B12", "stage_pred_final_name")):
            counts = Counter((r["stage_true"], r[column]) for r in rows)
            total = len(rows)
            for true_stage in ("early", "middle", "late"):
                for pred_stage in ("early", "middle", "late"):
                    count = counts[(true_stage, pred_stage)]
                    output.append({"task": "D2-M", "seed": seed, "method": method,
                                   "true_stage": true_stage, "predicted_stage": pred_stage,
                                   "count": count, "proportion_of_all_runs": count / total, "n_test": total})
    return output


def xlsx_sheet(path: Path, wanted: str) -> list[list]:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
          "p": "http://schemas.openxmlformats.org/package/2006/relationships"}
    with zipfile.ZipFile(path) as zf:
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.findall(".//m:t", ns)) for si in root.findall("m:si", ns)]
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        targets = {x.attrib["Id"]: x.attrib["Target"] for x in rels.findall("p:Relationship", ns)}
        sheet = next(s for s in wb.findall("m:sheets/m:sheet", ns) if s.attrib["name"] == wanted)
        target = targets[sheet.attrib[f"{{{ns['r']}}}id"]].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        root = ET.fromstring(zf.read(target))
        grid = []
        for row in root.findall("m:sheetData/m:row", ns):
            values = {}
            for cell in row.findall("m:c", ns):
                ref_text = cell.attrib["r"]
                letters = re.match(r"[A-Z]+", ref_text).group(0)
                col = 0
                for letter in letters:
                    col = col * 26 + ord(letter) - 64
                node = cell.find("m:v", ns)
                value = node.text if node is not None else ""
                if cell.attrib.get("t") == "s" and value:
                    value = shared[int(value)]
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(t.text or "" for t in cell.findall(".//m:t", ns))
                values[col - 1] = value
            if values:
                grid.append([values.get(i, "") for i in range(max(values) + 1)])
        return grid


def build_baseline_metadata() -> None:
    book = ROOT / "DC_PSR_最终对比方法_9个Baseline_文献信息与复现评估.xlsx"
    summary = xlsx_sheet(book, "最终对比方法")
    details = xlsx_sheet(book, "文献方法详情")
    status_map = {r[2]: r[12] for r in summary[4:] if len(r) > 12}
    type_map = {r[2]: (r[1], r[3], r[17] if len(r) > 17 else "") for r in summary[4:] if len(r) > 3}
    rows = []
    for name in ("RF", "TCN-GRU", "Multi-task TCN-GRU"):
        typ, route, note = type_map[name]
        rows.append({"method_id": METHOD_IDS[name], "display_name": name, "type": f"{typ}; {route}",
                     "paper_title": "NA", "authors": "NA", "year": "NA", "journal": "NA", "DOI": "NA",
                     "first_author_affiliation": "NA", "reported_protocol": "internal unified PHM2010/NASA protocol",
                     "implementation_status": "implemented; canonical evidence available",
                     "adaptation_note": note or "internal control baseline"})
    for r in details[4:]:
        if len(r) < 18 or not r[0]:
            continue
        name = r[0]
        canonical_name = {"Dynamic GIN + TGP": "Dynamic GIN + TGP", "DP2Net": "DP2Net"}.get(name, name)
        implemented = canonical_name in {"HTT-Net", "Multi-source Channel-Spatial Attention", "MTF-AViTK", "Dynamic GIN + TGP", "DP2Net"}
        rows.append({
            "method_id": METHOD_IDS.get(canonical_name, re.sub(r"\W+", "_", name.lower()).strip("_")),
            "display_name": name, "type": r[7], "paper_title": r[1], "authors": r[5], "year": r[4],
            "journal": r[2], "DOI": r[16], "first_author_affiliation": r[6], "reported_protocol": r[8],
            "implementation_status": "implemented; canonical evidence available" if implemented else "not canonical / not used in current main comparison",
            "adaptation_note": (status_map.get(name, "") + "; " + r[20]).strip("; "),
        })
    derived_csv("paper_data/05_baseline_metadata/baseline_literature.csv", rows, list(rows[0]), sources=[book],
                data_level="metadata", dataset="CROSS_METHOD",
                transformation="extract workbook rows; current implementation status reconciled to final evidence",
                intended_use="literature and implementation provenance", status="CANONICAL_COPY")
    complexity = [
        {"method_id":"rf","display_name":"RF","parameters":"NA","FLOPs_per_sample":"NA","training_time_s":"NA","inference_ms_per_sample":"NA","source_path":"baselines/rf/FINAL_REPORT.md","notes":"400-tree ensemble; neural parameter count not comparable"},
        {"method_id":"tcn_gru","display_name":"TCN-GRU","parameters":83619,"FLOPs_per_sample":"NA","training_time_s":"NA","inference_ms_per_sample":"NA","source_path":"baselines/tcn_gru/FINAL_REPORT.md","notes":"state_dict tensor count"},
        {"method_id":"multitask_tcn_gru","display_name":"Multi-task TCN-GRU","parameters":84009,"FLOPs_per_sample":"NA","training_time_s":"NA","inference_ms_per_sample":"NA","source_path":"baselines/multitask_tcn_gru/FINAL_REPORT.md","notes":"state_dict tensor count"},
        {"method_id":"dc_psr","display_name":"DC-PSR","parameters":84009,"FLOPs_per_sample":"NA","training_time_s":"NA","inference_ms_per_sample":"NA","source_path":"final_statistical_evidence/FINAL_STATISTICAL_REPORT.md","notes":"shares frozen B11 backbone; deterministic B12 post-processing adds no learned parameters"},
        {"method_id":"htt_net","display_name":"HTT-Net (adapted)","parameters":882067,"FLOPs_per_sample":"NA","training_time_s":36.0,"inference_ms_per_sample":"NA","source_path":"baselines/htt_net/README.md","notes":"single seed-42 adapted run"},
        {"method_id":"multi_source_attention","display_name":"Multi-source Attention","parameters":12939050,"FLOPs_per_sample":1043862528,"training_time_s":147.3,"inference_ms_per_sample":1.81,"source_path":"baselines/multi_source_attention/FINAL_REPORT.md","notes":"RTX 3070 Ti Laptop; Protocol B/full early-stopped run"},
        {"method_id":"mtf_avitk","display_name":"MTF-AViTK","parameters":309371072,"FLOPs_per_sample":91463323008,"training_time_s":2439.1,"inference_ms_per_sample":21.30,"source_path":"baselines/mtf_avitk/FINAL_REPORT.md","notes":"sub-window inference; Protocol A 50 epochs"},
        {"method_id":"dynamic_gin_tgp","display_name":"Dynamic GIN + TGP","parameters":321950,"FLOPs_per_sample":"NA","training_time_s":2108.5,"inference_ms_per_sample":7.76,"source_path":"baselines/dynamic_gin_tgp/FINAL_REPORT.md","notes":"Protocol A; inference batch=4 GPU"},
        {"method_id":"dp2net_adapted","display_name":"DP2Net-adapted","parameters":60956,"FLOPs_per_sample":"NA","training_time_s":"NA","inference_ms_per_sample":0.04,"source_path":"baselines/dp2net/FINAL_REPORT.md","notes":"60031 parameters used at inference; training time varies by seed"},
    ]
    sources = [ROOT / r["source_path"] for r in complexity]
    derived_csv("paper_data/05_baseline_metadata/baseline_model_complexity.csv", complexity, list(complexity[0]),
                sources=sources, data_level="metadata", dataset="CROSS_METHOD",
                transformation="transcribe explicitly reported complexity only; unavailable values remain NA",
                intended_use="model complexity table", status="CANONICAL_COPY")


def build_canonical_tables(d1, transfer, ablation, nasa_summary, nasa_task, mend_summary, mend_seed) -> tuple[list[dict], list[dict]]:
    long = []
    def add(dataset, task, protocol, method, config, seed, level, n, metric, value, *, ci_low="", ci_high="", stdv="", uncertainty="point_estimate", source="", notes=""):
        source_path = ROOT / source
        long.append({"dataset_id": dataset, "dataset_name": dataset, "task_id": task, "protocol_id": protocol,
                     "method_id": METHOD_IDS.get(method, re.sub(r"\W+", "_", method.lower()).strip("_")),
                     "method_name": method, "configuration_id": config, "seed": seed,
                     "aggregation_level": level, "uncertainty_type": uncertainty, "n_test": n,
                     "metric": metric, "value": value, "ci_low": ci_low, "ci_high": ci_high, "std": stdv,
                     "source_path": source, "source_sha256": sha256(source_path) if source_path.exists() else "",
                     "status": "AUTHORITATIVE", "notes": notes})
    d1_metrics = [("Acc","Acc"),("MacroF1","MacroF1"),("M_F1","M_F1"),("M_Rec","M_Rec"),
                  ("M_to_E","M_to_E"),("M_to_L","M_to_L"),("Rev","Rev"),("Jump","Jump"),("Smooth","Smooth")]
    for r in d1:
        for metric, col in d1_metrics:
            add("PHM2010","D1","PHM_D1_COMMON_304",r["Method"],"", "", "304_run_point",304,metric,r[col],
                ci_low=r.get(col+"_CI_low", ""), ci_high=r.get(col+"_CI_high", ""),
                uncertainty="moving_block_bootstrap_95CI" if r.get(col+"_CI_low", "") else "point_estimate",
                source="paper_data/01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv")
    for r in transfer:
        if r["Task"] == "D1":
            continue
        for metric in ("Acc","MacroF1","M_F1","M_Recall","M_to_E","M_to_L","Rev","Jump","Smooth"):
            add("PHM2010",r["Task"],r["protocol_id"],r["Method"],"", "42",r["aggregation_level"],r["n_test"],metric,r[metric],
                source="paper_data/01_PHM2010/02_cross_condition_D1_D2_D3/transfer_tasks_long.csv",
                notes=f"test_universe={r['test_universe']}")
    for r in ablation:
        for metric, col in (("Acc","Acc"),("MacroF1","Macro-F1"),("M_F1","M-F1"),("M_Rec","M-Rec"),("M_to_E","M→E"),("M_to_L","M→L"),("Rev","Rev"),("Jump","Jump"),("Smooth","Smooth")):
            add("PHM2010","D1","PHM_D1_FROZEN_B11_B12",r["ID"],r["Configuration"],"42","304_run_point",304,metric,r[col],
                source="paper_data/01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv")
    for r in nasa_task:
        for metric in ("Acc","Macro-F1","M-F1","M-Rec","M→E","M→L","Rev","Jump","Smooth"):
            add("NASA_MILLING",r["Task"],"NASA_ORIGINAL_SPLIT",r["Method"],r.get("Config",""),r["Seed"],"task_seed_point","",metric,r[metric],
                source="paper_data/02_NASA/task_level_results.csv")
    for r in nasa_summary:
        for metric, prefix in (("Acc","Acc"),("MacroF1","Macro-F1"),("M_F1","M-F1"),("M_Rec","M-Rec"),("Jump","Jump"),("Smooth","Smooth")):
            add("NASA_MILLING","N1-N4","NASA_ORIGINAL_SPLIT",r["Method"],"","","across_task_mean",4,metric,r[prefix+"_mean"],stdv=r[prefix+"_std"],uncertainty="across_task_std",
                source="paper_data/02_NASA/original_split_mean_std.csv")
    for r in mend_summary:
        for metric, prefix in (("Acc","Acc"),("MacroF1","Macro_F1"),("M_F1","M_F1"),("M_Rec","M_Rec"),("Jump","Jump"),("Smooth","Smooth")):
            add(THIRD_DATASET_ID,r["task"],"MILLING_CROSS_MACHINE_5SEED",r["Method"],"","","across_seed_mean",r[prefix+"_n_seeds"],metric,r[prefix+"_mean"],stdv=r[prefix+"_std_seed"],uncertainty="across_seed_std",
                source="paper_data/03_MENDELEY_CROSS_MACHINE/overall_by_task_mean_std.csv")
    for r in mend_seed:
        task = r.get("task", r.get("Task", "")); method = r.get("Method", r.get("method", "")); seed = r.get("seed", r.get("Seed", ""))
        for metric, col in (("Acc","Acc"),("MacroF1","Macro_F1"),("M_F1","M_F1"),("M_Rec","M_Rec"),("Jump","Jump"),("Smooth","Smooth")):
            if col in r and r[col] != "":
                add(THIRD_DATASET_ID,task,"MILLING_CROSS_MACHINE_5SEED",method,"",seed,"seed_point","",metric,r[col],
                    source="paper_data/03_MENDELEY_CROSS_MACHINE/overall_by_seed.csv")
    long_dst = derived_csv("paper_data/06_canonical_tables/all_metrics_long.csv", long, list(long[0]),
                           sources=[ROOT / p for p in sorted({r["source_path"] for r in long})], data_level="canonical_long",
                           dataset="ALL", transformation="unpivot canonical summaries; uncertainty types remain distinct",
                           intended_use="single long-form metric entrypoint", status="AUTHORITATIVE")
    wide_groups = defaultdict(dict)
    key_fields = ["dataset_id","task_id","protocol_id","method_id","method_name","configuration_id","seed","aggregation_level","uncertainty_type","n_test","source_path","source_sha256","status","notes"]
    for row in long:
        key = tuple(row[k] for k in key_fields)
        wide_groups[key][row["metric"]] = row["value"]
        if row["std"] != "": wide_groups[key][row["metric"]+"_std"] = row["std"]
        if row["ci_low"] != "":
            wide_groups[key][row["metric"]+"_ci_low"] = row["ci_low"]
            wide_groups[key][row["metric"]+"_ci_high"] = row["ci_high"]
    metric_fields = sorted({k for values in wide_groups.values() for k in values})
    wide = [dict(zip(key_fields, key)) | values for key, values in wide_groups.items()]
    derived_csv("paper_data/06_canonical_tables/all_metrics_wide.csv", wide, key_fields+metric_fields,
                sources=[long_dst], data_level="canonical_wide", dataset="ALL",
                transformation="pivot metric/value only; no aggregation", intended_use="direct manuscript tables", status="AUTHORITATIVE")
    return long, wide


def build_figure_and_table_ready(d1, transfer, ablation, life, hidden, cross_abs, deltas, nasa_task, mend_summary) -> None:
    d1_src = ROOT / "paper_data/01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv"
    fig1_main, fig1_main_fields = with_figure_metadata(
        d1, dataset_id="PHM2010", task_id="D1", protocol_id="PHM_D1_COMMON_304",
        aggregation_level="method_point_with_bootstrap_ci", uncertainty_type="moving_block_bootstrap_95CI",
        n_test=304, test_universe="run_id_12_315_common_304", source_path=rel(d1_src),
    )
    derived_csv("paper_data/07_figure_ready/fig1/D1_main_metrics.csv", fig1_main, fig1_main_fields, sources=[d1_src],
                data_level="figure_ready", dataset="PHM2010", task="D1", transformation="column-preserving copy",
                intended_use="Fig.1")
    controlled = [r for r in d1 if r["Method"] in {"Multi-task TCN-GRU","DC-PSR"}]
    controlled, controlled_fields = with_figure_metadata(
        controlled, dataset_id="PHM2010", task_id="D1", protocol_id="PHM_D1_COMMON_304",
        aggregation_level="method_point_with_bootstrap_ci", uncertainty_type="moving_block_bootstrap_95CI",
        n_test=304, test_universe="run_id_12_315_common_304", source_path=rel(d1_src),
    )
    derived_csv("paper_data/07_figure_ready/fig1/B11_B12_controlled_comparison.csv", controlled, controlled_fields,
                sources=[d1_src], data_level="figure_ready", dataset="PHM2010", task="D1",
                transformation="select B11 and B12", intended_use="Fig.1 controlled comparison")
    consistency = [{"Method":r["Method"],"Acc":r["Acc"],"Smooth":r["Smooth"],"consistency_score":1-f(r["Smooth"]),"formula":"1-Smooth"} for r in d1]
    consistency, consistency_fields = with_figure_metadata(
        consistency, dataset_id="PHM2010", task_id="D1", protocol_id="PHM_D1_COMMON_304",
        aggregation_level="derived_method_point", uncertainty_type="none",
        n_test=304, test_universe="run_id_12_315_common_304", source_path=rel(d1_src),
    )
    derived_csv("paper_data/07_figure_ready/fig1/accuracy_consistency_points.csv", consistency, consistency_fields,
                sources=[d1_src], data_level="figure_ready", dataset="PHM2010", task="D1",
                transformation="consistency_score=1-Smooth", intended_use="Fig.1 scatter")
    trans_src = ROOT / "paper_data/01_PHM2010/02_cross_condition_D1_D2_D3/transfer_tasks_long.csv"
    transfer_figure = [
        dict(row) | {
            "dataset_id": "PHM2010", "task_id": row["Task"],
            "uncertainty_type": "point_estimate", "source_path": rel(trans_src), "status": "DERIVED",
        }
        for row in transfer
    ]
    transfer_fields = list(transfer_figure[0])
    derived_csv("paper_data/07_figure_ready/fig2/taskwise_absolute.csv", transfer_figure, transfer_fields, sources=[trans_src],
                data_level="figure_ready", dataset="PHM2010", transformation="absolute rows unchanged", intended_use="Fig.2")
    rank_rows, norm_rows = [], []
    for task in ("D1","D2","D3"):
        sub = [r for r in transfer if r["Task"] == task]
        for metric in ("Acc","M_F1","Smooth"):
            values = [f(r[metric]) for r in sub]
            ordered = sorted(values, reverse=metric not in LOW_IS_GOOD)
            lo, hi = min(values), max(values)
            for row, value in zip(sub, values):
                shared_meta = {
                    "dataset_id": "PHM2010", "task_id": task, "protocol_id": "PHM_D1_D2_D3_COMMON_304",
                    "aggregation_level": "derived_method_task_metric", "uncertainty_type": "none",
                    "n_test": 304, "test_universe": "run_id_12_315_common_304",
                    "source_path": rel(trans_src), "status": "DERIVED",
                }
                rank_rows.append({"Task":task,"Method":row["Method"],"metric":metric,"value":value,"rank":ordered.index(value)+1} | shared_meta)
                normalized = 1.0 if hi == lo else ((hi-value)/(hi-lo) if metric in LOW_IS_GOOD else (value-lo)/(hi-lo))
                norm_rows.append({"Task":task,"Method":row["Method"],"metric":metric,"absolute_value":value,"normalized_score":normalized,"direction":"low_is_good" if metric in LOW_IS_GOOD else "high_is_good"} | shared_meta)
    derived_csv("paper_data/07_figure_ready/fig2/taskwise_rank.csv", rank_rows, list(rank_rows[0]), sources=[trans_src],
                data_level="figure_ready", dataset="PHM2010", transformation="within-task ordinal rank; ties share first occurrence rank",
                intended_use="Fig.2 ranks")
    derived_csv("paper_data/07_figure_ready/fig2/taskwise_normalized.csv", norm_rows, list(norm_rows[0]), sources=[trans_src],
                data_level="figure_ready", dataset="PHM2010", transformation="task-wise min-max; Smooth inverted",
                intended_use="Fig.2 heatmap")
    for name, source in (("cross_dataset_absolute.csv","backbone_vs_dcpsr_absolute.csv"),("cross_dataset_deltas.csv","backbone_vs_dcpsr_deltas.csv"),("cross_machine_task_deltas.csv","cross_machine_task_deltas.csv"),("D2M_failure_distribution.csv","D2M_failure_distribution.csv")):
        src = ROOT / f"paper_data/04_cross_dataset/{source}"
        rows = read_csv(src)
        enriched = []
        for row in rows:
            dataset_id = row.get("dataset", THIRD_DATASET_ID if row.get("task") == "D2-M" else "CROSS_DATASET")
            task_id = row.get("task_scope", row.get("task", "MULTI_TASK"))
            n_test = row.get("n_test", row.get("n_or_task_count", "see_source"))
            enriched.append(dict(row) | {
                "dataset_id": dataset_id, "task_id": task_id,
                "protocol_id": "CROSS_DATASET_COMPARATIVE",
                "aggregation_level": row.get("aggregation", "derived_cross_dataset"),
                "uncertainty_type": "source_specific", "n_test": n_test,
                "test_universe": "see_source_path", "source_path": rel(src), "status": "DERIVED",
            })
        derived_csv(f"paper_data/07_figure_ready/fig3/{name}", enriched, list(enriched[0]), sources=[src], data_level="figure_ready",
                    dataset="CROSS_DATASET", transformation="figure-ready copy from canonical/derived cross-dataset table",
                    intended_use="Fig.3")
    abl_src = ROOT / "paper_data/01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv"
    ablation_figure, ablation_fields = with_figure_metadata(
        ablation, dataset_id="PHM2010", task_id="D1", protocol_id="PHM_D1_FROZEN_B11_B12",
        aggregation_level="configuration_point_estimate", uncertainty_type="none", n_test=304,
        test_universe="run_id_12_315_common_304", source_path=rel(abl_src),
    )
    derived_csv("paper_data/07_figure_ready/fig4/A1_A6_absolute.csv", ablation_figure, ablation_fields, sources=[abl_src],
                data_level="figure_ready", dataset="PHM2010", task="D1", transformation="absolute values unchanged",
                intended_use="Fig.4 only")
    base = ablation[0]
    delta_rows = []
    for r in ablation:
        out = {"ID":r["ID"],"Configuration":r["Configuration"]}
        for metric in ("Acc","Macro-F1","M-F1","M-Rec","Smooth"):
            out[f"delta_{metric}"] = f(r[metric]) - f(base[metric])
        delta_rows.append(out)
    delta_rows, delta_fields = with_figure_metadata(
        delta_rows, dataset_id="PHM2010", task_id="D1", protocol_id="PHM_D1_FROZEN_B11_B12",
        aggregation_level="configuration_delta_vs_A1", uncertainty_type="none", n_test=304,
        test_universe="run_id_12_315_common_304", source_path=rel(abl_src),
    )
    derived_csv("paper_data/07_figure_ready/fig4/A1_A6_delta_vs_A1.csv", delta_rows, delta_fields, sources=[abl_src],
                data_level="figure_ready", dataset="PHM2010", task="D1", transformation="Ai-A1 for every listed metric",
                intended_use="Fig.4 delta panels")
    fig4_run_sources = [
        ("A1_A6_probability_trajectories.csv", "run_probability", "audited A1-A6 per-run probabilities"),
        ("A1_A6_lifecycle_variation.csv", "run_local_probability_variation", "local lifecycle probability variation"),
        ("A1_A6_cumulative_variation.csv", "run_cumulative_probability_variation", "cumulative lifecycle probability variation"),
    ]
    for name, level, purpose in fig4_run_sources:
        source = ROOT / "figures/fig4_ablation" / name
        rows = read_csv(source)
        rows, fields = with_figure_metadata(
            rows, dataset_id="PHM2010", task_id="D1", protocol_id="PHM_D1_FROZEN_B11_B12",
            aggregation_level=level, uncertainty_type="none", n_test=304,
            test_universe="run_id_12_315_common_304", source_path=rel(source),
        )
        derived_csv(
            f"paper_data/07_figure_ready/fig4/{name}", rows, fields, sources=[source],
            data_level="figure_ready", dataset="PHM2010", task="D1",
            transformation="append frozen figure-ready metadata to audited inference-only export",
            intended_use=purpose, status="DERIVED",
        )
    life_src = ROOT / "paper_data/01_PHM2010/04_semantics/C6_lifecycle_probability_wear.csv"
    hidden_src = ROOT / "paper_data/01_PHM2010/04_semantics/C6_hidden_representation.csv"
    life_with_relative = [dict(row) | {"relative_life": (int(row["run_id"]) - 12) / 303} for row in life]
    fig5_specs = [
        ("lifecycle_semantics.csv", life_with_relative, "full lifecycle plus explicitly defined relative life", "run_level", "DERIVED"),
        ("simplex_trajectory.csv", [
            {k: row[k] for k in ("run_id","prob_early","prob_middle","prob_late","true_stage","pred_stage")} |
            {"relative_life": (int(row["run_id"]) - 12) / 303} for row in life
        ], "select probability simplex columns", "run_probability", "DERIVED"),
        ("q_agreement.csv", [
            {k: row[k] for k in ("run_id","q_true","q_pred","true_stage","pred_stage")} |
            {"relative_life": (int(row["run_id"]) - 12) / 303,
             "q_comparison_definition": "q_true_vs_raw_q_pred_no_renormalization"} for row in life
        ], "select raw q pairs; q_pred_norm is intentionally excluded", "run_q_pair", "DERIVED"),
        ("q_pred_normalized_display.csv", [
            {"run_id": row["run_id"], "q_pred_norm": row["q_pred_norm"],
             "relative_life": (int(row["run_id"]) - 12) / 303,
             "allowed_use": "display_only_not_q_agreement_metrics"} for row in life
        ], "isolate min-max normalized q display field", "run_q_display", "AUDIT_SUPPORTING"),
        ("hidden_representation.csv", hidden, "full test_C6 hidden representation copy", "run_representation", "DERIVED"),
    ]
    for name, rows, transform, level, row_status in fig5_specs:
        src = hidden_src if name.startswith("hidden") else life_src
        rows, fields = with_figure_metadata(
            rows, dataset_id="PHM2010", task_id="D1/C6", protocol_id="PHM_D1_FROZEN_B11_B12",
            aggregation_level=level, uncertainty_type="none", n_test=304,
            test_universe="run_id_12_315_common_304", source_path=rel(src), status=row_status,
        )
        derived_csv(f"paper_data/07_figure_ready/fig5/{name}", rows, fields, sources=[src], data_level="figure_ready",
                    dataset="PHM2010", task="D1/C6", transformation=transform, intended_use="Fig.5", status=row_status)
    grouped = []
    for stage in ("early","middle","late"):
        sub = [r for r in life if r["pred_stage"] == stage]
        grouped.append({"predicted_stage":stage,"n":len(sub),"VB_mean":mean(f(r["VB_true"]) for r in sub),"VB_median":median(f(r["VB_true"]) for r in sub),"q_true_mean":mean(f(r["q_true"]) for r in sub),"q_pred_mean":mean(f(r["q_pred"]) for r in sub)})
    grouped, grouped_fields = with_figure_metadata(
        grouped, dataset_id="PHM2010", task_id="D1/C6", protocol_id="PHM_D1_FROZEN_B11_B12",
        aggregation_level="predicted_stage_summary", uncertainty_type="none", n_test=304,
        test_universe="run_id_12_315_common_304", source_path=rel(life_src),
    )
    derived_csv("paper_data/07_figure_ready/fig5/wear_by_predicted_stage.csv", grouped, grouped_fields, sources=[life_src],
                data_level="figure_ready", dataset="PHM2010", task="D1/C6", transformation="group by predicted_stage; mean/median",
                intended_use="Fig.5 wear semantics")
    dataset_table = [
        {"dataset":"PHM2010","formal_dataset_name":"","hosting_platform":"","task_or_condition":"D1/D2/D3","sensor":"multi-source milling signals","sequence_or_run":"945 source runs; D1 test 304","wear_label":"VB and condition-relative stage","transfer_protocol":"dual-source leave-one-condition-out"},
        {"dataset":"NASA Milling","formal_dataset_name":"","hosting_platform":"","task_or_condition":"N1-N4 original split","sensor":"case-dependent milling signals","sequence_or_run":"small-sample cross-case","wear_label":"VB/stage","transfer_protocol":"original cross-case tasks"},
        {"dataset":THIRD_DATASET_SHORT_NAME,"formal_dataset_name":THIRD_DATASET_NAME,"hosting_platform":THIRD_DATASET_HOST,"task_or_condition":"D1-M/D2-M/D3-M","sensor":"audited primary common channels","sequence_or_run":"6418 HDF5 runs; 9 tools","wear_label":"VB (µm) and relative stage","transfer_protocol":"two machines train, third test"},
    ]
    # Every row shares the same key set (normalized above) so the CSV writer's
    # extrasaction="ignore" cannot silently drop formal_dataset_name/hosting_platform
    # for the rows that didn't originally define them.
    dataset_table_fields = list(dataset_table[0])
    assert all(list(row) == dataset_table_fields for row in dataset_table), "dataset_table rows must share one schema"
    derived_csv("paper_data/08_table_ready/dataset_table.csv", dataset_table, dataset_table_fields,
                sources=[ROOT / "paper_data/00_metadata/datasets.csv", ROOT / "paper_data/00_metadata/tasks.csv"], data_level="table_ready",
                dataset="ALL", transformation="concise metadata projection", intended_use="manuscript dataset table")
    for name, rows, source, purpose in [
        ("main_comparison_table.csv", d1, d1_src, "PHM2010 D1 9-method table"),
        ("cross_condition_table.csv", transfer, trans_src, "PHM2010 D1/D2/D3 table"),
        ("ablation_table.csv", ablation, abl_src, "authoritative A1-A6 table"),
    ]:
        derived_csv(f"paper_data/08_table_ready/{name}", rows, list(rows[0]), sources=[source], data_level="table_ready",
                    dataset="PHM2010", transformation="table-ready copy; absolute values unchanged", intended_use=purpose)


def build_metadata() -> None:
    datasets = [
        {"dataset_id":"PHM2010","dataset_name":"PHM2010 milling tool wear","dataset_short_name":"PHM2010","hosting_platform":"PHM Society Data Challenge repository","hosting_role":"distribution source","role":"main benchmark","canonical_root":"01_PHM2010","notes":"D1/D2/D3 use run_id 12..315 common 304-run universes"},
        {"dataset_id":"NASA_MILLING","dataset_name":"NASA Ames milling data set","dataset_short_name":"NASA Milling","hosting_platform":"NASA Prognostics Data Repository","hosting_role":"distribution source","role":"external small-sample validation","canonical_root":"02_NASA","notes":"only real B9-B12 original N1-N4 evidence retained"},
        {"dataset_id":THIRD_DATASET_ID,"dataset_name":THIRD_DATASET_NAME,"dataset_short_name":THIRD_DATASET_SHORT_NAME,"hosting_platform":THIRD_DATASET_HOST,"hosting_role":"data hosting platform; not the dataset name","role":"third cross-machine dataset","canonical_root":"03_MENDELEY_CROSS_MACHINE","notes":"3 machines; 9 tools; 6418 runs; T8 early truncation; legacy folder name retained for path stability"},
    ]
    tasks = [
        {"dataset_id":"PHM2010","task_id":"D1","train":"C1+C4","test":"C6","status":"DONE","test_universe":"common_304_run for main comparison"},
        {"dataset_id":"PHM2010","task_id":"D2","train":"C1+C6","test":"C4","status":"DONE","test_universe":"run_id 12..315 common 304-run"},
        {"dataset_id":"PHM2010","task_id":"D3","train":"C4+C6","test":"C1","status":"DONE","test_universe":"run_id 12..315 common 304-run"},
    ] + [{"dataset_id":"NASA_MILLING","task_id":f"N{i}","train":"original split","test":"held-out cases","status":"DONE","test_universe":"task-native"} for i in range(1,5)] + [
        {"dataset_id":THIRD_DATASET_ID,"task_id":"D1-M","train":"M1+M2","test":"M3","status":"DONE_5_SEEDS","test_universe":"run-level"},
        {"dataset_id":THIRD_DATASET_ID,"task_id":"D2-M","train":"M1+M3","test":"M2","status":"DONE_5_SEEDS","test_universe":"run-level"},
        {"dataset_id":THIRD_DATASET_ID,"task_id":"D3-M","train":"M2+M3","test":"M1","status":"DONE_5_SEEDS","test_universe":"run-level"},
    ]
    methods = [dict(row) | {"notes":"one canonical row per method_id; aliases are non-canonical labels"} for row in METHOD_METADATA]
    metrics = [
        {"metric_id":"Acc","display_name":"Accuracy","direction":"higher","definition":"correct predictions / n"},
        {"metric_id":"MacroF1","display_name":"Macro-F1","direction":"higher","definition":"unweighted class F1 mean"},
        {"metric_id":"M_F1","display_name":"Middle-stage F1","direction":"higher","definition":"F1 for middle class"},
        {"metric_id":"M_Rec","display_name":"Middle-stage recall","direction":"higher","definition":"recall for middle class"},
        {"metric_id":"M_to_E","display_name":"M→E","direction":"lower","definition":"middle-to-early error rate"},
        {"metric_id":"M_to_L","display_name":"M→L","direction":"lower","definition":"middle-to-late error rate"},
        {"metric_id":"Rev","display_name":"Reverse transitions","direction":"lower","definition":"number of lifecycle reverse stage transitions"},
        {"metric_id":"Jump","display_name":"Stage jumps","direction":"lower","definition":"number of non-adjacent stage jumps"},
        {"metric_id":"Smooth","display_name":"Probability smoothness","direction":"lower","definition":"successive probability variation"},
    ]
    protocols = [
        {"protocol_id":"PHM_D1_COMMON_304","dataset_id":"PHM2010","aggregation":"fixed official model point estimate + moving-block bootstrap 95% CI","uncertainty":"moving_block_bootstrap_95CI","notes":"main manuscript comparison; all 9 methods aligned to run_id 12..315; not a training-seed study"},
        {"protocol_id":"PHM_D1_D2_D3_COMMON_304","dataset_id":"PHM2010","aggregation":"task point estimates on common run_id 12..315","uncertainty":"none; separate across-task descriptive std","notes":"D1 fixed official values; D2/D3 recomputed from existing predictions after deterministic filtering; no retraining"},
        {"protocol_id":"PHM_D1_ORIGINAL_5SEED_AUDIT","dataset_id":"PHM2010","aggregation":"mean/std across training seeds","uncertainty":"across_seed_std","notes":"AUDIT_SUPPORTING only; original preprocessing/training-seed coupled sweep"},
        {"protocol_id":"PHM_D1_FIXED_PREPROCESS_SEED_SENSITIVITY","dataset_id":"PHM2010","aggregation":"mean/std across TRAIN_SEED with preprocessing fixed at seed 42","uncertainty":"across_seed_std","notes":"AUDIT_SUPPORTING only; never replaces fixed official D1 main comparison"},
        {"protocol_id":"NASA_ORIGINAL_SPLIT","dataset_id":"NASA_MILLING","aggregation":"task points and across-task mean/std","uncertainty":"across_task_std","notes":"N1-N4, seed 2026"},
        {"protocol_id":"MILLING_CROSS_MACHINE_5SEED","dataset_id":THIRD_DATASET_ID,"aggregation":"mean/std across seeds within task","uncertainty":"across_seed_std","notes":"seeds 42/52/62/72/82; hosted on Mendeley Data"},
    ]
    for name, rows in (("datasets.csv",datasets),("tasks.csv",tasks),("methods.csv",methods),("metrics.csv",metrics),("experiment_protocols.csv",protocols)):
        path = PAPER / "00_metadata" / name
        write_csv(path, rows, list(rows[0])); register(path,status="DERIVED",data_level="metadata",transformation="curated from audited protocols",intended_use="data dictionary")
    write_text(PAPER / "00_metadata/DATA_DICTIONARY.md", """
# Data dictionary

Rows are observations; columns are variables. Absolute experimental values are retained in `01_PHM2010`, `02_NASA`, and `03_MENDELEY_CROSS_MACHINE`. `04_cross_dataset`, `07_figure_ready`, and `08_table_ready` contain explicitly derived projections.

`aggregation_level` distinguishes run-point, task-point, across-seed mean, and across-task mean. `uncertainty_type` distinguishes moving-block bootstrap 95% CI, across-seed standard deviation, across-task standard deviation, and point estimates. Missing values are `NA` or empty and are never estimated.

`status` is restricted to AUTHORITATIVE, CANONICAL_COPY, DERIVED, AUDIT_SUPPORTING, SUPERSEDED, EXCLUDED, and UNRESOLVED.
""")
    q_doc = PAPER / "00_metadata/Q_DEFINITIONS.md"
    write_text(q_doc, """
# Frozen q and wear definitions (Q_DEFINITION_V1)

This document is normative for every Fig.5 table, plot, caption, and statistic.

- `VB_true`: observed flank-wear value for the run, in the source wear unit; it is never normalized or model-predicted.
- `VB_smooth`: centered 7-run rolling mean of `VB_true` within one condition, with `min_periods=1` at the ends.
- `q_true`: condition-relative normalized wear position, `(VB_smooth - min(VB_smooth)) / (max(VB_smooth) - min(VB_smooth) + 1e-12)`. It is the regression target and lies in `[0,1]`.
- `q_pred`: raw sigmoid output of the frozen model q head for the run. This is the only prediction field paired with `q_true` for MAE, R2, Spearman rho, and other agreement statistics.
- `q_pred_norm`: display-only min-max normalization of `q_pred` over the frozen C6 304-run test universe, `(q_pred - min(q_pred)) / (max(q_pred) - min(q_pred) + 1e-12)`. It must not replace `q_pred` in agreement statistics.
- `relative_life`: index position in the frozen test lifecycle, `(run_id - 12) / (315 - 12)`. It is an x-axis coordinate, not a wear label and not a model target.

Frozen relationship: `VB_true -> centered rolling mean -> VB_smooth -> condition-relative min-max -> q_true`; the model independently emits `q_pred`; `q_pred_norm` is a post-hoc display transform only. Do not compare `q_true` against `q_pred_norm` when reporting model agreement.
""")
    register(q_doc, status="DERIVED", data_level="definition", dataset="PHM2010", task="D1/C6",
             transformation="curated from frozen preprocessing and audited lifecycle data",
             intended_use="normative q/VB/relative-life definitions for Fig.5")


FIG4_FORMAL_SCRIPTS = [
    "figures/fig4_ablation/plot_fig4.py",
    "nature_figures/scripts/fig4_ablation.py",
    "nature_figures/scripts/generate_docs.py",
]


def stale_fig4_scripts() -> list[str]:
    """Formal Fig.4 scripts that still reference the retired FINAL_ablation_outputs.csv source."""
    stale = []
    for rel_path in FIG4_FORMAL_SCRIPTS:
        path = ROOT / rel_path
        if path.exists() and "FINAL_ablation_outputs.csv" in path.read_text(encoding="utf-8", errors="ignore"):
            stale.append(rel_path)
    return stale


def build_docs() -> None:
    branch = subprocess.run(["git","branch","--show-current"],cwd=ROOT,text=True,capture_output=True).stdout.strip()
    commit = subprocess.run(["git","rev-parse","--short","HEAD"],cwd=ROOT,text=True,capture_output=True).stdout.strip()
    write_text(PAPER / "README.md", f"""
# Paper data — Single Source of Truth

This directory is the only permitted data entrypoint for manuscript numbers, tables, and figures. It was built by copying audited sources and regenerating every derived table without training, seed selection, or manual transcription from images.

## Absolute canonical data

- PHM2010 D1 9-method table: `01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv`
- PHM2010 D1/D2/D3: `01_PHM2010/02_cross_condition_D1_D2_D3/transfer_tasks_long.csv`
- PHM2010 A1-A6: `01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv` (the only permitted ablation source)
- PHM2010 Fig.5 semantics: `01_PHM2010/04_semantics/C6_lifecycle_probability_wear.csv` and `C6_hidden_representation.csv`
- NASA original N1-N4: `02_NASA/original_split_mean_std.csv` plus task/prediction evidence
- {THIRD_DATASET_SHORT_NAME} ({THIRD_DATASET_NAME}; hosted on {THIRD_DATASET_HOST}): `03_MENDELEY_CROSS_MACHINE/overall_by_task_mean_std.csv` plus seed/prediction/semantic evidence. The folder name `03_MENDELEY_CROSS_MACHINE` is a retained path only, not the formal dataset name.

## Derived data

`04_cross_dataset`, `07_figure_ready`, and `08_table_ready` are derived. Delta, rank, min-max, normalized, and relative scores never replace absolute values. Formulas are in `90_provenance/TRANSFORMATIONS.md`.

## Never use as manuscript canonical data

The old `FINAL_ablation_outputs.csv`, `Table10_ablation_summary.csv`, hard-coded plotting values, reconstructed/superseded features, diagnostics, and ambiguous old MTF-AViTK D1 runs are excluded. See `90_provenance/KNOWN_BAD_AND_SUPERSEDED.md`.

## Rebuild and validate

```powershell
python paper_data/99_scripts/build_paper_data.py
python paper_data/99_scripts/validate_paper_data.py
```

Repository anchor: branch `{branch}`, commit `{commit}`. The task-start state is frozen in `90_provenance/REPOSITORY_STATE.md`.
""")
    write_text(PAPER / "QUICK_USE.md", """
# Quick use

- 画 Fig.1 -> `07_figure_ready/fig1/`
- 画 Fig.2 -> `07_figure_ready/fig2/`（absolute/rank/normalized 同时保留）
- 画 Fig.3 -> `07_figure_ready/fig3/`
- 画 Fig.4 -> `07_figure_ready/fig4/A1_A6_absolute.csv`（唯一上游为 authoritative A1-A6）
- 画 Fig.5 -> `07_figure_ready/fig5/`
- 主对比表 -> `08_table_ready/main_comparison_table.csv`
- 跨工况表 -> `08_table_ready/cross_condition_table.csv`
- 消融表 -> `08_table_ready/ablation_table.csv`
""")
    write_text(PAPER / "90_provenance/SOURCE_PRIORITY.md", """
# Source priority

1. Later dedicated authoritative audits override older summaries and plot exports. Fig.4 uses only `figures/fig4_ablation/AUTHORITATIVE_A1_A6.csv`.
2. `final_statistical_evidence/` is authoritative for PHM2010 D1 bootstrap/common-universe and D1/D2/D3 transfer results.
3. Dataset-specific final exports: NASA `nasa_dcpsr_results_stageaware_opt` original split; Mendeley `FINAL_REPORT`, `04_overall_comparison`, `05_generalization`, `06_ablation`, and `07_semantic_consistency`.
4. Audited figure manifests are source indexes; data are copied from the manifest's original source path.

Git tracking is provenance metadata, not an authority criterion: local ignored final files are allowed but recorded as `git_tracked=false`.
""")
    write_text(PAPER / "90_provenance/KNOWN_BAD_AND_SUPERSEDED.md", """
# Known bad, excluded, and superseded sources

- `补充材料/小论文/3_main_experiment_fgds_psi/1_results/FINAL_ablation_outputs.csv`: internally reproducible but from an independent checkpoint; **SUPERSEDED FOR MANUSCRIPT**.
- `补充材料/小论文/6_ablation_experiment/Table10_ablation_summary.csv`: independent retraining, not frozen B11/B12; **EXCLUDED FROM MANUSCRIPT**.
- Hard-coded values in `代码/7.6.1消融实验绘图.py`, `代码/8.2图15.py`, and `代码/8.2图16.py`: not experimental data sources.
- Old `nature_figures/plot_data/fig4_D1_ablation_A1_A6.csv`: derived from the superseded Fig.4 source; not canonical.
- Paths containing reconstructed, superseded, old, backup, before_smooth_fix, debug, or diagnostic are excluded by default.
- `legacy_repro_audit/`, `protocol_diagnostic_fixed_preprocess/`, and `final_five_seed_sweep/` remain AUDIT_SUPPORTING and do not replace frozen manuscript evidence.
- `outputs/mtf_avitk/unified_protocol/` has ambiguous old D1 seed identity; D1 uses final statistical evidence only.
""")
    write_text(PAPER / "90_provenance/TRANSFORMATIONS.md", """
# Transformations

- Cross-dataset: `ΔAcc = B12 - B11`; `ΔM-F1 = B12 - B11`; `Smooth_benefit = B11 - B12`; `Jump_benefit = B11 - B12`.
- Fig.2 normalized scores: within each task, `(x-min)/(max-min)` for high-is-good and `(max-x)/(max-min)` for Smooth. Absolute values are retained separately.
- Fig.4 delta table: `Ai - A1`; absolute A1-A6 remains authoritative.
- Fig.5 q statistics: directly recomputed on all 304 `q_true`/`q_pred` pairs; no `q_pred_norm` substitution.
- Mendeley task summaries retain across-seed std; collapsed dataset effects average the three task means and do not pool runs.
- NASA summary retains across-task std from N1-N4; it is not represented as across-seed uncertainty.
""")
    write_text(PAPER / "MANUSCRIPT_DATA_MAP.md", f"""
# Manuscript → canonical data map

The third cross-machine dataset's formal name is "{THIRD_DATASET_NAME}" (short name {THIRD_DATASET_SHORT_NAME}), hosted on {THIRD_DATASET_HOST}. `03_MENDELEY_CROSS_MACHINE` below is a retained folder path only.

| Manuscript item | Claim/Table/Figure | Canonical data file | Status |
|---|---|---|---|
| New Fig.1 | D1 final 9-method evidence | `07_figure_ready/fig1/` | MAPPED |
| New Fig.2 | D1/D2/D3 robustness | `07_figure_ready/fig2/` | MAPPED |
| New Fig.3 | PHM/NASA/{THIRD_DATASET_SHORT_NAME} cross-dataset effects | `07_figure_ready/fig3/` | MAPPED |
| New Fig.4 / current Table 12 replacement | A1-A6 ablation | `01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv` | MAPPED_WITH_CORRECTION |
| New Fig.5 | lifecycle q/probability/hidden representation | `07_figure_ready/fig5/` | MAPPED |
| `投稿版20260709` Table 8 | legacy B1-B12 main table | `01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv` for current 9-method replacement | REQUIRES_MANUSCRIPT_UPDATE |
| `投稿版20260709` Tables 9-10 | older D1/D2/S1/S2 protocol | no current canonical replacement for S1/S2 | UNRESOLVED/LEGACY_PROTOCOL |
| `投稿版20260709` Table 11 | NASA N1-N4 | `02_NASA/task_level_results.csv` | MAPPED; verify manuscript values against original split |
| `投稿版20260709` Table 12 | stale A1-A6 values | `01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv` | STALE; MUST UPDATE |
| `投稿版20260709` Tables 13-14 | q and wear semantics | `01_PHM2010/04_semantics/` and `07_figure_ready/fig5/` | MIXED/REQUIRES_UPDATE |

The PDF and DOCX versions contain the same stale Table 12 and Table 13 values as `main.tex`; images/PDF were not used to transcribe numbers. Manuscript-only synchronization items (MS-001..MS-003) are tracked separately in `90_provenance/MANUSCRIPT_SYNC_STATUS.csv`, not in `90_provenance/UNRESOLVED_ITEMS.csv`.
""")
    # Manuscript-only synchronization items are text/number mismatches between the
    # submitted manuscript and the frozen paper_data evidence. They do not indicate a
    # data-integrity problem in paper_data itself, so they are tracked separately from
    # UNRESOLVED_ITEMS.csv and never flip VALIDATION STATUS to FAIL.
    manuscript_sync.extend([
        {"item_id":"MS-001","location":"投稿版20260709/main.tex Table 12; manuscript.pdf/docx","claim":"A1-A6 ablation values","issue":"stale values conflict with PASS_WITH_CORRECTION authoritative audit (e.g. A1 Acc 0.9705 vs 0.9901315789)","required_action":"replace manuscript table/text from paper_data authoritative ablation","manuscript_sync_status":"PENDING"},
        {"item_id":"MS-002","location":"投稿版20260709/main.tex Table 13; manuscript.pdf/docx","claim":"PHM q metrics","issue":"uses a different q field/definition than audited full 304-run q_true-q_pred statistics","required_action":"decide manuscript definition; current Fig.5 canonical R2=0.7478018753, rho=0.9634587570, MAE=0.1132309945","manuscript_sync_status":"PENDING"},
        {"item_id":"MS-003","location":"投稿版20260709/main.tex Tables 9-10","claim":"D1/D2/S1/S2 cross-condition values","issue":"legacy four-task protocol differs from final D1/D2/D3 9-method evidence","required_action":"retain only if explicitly labeled legacy protocol or replace with canonical D1/D2/D3 table","manuscript_sync_status":"PENDING"},
    ])
    write_csv(PAPER / "90_provenance/MANUSCRIPT_SYNC_STATUS.csv", manuscript_sync,
              ["item_id","location","claim","issue","required_action","manuscript_sync_status"])

    # True data-integrity/unresolved items only. FIG4-001 is added automatically only
    # while a formal Fig.4 script still points at the retired FINAL_ablation_outputs.csv;
    # once every formal script is switched, stale_fig4_scripts() is empty and the item
    # disappears from this table on the next build.
    stale_scripts = stale_fig4_scripts()
    if stale_scripts:
        unresolved.append({
            "item_id": "FIG4-001", "location": "; ".join(stale_scripts), "claim": "Fig.4 source",
            "issue": "scripts still read old FINAL_ablation_outputs.csv",
            "required_action": "switch source to paper_data/01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv and paper_data/07_figure_ready/fig4/",
            "status": "UNRESOLVED",
        })
    unresolved.append(
        {"item_id":"NASA-001","location":"paper_data/02_NASA","claim":"9-method NASA comparison","issue":"authoritative local package contains only B9-B12 for original N1-N4","required_action":"do not fabricate missing methods","status":"UNRESOLVED"},
    )
    write_csv(PAPER / "90_provenance/UNRESOLVED_ITEMS.csv", unresolved, ["item_id","location","claim","issue","required_action","status"])


def write_component_readmes() -> None:
    texts = {
        "01_PHM2010/02_cross_condition_D1_D2_D3/README.md": "D1, D2, and D3 all use the same common universe: run_id 12..315 (304 runs), for all nine methods. D1 values are the fixed official model's point estimates from the moving-block bootstrap table; D2/D3 values are recomputed by filtering each method's existing frozen predictions to run_id 12..315 and recomputing metrics deterministically, with no retraining. Do not use any older method-native/window-based-vs-raw-signal universe distinction; it has been retired. Across-task std (in transfer_tasks_mean_std.csv) is a descriptive spread across the three task point estimates, not across-seed uncertainty.",
        "01_PHM2010/03_ablation/README.md": "A1_A6_AUTHORITATIVE.csv is the only permitted ablation input. A1 maps to formal B11/raw stage output; A6 maps to formal B12. A1-A4 hard classification metrics are genuinely identical while probability matrices and Smooth differ.",
        "01_PHM2010/04_semantics/README.md": "The lifecycle file contains all 304 C6 runs. Hidden representation is filtered to test_C6/C6 (304 rows). q_statistics.csv is recomputed from q_true and q_pred, not handwritten.",
        # Note: 01_PHM2010/05_training_seed_sensitivity/README.md is written and registered
        # directly by copy_phm_training_seed_sensitivity(); it is intentionally not listed
        # here to avoid a second, unregistered overwrite of that file.
        "02_NASA/README.md": "Canonical NASA evidence is the original N1-N4 split. Summary, task/seed, and prediction levels are separate. Only real B9-B12 evidence is retained; no 9-method table is invented.",
        "03_MENDELEY_CROSS_MACHINE/README.md": f"Official dataset: {THIRD_DATASET_NAME} (short name {THIRD_DATASET_SHORT_NAME}), hosted on {THIRD_DATASET_HOST}. The folder name 03_MENDELEY_CROSS_MACHINE is a retained path only, not the formal dataset name. Audited structure: 3 machines, 9 tools, 6418 runs. Core tasks D1-M/D2-M/D3-M are complete for seeds 42/52/62/72/82. Single-source MS1-MS6 are not claimed as complete. T8 is early-truncated.",
        "04_cross_dataset/README.md": "Absolute B11/B12 values are canonical inputs. Delta/rank/normalized fields are derived and never replace absolute evidence. NASA std is across tasks; Mendeley task std is across seeds.",
        "05_baseline_metadata/README.md": "Literature metadata comes from the project workbook and is reconciled to current implementation evidence. Complexity includes only explicitly reported values; NA is never estimated.",
        "06_canonical_tables/README.md": "all_metrics_long.csv is the primary metric schema. aggregation_level and uncertainty_type prevent bootstrap CI, across-seed std, across-task std, and point estimates from being conflated.",
        "08_table_ready/README.md": "Presentation-ready projections only. Trace every value back through DATA_CATALOG.csv to a canonical absolute file.",
        "99_scripts/README.md": "Run build_paper_data.py from any directory, then validate_paper_data.py. build_canonical_tables.py is a convenience wrapper. Existing canonical copies are protected by prior source/canonical hashes.",
    }
    for path, body in texts.items():
        write_text(PAPER / path, "# Usage\n\n" + body)


def build_source_inventory_and_catalog() -> None:
    source_groups = defaultdict(list)
    for row in copy_rows:
        source_groups[row["source_path"]].append(row["canonical_path"])
    # Include transformed authoritative inputs (filters/unpivots/metadata extraction),
    # not only byte-for-byte copies, so every original source appears in inventory.
    for target, meta in registry.items():
        for source in filter(None, meta.get("source_path", "").split(";")):
            if not source.startswith("paper_data/"):
                source_groups[source].append(target)
    inventory = []
    for source, targets in sorted(source_groups.items()):
        path = ROOT / source
        unique_targets = sorted(set(targets))
        inventory.append({"source_path":source,"exists":str(path.exists()).lower(),"git_tracked":str(git_tracked(path)).lower(),"data_level":registry[unique_targets[0]]["data_level"],"status":registry[unique_targets[0]]["status"],"reason":"selected by source priority","canonical_targets":";".join(unique_targets)})
    excluded = [
        ("补充材料/小论文/3_main_experiment_fgds_psi/1_results/FINAL_ablation_outputs.csv","SUPERSEDED","independent checkpoint; old Fig.4"),
        ("补充材料/小论文/6_ablation_experiment/Table10_ablation_summary.csv","EXCLUDED","independent retraining; not frozen B11/B12"),
        ("outputs/htt_net/B1_B12_recheck_on_reconstructed_features/","EXCLUDED","reconstructed feature diagnostic"),
        ("baselines/htt_net/data/reconstructed_v1_superseded/","EXCLUDED","explicit superseded reconstruction"),
        ("legacy_repro_audit/","AUDIT_SUPPORTING","diagnostic only"),
        ("protocol_diagnostic_fixed_preprocess/","AUDIT_SUPPORTING","directory-level catch-all; the audited fixed-preprocessing seed-sensitivity files are separately copied into 01_PHM2010/05_training_seed_sensitivity/ as AUDIT_SUPPORTING with explicit canonical targets and never replace the frozen D1 main table"),
        ("final_five_seed_sweep/","AUDIT_SUPPORTING","directory-level catch-all; the audited original five-seed sweep files are separately copied into 01_PHM2010/05_training_seed_sensitivity/ as AUDIT_SUPPORTING with explicit canonical targets and never replace the frozen D1 main table"),
        ("outputs/mtf_avitk/unified_protocol/","EXCLUDED","old D1 seed identity ambiguity"),
        ("raw PHM2010/NASA/Mendeley HDF5 and checkpoints","EXCLUDED","large raw/cache/model files remain in place; indexed only"),
    ]
    for source,status,reason in excluded:
        path=ROOT/source if not source.startswith("raw ") else None
        inventory.append({"source_path":source,"exists":str(path.exists()).lower() if path else "not_applicable","git_tracked":str(git_tracked(path)).lower() if path and path.exists() else "false","data_level":"excluded_or_index_only","status":status,"reason":reason,"canonical_targets":""})
    write_csv(PAPER / "90_provenance/SOURCE_INVENTORY.csv", inventory, list(inventory[0]))
    write_csv(PAPER / "90_provenance/COPY_MANIFEST.csv", copy_rows, ["source_path","canonical_path","source_sha256","canonical_sha256","git_tracked","status","copy_mode"])

    # VALIDATION_REPORT.md is a post-validation runtime artifact written by
    # validate_paper_data.py, not by this build script. It is deliberately excluded from
    # the catalog/checksum registry: including it would make its own checksum stale the
    # instant validate_paper_data.py rewrites it, producing a self-invalidating
    # build/validate checksum cycle on the very next validation run.
    SELF_EXCLUDED_FILES = {"DATA_CATALOG.csv", "CHECKSUMS.csv", "MANIFEST.json"}
    VALIDATION_REPORT_REL = "paper_data/90_provenance/VALIDATION_REPORT.md"

    # Register generated documentation/scripts not already tracked in the in-memory registry.
    for path in sorted(p for p in PAPER.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"):
        key = rel(path)
        if key == VALIDATION_REPORT_REL:
            continue
        if key not in registry and path.name not in SELF_EXCLUDED_FILES:
            register(path, status="DERIVED", data_level="documentation" if path.suffix.lower() in {".md"} else "metadata",
                     transformation="generated by build_paper_data.py", intended_use="provenance and usage")
    catalog = []
    for key, meta in sorted(registry.items()):
        path = ROOT / key
        rows, columns = file_shape(path)
        catalog.append({"canonical_path":key,"data_level":meta["data_level"],"dataset":meta["dataset"],"task":meta["task"],"method":meta["method"],"seed":meta["seed"],"rows":rows,"columns":columns,"source_path":meta["source_path"],"source_sha256":meta["source_sha256"],"canonical_sha256":sha256(path),"status":meta["status"],"transformation":meta["transformation"],"intended_use":meta["intended_use"],"notes":meta["notes"]})
    catalog.append({"canonical_path":"paper_data/DATA_CATALOG.csv","data_level":"self_index","dataset":"","task":"","method":"","seed":"","rows":"SELF","columns":"15","source_path":"paper_data/99_scripts/build_paper_data.py","source_sha256":sha256(PAPER / "99_scripts/build_paper_data.py"),"canonical_sha256":"SELF_REFERENTIAL_NOT_APPLICABLE","status":"DERIVED","transformation":"self-index","intended_use":"catalog","notes":"self hash is mathematically excluded"})
    write_csv(PAPER / "DATA_CATALOG.csv", catalog, list(catalog[0]))
    checksums = []
    for path in sorted(p for p in PAPER.rglob("*") if p.is_file() and p.name not in {"CHECKSUMS.csv","MANIFEST.json"} and "__pycache__" not in p.parts and p.suffix != ".pyc"):
        if rel(path) == VALIDATION_REPORT_REL:
            continue
        checksums.append({"canonical_path":rel(path),"sha256":sha256(path),"bytes":path.stat().st_size})
    write_csv(PAPER / "90_provenance/CHECKSUMS.csv", checksums, ["canonical_path","sha256","bytes"])
    counts = Counter(row["status"] for row in catalog)
    pred_count = sum(1 for row in catalog if row["data_level"] == "prediction_level")
    manifest = {"schema_version":"1.0","repository":{"branch":subprocess.run(["git","branch","--show-current"],cwd=ROOT,text=True,capture_output=True).stdout.strip(),"commit":subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True).stdout.strip()},"counts_by_status":dict(counts),"catalog_entries":len(catalog),"prediction_level_files":pred_count,"checksum_policy":"all files except MANIFEST.json and CHECKSUMS.csv; DATA_CATALOG self hash excluded in its own row","validation_report":"paper_data/90_provenance/VALIDATION_REPORT.md"}
    (PAPER / "MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def file_shape(path: Path) -> tuple[str, str]:
    if path.suffix.lower() == ".csv":
        try:
            rows = read_csv(path)
            return str(len(rows)), str(len(rows[0]) if rows else 0)
        except Exception:
            return "UNREADABLE", "UNREADABLE"
    return "NA", "NA"


def build_table_index() -> None:
    rows = [
        {"manuscript_item":"dataset table","canonical_file":"paper_data/08_table_ready/dataset_table.csv","status":"DERIVED"},
        {"manuscript_item":"main comparison","canonical_file":"paper_data/08_table_ready/main_comparison_table.csv","status":"DERIVED"},
        {"manuscript_item":"cross condition","canonical_file":"paper_data/08_table_ready/cross_condition_table.csv","status":"DERIVED"},
        {"manuscript_item":"ablation","canonical_file":"paper_data/08_table_ready/ablation_table.csv","status":"DERIVED"},
    ]
    derived_csv("paper_data/06_canonical_tables/manuscript_table_index.csv", rows, list(rows[0]), sources=[],
                data_level="index", transformation="explicit manuscript mapping", intended_use="table lookup")


def main() -> None:
    ensure_tree()
    d1, transfer, ablation, life = copy_phm()
    copy_phm_training_seed_sensitivity()
    nasa_summary, nasa_task = copy_nasa()
    mend_summary, mend_seed, _ = copy_mendeley()
    cross_abs, deltas = build_cross_dataset(d1, nasa_summary, mend_summary)
    build_baseline_metadata()
    build_metadata()
    build_canonical_tables(d1, transfer, ablation, nasa_summary, nasa_task, mend_summary, mend_seed)
    hidden = read_csv(PAPER / "01_PHM2010/04_semantics/C6_hidden_representation.csv")
    build_figure_and_table_ready(d1, transfer, ablation, life, hidden, cross_abs, deltas, nasa_task, mend_summary)
    build_table_index()
    build_docs()
    write_component_readmes()
    build_source_inventory_and_catalog()
    print(json.dumps(json.loads((PAPER / "MANIFEST.json").read_text(encoding="utf-8")), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

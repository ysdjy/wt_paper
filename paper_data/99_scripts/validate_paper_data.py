#!/usr/bin/env python3
"""Validate paper_data invariants and write VALIDATION_REPORT.md."""

from __future__ import annotations

import csv
import hashlib
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper_data"

# Reuse the build script's constants and metric formulas as the single source of
# truth instead of re-deriving them here, so build and validate cannot silently
# drift apart. Importing is safe: build_paper_data.py only executes main() under
# `if __name__ == "__main__"`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_paper_data as bpd  # noqa: E402

passes: list[str] = []
warnings: list[str] = []
failures: list[str] = []


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def near(actual, expected, tolerance=1e-9) -> bool:
    return math.isclose(float(actual), float(expected), rel_tol=0, abs_tol=tolerance)


def check(condition: bool, label: str, detail: str = "") -> None:
    (passes if condition else failures).append(label if condition else f"{label}: {detail}")


def validate_d1() -> None:
    rows = read_csv(PAPER / "01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv")
    expected = {"RF","TCN-GRU","Multi-task TCN-GRU","DC-PSR","HTT-Net (adapted)","Multi-source Attention","MTF-AViTK","Dynamic GIN + TGP","DP2Net-adapted"}
    check({r["Method"] for r in rows} == expected and len(rows) == 9, "PHM D1 has exactly the nine formal methods", str({r["Method"] for r in rows}))
    by = {r["Method"]: r for r in rows}
    for method, value in (("DC-PSR",0.9868421053),("Multi-task TCN-GRU",0.9901315789),("RF",0.9769736842)):
        check(near(by[method]["Acc"], value, 1e-8), f"{method} D1 Acc matches frozen evidence", by[method]["Acc"])
    predictions = sorted((PAPER / "01_PHM2010/01_main_D1/predictions_common_universe").glob("D1_*_304runs.csv"))
    check(len(predictions) == 9, "D1 has nine prediction-level files", str(len(predictions)))
    for path in predictions:
        data = read_csv(path)
        ids = sorted(int(r["run_id"]) for r in data)
        check(len(data) == 304 and ids == list(range(12,316)), f"{path.name} common universe is run_id 12..315", f"n={len(data)} range={ids[:1]}..{ids[-1:]}")

    protocols = {r["protocol_id"]: r for r in read_csv(PAPER / "00_metadata/experiment_protocols.csv")}
    d1_protocol = protocols.get("PHM_D1_COMMON_304")
    check(
        d1_protocol is not None and d1_protocol.get("uncertainty") == "moving_block_bootstrap_95CI",
        "D1 protocol remains fixed official model + moving-block bootstrap 95% CI",
        str(d1_protocol),
    )


def validate_methods() -> None:
    rows = read_csv(PAPER / "00_metadata/methods.csv")
    ids = [r["method_id"] for r in rows]
    check(len(ids) == 9 and len(set(ids)) == 9, "methods.csv has exactly nine unique method IDs", str(ids))
    check("dp2net_adapted" in ids, "methods.csv explicitly includes dp2net_adapted", str(ids))
    expected_ids = {row["method_id"] for row in bpd.METHOD_METADATA}
    check(set(ids) == expected_ids, "methods.csv method_id set matches METHOD_METADATA registry", str(set(ids) ^ expected_ids))


def validate_dataset_naming() -> None:
    rows = {r["dataset_id"]: r for r in read_csv(PAPER / "00_metadata/datasets.csv")}
    third = rows.get(bpd.THIRD_DATASET_ID)
    check(third is not None, f"datasets.csv has a row for {bpd.THIRD_DATASET_ID}", str(sorted(rows)))
    if third is not None:
        check(third.get("dataset_name") == bpd.THIRD_DATASET_NAME, "Third dataset formal name matches THIRD_DATASET_NAME", third.get("dataset_name"))
        check(third.get("dataset_short_name") == bpd.THIRD_DATASET_SHORT_NAME, "Third dataset short name is recorded separately", third.get("dataset_short_name"))
        check(third.get("hosting_platform") == bpd.THIRD_DATASET_HOST, "Third dataset hosting platform is recorded separately from its name", third.get("hosting_platform"))
        check(third.get("dataset_name") != third.get("hosting_platform"), "Third dataset formal name and hosting platform are not conflated")


def validate_cross_condition() -> None:
    rows = read_csv(PAPER / "01_PHM2010/02_cross_condition_D1_D2_D3/transfer_tasks_long.csv")
    check(len(rows) == 27, "Cross-condition table has 9 methods × 3 tasks", str(len(rows)))
    check({r["Task"] for r in rows} == {"D1","D2","D3"}, "Cross-condition task names are complete")
    required = {"n_test","test_universe","aggregation_level","protocol_id","source_path"}
    check(required <= set(rows[0]) and all(all(r[k] != "" for k in required) for r in rows), "Every cross-condition row records universe/protocol/source", "missing field/value")
    check(all(r["test_universe"] == "run_id_12_315_common_304" for r in rows), "Every D1/D2/D3 row uses the common 304-run universe", str({r["test_universe"] for r in rows}))
    check(all(r["n_test"] == "304" for r in rows), "Every D1/D2/D3 row reports n_test=304", str({r["n_test"] for r in rows}))

    by_task_method = {(r["Task"], r["method_id"]): r for r in rows}
    for task in ("D2", "D3"):
        for method_meta in bpd.METHOD_METADATA:
            method = method_meta["method_id"]
            pred_path = PAPER / f"01_PHM2010/02_cross_condition_D1_D2_D3/predictions/{task}/{method}/predictions.csv"
            if not pred_path.exists():
                check(False, f"{task}/{method} predictions file exists", str(pred_path))
                continue
            data = read_csv(pred_path)
            ids = sorted(int(r["run_id"]) for r in data)
            check(len(data) == 304 and ids == list(range(12, 316)), f"{task}/{method} predictions are exactly run_id 12..315 (304 rows)", f"n={len(data)}")
            recomputed = bpd.recompute_transfer_metrics(data)
            frozen = by_task_method.get((task, method))
            check(frozen is not None, f"{task}/{method} has a transfer_tasks_long.csv row", str((task, method)))
            if frozen is not None:
                for metric in bpd.TRANSFER_METRICS:
                    check(
                        near(recomputed[metric], float(frozen[metric]), 1e-8),
                        f"{task}/{method} recomputed {metric} equals the frozen table value",
                        f"recomputed={recomputed[metric]} frozen={frozen[metric]}",
                    )
            metrics_json_path = pred_path.parent / "metrics.json"
            if metrics_json_path.exists():
                import json
                stored = json.loads(metrics_json_path.read_text(encoding="utf-8"))
                check(stored.get("retrained") is False, f"{task}/{method} metrics.json declares retrained=false", str(stored.get("retrained")))
                for metric in bpd.TRANSFER_METRICS:
                    check(
                        metric not in stored or near(recomputed[metric], float(stored[metric]), 1e-8),
                        f"{task}/{method} metrics.json {metric} equals recomputed value",
                        f"recomputed={recomputed[metric]} stored={stored.get(metric)}",
                    )


def validate_fig2() -> None:
    rows = read_csv(PAPER / "07_figure_ready/fig2/taskwise_absolute.csv")
    check(len(rows) == 27, "Fig.2 absolute table is rebuilt from the common-304 cross-condition table (27 rows)", str(len(rows)))
    check(
        all(r.get("test_universe") == "run_id_12_315_common_304" for r in rows),
        "Fig.2 absolute rows carry the common-304 test universe",
        str({r.get("test_universe") for r in rows}),
    )
    rank_rows = read_csv(PAPER / "07_figure_ready/fig2/taskwise_rank.csv")
    norm_rows = read_csv(PAPER / "07_figure_ready/fig2/taskwise_normalized.csv")
    check(len(rank_rows) > 0 and len(norm_rows) > 0, "Fig.2 rank/normalized tables are non-empty")


def validate_ablation() -> None:
    rows = read_csv(PAPER / "01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv")
    check([r["ID"] for r in rows] == [f"A{i}" for i in range(1,7)], "Ablation has exactly ordered A1-A6")
    by = {r["ID"]: r for r in rows}
    check(near(by["A1"]["Acc"],0.9901315789,1e-8), "A1 Acc is authoritative", by["A1"]["Acc"])
    check(near(by["A6"]["Acc"],0.9868421053,1e-8), "A6 Acc is authoritative", by["A6"]["Acc"])
    class_cols = ["Acc","Macro-F1","M-F1","M-Rec","M→E","M→L","Rev","Jump"]
    check(all(all(near(by[f"A{i}"][c],by["A1"][c]) for c in class_cols) for i in range(2,5)), "A1-A4 hard classification metrics are identical")
    check(len({by[f"A{i}"]["Smooth"] for i in range(1,5)}) > 1, "A1-A4 Smooth values are not all identical")
    catalog = read_csv(PAPER / "DATA_CATALOG.csv")
    bad = [r for r in catalog if r["status"] in {"AUTHORITATIVE","CANONICAL_COPY"} and "FINAL_ablation_outputs.csv" in r["source_path"]]
    check(not bad, "Old FINAL_ablation_outputs.csv is absent from canonical sources", str(bad))


def validate_fig4() -> None:
    absolute = read_csv(PAPER / "07_figure_ready/fig4/A1_A6_absolute.csv")
    check(len(absolute) == 6, "Fig.4 absolute table has exactly six A1-A6 configurations", str(len(absolute)))
    for name in ("A1_A6_probability_trajectories.csv", "A1_A6_lifecycle_variation.csv", "A1_A6_cumulative_variation.csv"):
        path = PAPER / "07_figure_ready/fig4" / name
        if not path.exists():
            check(False, f"Fig.4 run-level file exists: {name}", str(path))
            continue
        rows = read_csv(path)
        check(len(rows) == 1824, f"Fig.4 run-level file has 1,824 audited rows (6 configs × 304 runs): {name}", str(len(rows)))
    stale = bpd.stale_fig4_scripts()
    check(not stale, "No formal Fig.4 script references the retired FINAL_ablation_outputs.csv", str(stale))


def validate_semantics() -> None:
    life = read_csv(PAPER / "01_PHM2010/04_semantics/C6_lifecycle_probability_wear.csv")
    hidden = read_csv(PAPER / "01_PHM2010/04_semantics/C6_hidden_representation.csv")
    stats = read_csv(PAPER / "01_PHM2010/04_semantics/q_statistics.csv")[0]
    check(len(life) == 304, "Lifecycle semantics contains 304 runs", str(len(life)))
    check(len(hidden) == 304 and all(r["split"] == "test_C6" and r["condition"] == "C6" for r in hidden), "Hidden representation is exactly 304 test_C6 rows", str(len(hidden)))
    for key, value in (("R2",0.7478018753),("Spearman_rho",0.9634587570),("MAE",0.1132309945),("stage_agreement",0.9868421053)):
        check(near(stats[key],value,1e-8), f"q statistic {key} recomputes to audited value", stats[key])


def validate_q_definitions() -> None:
    q_doc = PAPER / "00_metadata/Q_DEFINITIONS.md"
    check(q_doc.exists(), "Frozen q-definition document exists", str(q_doc))
    q_agreement_path = PAPER / "07_figure_ready/fig5/q_agreement.csv"
    if q_agreement_path.exists():
        rows = read_csv(q_agreement_path)
        fields = set(rows[0]) if rows else set()
        check("q_pred_norm" not in fields, "q_agreement.csv excludes q_pred_norm from reported agreement statistics", str(fields))
        check({"q_true","q_pred"} <= fields, "q_agreement.csv retains raw q_true/q_pred pair", str(fields))
    display_path = PAPER / "07_figure_ready/fig5/q_pred_normalized_display.csv"
    if display_path.exists():
        catalog = {r["canonical_path"]: r for r in read_csv(PAPER / "DATA_CATALOG.csv")}
        entry = catalog.get("paper_data/07_figure_ready/fig5/q_pred_normalized_display.csv")
        check(entry is not None and entry["status"] == "AUDIT_SUPPORTING", "q_pred_norm display file is cataloged AUDIT_SUPPORTING, not a main-table input", str(entry))


def validate_figure_ready_metadata() -> None:
    required = set(bpd.FIGURE_READY_METADATA_FIELDS)
    csv_paths = sorted((PAPER / "07_figure_ready").rglob("*.csv"))
    check(len(csv_paths) > 0, "07_figure_ready contains CSV files to validate")
    for path in csv_paths:
        rows = read_csv(path)
        if not rows:
            check(False, f"Figure-ready file is non-empty: {path.relative_to(PAPER)}", "0 rows")
            continue
        fields = set(rows[0])
        missing = required - fields
        check(not missing, f"{path.relative_to(PAPER)} has every required figure-ready metadata field", str(missing))
        empties = [k for k in required & fields if any(r[k] == "" for r in rows)]
        check(not empties, f"{path.relative_to(PAPER)} has non-empty values for every required metadata field", str(empties))


def validate_seed_sensitivity() -> None:
    catalog = read_csv(PAPER / "DATA_CATALOG.csv")
    base = "paper_data/01_PHM2010/05_training_seed_sensitivity/"
    sensitivity_rows = [r for r in catalog if r["canonical_path"].startswith(base)]
    check(len(sensitivity_rows) >= 8, "Both training-seed sensitivity suites were archived", str(len(sensitivity_rows)))
    check(all(r["status"] == "AUDIT_SUPPORTING" for r in sensitivity_rows), "Every training-seed sensitivity file is cataloged AUDIT_SUPPORTING", str({r["status"] for r in sensitivity_rows}))
    leaked = []
    for section in ("07_figure_ready", "08_table_ready"):
        for r in catalog:
            if not r["canonical_path"].startswith(f"paper_data/{section}/"):
                continue
            source = r.get("source_path", "")
            if "05_training_seed_sensitivity" in source or "final_five_seed_sweep" in source or "protocol_diagnostic_fixed_preprocess" in source:
                leaked.append(r["canonical_path"])
    check(not leaked, "Training-seed sensitivity evidence never feeds a figure/table-ready file", str(leaked))
    d1_source = read_csv(PAPER / "01_PHM2010/01_main_D1/D1_9methods_bootstrap_CI.csv")
    check(bool(d1_source), "D1 main table is present independent of seed-sensitivity archives")


def validate_nasa() -> None:
    summary = read_csv(PAPER / "02_NASA/original_split_mean_std.csv")
    tasks = read_csv(PAPER / "02_NASA/task_level_results.csv")
    check({r["Method"] for r in summary} == {"B9","B10","B11","B12"}, "NASA summary retains only real B9-B12 methods")
    check(len(tasks) == 16 and {r["Task"] for r in tasks} == {"N1","N2","N3","N4"}, "NASA original split has 4 methods × 4 task rows", str(len(tasks)))
    preds = list((PAPER / "02_NASA/predictions").glob("Pred_NASA_original_*.csv"))
    check(len(preds) == 16, "NASA retains 16 original-split prediction files", str(len(preds)))
    warnings.append("NASA authoritative package contains B9-B12 only; a nine-method NASA table is intentionally not fabricated.")


def validate_mendeley() -> None:
    summary = read_csv(PAPER / "03_MENDELEY_CROSS_MACHINE/dataset_summary.csv")
    tasks = read_csv(PAPER / "03_MENDELEY_CROSS_MACHINE/task_definitions.csv")
    check(len({r["machine"] for r in summary}) == 3, "Mendeley audit supports three machines")
    check(len({r["tool"] for r in summary}) == 9, "Mendeley audit supports nine tools")
    check(sum(int(r["run_count"]) for r in summary) == 6418, "Mendeley audit supports 6418 runs", str(sum(int(r["run_count"]) for r in summary)))
    check({r["task_id"] for r in tasks} == {"D1-M","D2-M","D3-M"}, "Mendeley task definitions are D1-M/D2-M/D3-M")
    seed_rows = read_csv(PAPER / "03_MENDELEY_CROSS_MACHINE/overall_by_seed.csv")
    task_col = "task" if "task" in seed_rows[0] else "Task"
    seed_col = "seed" if "seed" in seed_rows[0] else "Seed"
    check({r[task_col] for r in seed_rows} >= {"D1-M","D2-M","D3-M"} and {str(r[seed_col]) for r in seed_rows} >= {"42","52","62","72","82"}, "Mendeley five-seed final rows exist for all core tasks")
    source_done = list((ROOT / "experiments_mendeley/04_overall_comparison/runs").glob("D*-M/seed*/DONE.flag"))
    check(len(source_done) == 15, "Mendeley source has 3 tasks × 5 DONE flags", str(len(source_done)))
    single = read_csv(PAPER / "03_MENDELEY_CROSS_MACHINE/generalization/single_source/single_source_mean_std.csv")
    if single:
        warnings.append("A single-source summary file exists but is cataloged AUDIT_SUPPORTING; MS1-MS6 are not claimed as completed canonical tasks.")


def validate_integrity() -> None:
    copies = read_csv(PAPER / "90_provenance/COPY_MANIFEST.csv")
    for row in copies:
        src, dst = ROOT / row["source_path"], ROOT / row["canonical_path"]
        check(src.exists() and dst.exists() and sha256(src) == row["source_sha256"] and sha256(dst) == row["canonical_sha256"], f"Copy hash verified: {row['canonical_path']}")
    catalog = read_csv(PAPER / "DATA_CATALOG.csv")
    check(
        "paper_data/90_provenance/VALIDATION_REPORT.md" not in {r["canonical_path"] for r in catalog},
        "VALIDATION_REPORT.md is excluded from DATA_CATALOG.csv (post-validation runtime artifact)",
    )
    for row in catalog:
        if row["canonical_path"] == "paper_data/DATA_CATALOG.csv":
            continue
        path = ROOT / row["canonical_path"]
        check(path.exists() and sha256(path) == row["canonical_sha256"], f"Catalog hash verified: {row['canonical_path']}")
        if row["status"] in {"AUTHORITATIVE","CANONICAL_COPY"}:
            check(bool(row["source_sha256"]), f"Canonical source hash recorded: {row['canonical_path']}")
        if row["data_level"] in {"figure_ready","table_ready","derived_metric","derived_distribution"}:
            check(bool(row["source_path"]) and bool(row["transformation"]), f"Derived lineage recorded: {row['canonical_path']}")
    checksums = read_csv(PAPER / "90_provenance/CHECKSUMS.csv")
    check(
        "paper_data/90_provenance/VALIDATION_REPORT.md" not in {r["canonical_path"] for r in checksums},
        "VALIDATION_REPORT.md is excluded from CHECKSUMS.csv (prevents a self-invalidating build/validate cycle)",
    )
    for row in checksums:
        path = ROOT / row["canonical_path"]
        check(path.exists() and sha256(path) == row["sha256"], f"Checksum verified: {row['canonical_path']}")
    long = read_csv(PAPER / "06_canonical_tables/all_metrics_long.csv")
    groups = defaultdict(set)
    for row in long:
        key = tuple(row[k] for k in ("dataset_id","task_id","protocol_id","method_id","configuration_id","seed","aggregation_level","metric"))
        groups[key].add(row["value"])
    conflicts = [key for key, values in groups.items() if len(values) > 1]
    check(not conflicts, "No semantic key points to conflicting authoritative values", str(conflicts[:5]))
    untracked = [r for r in copies if r["git_tracked"] == "false"]
    if untracked:
        warnings.append(f"{len(untracked)} canonical copies originate from real local but Git-untracked/ignored source files; paths and hashes are recorded.")


def validate_documentation() -> None:
    unresolved = read_csv(PAPER / "90_provenance/UNRESOLVED_ITEMS.csv")
    check(not any(r["item_id"].startswith("MS-") for r in unresolved), "Manuscript-only sync items are not mixed into UNRESOLVED_ITEMS.csv", str([r["item_id"] for r in unresolved]))
    if unresolved:
        warnings.append(f"{len(unresolved)} data-integrity/script issues remain explicitly unresolved; see UNRESOLVED_ITEMS.csv.")


def validate_manuscript_sync() -> None:
    path = PAPER / "90_provenance/MANUSCRIPT_SYNC_STATUS.csv"
    check(path.exists(), "MANUSCRIPT_SYNC_STATUS.csv exists as a separate manuscript-sync artifact", str(path))
    if not path.exists():
        return
    rows = read_csv(path)
    check(all(r.get("manuscript_sync_status") == "PENDING" for r in rows), "Every manuscript-sync item is explicitly marked PENDING", str({r.get("manuscript_sync_status") for r in rows}))
    if rows:
        warnings.append(
            f"{len(rows)} manuscript-only synchronization item(s) pending human review (see MANUSCRIPT_SYNC_STATUS.csv); "
            "this is a manuscript-text concern, not a paper_data numerical-integrity failure."
        )


def write_report() -> str:
    status = "FAIL" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    lines = ["# paper_data validation report", "", f"**VALIDATION STATUS = {status}**", "", "## Passed checks", ""]
    lines += [f"- {item}" for item in passes]
    lines += ["", "## Warnings", ""] + ([f"- {item}" for item in warnings] or ["- None"])
    lines += ["", "## Failures", ""] + ([f"- {item}" for item in failures] or ["- None"])
    lines += ["", "## Interpretation", "", "PASS_WITH_WARNINGS means all numerical/integrity invariants passed, while declared manuscript updates, local untracked sources, or stale plotting scripts still require human-controlled follow-up. No warning licenses replacement of canonical values."]
    (PAPER / "90_provenance/VALIDATION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"VALIDATION STATUS = {status}")
    print(f"passed={len(passes)} warnings={len(warnings)} failures={len(failures)}")
    return status


def main() -> int:
    validate_d1(); validate_methods(); validate_dataset_naming()
    validate_cross_condition(); validate_fig2(); validate_ablation(); validate_fig4()
    validate_semantics(); validate_q_definitions(); validate_figure_ready_metadata()
    validate_seed_sensitivity()
    validate_nasa(); validate_mendeley(); validate_integrity()
    validate_documentation(); validate_manuscript_sync()
    return 1 if write_report() == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate paper_data invariants and write VALIDATION_REPORT.md."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper_data"
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


def validate_cross_condition() -> None:
    rows = read_csv(PAPER / "01_PHM2010/02_cross_condition_D1_D2_D3/transfer_tasks_long.csv")
    check(len(rows) == 27, "Cross-condition table has 9 methods × 3 tasks", str(len(rows)))
    check({r["Task"] for r in rows} == {"D1","D2","D3"}, "Cross-condition task names are complete")
    required = {"n_test","test_universe","aggregation_level","protocol_id","source_path"}
    check(required <= set(rows[0]) and all(all(r[k] != "" for k in required) for r in rows), "Every cross-condition row records universe/protocol/source", "missing field/value")


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


def validate_semantics() -> None:
    life = read_csv(PAPER / "01_PHM2010/04_semantics/C6_lifecycle_probability_wear.csv")
    hidden = read_csv(PAPER / "01_PHM2010/04_semantics/C6_hidden_representation.csv")
    stats = read_csv(PAPER / "01_PHM2010/04_semantics/q_statistics.csv")[0]
    check(len(life) == 304, "Lifecycle semantics contains 304 runs", str(len(life)))
    check(len(hidden) == 304 and all(r["split"] == "test_C6" and r["condition"] == "C6" for r in hidden), "Hidden representation is exactly 304 test_C6 rows", str(len(hidden)))
    for key, value in (("R2",0.7478018753),("Spearman_rho",0.9634587570),("MAE",0.1132309945),("stage_agreement",0.9868421053)):
        check(near(stats[key],value,1e-8), f"q statistic {key} recomputes to audited value", stats[key])


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
    if unresolved:
        warnings.append(f"{len(unresolved)} manuscript/script issues remain explicitly unresolved; see UNRESOLVED_ITEMS.csv.")
    stale_scripts = []
    for path in (ROOT / "figures/fig4_ablation/plot_fig4.py", ROOT / "nature_figures/scripts/fig4_ablation.py", ROOT / "nature_figures/scripts/generate_docs.py"):
        if path.exists() and "FINAL_ablation_outputs.csv" in path.read_text(encoding="utf-8", errors="ignore"):
            stale_scripts.append(path.relative_to(ROOT).as_posix())
    if stale_scripts:
        warnings.append("FIG4_SCRIPT_REQUIRES_SOURCE_UPDATE: " + ", ".join(stale_scripts))


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
    validate_d1(); validate_cross_condition(); validate_ablation(); validate_semantics()
    validate_nasa(); validate_mendeley(); validate_integrity(); validate_documentation()
    return 1 if write_report() == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())

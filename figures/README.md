# 第 4 章正式组图

本目录包含 5 张基于项目真实实验结果重建的正式论文组图。全部图采用同一套 Python/Matplotlib 样式、方法配色和阶段配色；子图说明均位于图框下方居中。每张图均提供 PDF、600 dpi PNG、保留文本节点的 SVG、独立绘图脚本、数据清单和复现说明。

## 图组索引

| 图 | 功能 | 主要输入 | 输出 |
|---|---|---|---|
| Fig.1 | D1 正式性能证据、bootstrap CI 与精度–连续性权衡 | `final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv` | `fig1_overall_performance/fig1_overall_performance.{pdf,png,svg}` |
| Fig.2 | D1/D2/D3 条件内相对性能与 DC-PSR 排名轮廓 | `final_statistical_evidence/results/TRANSFER_TASKS_D1_D2_D3.csv` | `fig2_cross_condition/fig2_cross_condition.{pdf,png,svg}` |
| Fig.3 | PHM2010、NASA 与跨机器任务的迁移视角及 D2-M 失效边界 | D1、NASA、cross-machine 汇总与 D2-M seed-42 预测文件 | `fig3_cross_dataset/fig3_cross_dataset.{pdf,png,svg}` |
| Fig.4 | A1–A6 权威消融审计、增益分解与权衡轨迹 | `补充材料/小论文/3_main_experiment_fgds_psi/1_results/FINAL_ablation_outputs.csv` | `fig4_ablation/fig4_ablation.{pdf,png,svg}` |
| Fig.5 | 工具寿命中的阶段概率、q 一致性、隐藏表示与物理磨损语义 | A6 概率–磨损轨迹及保存的 HCT 隐藏表示 | `fig5_semantics/fig5_semantics.{pdf,png,svg}` |

## 三项强制数据审计摘要

1. **Fig.3 跨数据集数值**：PHM2010 使用 304-run D1 common-universe 最终表；NASA 使用 original N1–N4 汇总；跨机器任务使用 D1-M/D2-M/D3-M 五随机种子汇总。三种统计口径不混合估计，也不作 pooled significance 声明；所有负的 Accuracy delta 均原样保留。
2. **Fig.4 A1–A6**：最终权威文件确认 A1–A4 的 Acc、Macro-F1、M-F1、M-Rec 完全相同，差异只出现在 Smooth。该结果被如实保留并明确标注，不按预期叙事修改。Rev、Jump、M→L 在 A1–A6 中均为 0，因此写入 manifest，但不占用视觉面板。
3. **Fig.5(c) q 指标**：R²、Spearman rho 和 MAE 均在完整 C6 生命周期的 304 个 run 上，由 `q_true` 与 `q_pred` 直接计算；对应结果为 R² = 0.7478、rho = 0.9635、MAE = 0.1132。

每项输入文件的 SHA-256、读取列、聚合、归一化、bootstrap 处理和关键数值见各子目录的 `data_manifest.json`。

## 复现

在项目根目录执行：

```powershell
C:\Users\banghai\miniconda3\python.exe figures\fig1_overall_performance\plot_fig1.py
C:\Users\banghai\miniconda3\python.exe figures\fig2_cross_condition\plot_fig2.py
C:\Users\banghai\miniconda3\python.exe figures\fig3_cross_dataset\plot_fig3.py
C:\Users\banghai\miniconda3\python.exe figures\fig4_ablation\plot_fig4.py
C:\Users\banghai\miniconda3\python.exe figures\fig5_semantics\plot_fig5.py
```

脚本从项目中的源 CSV 重新读取数据，并覆盖对应的 PDF、PNG、SVG 和 `data_manifest.json`。公共样式与导出逻辑位于 `_shared/`。

## 最终质检

- 5/5 图均为规则 2×2 或 2×3 布局，白底、无顶部子图标题。
- 5/5 图的 `(a)–(f)` 子图说明均位于各自图框下方并居中。
- 5/5 PDF 均可解析且为单页；5/5 SVG 均可解析并保留文本节点。
- 5/5 PNG 均以 600 dpi 导出，宽度约 4157–4421 px。
- 5/5 脚本已在指定 Python 环境中从真实源文件独立运行通过。


# Fig.3 — Cross-dataset / Cross-benchmark Perspective

## 图意

将 PHM2010、NASA 和跨机器任务组织为逐步增大的 domain shift 视角。图中如实呈现负 Accuracy delta，并突出 DC-PSR 在 M-F1、Smooth 和 ordered inference 上的相对收益以及 D2-M 的可解释失效模式。

## 子图

- (a) 三类 benchmark 的 shift ladder 与统计口径说明。
- (b) 各数据集/场景中 DC-PSR 相对 backbone 的关键指标 delta 热图。
- (c) D1-M、D2-M、D3-M 的任务级相对增益 small multiples。
- (d) 2,751 个 D2-M seed-42 测试 run 的真实阶段与预测阶段分布，揭示 middle collapse。

## 数据来源与审计结论

- PHM2010：`final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv`，304-run D1 common universe。
- NASA：`补充材料/小论文/nasa_dcpsr_results_stageaware_opt/Table_NASA_original_split_mean_std.csv`，original N1–N4 汇总。
- 跨机器：`experiments_mendeley/04_overall_comparison/summary/overall_comparison_mean_std_by_task.csv`，D1-M/D2-M/D3-M 五随机种子汇总。
- D2-M 失效边界：`experiments_mendeley/07_semantic_consistency/probability_evolution/D2-M_seed42_predictions_test_B11B12.csv`。

NASA 与跨机器源文件的统计重复单位不同，因此不合并方差、不做 pooled significance 声明。负的 Accuracy delta 未裁剪、未择优种子。文件哈希、读取列和全部关键 delta 见 `data_manifest.json`。

## 重新运行

```powershell
C:\Users\banghai\miniconda3\python.exe figures\fig3_cross_dataset\plot_fig3.py
```

输出为 `fig3_cross_dataset.pdf`、`.png`、`.svg`，并同步更新 `data_manifest.json`。


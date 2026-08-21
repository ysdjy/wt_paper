# Fig.4 — Ablation Study

## 图意

基于权威 A1–A6 最终文件展示分类性能与连续性之间的逐步权衡，重点支撑方法组件如何改变最终行为，而不人为制造源文件中不存在的分类差异。

## 子图

- (a) A1–A6 相对 A1 的 raw delta 矩阵；颜色只辅助判断方向，格内数字为真实 delta。
- (b) 分类指标与连续性指标的双视图分解。
- (c) A1→A6 在 Smooth–Accuracy 空间的真实演进轨迹。
- (d) 由观测结果支持的组件阶段摘要卡片。

## 数据来源与权威审计

唯一输入为 `补充材料/小论文/3_main_experiment_fgds_psi/1_results/FINAL_ablation_outputs.csv`，筛选 A1–A6、`Split=test_C6`，每行为完整 304-run C6 最终汇总。

**保留的 warning**：权威文件确认 A1–A4 的 Acc、Macro-F1、M-F1、M-Rec 完全相同；只有 Smooth 发生变化。这一事实不是绘图错误，图中按原始数据保留。Rev、Jump、M→L 在 A1–A6 中全部为 0，已记录在 `data_manifest.json`，但因无区分度未放入视觉面板。

## 重新运行

```powershell
C:\Users\banghai\miniconda3\python.exe figures\fig4_ablation\plot_fig4.py
```

输出为 `fig4_ablation.pdf`、`.png`、`.svg`，并同步更新 `data_manifest.json`。


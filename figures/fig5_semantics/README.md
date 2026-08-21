# Fig.5 — Degradation Semantics and Probability Structure

## 图意

展示 DC-PSR 在完整工具寿命上的阶段概率迁移、q 估计一致性、隐藏表示结构，以及预测阶段与真实物理磨损 VB 的对应关系。

## 子图

- (a) 304 个 C6 run 上的 Early/Middle/Late 概率演化。
- (b) 同一批 run 的三元概率 simplex 轨迹。
- (c) `q_true` 与 `q_pred` 的一致性散点及真实统计量。
- (d) 保存的 64 维 HCT 隐藏表示经标准化后进行确定性 NumPy SVD PCA。
- (e) 按预测阶段分组的真实 VB 分布。
- (f) 样本数、阶段一致率及三个核心 q 统计量摘要。

## 数据来源与审计结论

概率、q 与磨损数据来自 `补充材料/小论文/9_probability_wear_consistency_analysis/Data_5_4_A6_probability_wear_trajectory.csv`，使用完整 C6 生命周期 304 行。R² = 0.7478、Spearman rho = 0.9635、MAE = 0.1132 均由这 304 行的 `q_true` 与 `q_pred` 直接计算。

隐藏表示来自 `补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/repr_hidden_hct.csv`，仅筛选 `split=test_C6`、`condition=C6` 的 304 行和 `h_00–h_63`。PCA 不重训模型、不调参、不用标签拟合。详细哈希、列和统计量见 `data_manifest.json`。

## 重新运行

```powershell
C:\Users\banghai\miniconda3\python.exe figures\fig5_semantics\plot_fig5.py
```

输出为 `fig5_semantics.pdf`、`.png`、`.svg`，并同步更新 `data_manifest.json`。


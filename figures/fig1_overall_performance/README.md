# Fig.1 — Overall Performance

## 图意

展示 D1 正式实验中 DC-PSR 的分类性能、bootstrap 不确定性，以及相对共享 backbone 的连续性收益。核心结论是分类性能基本保留，同时 Smooth 降低约 20.46%。

## 子图

- (a) 9 种方法的 D1 Accuracy 与 moving-block bootstrap 95% CI。
- (b) Accuracy–Smooth Pareto 视图；横轴越右、纵轴越低越优。
- (c) Multi-task TCN-GRU 与 DC-PSR 的受控指标对比，省略无信息增量的 Rev。
- (d) 相对 backbone 的归一化摘要：分类保留率与 Smooth 改善。

## 数据来源与口径

输入为 `final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv`。使用全部 9 个方法行；panel (c)/(d) 仅使用 Multi-task TCN-GRU 与 DC-PSR。CI 直接读取最终表，不重新 bootstrap。DC-PSR Accuracy = 0.986842，95% CI = [0.963816, 1.000000]；详细列、哈希和关键数值见 `data_manifest.json`。

## 重新运行

在项目根目录执行：

```powershell
C:\Users\banghai\miniconda3\python.exe figures\fig1_overall_performance\plot_fig1.py
```

输出为 `fig1_overall_performance.pdf`、`.png`、`.svg`，并同步更新 `data_manifest.json`。


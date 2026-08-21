# Fig.2 — Cross-condition Robustness

## 图意

强调 D1/D2/D3 的目标条件依赖性，并把 DC-PSR 的贡献定位为 ordered inference/consistency 改善，而非跨条件的绝对精度统治。

## 子图

- (a) 各任务内部 min–max 的相对 Accuracy，格内数字为任务内排名。
- (b) 各任务内部 min–max 的相对 M-F1，格内数字为任务内排名。
- (c) 由 Smooth 反向 min–max 得到的相对 Consistency，格内数字为任务内排名。
- (d) DC-PSR 在 D1/D2/D3 的三类指标排名轮廓。

## 数据来源与口径

输入为 `final_statistical_evidence/results/TRANSFER_TASKS_D1_D2_D3.csv`，共 27 行（9 方法 × 3 任务）。颜色只表示各任务内部相对水平，不跨任务比较绝对量；图中不展示跨任务绝对均值。D1/D2/D3 使用各自正式 native test universe，详细处理见 `data_manifest.json`。

## 重新运行

```powershell
C:\Users\banghai\miniconda3\python.exe figures\fig2_cross_condition\plot_fig2.py
```

输出为 `fig2_cross_condition.pdf`、`.png`、`.svg`，并同步更新 `data_manifest.json`。


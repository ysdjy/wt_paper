# Fig.4 Refined — 可视化精修说明

## 结论与数据冻结

本次只优化 Fig.4 的视觉表达，没有改变 A1–A6 定义、D1（C1+C4 → C6）任务、统计口径、实验协议或任何数值；没有训练、调参或重新推理。

## 数据来源

- 子图 (a)：`AUTHORITATIVE_A1_A6.csv`。
- 子图 (b)：`A1_A6_lifecycle_variation.csv`。浅线为原始相邻概率 L1 变化，深线为仅供显示的 11-run 居中滑动平均。
- 子图 (c)：`AUTHORITATIVE_A1_A6.csv`；其中 M-Precision 来自审计通过的 `ABLATION_RECOMPUTED.csv`。
- 子图 (d)：`A1_A6_cumulative_variation.csv`，由未经平滑的相邻概率 L1 变化累计得到。
- 审计依据：`ABLATION_DATA_AUDIT.md`、`FIG4_V2_DATA_AUDIT.md` 和 `data_manifest.json`。

## 相对上一版的精修

1. (a) 的 Smooth A1–A6 六个点全部标注 4 位小数；标签上下交错，A5/A6 加粗。
2. (c) 的 M→E 与 M→L 六个点全部标注 3 位小数；零值也逐点显示为 `0.000`。
3. (b) 与 (d) 的 A1–A6 图例统一为竖向单列，并使用半透明白底与弱边框。
4. (b) 的 raw / 11-run mean 说明移动到顶部曲线稀疏区。
5. (d) 移除了上一版拥挤的右侧端点标签连线；竖排图例、终端关系说明、A5 与 A6 结论分别放在独立留白区，避免穿越主要曲线。
6. 四个标题统一放在子图正下方居中，编号格式、字号和间距一致。
7. A5/A6 背景高亮继续保留，但透明度降低；它仍支持“平滑约束 → 最终 ordered inference”的叙事，同时不压过柱体和折线。

## 输出

- `fig4_ablation_refined.pdf`
- `fig4_ablation_refined.png`（600 dpi）
- `fig4_ablation_refined.svg`（文本可编辑）
- `plot_fig4_ablation_refined.py`

明确声明：**未修改权威数据，未改变实验协议，未发生训练或重新推理。**

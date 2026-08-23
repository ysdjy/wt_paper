# Fig4-4 消融实验 — Refinement Round 5（多处间距微调）

## 改了哪些布局项

1. **(a)/(b) caption 拉近**：偏移量从 `y=-0.24` 收紧到 `y=-0.16`，标题现在离柱状图/折线图更近。
2. **(c) 共享图例拉近**：`p_E/p_M/p_L` 图例与四个子图之间的间距从 `c_top + 0.014` 收紧到
   `c_top + 0.004`。
3. **(c) 组标题拉近**：子标题（A1/A4/A5/A6）偏移量从 `y=-0.18` 收紧到 `y=-0.13`；组标题
   `"(c) Probability-state formation: ..."` 与子标题之间的间距从 `0.032/0.014` 收紧到
   `0.022/0.008`，整体离四个子图更近。
4. **(d) 图例线段拉长**：`handlelength` 从 `1.3` 增加到 `2.2`，图例中 A1-A6 的线段样本更长
   更醒目。
5. **(e) 整体下移，靠近自己的 caption**：面板内部的模块垂直中心从 `0.64` 降到 `0.48`
   （ylim 下界相应从 `0.18` 收紧到 `0.06`，避免下方文字被裁切）——六个模块和它们下方的
   description 文字现在更靠近 (e) 自己的 caption，同时与上方 (d1)/(d2) 之间的空白相应增大。

## 检查结果

打开最终 PNG 逐项确认：所有 caption/图例改动后均未产生新的重叠或裁切；(a)(b) 标题、(c) 图例
与组标题、(d) 图例、(e) 模块位置均达到"不贴、不远"的效果。

## 是否改动了任何数据？

**没有。** 本轮只修改了 `scripts/panels.py`（caption 偏移量、panel (e) 的垂直中心与 ylim）
和 `scripts/assemble.py`（共享图例的间距参数）。`scripts/load_data.py`、`derived/*.csv`
均未改动。所有数值与此前版本完全一致。

## 输出文件

- `outputs/Fig4_4_ablation.pdf` / `.svg` / `_600dpi.png` / `_preview.png`
- `../final_pdf/fig4_4_ablation.pdf` / `_600dpi.png`（提交用固定文件名，已更新）

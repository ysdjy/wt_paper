# Fig4-5 退化语义与表示几何 — Refinement Round 2（取消所有边框，修复标题碰撞）

沿用对 Fig4-2/Fig4-3/Fig4-4 应用的同一套精修要求：不加任何边框，检查并修复潜在的
caption 碰撞，不改动任何数据。这是 Fig4-5 在"无边框"方向上的第一轮精修。

## 改了哪些布局项

1. **移除所有边框**：删除了此前的四个 block 边框（"Raw-feature geometry" /
   "Shared latent geometry" / "Probability-state geometry" / "Semantic anchors"）以及整图
   外框。现在没有任何装饰性边框。
2. **主动修复 (A)/(B) 组标题的潜在碰撞**：两个组标题原来都用固定偏移量
   （`a_bottom - 0.055` / `b_bottom - 0.055`）定位，没有考虑每个子图下方的
   `(a)(b)(c)`/`(d)(e)(f)` 子标题（`y=-0.20`）——这与 Fig4-2 panel (d)、Fig4-4 panel (c)
   是同一类问题，本轮压缩留白前主动用 `caption_bottom_fig_frac()` 改为从子标题的真实
   渲染位置计算，防患于未然。
3. **间距重新分配**：
   - Block A ↔ Block B 之间的 spacer：初次设为 `0.20` 后打开 PNG 发现 (A) 组标题仍然
     溢出到 Block B 的图上（间距不够同时容纳"清理自己子标题"和"留出到下一块的净空"两个
     要求），已增加到 `0.34` 解决。
   - Block B ↔ Block C/D、Block C/D ↔ Block E 的 spacer 保持 `0.20`，全局 `hspace` 收紧到
     `0.10`（显式 spacer 承担主要间距，避免 hspace 在 7 行结构中被平均高度放大而失控——
     沿用 Fig4-3 学到的教训）。
   - 整图高度：240mm → 222mm。

## 检查结果

打开最终 PNG 逐项检查：(A)/(B) 组标题与各自的子标题、以及下一个 block 的内容均无重叠；
(C)/(D) 3D 图的 caption 与 (E) 语义锚点面板之间间距正常；顶部无遮挡，底部 (e1)/(e2) caption
完整可见，无裁切。

## 是否改动了任何数据？

**没有。** 本轮只修改了 `scripts/assemble.py`（删除边框调用、GridSpec 比例、组标题定位逻辑）。
`scripts/panels.py`、`scripts/load_data.py`、`derived/*.csv` 均未改动。所有数值（PCA 坐标、
q_true/q_pred、VB 数值、R²/Spearman/MAE、颜色语义）与此前版本完全一致。

## 输出文件

- `outputs/Fig4_5_semantics_geometry.pdf` / `.svg` / `_600dpi.png` / `_preview.png`
- `../final_pdf/fig4_5_degradation_representation.pdf` / `_600dpi.png`（提交用固定文件名，已更新）

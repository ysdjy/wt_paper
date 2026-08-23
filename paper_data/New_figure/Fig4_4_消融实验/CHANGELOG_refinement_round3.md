# Fig4-4 消融实验 — Refinement Round 3（取消所有边框，修复间距问题）

沿用对 Fig4-2/Fig4-3 应用的同一套精修要求：不加任何边框，每个子图与自己 caption 的距离、
以及两排图之间的距离都要恰当（不贴、不空），不改动任何数据。

## 改了哪些布局项

1. **移除所有边框**：删除了此前的三个 block 边框（"Performance" / "Probability-state
   formation" / "Variation & mechanism"）以及整图外框。现在没有任何装饰性边框。
2. **修复 (c) 组标题与子标题的重叠**（真实碰撞，打开 PNG 发现）：组标题
   `"(c) Probability-state formation: ..."` 原来用固定偏移 `c_bottom - 0.075` 定位，没有考虑
   每个小图下方的 A1/A4/A5/A6 子标题（`y=-0.30`），二者几乎在同一高度，导致 "A4 (mix,
   pre-ordering)" 和部分 "A5" 文字被组标题覆盖——与 Fig4-2 panel (d) 的碰撞是同一类问题。
   修复为用 `caption_bottom_fig_frac()` 先算出四个子标题中最深的真实底部位置（并加大
   `extra` 余量到 0.050），组标题再定位到它下方。中间尝试过一次余量不够，组标题又和下方
   (d1)/(d2) 的绘图区顶部太近，也已发现并修正。
3. **重新分配三处纵向间距**（既不贴、也不留大空白，逐次渲染检查后确定）：
   - row1（(a)(b)）↔ row2（(c) 四小图）：spacer 从 `0.16` 增加到 `0.26`——此前 (a)/(b) 的
     caption 几乎贴着 (c) 的绘图区顶部。
   - row2（(c)）↔ row3（(d1)(d2)+(e) 整体）：spacer 从 `0.15` 增加到 `0.40`——(c) 的组标题
     修复后位置下移，需要更多余量才能不贴到 (d1)/(d2)。
   - Block III 内部 (d1)(d2) ↔ (e)：保持 `hspace=0.55` 不变，检查确认间距本身已经合适。
   - `hspace`（全局，跨 5 行）保持很小的 `0.14`——沿用 Fig4-3 学到的教训：在多行 GridSpec 里
     `hspace` 会按平均行高同时作用在所有相邻行对上，容易在不知不觉中主导间距；本轮统一让显式
     spacer 承担"有意为之"的间隙，`hspace` 只提供最小限度的基础间距。
   - 整图高度：196mm → 188mm。

## 检查结果

打开最终 PNG 逐项检查：
- (a)/(b) 的 caption 与 (c) 的绘图区无碰撞，间距适中。
- (c) 的四个子标题（A1/A4/A5/A6）完整可读，组标题与它们、以及与下方 (d1)/(d2) 均无重叠。
- (d1)/(d2) 的图例、caption 与 (e) 机制条之间间距正常，不贴不空。
- 顶部图例（(a)/(b)）与图像上边缘、底部 (e) caption 与图像下边缘均有合理余量，无裁切。

## 是否改动了任何数据？

**没有。** 本轮只修改了 `scripts/assemble.py`（删除边框调用、GridSpec 高度比例、(c) 组标题
定位逻辑）。`scripts/panels.py`、`scripts/load_data.py`、`derived/*.csv` 均未改动。所有数值、
A1–A6 配置定义、Smooth/Acc/Macro-F1/M-Rec 数值、stage-wise F1、local/cumulative variation
数据、颜色语义均与此前版本完全一致。

## 输出文件

- `outputs/Fig4_4_ablation.pdf` / `.svg` / `_600dpi.png` / `_preview.png`
- `../final_pdf/fig4_4_ablation.pdf` / `_600dpi.png`（提交用固定文件名，已更新）

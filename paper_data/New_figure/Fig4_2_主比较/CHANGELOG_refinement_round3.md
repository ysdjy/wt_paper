# Fig4-2 主比较 — Refinement Round 3（版式微调，不改结构/数据）

## 改了哪些布局项

1. **压缩 (d)↔(e1-e3) 间距**：GridSpec 中 d-e 之间的 spacer 行高度比例从 `0.13` 降到 `0.07`
   （−46%，落在要求的 40-50% 区间）；腾出的空间没有简单丢弃，而是**回补给了 (d) 和 (e) 自身的
   绘图区**（`ROW2_H` 0.80→0.85，`ROW3_H` 1.00→1.05），即两块的实际 plotting area 略有增大，
   不是缩小。整图高度 168mm→160mm。
2. **e1/e2/e3 caption 纳入 outer border**：GridSpec 的 `bottom` 边距从 `0.045` 增加到
   `0.090`，确保三个两行 caption（"(e1) Middle-stage recognition" 等）完整落在 figure 的
   `(0,1)` 范围以内——根因是此前 `bottom` 太小，`bbox_inches="tight"` 导出时把画布向下"偷偷"
   扩展去容纳这些 caption，而外框是按原始 `(0,1)` 画的，于是外框看起来在 caption 上方而不是
   包住它们。现在 caption 在导出前就已经完整落在画布内，外框自然包住它们。
3. **顶部 legend 与外框间距**：GridSpec 的 `top` 边距从 `0.975` 降到 `0.955`，为 (a)/(c) 的
   悬浮图例与外框之间增加了稳定的小间距，没有大幅增加整图高度。
4. **panel (a) 方法名**：旋转角 30°→33°（在 30-40° 要求区间内，right-aligned 不变），新增
   `rotation_mode="anchor"`（旋转锚点更准确，避免默认模式下文字轻微偏移），`tick_params(pad=1.5)`
   缩短刻度线与文字的距离；panel (a) 自身宽度比例从 `1.15`→`1.25`（(b)/(c) 相应从 `1.0`→`0.95`），
   为最长的方法名（"Multi-source Attention" 等）留出更多横向空间。
5. **panel (b) 清理**：删除了 "Multi-source Attention" 灰色文字标注，现在除 Multi-task
   TCN-GRU / DC-PSR 外的所有 baseline 都只画朴素灰色 marker，不再有任何内嵌文字——不再与
   y 轴区域产生视觉冲突。Multi-task TCN-GRU / DC-PSR 仍通过图例明确标识。
6. **panel (c) 精简坐标轴标题**：x 轴标题从 `"Value (%), moving-block bootstrap 95% CI"` 简化为
   `"Score (%)"`；统计含义移到 caption：`"(c) Moving-block bootstrap 95% CIs"`（原来的
   `"(c) Bootstrap 95% CI, representative methods"` 两行文本替换为这一行）。

## 修复的问题

- (d)/(e) 之间空白过大 → 已压缩约 46%，同时增大了 (d)/(e) 自身绘图区。
- e1/e2/e3 caption 溢出 outer border → 已通过增加 `bottom` 边距修复（根因修复，非硬塞）。
- 顶部 legend 贴边框 → 已通过增加 `top` 边距修复。
- panel (a) 方法名拥挤感 → 已通过加宽 panel + 微调旋转角/tick pad 缓解，字号未缩小。
- panel (b) annotation 与坐标轴冲突 → 已删除该 annotation。
- panel (c) x 轴标题过长 → 已简化，统计含义保留在 caption。

**注意**：第一次尝试本轮改动时，为了同时压缩 spacer 还顺手把 `hspace`（0.55→0.32）和
`SPACER1_H`（0.11→0.10）也调小了，结果导致 panel (a)/(b)/(c) 的 caption 与 (d) 的混淆矩阵发生
碰撞（打开 PNG 检查发现）。已回退这两处改动到第二轮的原值——本轮**只**压缩了 (d)↔(e) 之间的
spacer，(a,b,c)↔(d) 之间的间距未受影响。

## 残留问题

无新增残留问题。此前已记录的细节（如 panel (b) 的 gray marker 分布本身、部分数值标签在极小
物理尺寸下的可读性）不在本轮修改范围内，未受影响。

## 是否改动了任何数据？

**没有。** 本轮只修改了 `scripts/panels.py`（x-tick 旋转角/pad、panel (b) 的 annotation 删除、
panel (c) 的坐标轴标题文字与 caption 文字）和 `scripts/assemble.py`（GridSpec 高度比例、上下
边距、panel (a) 宽度比例）。未触碰 `scripts/load_data.py`、`derived/*.csv`，或任何数值计算逻辑。
所有数值、排序、方法优劣关系、confusion matrix 数值、bootstrap CI、指标定义、色彩语义均与此前
版本完全一致。

## 自检清单

- [x] (d) 和 (e) 之间的大空白已明显压缩（spacer 高度 −46%，同时 (d)/(e) 绘图区略有增大）
- [x] e1/e2/e3 captions 全部在 outer border 内（`bottom` 边距增加，根因修复）
- [x] 顶部 legends 不再贴边（`top` 边距增加）
- [x] panel (a) 方法名没有严重拥挤（33°、加宽 panel、缩短 tick pad，字号未缩小）
- [x] panel (b) 没有 annotation 与 y-axis 冲突（annotation 已删除）
- [x] panel (c) 横轴标题不再过长（简化为 "Score (%)"，统计含义移入 caption）
- [x] 所有子图 caption 仍位于各自子图下方居中
- [x] 没有修改任何原始数据
- [x] PDF 与 600-dpi PNG 均正常导出（见下方输出文件）

## 输出文件

- `outputs/Fig4_2_main_comparison.pdf` / `.svg` / `_600dpi.png` / `_preview.png`
- `../final_pdf/fig4_2_main_comparison.pdf` / `_600dpi.png`（提交用固定文件名，已更新）

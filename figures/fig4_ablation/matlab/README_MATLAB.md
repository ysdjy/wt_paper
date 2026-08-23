# Fig.4 MATLAB 复现版

## 内容

- `plot_fig4_ablation_refined_matlab.m`：MATLAB R2021a 绘图脚本。
- `fig4_ablation_refined_matlab.pdf`：矢量 PDF。
- `fig4_ablation_refined_matlab.png`：600 dpi PNG。
- `fig4_ablation_refined_matlab.svg`：矢量 SVG。
- `fig4_ablation_refined_matlab.fig`：MATLAB 原生可编辑图，可直接点选文字、曲线和图例。

## 数据来源

脚本只读上一级 `fig4_ablation` 目录中的审计通过数据：

- `AUTHORITATIVE_A1_A6.csv`
- `ABLATION_RECOMPUTED.csv`
- `A1_A6_lifecycle_variation.csv`
- `A1_A6_cumulative_variation.csv`

脚本不会修改数据，不会训练、调参或重新推理。绘图前会检查 A1–A6 顺序、轨迹行数、每组生命周期点数以及 Smooth 与局部/累计变化的一致性。

## 运行方式

在 MATLAB 中执行：

```matlab
cd('项目目录/figures/fig4_ablation/matlab')
plot_fig4_ablation_refined_matlab
```

或者在 Windows PowerShell 中执行：

```powershell
& 'C:\Program Files\Polyspace\R2021a\bin\matlab.exe' -batch "cd('项目目录/figures/fig4_ablation/matlab'); plot_fig4_ablation_refined_matlab"
```

## 快速修改入口

- 配色、字体、字号：脚本中的 `figureStyle()`。
- 四个子图内容：`drawPanelA()`、`drawPanelB()`、`drawPanelC()`、`drawPanelD()`。
- 四个子图位置：主函数中的 `panelPos`。
- 子图下方标题：`belowTitle()`。
- A5/A6 浅色背景：`drawHighlights()`。
- 数值标签位置：`drawPanelA()` 中的 `labelOffsets`，以及 `drawPanelC()` 中的 `eOffsets`。

明确声明：**该目录为 MATLAB 可视化复现，不改变正式实验结果。**

补充说明：MATLAB R2021a 的 `print -dsvg` 会将部分文字转换成矢量轮廓。需要交互式修改文字时，优先打开 `.fig` 文件，修改后再由 MATLAB 重新导出。

# Authoritative A1–A6 Ablation Data Provenance Audit

## Audit status: PASS_WITH_CORRECTION

旧 Fig.4 使用的 `FINAL_ablation_outputs.csv` 本身可由其配套 prediction 文件重新计算，但它来自主实验目录中的一次独立训练 checkpoint，并不是论文冻结 B11/B12 比较实验所保存的 checkpoint。两者的分类标签恰好相同，概率值和 Smooth 略有差异。现已改为以正式 B11/B12 checkpoint 为唯一 backbone，按代码中的 A1–A6 输出定义重新推理和计算。

本轮没有运行、修改或重新导出 Fig.4 图像，也没有重新训练模型。

## 1. 审计目标与最终证据链

- Dataset：PHM2010。
- D1：Train = C1 + C4；Test = C6。
- 输入特征：正式恢复版 `run_level_features_all.csv`，945 行 × 345 列，C1/C4/C6 各 315 行。
- 序列长度：L = 12，因此 C6 可评价窗口为 run 12–315，共 304 个。
- 正式 backbone：`补充材料/小论文/4_comparison_experiment_recheck/3_models/B11_B12_multitask_tcn_gru.pth`。
- A1–A6：从该同一冻结 backbone 的 stage/fine/q 输出，经同一概率推理函数派生，不重新训练。
- A1 对应正式 B11 raw output；A6 对应正式 B12 final output。
- 指标评价器：`代码/main_experiment_3_fgds_psi_optimized.py:254-345`。

可追溯链：

```text
run_level_features_all.csv
  -> condition-relative stage definition
  -> C1+C4 train/internal-val, C6 test split
  -> train-only feature selection / scaling / GMM
  -> L=12 C6 windows (304)
  -> frozen formal B11/B12 checkpoint
  -> raw/fine/q outputs
  -> apply_probability_inference(A1–A6)
  -> manuscript_metric_row
  -> AUTHORITATIVE_A1_A6.csv
```

## 2. A1–A6 的真实代码定义

重要：A1–A6 只消融**输出概率推理模块**。共享 TCN-GRU backbone 始终同时训练 stage head、fine-state head 和 q head，且训练损失始终包含 stage、fine、q 和 monotonic 四项（`代码/main_experiment_3_fgds_psi_optimized.py:703-729, 752-756`）。因此不能把 A1 解释成“训练时关闭 fine/q 任务”。

| ID | 实际启用模块 | 实际关闭模块 | 对应函数/参数 |
|---|---|---|---|
| A1 | temperature-scaled raw stage head | fine-stage fusion、q prior、fine/prior mix、ordered filter、final blend | raw temperature scaling：`代码/main_experiment_3_fgds_psi_optimized.py:862-865`；A1 映射：`:1146-1156` |
| A2 | A1 raw + fine-state-to-stage probability，按 `eta` 混合 | q prior、combined fine/prior mix、ordered filter、final blend | fine mapping：`:835-840`；`raw_fine`：`:866-868`；A2 映射：`:1148` |
| A3 | A1 raw + q-hat degradation-position prior，按 `eta` 混合 | fine-state fusion、combined fine/prior mix、ordered filter、final blend | q prior：`:825-832`；`raw_prior`：`:865, 869-870`；A3 映射：`:1149` |
| A4 | raw + weighted fine/prior auxiliary mixture | ordered filter、final blend | `aux` 与 `mix`：`:871-873`；A4 映射：`:1150` |
| A5 | causal ordered filter applied to A4 mix | final convex blend | transition/filter：`:850-859`；对 A4 mix 过滤：`:874-877`；A5 映射：`:1151` |
| A6 | A4 mix 与 A5 ordered output 的最终凸组合 | 无 | `final=(1-beta)mix+beta*ordered`：`:878-882`；A6 映射：`:1152` |

正式比较脚本把同一网络的 raw output 定义为 B11、final output 定义为 B12，并使用同一组冻结参数（`代码/7.4对比实验.py:60-68, 396-408`）。

## 3. 所有候选结果与排除结论

| Candidate | Dataset | Task | Feature source | Test universe | Seed/protocol | Status |
|---|---|---|---|---|---|---|
| `4_comparison_experiment_recheck/3_models/B11_B12_multitask_tcn_gru.pth` + comparison predictions | PHM2010 | C1+C4→C6 | recovered original `run_level_features_all.csv` | 304, run 12–315 | seed 42, formal B11/B12 | **AUTHORITATIVE ANCHOR**；原文件仅保存 B11/A1 与 B12/A6，A2–A5 由同一 checkpoint 按代码派生 |
| `3_main_experiment_fgds_psi/FINAL_ablation_outputs.csv` + full predictions | PHM2010 | C1+C4→C6 | same formal feature path | 304 | seed 42, main-script run | 内部重算通过，但 checkpoint SHA-256 与正式 B11/B12 不同；旧 Fig.4 来源，**替换** |
| `6_ablation_experiment/Table10_ablation_summary.csv` + probabilities | PHM2010 | C1+C4→C6 | same formal feature path | 304 | seed 42, independent retrain | 内部重算通过，但 `7.6消融实验.py:577-581` 明确重新训练；不是冻结正式 B11/B12 checkpoint，**排除** |
| `代码/7.6.1消融实验绘图.py`、`代码/8.2图15.py`、`代码/8.2图16.py` 内嵌表 | 声称 PHM2010 | 声称 C1+C4→C6 | 未绑定 prediction/checkpoint | 不可验证 | hard-coded plotting values | 数值与现存正式 prediction 不一致，且不是实验输出，**排除** |
| `小论文/10_第五章顶刊风格可视化/data_exports/*ablation*` | PHM2010 downstream export | C1+C4→C6 | downstream copy | 304 | derived | 下游可视化导出，不是 primary result，**排除** |
| `experiments_mendeley/06_ablation/*` | Mendeley/Hannover cross-machine | D1-M/D2-M/D3-M | third-dataset features | task-specific | five seeds | 数据集与任务不符，**排除** |
| `final_five_seed_sweep/` | PHM2010 | D1 | formal feature file | 304 | five-seed diagnostic/sweep | 不是冻结单 seed 正式 A1–A6，且无完整 formal A1–A6 prediction，**排除** |
| `legacy_repro_audit/`、`protocol_diagnostic_fixed_preprocess/` | PHM2010 | D1 | formal feature file | 304 | diagnostic reruns | 诊断/复现实验，不是正式冻结 A1–A6，**排除** |
| `outputs/htt_net/B1_B12_recheck_on_reconstructed_features/` | PHM2010 | D1-like | reconstructed features | 304 | superseded recheck | reconstructed/superseded，**排除** |
| NASA result directories | NASA | N1–N4/candidate splits | NASA features | non-PHM | NASA protocol | 数据集不符；未发现可作为 PHM D1 A1–A6 的候选，**排除** |

## 4. Authoritative 条件逐项检查

| 条件 | 结论 | 证据 |
|---|---|---|
| PHM2010 | PASS | 正式 feature file 为 PHM C1/C4/C6，945×345 |
| D1 = C1+C4→C6 | PASS | split code：`main...py:465-490`；formal comparison：`7.4对比实验.py:278-311` |
| 与旧正式 B11/B12 路径一致 | PASS after correction | 直接锚定 formal `B11_B12_multitask_tcn_gru.pth`，不再使用 main/7.6 的独立 checkpoint |
| 正式 `run_level_features_all.csv` | PASS | `baselines/htt_net/data/run_level_features_all.csv`；SHA-256 `6e8aff...eeb88`；该文件由补充材料中的原始缓存表恢复并已复现正式 B11/B12 |
| L=12 | PASS | `main...py:125-132, 1122-1125`；C6 315−11=304 |
| 正式 stage/FS/GMM 路径 | PASS | stage `:432-462`；train-only FS `:566-609`；train GMM `:612-624`；正式 main 与 comparison cache 的四份 preprocessing 文件逐字节哈希一致 |
| A1–A6 同一 backbone | PASS | 全部由同一 formal checkpoint 一次 forward 的 raw/fine/q 输出派生 |
| C6 未用于调参 | PASS | C6 只作为 test pack；feature selection、scaler、GMM 在 C1+C4 train 上拟合；B12 参数在正式比较脚本中冻结。C6 的 VB 仅用于定义评价真值 stage，不参与模型或参数选择 |
| A6 与正式 B12 兼容 | PASS | 304 个 A6 标签与 formal B12 标签逐行完全一致；A6 Acc = 0.9868421053，formal B12 存储值 = 0.9868 |
| 非 diagnostic/superseded | PASS | authoritative anchor 是论文冻结 comparison run；diagnostic、five-seed、reconstructed 路径均排除 |

## 5. Prediction 级重新计算

重新计算指标：Acc、Macro-F1、E-F1、M-F1、L-F1、M-Precision、M-Recall、M→E、M→L、Rev、Jump、Smooth。定义完全复用 `main...py:254-345`：

- confusion-based metrics 使用固定标签 `[early, middle, late]`；
- Rev 为相邻预测阶段的负向跳转数；
- Jump 为绝对阶段差 ≥2 的跳转数；
- Smooth 为相邻概率向量 L1 差的均值。

内部一致性检查：

- main prediction → `FINAL_ablation_outputs.csv`：全部分类/transition 指标一致；最大数值差为 A1 Smooth 的 `2.35×10⁻⁹`，来自 CSV 浮点表示。
- 7.6 probability file → `Table10_ablation_summary.csv`：全部指标在浮点精度内一致。
- formal checkpoint → stored formal B11/B12：A1/B11 与 A6/B12 的 304 个标签逐行完全一致。正式 comparison prediction 仅保留 4 位小数；当前 PyTorch/CUDA 推理与该旧环境导出的概率逐点最大差分别为 `4.32×10⁻⁴` 和 `2.29×10⁻⁴`，但分类指标完全一致。A6 Smooth 与冻结 common-universe 值仅差 `1.78×10⁻⁶`。

逐指标旧源表与正式 checkpoint 复算的比较见 `ABLATION_RECOMPUTED.csv`。正式宽表见 `AUTHORITATIVE_A1_A6.csv`。

## 6. A1–A4 完全相同模式的追查

结论：**A1–A4 分类指标完全相同是原始实验的真实 argmax 结果，不是 CSV/merge/index bug。**

证据：

1. 在 formal checkpoint 派生的 304 行上，A1、A2、A3、A4 的预测标签逐行完全相同。
2. 每个方法从不同代码分支和不同 probability matrix 计算；未引用同一 prediction 列。
3. 概率矩阵并不相同。A1–A4 两两比较的最大绝对差范围为 `0.01727–0.21524`。
4. main prediction 和独立 7.6 prediction 各自重新计算后，也都复现 A1–A4 相同分类指标。
5. 差异确实反映在概率层：A2/A3/A4 的 Smooth 分别不同于 A1。因此不存在“六行共用同一 prediction file/同一列”的证据。

## 7. 发现的第一个旧 Fig.4 来源差异

- formal checkpoint SHA-256：`17299bbc...9ec69b`。
- old main-ablation checkpoint SHA-256：`20e5214e...f6b9b2`。
- 二者 state-dict keys 相同，但 tensor 不完全相同；最大绝对 tensor 差为 `0.00729787`。
- 第一个 probability 差异发生在 C6 run 12。A6 formal final probability 为 `[0.85681086, 0.12514354, 0.01804560]`，old main 为 `[0.85715660, 0.12470015, 0.01814326]`。

因此旧 Fig.4 不是“读错了第三数据集”，也不是 summary 计算错误；真正问题是**使用了与正式 B11/B12 不同的一次训练 checkpoint**。分类标签碰巧完全一致，掩盖了概率与 Smooth 的来源差异。

## 8. 最终判定

**PASS_WITH_CORRECTION**

已定位并纠正旧 Fig.4 的 checkpoint provenance。`AUTHORITATIVE_A1_A6.csv` 中六个配置均来自同一正式 B11/B12 backbone；A6 与正式 B12 的 304 个标签及 Acc 完全一致，可以作为后续 Fig.4 的唯一输入。后续绘图不得再直接读取旧 `FINAL_ablation_outputs.csv` 或 `Table10_ablation_summary.csv`。


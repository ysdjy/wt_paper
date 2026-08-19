# Dynamic GIN + TGP 和 DP2Net 训练教程（给你自己跑训练用）

写这份教程的时候，进度是：
- ✅ 两个baseline的代码、PAPER_SPEC.md、单元测试（CPU上全部通过：Dynamic GIN 13/13，DP2Net 15/15）、数据缓存 —— 全部已完成
- ✅ 两个baseline的 smoke test（冒烟测试，验证流程能跑通）—— 已完成，无报错
- ⬜ Dynamic GIN + TGP Protocol A（论文复现校验）—— 还没跑
- ⬜ Dynamic GIN + TGP Protocol B（统一对比，正文要用）—— 还没跑
- ⬜ DP2Net Protocol A（论文复现校验）—— 还没跑
- ⬜ DP2Net Protocol B-S / B-D1（统一对比，正文要用）—— 还没跑

**重要**：每一步命令跑完之后再跑下一条，不要同时跑两条（会抢显卡资源导致显存不够）。

---

## 第0步：打开终端 + 检查显卡

1. 按键盘上的 `Win` 键，输入 `PowerShell`，回车打开。
2. 复制粘贴下面这行，切换到项目目录，回车：

```powershell
cd "C:\Users\banghai\Documents\BaiduSyncdisk\西工大\王婷\论文"
```

3. 每次运行命令前，先检查显卡有没有被占用：

```powershell
nvidia-smi
```

看 `GPU-Util` 那一列，如果是 `0%` 或个位数，说明显卡空闲，可以继续。如果持续 `30%` 以上，说明有别的程序（比如另一个Claude实例）在用显卡，等它跑完再继续。

---

## 关于这两个模型你需要知道的两点

1. **Dynamic GIN + TGP 比较"重"**：论文里 Conv2d_4 那一层输出通道数高达288（Table 1原文如此），空间特征图很大，训练一个epoch可能比较慢，具体多慢取决于你的显卡，建议先跑 Protocol A 顺便看看每个epoch实际花多久，再心里有数。
2. **DP2Net 比较"轻"**：只有约6万参数，一维卷积为主，训练应该会明显快很多。

数据缓存我已经全部提前建好了（Dynamic GIN的945个run×10段窗口、DP2Net的Protocol A 18000个窗口 + Protocol B 7560个窗口），你不需要自己跑预处理脚本。

---

## 第1步：Dynamic GIN + TGP —— Protocol A（论文复现校验）

复制粘贴下面这一整行，回车：

```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dynamic_gin_tgp\train.py" --protocol A --device cuda
```

**这条命令的作用**：用论文自己的D1划分（C1+C4训练，C6测试，论文原始的固定阶段标签，前300刀），跑50个epoch（论文3.4节Scheme 1的超参数：Adam, lr=1e-4, L2=0.1, batch=4），然后在C6上评估，结果存到 `outputs\dynamic_gin_tgp\original_protocol\`。

**跑的时候你会看到**：
```
[Protocol A/D1] epoch 0: train_acc=0.xxxx val_acc=0.xxxx (best=0.xxxx) [xx.xs]
[Protocol A/D1] epoch 1: ...
```
一直跑到 `epoch 49`，最后打印：
```
[Protocol A/D1] sample-level Acc=0.xxxx (paper reports 0.9571, gap=...)
```
**看到这一行就说明跑完了。** 论文报的D1准确率是 **95.71%**，如果你跑出来的数字和这个差太远（比如低于85%），先别继续跑Protocol B，把结果告诉我，我来排查。

**如果中途断了**：重新跑同一条命令，加上 `--resume`：
```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dynamic_gin_tgp\train.py" --protocol A --device cuda --resume
```

**验证是否真的跑完**：
```powershell
type outputs\dynamic_gin_tgp\original_protocol\metrics.csv
```
能看到一大串逗号分隔的数字就说明完成了。也可以看有没有生成这个文件：
```powershell
type outputs\dynamic_gin_tgp\original_protocol\DONE.flag
```

**如果报"CUDA out of memory"（显存不够）**：这个架构比较吃显存，试试改小batch size：
```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dynamic_gin_tgp\train.py" --protocol A --device cuda --batch-size 2
```

---

## 第2步：Dynamic GIN + TGP —— Protocol B（统一对比，正文要用）

**必须等第1步完全跑完（看到 `sample-level Acc=...` 那一行）之后再开始。**

这一步默认用种子42，需要跑5个种子（42/52/62/72/82）才能进最终对比表。**建议先只跑一个种子看看效果和耗时**：

```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dynamic_gin_tgp\train.py" --protocol B --device cuda --seed 42
```

**这条命令的作用**：用本项目统一的Early/Middle/Late标签（C1+C4训练，C6测试，测试时按run聚合10段窗口的平均概率），最多50个epoch，15个epoch没提升就早停。结果存到 `outputs\dynamic_gin_tgp\unified_protocol\seed42\`。

**跑完会打印**：
```
[Protocol B] test C6 (run-level, seed=42): Acc=0.xxxx Macro-F1=0.xxxx
```

**确认跑完一个种子、觉得没问题之后**，再依次跑剩下4个种子（每条跑完再跑下一条）：
```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dynamic_gin_tgp\train.py" --protocol B --device cuda --seed 52
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dynamic_gin_tgp\train.py" --protocol B --device cuda --seed 62
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dynamic_gin_tgp\train.py" --protocol B --device cuda --seed 72
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dynamic_gin_tgp\train.py" --protocol B --device cuda --seed 82
```

**中途断了怎么办**：同样加 `--resume`（记得带上对应的 `--seed`）：
```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dynamic_gin_tgp\train.py" --protocol B --device cuda --seed 42 --resume
```

**验证**：
```powershell
type outputs\dynamic_gin_tgp\unified_protocol\seed42\metrics.csv
```

---

## 第3步：DP2Net —— Protocol A（论文复现校验）

这一步会比Dynamic GIN快很多（模型小很多）。

```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dp2net\train.py" --protocol A --device cuda
```

**这条命令的作用**：源域C1训练（70/30分train/val），分别在目标域C4和C6上测试。分两个阶段各跑100个epoch（Algorithm 1）：第一阶段先训练S+F（普通交叉熵），第二阶段冻结S、训练G+F（G用"物理约束MSE - 20倍MMD"这个损失，F用source+generated两部分交叉熵）。结果分别存到 `outputs\dp2net\original_protocol\target_C4\` 和 `target_C6\`。

**跑的时候你会看到**（先是Stage1，再是Stage2）：
```
[Stage1 pretrain S+F] epoch 0: loss=x.xxxx train_acc=0.xxxx val_acc=0.xxxx [x.xs]
...
[Stage2 train G+F] epoch 0: l_g=-x.xxxx l_task=x.xxxx val_acc=0.xxxx [x.xs]
...
```
最后打印：
```
[Protocol A] Target=C4: Acc=0.xxxx (paper reports 0.9091, gap=...)
[Protocol A] Target=C6: Acc=0.xxxx (paper reports 0.8766, gap=...)
```

**重要提醒**：这个baseline的Protocol A论文里是4分类（含"失效"阶段），但我在预处理时发现C1/C4/C6这三把刀的真实磨损数据从来没有达到过论文说的"失效"阈值（0.3mm），所以这里实际跑的是**调整后的3分类**任务（详见 `baselines\dp2net\PAPER_SPEC.md` 第6b节）。这意味着即使跑出来的准确率和论文数字接近甚至更高，也不能完全当作"完全复现"来看，因为3分类任务本身比4分类更容易。

**如果中途断了**：加 `--resume`：
```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dp2net\train.py" --protocol A --device cuda --resume
```

**验证**：
```powershell
type outputs\dp2net\original_protocol\target_C4\metrics.csv
type outputs\dp2net\original_protocol\target_C6\metrics.csv
```

---

## 第4步：DP2Net —— Protocol B-D1（统一对比，进最终正文对比表）

**必须等第3步跑完之后再开始。**

```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dp2net\train.py" --protocol B-D1 --device cuda --seed 42
```

**这条命令的作用**：C1+C4合并当作源域（论文本身只用单一源域，这里为了能跟DC-PSR主表的D1任务对齐做了调整，所以命名为"DP2Net-adapted (pooled source)"，不是原始DP2Net），C6作为目标域测试，用本项目统一的Early/Middle/Late标签，按run聚合8段窗口的平均概率。结果存到 `outputs\dp2net\unified_protocol_B-D1\seed42\`。

跑完打印：
```
[Protocol B-D1] test C6 (run-level, seed=42): Acc=0.xxxx Macro-F1=0.xxxx
```

**跑完一个种子确认没问题后，依次跑剩下4个种子**：
```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dp2net\train.py" --protocol B-D1 --device cuda --seed 52
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dp2net\train.py" --protocol B-D1 --device cuda --seed 62
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dp2net\train.py" --protocol B-D1 --device cuda --seed 72
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dp2net\train.py" --protocol B-D1 --device cuda --seed 82
```

**验证**：
```powershell
type outputs\dp2net\unified_protocol_B-D1\seed42\metrics.csv
```

---

## 第5步（可选，补充参考）：DP2Net —— Protocol B-S（单源对比）

这一步不是进最终主表的，是保留DP2Net"单源域泛化"这个方法本身特性的补充版本（C1单独作为源域，不合并C4），只需要跑1个种子做参考即可：

```powershell
& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\dp2net\train.py" --protocol B-S --device cuda --seed 42
```

---

## 全部跑完之后

五步（第1-4步必须，第5步可选）都跑完之后，**回来告诉我一声（比如说"都跑完了"）**，我会帮你：
1. 读取所有结果文件（metrics.csv / metrics.json / run_predictions.csv）
2. 补充参数量、推理耗时等复杂度测试（这个我自己在CPU上就能跑，不用你操心）
3. 把真实数字填进两份 `FINAL_REPORT.md`（替换掉现在的"TBD"占位符）
4. 给你一份完整的复现结论总结

---

## 万一遇到报错

如果某一步跑完后屏幕上出现红色的 `Traceback` 或 `Error` 字样（不是正常的 `[Protocol ...] epoch ...` 那种打印），**不要删除任何文件**，直接把报错内容整个复制给我，我来看是什么问题。

## 万一显存不够（报错里有 "CUDA out of memory"）

- Dynamic GIN + TGP：加 `--batch-size 2`（见第1步末尾说明）。
- DP2Net：模型很小，理论上不太会遇到这个问题；如果真遇到了，同样可以加 `--batch-size 32` 试试（默认64）。

## 两个baseline命令速查表

| 步骤 | 命令核心部分 |
|---|---|
| Dynamic GIN Protocol A | `train.py --protocol A --device cuda` |
| Dynamic GIN Protocol B | `train.py --protocol B --device cuda --seed <42/52/62/72/82>` |
| DP2Net Protocol A | `train.py --protocol A --device cuda` |
| DP2Net Protocol B-D1（主表用） | `train.py --protocol B-D1 --device cuda --seed <42/52/62/72/82>` |
| DP2Net Protocol B-S（补充参考） | `train.py --protocol B-S --device cuda --seed 42` |

所有命令都要在最前面加上 `& "C:\Users\banghai\miniconda3\envs\pub_baselines\python.exe" "baselines\<baseline名>\` 这部分，完整示例已经在上面每一步里给出，直接复制粘贴即可。

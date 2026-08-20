# Dynamic GIN + TGP 和 DP2Net 训练教程（全部完成）

**状态：所有实验已全部跑完，这份文件现在只作为最终结果存档，不需要再执行任何命令。**

最终进度：

- ✅ 两个baseline的代码、单元测试、数据缓存 —— 全部完成
- ✅ Dynamic GIN + TGP的batch泄露bug —— 已定位、已修复、已用真实训练验证
- ✅ Dynamic GIN + TGP Protocol A —— Acc=95.12%（论文95.71%，差距-0.59pp）
- ✅ Dynamic GIN + TGP Protocol B（5个种子全部完成）—— 均值Acc=88.44%±6.83%
- ✅ DP2Net Protocol A（C1→C4/C6）—— C4: Acc=82.67%，C6: Acc=81.15%
- ✅ DP2Net Protocol B-D1（5个种子全部完成）—— 均值Acc=90.73%±3.81%
- ✅ DP2Net Protocol B-S（补充参考，种子42）—— Acc=95.87%

**这两个baseline（Dynamic GIN + TGP、DP2Net）的复现工作已经完成**，可以交给总管理者纳入DC-PSR最终的5篇Published Baseline对比体系了。

---

## 最终结果总览

### Dynamic GIN + TGP

| 协议 | 指标 | 结果 |
|---|---|---|
| Protocol A（论文校验，D1） | Acc | **95.12%**（论文95.71%，差距-0.59pp） |
| Protocol B（统一对比，5种子均值） | Acc | **88.44% ± 6.83%**（范围80.95%~96.51%） |
| Protocol B（统一对比，5种子均值） | Macro-F1 | **88.69% ± 6.77%** |

参数量：321,950（论文报告321,002，差异+0.29%）

### DP2Net

| 协议 | 指标 | 结果 |
|---|---|---|
| Protocol A（论文校验，C1→C4） | Acc | **82.67%**（论文90.91%，差距-8.24pp，注：实际是调整后的3分类任务） |
| Protocol A（论文校验，C1→C6） | Acc | **81.15%**（论文87.66%，差距-6.51pp，同上） |
| Protocol B-D1（统一对比主表，5种子均值） | Acc | **90.73% ± 3.81%**（范围86.03%~94.92%） |
| Protocol B-D1（统一对比主表，5种子均值） | Macro-F1 | **90.98% ± 3.65%** |
| Protocol B-S（补充参考，单种子） | Acc | **95.87%** |

参数量：60,956（S+G+F合计，推理时只用S+F，60,031）

### 跟本项目其他baseline的横向参考（同一切分/标签，单次运行）

| Baseline | Protocol B Acc |
|---|---|
| mtf_avitk | 90.16% |
| Dynamic GIN + TGP（5种子均值） | 88.44% |
| DP2Net-adapted (pooled source)（5种子均值，即B-D1） | **90.73%** |
| multi_source_attention | 81.90% |

DP2Net-adapted在这几个baseline里表现最好，而且5种子标准差（3.81pp）也是最小的，稳定性最好。

---

## 关键发现存档（供以后查阅）

1. **真实bug**：Dynamic GIN + TGP的static graph模块（论文Eq.7-9）把同一batch内所有样本拼接起来算余弦相似度，导致预测结果依赖"batch内其他样本"。最初验证/测试用的DataLoader按run连续排列且未打乱，导致每个batch全是同一run、同一真实标签，模型能"偷看"标签，验证集准确率被人为拉高到100%。已通过在`baselines/dynamic_gin_tgp/train.py`的Dataset构造时固定种子打乱行顺序修复。

2. **真实bug（更早期）**：Dynamic GIN + TGP的GASF编码器中`sqrt(1-x²)`在每个特征的最大/最小值点处恰好等于0，导致该处梯度为无穷大，第一次反向传播就产生NaN。已通过添加epsilon下限修复（CPU单元测试阶段就发现并修复，未影响任何正式训练结果）。

3. **重要实证发现**：DP2Net论文中"平均VB>0.3mm"的失效阈值（Stage IV），在本项目C1/C4/C6真实数据中从未被触发过（原始数据单位是微米，最大值仅216微米）。因此DP2Net的Protocol A实际跑的是调整后的三分类任务，而非论文声称的四分类，这也是Protocol A准确率跟论文有6-8个百分点差距的主要原因之一。

4. **Dynamic GIN + TGP的跨种子方差明显大于DP2Net**（Protocol B标准差6.83pp vs 3.81pp），这一点值得在最终论文正文的对比表里注明——单一种子的数字对Dynamic GIN来说波动较大，报告时应带上均值±标准差，而不是单个数字。

---

## 文件位置

- `baselines/dynamic_gin_tgp/PAPER_SPEC.md` / `README.md` / `FINAL_REPORT.md`
- `baselines/dp2net/PAPER_SPEC.md` / `README.md` / `FINAL_REPORT.md`
- `outputs/dynamic_gin_tgp/` — 所有训练日志、checkpoint、逐run预测结果
- `outputs/dp2net/` — 同上

如果之后需要重新验证某个种子的结果，两个baseline的`train.py`都支持`--resume`断点续训，命令格式可以参考各自的README.md（虽然目前已经不需要再跑了）。

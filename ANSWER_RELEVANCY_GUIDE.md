# 答案相关性评估器 - 添加指南

## ✅ 好消息！

**答案相关性（Answer Relevancy）评估器已经内置在系统中！**

您无需额外配置，可以直接使用。

---

## 📋 什么是答案相关性评估？

### 定义

答案相关性衡量**生成的答案与用户问题或查询的关联紧密程度**。

### 评估目标

- ✅ 回答直接解释问题核心
- ✅ 避免答非所问
- ✅ 避免包含大量无关信息
- ✅ 答案简洁、准确、相关

### DeepEval 的评估方法

DeepEval 使用以下方法评估答案相关性：

1. **生成反向问题** - 基于实际答案，生成一些问题
2. **相似度对比** - 比较生成的问题与原问题的相似度
3. **计算得分** - 相似度越高，说明答案越相关

**得分范围**: 0.0 - 1.0
- **1.0** = 完全相关（答案完美回应了问题）
- **0.5** = 部分相关（答案有关但不完全准确）
- **0.0** = 完全无关（答非所问）

---

## 🚀 如何添加

### 方法1：通过界面添加

1. **打开主界面**
   ```bash
   cd evaluator_gui
   python main.py
   ```

2. **点击"添加评估器"按钮**

3. **填写信息**：
   - **评估器名称**: `答案相关性评估器`（或您喜欢的任何名称）
   - **评估框架**: 选择 `DeepEval`
   - **评估器类型**: 选择 `Answer Relevancy`
   - **阈值**: 输入 `0.5` 或 `0.6`（建议值）

4. **点击"添加"按钮**

### 方法2：直接使用

如果系统中已经有"答案相关性"评估器，可以直接：

1. 点击"评估器列表"
2. 选择"答案相关性评估器"
3. 点击"使用选中"
4. 执行评估

---

## 📊 评估数据要求

### 必需数据

Answer Relevancy 评估需要：

```python
{
    "input": "用户的问题",           # 必需
    "actual_output": "生成的答案"     # 必需
}
```

### 可选数据

```python
{
    "input": "用户的问题",
    "actual_output": "生成的答案",
    "retrieval_context": [...]       # 可选，检索上下文
}
```

### 示例数据

**高相关性示例** (得分接近1.0):
```json
{
    "input": "车险理赔需要准备哪些材料？",
    "actual_output": "车险理赔通常需要准备以下材料：1. 事故责任认定书；2. 维修发票；3. 驾驶证和行驶证；4. 保险单；5. 银行账户信息。具体材料可能根据事故情况有所不同。"
}
```

**低相关性示例** (得分较低):
```json
{
    "input": "车险理赔需要准备哪些材料？",
    "actual_output": "重疾险是一种保障重大疾病的保险产品，包括癌症、心肌梗死等重大疾病。投保时需要如实告知健康状况。"
}
```

---

## 🧪 测试示例

### 示例1：高相关性（应该通过）

**问题**:
```
重疾险的等待期是多久？
```

**答案**:
```
重疾险的等待期通常是90天或180天，具体取决于保险产品。在等待期内确诊的疾病，保险公司不承担赔偿责任。等待期是为了防止逆选择风险。
```

**预期结果**: ✅ 通过 (得分 > 0.6)
- 答案直接回答了问题
- 提供了具体的时间范围
- 解释了等待期的概念和作用

### 示例2：低相关性（可能失败）

**问题**:
```
重疾险的等待期是多久？
```

**答案**:
```
重疾险可以保障多种重大疾病，如恶性肿瘤、急性心肌梗死、脑中风后遗症等。投保时需要如实告知健康状况，否则可能影响理赔。
```

**预期结果**: ❌ 失败 (得分 < 0.6)
- 答案没有回答"等待期是多久"
- 提供了与问题无关的信息
- 答非所问

---

## 📈 评估结果解读

### 通过（得分 >= 阈值）

**原因示例**:
```
The output directly addresses the user's question about the waiting period
for critical illness insurance. It provides specific information (90 or 180 days)
and explains the concept clearly.
```

**中文翻译**:
```
该输出直接回答了用户关于重疾险等待期的问题。提供了具体信息（90天或180天）
并清晰地解释了相关概念。
```

### 失败（得分 < 阈值）

**原因示例**:
```
The output does not address the user's question about the waiting period.
Instead, it discusses covered diseases and underwriting requirements,
which are not relevant to the question asked.
```

**中文翻译**:
```
该输出没有回答用户关于等待期的问题。相反，它讨论了保障疾病和投保要求，
这与所问的问题无关。
```

---

## 🎯 最佳实践

### 1. 问题设计

**✅ 好的问题**（清晰、具体）:
- "重疾险的等待期是多久？"
- "车险理赔需要准备哪些材料？"
- "意外险的保障范围包括哪些？"

**❌ 差的问题**（模糊、不完整）:
- "重疾险怎么样？"
- "理赔怎么办？"
- "保险有什么用？"

### 2. 答案质量

**✅ 好的答案**（高相关性）:
- 直接回答问题
- 不包含无关信息
- 长度适中（不要太长也不要太短）
- 准确、专业

**❌ 差的答案**（低相关性）:
- 答非所问
- 包含大量无关信息
- 过于简短或过于冗长
- 不准确或含糊

### 3. 阈值设置

- **严格评估**: 0.7 - 0.8（要求高度相关）
- **标准评估**: 0.5 - 0.6（推荐）
- **宽松评估**: 0.3 - 0.4（允许一定偏差）

---

## 🔧 技术细节

### 已实现的代码

**文件**: `evaluators/deepeval_executor.py`

**导入** (line 11):
```python
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,  # ← 已导入
    BiasMetric,
    ToxicityMetric,
    GEval
)
```

**创建指标** (lines 132-139):
```python
# Answer Relevancy (答案相关性)
elif metric_type == "Answer Relevancy" or metric_type == "答案相关性":
    return AnswerRelevancyMetric(
        threshold=self.threshold,
        model=model,
        verbose_mode=True,
        include_reason=True
    )
```

**UI支持** (line 162):
```python
# DeepEval 支持的评估器类型
self.metric_combo['values'] = [
    "Faithfulness",
    "Answer Relevancy",  # ← 已在列表中
    "Contextual Precision",
    "Contextual Recall",
    "Contextual Relevancy",
    "Bias",
    "Toxicity",
    "GEval (Custom)"
]
```

---

## 💡 使用建议

### 适用场景

答案相关性评估特别适合：

1. ✅ **问答系统** - 检查AI回答是否准确回应问题
2. ✅ **客服机器人** - 确保回答直接解决客户问题
3. ✅ **知识库检索** - 评估检索到的答案是否相关
4. ✅ **对话系统** - 检查对话回复是否切题

### 不适用场景

1. ❌ **开放式生成任务**（如写文章、写代码）
2. ❌ **创意性内容生成**
3. ❌ **需要发散思维的任务**

---

## 📝 总结

### ✅ 已完成

1. ✅ DeepEval框架已集成
2. ✅ AnswerRelevancyMetric已导入
3. ✅ 执行器支持"Answer Relevancy"和"答案相关性"
4. ✅ UI下拉列表已包含"Answer Relevancy"
5. ✅ 启用了详细模式（verbose_mode=True）
6. ✅ 启用了原因说明（include_reason=True）

### 🎯 下一步

1. **打开主界面**: `python main.py`
2. **添加评估器**（如果还没有）:
   - 名称: "答案相关性评估器"
   - 框架: DeepEval
   - 类型: Answer Relevancy
   - 阈值: 0.6
3. **准备测试数据**:
   - 问题（input）
   - 答案（actual_output）
4. **执行评估**
5. **查看结果**:
   - 得分（0-1）
   - 通过/失败状态
   - 详细原因（中英对照）

---

**文档时间**: 2025-01-22
**评估器**: Answer Relevancy (答案相关性)
**框架**: DeepEval
**状态**: ✅ 已内置，可直接使用

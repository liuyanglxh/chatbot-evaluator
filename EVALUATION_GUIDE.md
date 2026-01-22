# 评估执行功能说明

## ✅ 已实现的功能

### 1. **评估器列表 - "使用"按钮**
在评估器列表窗口新增了"✓ 使用选中"按钮，点击后会：
- 检查是否选中了评估器
- 获取选中评估器的完整信息（名称、框架、类型、阈值）
- 打开评估执行窗口

### 2. **评估执行窗口**
新的窗口包含：

#### 输入区域
- **问题**（必填）：用户提问
- **回答**（必填）：Chatbot 的回答
- **上下文**（可选）：检索到的上下文或参考信息

#### 功能按钮
- **▶ 执行评估**：运行真实评估（调用 DeepEval 框架）
- **🗑 清空**：清空所有输入和结果
- **关闭**：关闭窗口

#### 结果显示
- 实时显示评估进度（⏳ 正在执行评估...）
- 显示评估结果（分数、是否通过、评估原因）
- 支持中英文结果展示
- 如果是英文，会显示【英文原文】和【中文翻译】（自动调用大模型翻译）

## 🎯 使用流程

```
1. 打开评估器列表
   ↓
2. 选中一个评估器
   ↓
3. 点击"✓ 使用选中"按钮
   ↓
4. 在新窗口中输入：
   - 问题（必填）
   - 回答（必填）
   - 上下文（可选）
   ↓
5. 点击"▶ 执行评估"
   ↓
6. 查看评估结果
```

## 📊 结果展示格式

### 中文结果示例
```
评估器：忠实度评估器
框架：DeepEval
类型：Faithfulness

✅ 通过
得分：0.850 / 0.6

评估原因：
该回答在事实方面与上下文一致，准确地回答了用户的问题...
```

### 英文结果示例
```
【英文原文】
Evaluator: Faithfulness Evaluator
Framework: DeepEval
Type: Faithfulness

✅ PASS
Score: 0.850 / 0.6

Reason:
The output is factually consistent with the retrieval context...

============================================================

【中文翻译】
评估器：忠实度评估器
框架：DeepEval
类型：Faithfulness

✅ 通过
得分：0.850 / 0.6

评估原因：
输出与检索上下文在事实上一致...
```

## 🔧 当前实现状态

### ✅ 已完成
1. **UI 界面**：完整的输入、执行、结果展示界面
2. **按钮功能**：使用、清空、关闭
3. **后台线程**：避免阻塞 UI，用户体验好
4. **输入验证**：检查必填项
5. **真实评估**：集成 DeepEval 框架进行真实评估
6. **多指标支持**：支持 Faithfulness、Answer Relevancy、Bias、Toxicity、Contextual 系列指标、GEval 自定义指标
7. **中英文处理**：自动检测英文结果并调用大模型翻译
8. **结果格式化**：显示分数、通过状态和详细的评估原因

### 🔄 架构设计

#### 评估执行器模块 (`evaluators/`)
- **BaseExecutor**: 抽象基类（待扩展）
- **DeepEvalExecutor**: DeepEval 框架的具体实现
  - `execute()`: 执行评估的主方法
  - `_create_test_case()`: 根据指标类型创建测试用例
  - `_create_metric()`: 创建评估指标
  - `_parse_result()`: 解析评估结果
  - `_is_english_text()`: 检测文本是否为英文

#### 工厂模式
```python
# 在 evaluators/__init__.py 中
def get_executor(evaluator_info):
    """根据评估器配置返回对应的执行器"""
    framework = evaluator_info.get('framework', '').lower()

    if framework == 'deepeval':
        return DeepEvalExecutor(evaluator_info)
    elif framework == 'ragas':
        # TODO: 实现 Ragas 执行器
        raise NotImplementedError("Ragas 框架支持待实现")
```

## 💡 支持的评估指标

### DeepEval 内置指标
1. **Faithfulness**（忠实度）：评估回答是否与上下文事实一致
2. **Answer Relevancy**（答案相关性）：评估回答是否与问题相关
3. **Bias**（偏见）：评估回答是否存在偏见
4. **Toxicity**（毒性）：评估回答是否存在有害内容
5. **Contextual Precision**（上下文精确度）：评估检索上下文的精确度
6. **Contextual Recall**（上下文召回率）：评估检索上下文的召回率
7. **Contextual Relevancy**（上下文相关性）：评估上下文与问题的相关性

### GEval 自定义指标
1. **Role Adherence**（角色遵循）：评估回答是否符合专业保险客服角色
2. **Correctness**（正确性）：评估回答在事实、逻辑和数据上的准确性

## 🎨 界面特点

- **响应式设计**：窗口大小合适（900x750）
- **居中显示**：自动适配屏幕位置
- **模态窗口**：专注当前评估任务
- **多行文本框**：支持长文本输入
- **滚动结果显示**：便于查看长结果
- **状态提示**：实时显示执行状态和翻译进度
- **异步处理**：评估和翻译都在后台线程执行，不阻塞 UI

## 📝 使用示例

### 示例 1：测试忠实度（Faithfulness）
```
问题：车险理赔需要准备哪些材料？
回答：需要准备事故责任认定书、维修发票、驾驶证和行驶证。
上下文：车险理赔材料包括：1.事故责任认定书 2.维修发票 3.驾驶证 4.行驶证

[点击执行]
→ 显示：✅ 通过 | 得分：0.900 / 0.6
→ 评估原因：该回答在事实方面与上下文完全一致...
```

### 示例 2：测试答案相关性（Answer Relevancy）
```
问题：重疾险的等待期是多久？
回答：重疾险等待期通常是90天或180天，具体看产品条款
上下文：（空）

[点击执行]
→ 显示：✅ 通过 | 得分：0.850 / 0.6
→ 评估原因：回答直接针对用户的问题，提供了准确的信息...
```

### 示例 3：测试角色遵循（Role Adherence）
```
问题：我不买你的保险行不行？
回答：您好，购买保险是个人选择，我们尊重您的决定。不过我可以为您详细介绍不同产品的优势，帮助您做出最适合的选择...

[点击执行]
→ 显示：✅ 通过 | 得分：0.920 / 0.6
→ 评估原因：回答体现了专业、礼貌的态度，没有表现出冷漠或不尊重...
```

## ⚠️ 注意事项

1. **需要安装 DeepEval**：运行前请确保已安装 `deepeval` 包
   ```bash
   pip install deepeval
   ```

2. **需要配置大模型**：确保"大模型设置"已正确配置
   - 模型类型（如：qwen-max、gpt-4等）
   - Base URL（如：https://dashscope.aliyuncs.com/compatible-mode/v1）
   - API Key

3. **上下文要求**：
   - Faithfulness、Contextual 系列指标：**必须提供上下文**
   - Answer Relevancy、Bias、Toxicity：可以不提供上下文

4. **评估时间**：真实评估需要调用大模型，可能需要几秒到十几秒

5. **英文结果翻译**：如果评估结果是英文，系统会自动调用大模型进行翻译

## 🚀 技术实现

### 1. 评估执行流程
```python
# evaluation_execution_window.py
def _execute_evaluation_thread(self, question, answer, context):
    # 1. 获取大模型配置
    model_settings = self.config_manager.get_model_settings()

    # 2. 获取评估执行器（工厂模式）
    executor = get_executor(self.evaluator_info)

    # 3. 执行真实评估
    result = executor.execute(question, answer, context, model_settings)

    # 4. 更新 UI
    self.window.after(0, self._update_result, result)
```

### 2. DeepEval 执行器实现
```python
# evaluators/deepeval_executor.py
def execute(self, question, answer, context, model_settings):
    # 1. 配置 API
    os.environ["OPENAI_API_KEY"] = model_settings['api_key']
    os.environ["OPENAI_BASE_URL"] = model_settings['base_url']

    # 2. 创建模型实例
    qwen_model = GPTModel(
        model=model_settings['model_type'],
        base_url=model_settings['base_url']
    )

    # 3. 创建测试用例
    test_case = self._create_test_case(question, answer, context)

    # 4. 创建评估指标
    metric = self._create_metric(qwen_model)

    # 5. 运行评估
    result = evaluate(test_cases=[test_case], metrics=[metric])

    # 6. 解析结果
    return self._parse_result(result)
```

### 3. 英文检测与翻译
```python
# 英文检测（基于中文字符比例）
def _is_english_text(self, text):
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    chinese_ratio = chinese_chars / len(text)
    return chinese_ratio < 0.2

# 翻译实现（调用大模型）
def _translate_result(self, english_text):
    translate_prompt = f"""请将以下评估结果翻译成中文，保持原有的格式和结构：

{english_text}

要求：
1. 保留所有数字、分数、符号（如 ✅、❌）
2. 专业术语要准确翻译
3. 保持换行和段落结构
"""
    success, response = model._send_request(translate_prompt)
    return response.get('content', english_text)
```

## 🎯 下一步扩展建议

### 1. 添加 Ragas 框架支持
```python
# evaluators/ragas_executor.py
class RagasExecutor(BaseExecutor):
    def execute(self, question, answer, context, model_settings):
        # 类似 DeepEval 的实现方式
        pass
```

### 2. 保存评估历史
- 将评估结果保存到数据库或文件
- 提供历史记录查看界面
- 支持导出评估报告

### 3. 批量评估
- 支持从 CSV/Excel 导入测试用例
- 批量执行多个评估器
- 生成统计报告和图表

### 4. 评估结果对比
- 同一测试用例使用不同评估器对比
- 结果可视化展示
- 评估器性能分析

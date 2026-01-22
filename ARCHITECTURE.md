# 代码架构说明

## 📁 项目结构（规范、可扩展）

```
evaluator_gui/
├── main.py                           # 主程序入口
├── config_manager.py                 # 配置管理模块（跨平台）
├── requirements.txt                  # 依赖包列表
├── models/                           # 模型管理模块（新增）
│   ├── __init__.py                  # 模型工厂
│   ├── base_model.py                # 抽象基类
│   ├── qwen_model.py               # 通义千问实现
│   ├── deepseek_model.py           # DeepSeek 实现
│   └── openai_model.py             # OpenAI/GPT 实现
└── windows/                          # GUI 窗口模块
    ├── __init__.py
    ├── model_settings_window.py     # 大模型设置窗口
    ├── add_evaluator_window.py      # 添加评估器窗口
    └── evaluator_list_window.py     # 评估器列表窗口
```

## 🏗️ 设计原则

### 1. **分层架构**
```
GUI 层 (windows/)
    ↓
业务逻辑层 (config_manager.py)
    ↓
数据模型层 (models/)
```

### 2. **面向对象设计**

#### 基类抽象（`models/base_model.py`）
```python
BaseModel (ABC)
    ├── get_api_endpoint()      # 抽象方法
    ├── get_headers()           # 抽象方法
    ├── format_payload()        # 抽象方法
    ├── extract_response()      # 抽象方法
    ├── test_connection()       # 通用方法
    └── generate()             # 便捷方法
```

#### 具体实现（继承基类）
```python
QwenModel(BaseModel)
DeepSeekModel(BaseModel)
OpenAIModel(BaseModel)
```

### 3. **工厂模式**
```python
# models/__init__.py
def get_model(model_type, base_url, api_key):
    """根据类型返回对应模型实例"""
    if 'qwen' in model_type:
        return QwenModel(...)
    elif 'deepseek' in model_type:
        return DeepSeekModel(...)
    elif 'gpt' in model_type:
        return OpenAIModel(...)
    else:
        return QwenModel(...)  # 默认
```

## 🔌 可扩展性

### 添加新的模型支持

**步骤 1：创建模型类**
```python
# models/new_model.py
from .base_model import BaseModel

class NewModel(BaseModel):
    def get_api_endpoint(self):
        return f"{self.base_url}/v1/chat"

    def get_headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def format_payload(self, prompt):
        return {"model": self.model_type, "prompt": prompt}

    def extract_response(self, response_data):
        return response_data['text']
```

**步骤 2：注册到工厂**
```python
# models/__init__.py
from .new_model import NewModel

def get_model(model_type, base_url, api_key):
    if 'new' in model_type:
        return NewModel(...)
    # ...
```

**完成！** 无需修改其他代码，GUI 自动支持新模型。

### 添加新的评估指标

**步骤 1：在 `add_evaluator_window.py` 中添加选项**
```python
elif framework == "deepeval":
    self.metric_combo['values'] = [
        "Faithfulness",
        "Answer Relevancy",
        "New Metric"  # ← 添加这里
    ]
```

**步骤 2：创建评估器实现**
```python
# evaluators/new_metric_evaluator.py
class NewMetricEvaluator:
    def evaluate(self, test_case):
        # 实现评估逻辑
        pass
```

**步骤 3：集成到评估流程**
```python
# evaluation_engine.py
if evaluator_config['metric_type'] == 'New Metric':
    evaluator = NewMetricEvaluator(...)
```

## 🔒 关键设计模式

### 1. **工厂模式**
- 位置：`models/__init__.py`
- 作用：根据类型自动创建对应的模型实例
- 优点：添加新模型无需修改调用代码

### 2. **模板方法模式**
- 位置：`models/base_model.py`
- 作用：定义算法骨架，子类实现具体步骤
- 优点：统一接口，代码复用

### 3. **单例模式**
- 位置：`config_manager.py`
- 作用：全局唯一的配置管理器
- 优点：避免配置冲突

## 🎯 测试连接功能实现

### 工作流程
```
1. 用户点击"测试连接"
   ↓
2. 验证输入（模型类型、Base URL、API Key）
   ↓
3. 在后台线程中执行（避免阻塞 UI）
   ↓
4. 使用工厂方法创建模型实例
   model = get_model(model_type, base_url, api_key)
   ↓
5. 调用模型的 test_connection() 方法
   ↓
6. 发送测试请求（"你好"）
   ↓
7. 更新 UI（显示成功或失败）
```

### 关键代码
```python
# 后台线程测试
def _test_connection_thread(self, model_type, base_url, api_key):
    model = get_model(model_type, base_url, api_key)
    success, message = model.test_connection()
    self.window.after(0, self._update_test_result, success, message)
```

## 📊 数据流

```
用户操作
    ↓
GUI (windows/)
    ↓
Config Manager (配置读写)
    ↓
Model Factory (模型创建)
    ↓
BaseModel (统一接口)
    ↓
具体模型 (Qwen/DeepSeek/OpenAI)
    ↓
API 请求/响应
```

## 🧪 测试要点

### 单元测试
```python
# tests/test_models.py
def test_qwen_model():
    model = QwenModel("qwen-max", base_url, api_key)
    assert model.get_api_endpoint() == "https://..."

def test_factory():
    model = get_model("qwen-max", base_url, api_key)
    assert isinstance(model, QwenModel)
```

### 集成测试
```python
# tests/test_connection.py
def test_model_connection():
    model = get_model(...)
    success, message = model.test_connection()
    assert success == True
```

## 🚀 未来扩展方向

### 1. 评估引擎
```python
# evaluation_engine.py
class EvaluationEngine:
    def run_evaluation(self, test_cases, evaluators):
        results = []
        for test_case in test_cases:
            for evaluator in evaluators:
                result = evaluator.evaluate(test_case)
                results.append(result)
        return results
```

### 2. 报告生成器
```python
# report_generator.py
class ReportGenerator:
    def generate_excel(self, results):
        # 生成 Excel 报告
        pass

    def generate_html(self, results):
        # 生成 HTML 报告
        pass
```

### 3. 批量测试
```python
# batch_tester.py
class BatchTester:
    def load_from_excel(self, file_path):
        # 从 Excel 加载测试用例
        pass

    def run_batch(self, test_cases):
        # 批量运行测试
        pass
```

## 📝 代码规范

### 命名规范
- **类名**: `PascalCase` (如 `BaseModel`, `ConfigManager`)
- **函数名**: `snake_case` (如 `test_connection`, `save_settings`)
- **常量**: `UPPER_SNAKE_CASE` (如 `DEFAULT_TIMEOUT`)
- **私有方法**: `_leading_underscore` (如 `_send_request`)

### 文档字符串
```python
def test_connection(self) -> tuple[bool, str]:
    """
    测试模型连接

    Returns:
        (是否成功, 消息)
    """
```

### 类型提示
```python
from typing import Dict, Any, Optional

def format_payload(self, prompt: str) -> Dict[str, Any]:
    """格式化请求载荷"""
```

## ✅ 优点总结

1. **高度模块化**：每个模块职责单一
2. **易于扩展**：添加新模型/指标无需修改核心代码
3. **可测试性强**：每个组件可独立测试
4. **代码复用**：基类提供通用功能
5. **统一接口**：工厂模式提供一致的访问方式
6. **线程安全**：后台线程避免 UI 阻塞

这个架构为后续功能扩展（实际评估、报告生成、批量测试等）打下了坚实基础！

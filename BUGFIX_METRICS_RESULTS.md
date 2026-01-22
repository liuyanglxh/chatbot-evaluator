# Bug 修复记录

## 问题描述

在使用"正确性"评估器（或其他 GEval 自定义评估器）时，评估结果显示：

```
❌ 结果解析失败: 'TestResult' object has no attribute 'metrics_results'
```

## 问题原因

DeepEval 框架在版本更新后，其 API 数据结构发生了变化：

- **旧版本**：`test_result.metrics_results` (列表)
- **新版本**：`test_result.metrics_data` (列表)

代码中使用了旧版本的属性名 `metrics_results`，导致属性访问失败。

## 修复内容

### 1. 修改属性名称

**文件**: `evaluators/deepeval_executor.py`

**修改位置**: `_parse_result()` 方法，第 252 行

**修改前**:
```python
test_result = result.test_results[0]
metric_result = test_result.metrics_results[0]  # ❌ 错误的属性名
```

**修改后**:
```python
test_result = result.test_results[0]
metrics_data = test_result.metrics_data  # ✅ 正确的属性名

if not metrics_data or len(metrics_data) == 0:
    return {
        'success': False,
        'error': 'No metrics data returned',
        'message': '评估失败: 未返回指标数据'
    }

metric_data = metrics_data[0]
```

### 2. 更新数据访问方式

**修改前**:
```python
metric_result = test_result.metrics_results[0]
score = metric_result.score
passed = metric_result.success
reason = getattr(metric_result, 'reason', '')
```

**修改后**:
```python
metric_data = metrics_data[0]

# 检查是否有错误
if hasattr(metric_data, 'error') and metric_data.error:
    return {
        'success': False,
        'error': metric_data.error,
        'message': f"评估失败: {metric_data.error}"
    }

# 提取分数
score = metric_data.score if metric_data.score is not None else 0.0
passed = metric_data.success

# 获取原因（如果有）
reason = metric_data.reason if metric_data.reason else ""
```

### 3. 增强错误处理

添加了详细的调试信息，帮助快速定位问题：

```python
except Exception as e:
    # 添加详细的调试信息
    import traceback
    error_details = f"{str(e)}\n\n"
    error_details += f"Result type: {type(result)}\n"
    error_details += f"Result attributes: {([a for a in dir(result) if not a.startswith('_')])}\n"

    if hasattr(result, 'test_results'):
        error_details += f"\ntest_results length: {len(result.test_results)}\n"
        if len(result.test_results) > 0:
            test_result = result.test_results[0]
            error_details += f"test_result type: {type(test_result)}\n"
            error_details += f"test_result attributes: {([a for a in dir(test_result) if not a.startswith('_')])}\n"

    error_details += f"\n{traceback.format_exc()}"

    return {
        'success': False,
        'error': str(e),
        'message': f"结果解析失败: {str(e)}",
        'debug_info': error_details
    }
```

## DeepEval 数据结构说明

### EvaluationResult
`evaluate()` 函数的返回值，包含以下字段：
- `test_results`: List[TestResult]
- `confident_link`: Optional[str]
- `test_run_id`: Optional[str]

### TestResult
单个测试用例的结果，包含以下字段：
- `name`: str
- `success`: bool
- `metrics_data`: Union[List[MetricData], None]  ⬅️ **关键字段**
- `conversational`: bool
- `input`: str
- `actual_output`: str
- `expected_output`: Optional[str]
- `context`: Optional[List[str]]
- `retrieval_context`: Optional[List[str]]
- `turns`: Optional[List[TurnApi]]
- `additional_metadata`: Optional[Dict]

### MetricData
单个指标的数据，包含以下字段：
- `name`: str
- `threshold`: float
- `success`: bool
- `score`: Optional[float]
- `reason`: Optional[str]
- `strict_mode`: Optional[bool]
- `evaluation_model`: Optional[str]
- `error`: Optional[str]
- `evaluation_cost`: Optional[float]
- `verbose_logs`: Optional[str]

## 测试建议

修复后，建议测试以下场景：

1. **测试 GEval 自定义指标**（如"正确性"、"角色遵循"）
2. **测试内置指标**（如 Faithfulness、Answer Relevancy）
3. **测试失败场景**（如 API key 错误、网络超时）

## 版本兼容性

- DeepEval 版本: 3.8.1
- Python 版本: 3.11+

## 注意事项

如果 DeepEval 未来再次更新 API，此错误处理机制会提供详细的调试信息，帮助快速定位新的属性名称或结构变化。

---

**修复时间**: 2025-01-22
**修复人员**: Claude Code
**影响范围**: 所有使用 DeepEval 框架的评估器

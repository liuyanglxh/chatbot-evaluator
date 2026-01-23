"""
调试GEval的criteria是否正确传递
"""
import json
import os
from pathlib import Path

# 加载配置
config_path = Path.home() / "Library" / "Application Support" / "llm_evaluator" / "config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

# 获取评估器配置
evaluator = config['evaluators'][0]
print("="*60)
print("评估器配置:")
print(f"  名称: {evaluator['name']}")
print(f"  框架: {evaluator['framework']}")
print(f"  类型: {evaluator['metric_type']}")
print(f"  阈值: {evaluator['threshold']}")
print(f"  Criteria: {evaluator.get('criteria', '')}")
print("="*60)

# 模拟DeepEvalExecutor的逻辑
metric_type = evaluator['metric_type']
evaluator_info = evaluator  # 模拟evaluator_info

# 检查是否匹配GEval条件
print("\n检查metric_type匹配:")
print(f"  metric_type.startswith('GEval'): {metric_type.startswith('GEval')}")
print(f"  'Custom' in metric_type: {'Custom' in metric_type}")
print(f"  'Correctness' in metric_type: {'Correctness' in metric_type}")

# 检查是否会进入GEval分支
is_geval = (
    metric_type.startswith("GEval") or
    "Custom" in metric_type or
    "Conversation Completeness" in metric_type or
    "对话完整性" in metric_type or
    "Role Adherence" in metric_type or
    "角色遵循" in metric_type or
    "Correctness" in metric_type or
    "正确性" in metric_type
)

print(f"\n是否进入GEval分支: {is_geval}")

if is_geval:
    # 获取criteria
    criteria = evaluator_info.get("criteria", "")
    print(f"\n获取到的criteria:")
    print(f"  长度: {len(criteria)}")
    print(f"  内容: {criteria}")

    if not criteria:
        print("\n❌ 问题：criteria为空！会使用默认criteria")
    else:
        print("\n✅ criteria不为空，应该会使用自定义criteria")

# 检查evaluation_params
print("\n" + "="*60)
print("检查evaluation_params:")

from deepeval.test_case import LLMTestCaseParams

def _get_evaluation_params(metric_type: str) -> list:
    """获取 evaluation_params"""
    if "Role Adherence" in metric_type or "角色遵循" in metric_type:
        return [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
    elif "Correctness" in metric_type or "正确性" in metric_type:
        return [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.RETRIEVAL_CONTEXT]
    elif "Conversation Completeness" in metric_type or "对话完整性" in metric_type:
        return [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
    else:
        return [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]

evaluation_params = _get_evaluation_params(metric_type)
print(f"  evaluation_params: {evaluation_params}")

# 打印每个param的含义
param_names = {
    LLMTestCaseParams.INPUT: "INPUT (问题)",
    LLMTestCaseParams.ACTUAL_OUTPUT: "ACTUAL_OUTPUT (回答)",
    LLMTestCaseParams.RETRIEVAL_CONTEXT: "RETRIEVAL_CONTEXT (上下文)"
}

print("\n  参数含义:")
for param in evaluation_params:
    print(f"    - {param_names.get(param, param)}")

print("\n" + "="*60)

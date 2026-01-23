"""
调试真实评估过程
"""
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入必要的模块
from evaluators.deepeval_executor import DeepEvalExecutor
from config_manager import ConfigManager

# 加载配置
config_manager = ConfigManager()

# 获取模型设置
model_settings = config_manager.get_model_settings()

# 获取评估器配置
evaluators = config_manager.get_evaluators()
evaluator = evaluators[0]  # Correctness-DeepEval

print("="*60)
print("评估器配置:")
print(f"  名称: {evaluator['name']}")
print(f"  类型: {evaluator['metric_type']}")
print(f"  Criteria: {evaluator.get('criteria', '')[:50]}...")
print("="*60)

# 创建执行器
executor = DeepEvalExecutor(evaluator)

# 测试数据
question = "这个保险的手续费是多少？"
answer = "该保险产品需要支付26元的手续费。"
context = "该保险产品需要支付25元的手续费，在投保时一次性收取。"

print("\n开始评估...")
print(f"  问题: {question}")
print(f"  回答: {answer}")
print(f"  上下文: {context}")

# 执行评估
result = executor.execute(question, answer, context, model_settings)

print("\n" + "="*60)
print("评估结果:")
print(f"  Success: {result.get('success')}")
print(f"  Score: {result.get('score')}")
print(f"  Passed: {result.get('passed')}")
print(f"  Reason: {result.get('reason', '')[:100]}...")
print("="*60)

# 打印verbose_logs（如果有）
if result.get('verbose_logs'):
    print("\nVerbose Logs:")
    print(result['verbose_logs'][:500])

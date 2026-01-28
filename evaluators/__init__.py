"""
评估器执行模块
基于真实评估框架的实现
"""
from .deepeval_executor import DeepEvalExecutor
from .custom_executor import CustomExecutor
from .sequential_rule_executor import SequentialRuleExecutor

__all__ = ['DeepEvalExecutor', 'CustomExecutor', 'SequentialRuleExecutor']

from .ragas_executor import RagasExecutor


def get_executor(evaluator_info):
    """
    工厂方法：根据评估器配置返回对应的执行器

    Args:
        evaluator_info: 评估器配置字典
            {
                'framework': 'deepeval' or 'ragas' or 'custom',
                'metric_type': 'Faithfulness' or '规则评分' or '顺序规则',
                'threshold': 0.6
            }

    Returns:
        评估器执行器实例
    """
    framework = evaluator_info.get('framework', '').lower()
    metric_type = evaluator_info.get('metric_type', '')

    if framework == 'deepeval':
        return DeepEvalExecutor(evaluator_info)
    elif framework == 'ragas':
        return RagasExecutor(evaluator_info)
    elif framework == 'custom':
        # 自定义框架根据metric_type选择执行器
        if metric_type == '顺序规则':
            return SequentialRuleExecutor(evaluator_info)
        else:  # 规则评分
            return CustomExecutor(evaluator_info)
    else:
        raise ValueError(f"不支持的框架: {framework}")

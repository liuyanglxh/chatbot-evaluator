"""
评估器执行模块
基于真实评估框架的实现
"""
from .deepeval_executor import DeepEvalExecutor
from .custom_executor import CustomExecutor

__all__ = ['DeepEvalExecutor', 'CustomExecutor']

from .ragas_executor import RagasExecutor


def get_executor(evaluator_info):
    """
    工厂方法：根据评估器配置返回对应的执行器

    Args:
        evaluator_info: 评估器配置字典
            {
                'framework': 'deepeval' or 'ragas' or 'custom',
                'metric_type': 'Faithfulness',
                'threshold': 0.6
            }

    Returns:
        评估器执行器实例
    """
    framework = evaluator_info.get('framework', '').lower()

    if framework == 'deepeval':
        return DeepEvalExecutor(evaluator_info)
    elif framework == 'custom':
        return CustomExecutor(evaluator_info)
    elif framework == 'ragas':
        # raise NotImplementedError("Ragas 框架支持待实现")
        return RagasExecutor(evaluator_info)
    else:
        raise ValueError(f"不支持的框架: {framework}")

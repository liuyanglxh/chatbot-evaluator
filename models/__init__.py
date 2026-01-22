"""
模型管理模块
支持多种大模型的统一接口
"""
from .base_model import BaseModel
from .qwen_model import QwenModel
from .deepseek_model import DeepSeekModel
from .openai_model import OpenAIModel

__all__ = [
    'BaseModel',
    'QwenModel',
    'DeepSeekModel',
    'OpenAIModel'
]


def get_model(model_type, base_url, api_key):
    """
    工厂方法：根据模型类型返回对应的模型实例

    Args:
        model_type: 模型类型（如 qwen-max, deepseek-chat, gpt-4）
        base_url: API 基础 URL
        api_key: API 密钥

    Returns:
        BaseModel 实例
    """
    model_type = model_type.lower()

    # 通义千问系列
    if 'qwen' in model_type:
        return QwenModel(model_type, base_url, api_key)

    # DeepSeek 系列
    elif 'deepseek' in model_type:
        return DeepSeekModel(model_type, base_url, api_key)

    # OpenAI 系列
    elif 'gpt' in model_type:
        return OpenAIModel(model_type, base_url, api_key)

    # 默认使用通用的 OpenAI 兼容接口
    else:
        return QwenModel(model_type, base_url, api_key)

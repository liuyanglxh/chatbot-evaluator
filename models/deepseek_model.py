"""
DeepSeek 模型实现
"""
from typing import Dict, Any
from .base_model import BaseModel


class DeepSeekModel(BaseModel):
    """DeepSeek 模型"""

    def get_api_endpoint(self) -> str:
        """获取 API 端点"""
        return f"{self.base_url}/chat/completions"

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def format_payload(self, prompt: str) -> Dict[str, Any]:
        """格式化请求载荷"""
        return {
            "model": self.model_type,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }

    def extract_response(self, response_data: Dict[str, Any]) -> str:
        """从响应中提取生成的文本"""
        try:
            return response_data['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            raise Exception(f"响应格式错误: {e}")

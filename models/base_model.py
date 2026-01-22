"""
大模型基类
定义所有模型必须实现的接口
"""
from abc import ABC, abstractmethod
import requests
from typing import Dict, Any, Optional


class BaseModel(ABC):
    """大模型基类"""

    def __init__(self, model_type: str, base_url: str, api_key: str):
        """
        初始化模型

        Args:
            model_type: 模型类型（如 qwen-max, gpt-4）
            base_url: API 基础 URL
            api_key: API 密钥
        """
        self.model_type = model_type
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    @abstractmethod
    def get_api_endpoint(self) -> str:
        """
        获取 API 端点

        Returns:
            完整的 API URL
        """
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """
        获取请求头

        Returns:
            请求头字典
        """
        pass

    @abstractmethod
    def format_payload(self, prompt: str) -> Dict[str, Any]:
        """
        格式化请求载荷

        Args:
            prompt: 用户提示词

        Returns:
            请求载荷字典
        """
        pass

    @abstractmethod
    def extract_response(self, response_data: Dict[str, Any]) -> str:
        """
        从响应中提取生成的文本

        Args:
            response_data: API 响应数据

        Returns:
            生成的文本
        """
        pass

    def test_connection(self) -> tuple[bool, str]:
        """
        测试模型连接

        Returns:
            (是否成功, 消息)
        """
        try:
            # 发送测试请求
            response = self._send_request("你好")

            if response.get('success'):
                return True, "连接成功！模型响应正常。"
            else:
                return False, f"连接失败：{response.get('error', '未知错误')}"

        except Exception as e:
            return False, f"连接异常：{str(e)}"

    def _send_request(self, prompt: str) -> Dict[str, Any]:
        """
        发送请求到模型 API

        Args:
            prompt: 用户提示词

        Returns:
            响应字典 {'success': bool, 'data': dict, 'error': str}
        """
        try:
            # 构建请求
            url = self.get_api_endpoint()
            headers = self.get_headers()
            payload = self.format_payload(prompt)

            # 发送请求
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            # 检查 HTTP 状态
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

            # 解析响应
            response_data = response.json()
            content = self.extract_response(response_data)

            return {
                'success': True,
                'data': response_data,
                'content': content
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "请求超时，请检查网络连接"
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': "网络连接失败，请检查 Base URL"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate(self, prompt: str) -> str:
        """
        生成文本（便捷方法）

        Args:
            prompt: 用户提示词

        Returns:
            生成的文本
        """
        response = self._send_request(prompt)
        if response.get('success'):
            return response.get('content', '')
        else:
            raise Exception(response.get('error', '生成失败'))

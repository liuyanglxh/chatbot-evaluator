"""
配置管理模块
负责保存和加载应用程序配置
支持跨平台（Windows、macOS、Linux）
"""
import json
import os
import platform
from pathlib import Path


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        # 根据操作系统确定配置目录
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"

        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        print(f"配置目录: {self.config_dir}")  # 调试信息

        # 默认配置
        self.default_config = {
            "model_settings": {
                "model_type": "qwen-max",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": ""
            },
            "evaluators": []
        }

    def _get_config_dir(self):
        """根据操作系统获取配置目录"""
        system = platform.system()

        if system == "Windows":
            # Windows: C:\Users\用户名\AppData\Roaming\llm_evaluator
            appdata = os.environ.get("APPDATA")
            if appdata:
                return Path(appdata) / "llm_evaluator"
            else:
                # 降级方案
                return Path.home() / ".llm_evaluator"

        elif system == "Darwin":
            # macOS: ~/Library/Application Support/llm_evaluator
            return Path.home() / "Library" / "Application Support" / "llm_evaluator"

        else:
            # Linux/其他: ~/.config/llm_evaluator (遵循 XDG Base Directory 规范)
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config:
                return Path(xdg_config) / "llm_evaluator"
            else:
                # 降级到 ~/.config/llm_evaluator
                return Path.home() / ".config" / "llm_evaluator"

    def save_config(self, config):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def load_config(self):
        """从文件加载配置"""
        if not self.config_file.exists():
            # 如果配置文件不存在，返回默认配置
            return self.default_config.copy()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"加载配置失败: {e}")
            return self.default_config.copy()

    def update_model_settings(self, model_type, base_url, api_key):
        """更新大模型设置"""
        config = self.load_config()
        config["model_settings"] = {
            "model_type": model_type,
            "base_url": base_url,
            "api_key": api_key
        }
        self.save_config(config)
        return True

    def get_model_settings(self):
        """获取大模型设置"""
        config = self.load_config()
        return config.get("model_settings", self.default_config["model_settings"])

    def add_evaluator(self, evaluator_config):
        """添加评估器"""
        config = self.load_config()
        config["evaluators"].append(evaluator_config)
        self.save_config(config)
        return True

    def get_evaluators(self):
        """获取所有评估器"""
        config = self.load_config()
        return config.get("evaluators", [])

    def remove_evaluator(self, evaluator_name):
        """删除评估器"""
        config = self.load_config()
        config["evaluators"] = [
            e for e in config["evaluators"]
            if e["name"] != evaluator_name
        ]
        self.save_config(config)
        return True

    # ========== 测试数据管理 ==========

    def add_test_data(self, test_data):
        """
        添加测试数据

        Args:
            test_data: 测试数据字典
                {
                    'name': '测试数据名称',
                    'question': '问题',
                    'answer': '回答',
                    'context': '上下文（可选）'
                }
        """
        config = self.load_config()

        # 确保 test_data 字段存在
        if "test_data" not in config:
            config["test_data"] = []

        config["test_data"].append(test_data)
        self.save_config(config)
        return True

    def get_test_data_list(self):
        """获取所有测试数据"""
        config = self.load_config()
        return config.get("test_data", [])

    def remove_test_data(self, test_name):
        """删除测试数据"""
        config = self.load_config()
        config["test_data"] = [
            td for td in config.get("test_data", [])
            if td["name"] != test_name
        ]
        self.save_config(config)
        return True

    def get_test_data_by_name(self, test_name):
        """根据名称获取测试数据"""
        test_data_list = self.get_test_data_list()
        for td in test_data_list:
            if td["name"] == test_name:
                return td
        return None

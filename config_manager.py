"""
配置管理模块
负责保存和加载应用程序配置
支持跨平台（Windows、macOS、Linux）
"""
import json
import os
import platform
import uuid
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
            "evaluators": [],
            "test_groups": [
                {"name": "Correctness", "description": "正确性测试"},
                {"name": "Toxicity", "description": "毒性检测测试"}
            ]
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

        # 如果没有ID，生成新的UUID
        if "id" not in evaluator_config:
            evaluator_config["id"] = str(uuid.uuid4())

        config["evaluators"].append(evaluator_config)
        self.save_config(config)
        return True

    def get_evaluators(self):
        """获取所有评估器"""
        config = self.load_config()

        # 迁移：为没有ID的评估器生成ID
        evaluators = config.get("evaluators", [])
        for evaluator in evaluators:
            if "id" not in evaluator:
                evaluator["id"] = str(uuid.uuid4())

        # 如果有迁移，保存回文件
        if any("id" not in e for e in config.get("evaluators", [])):
            self.save_config(config)

        return evaluators

    def remove_evaluator(self, evaluator_id):
        """删除评估器（根据ID）"""
        config = self.load_config()
        config["evaluators"] = [
            e for e in config["evaluators"]
            if e.get("id") != evaluator_id
        ]
        self.save_config(config)
        return True

    def remove_evaluator_by_name(self, evaluator_name):
        """删除评估器（根据名称）- 兼容旧方法"""
        config = self.load_config()
        config["evaluators"] = [
            e for e in config["evaluators"]
            if e["name"] != evaluator_name
        ]
        self.save_config(config)
        return True

    def update_evaluator(self, evaluator_id, updated_config):
        """更新评估器（根据ID）"""
        config = self.load_config()

        # 找到要更新的评估器索引
        for i, evaluator in enumerate(config["evaluators"]):
            if evaluator.get("id") == evaluator_id:
                # 保留原有的ID
                updated_config["id"] = evaluator_id
                config["evaluators"][i] = updated_config
                self.save_config(config)
                return True

        return False

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
                    'context': '参考资料（可选）'
                }
        """
        config = self.load_config()

        # 确保 test_data 字段存在
        if "test_data" not in config:
            config["test_data"] = []

        # 如果没有ID，生成新的UUID
        if "id" not in test_data:
            test_data["id"] = str(uuid.uuid4())

        config["test_data"].append(test_data)
        self.save_config(config)
        return True

    def get_test_data_list(self):
        """获取所有测试数据"""
        config = self.load_config()

        # 迁移：为没有ID的测试数据生成ID
        test_data_list = config.get("test_data", [])
        need_save = False

        for td in test_data_list:
            if "id" not in td:
                td["id"] = str(uuid.uuid4())
                need_save = True

        # 如果有迁移，保存回文件
        if need_save:
            self.save_config(config)

        return test_data_list

    def remove_test_data(self, test_data_id):
        """删除测试数据（根据ID）"""
        config = self.load_config()
        config["test_data"] = [
            td for td in config.get("test_data", [])
            if td.get("id") != test_data_id
        ]
        self.save_config(config)
        return True

    def remove_test_data_by_name(self, test_name):
        """删除测试数据（根据名称）- 兼容旧方法"""
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

    def get_test_data_by_id(self, test_data_id):
        """根据ID获取测试数据"""
        test_data_list = self.get_test_data_list()
        for td in test_data_list:
            if td.get("id") == test_data_id:
                return td
        return None

    def update_test_data(self, test_data_id, updated_data):
        """更新测试数据（根据ID）"""
        config = self.load_config()

        # 找到要更新的测试数据索引
        for i, td in enumerate(config["test_data"]):
            if td.get("id") == test_data_id:
                # 保留原有的ID
                updated_data["id"] = test_data_id
                config["test_data"][i] = updated_data
                self.save_config(config)
                return True

        return False

    def save_font_size(self, font_size: int):
        """保存字体大小设置"""
        config = self.load_config()
        config["font_size"] = font_size
        self.save_config(config)

    def get_font_size(self) -> int:
        """获取字体大小设置"""
        config = self.load_config()
        return config.get("font_size", 11)  # 默认11号字体

    def save_menu_font_size(self, menu_font_size: int):
        """保存菜单栏字体大小设置"""
        config = self.load_config()
        config["menu_font_size"] = menu_font_size
        self.save_config(config)

    def get_menu_font_size(self) -> int:
        """获取菜单栏字体大小设置"""
        config = self.load_config()
        return config.get("menu_font_size", 11)  # 默认11号字体

    def save_panel_font_size(self, panel_font_size: int):
        """保存功能区字体大小设置"""
        config = self.load_config()
        config["panel_font_size"] = panel_font_size
        self.save_config(config)

    def get_panel_font_size(self) -> int:
        """获取功能区字体大小设置"""
        config = self.load_config()
        return config.get("panel_font_size", 11)  # 默认11号字体

    # ========== 测试分组管理 ==========

    def get_test_groups(self) -> list:
        """获取所有测试分组"""
        config = self.load_config()
        return config.get("test_groups", [])

    def add_test_group(self, group_name: str, description: str = "") -> bool:
        """
        添加测试分组

        Args:
            group_name: 分组名称
            description: 分组描述

        Returns:
            是否成功
        """
        config = self.load_config()

        # 确保test_groups字段存在
        if "test_groups" not in config:
            config["test_groups"] = []

        # 检查是否已存在
        for group in config["test_groups"]:
            if group["name"] == group_name:
                return False  # 已存在

        config["test_groups"].append({
            "name": group_name,
            "description": description
        })

        return self.save_config(config)

    def remove_test_group(self, group_name: str) -> bool:
        """
        删除测试分组

        Args:
            group_name: 分组名称

        Returns:
            是否成功
        """
        config = self.load_config()

        if "test_groups" not in config:
            return False

        # 删除分组
        config["test_groups"] = [
            g for g in config["test_groups"]
            if g["name"] != group_name
        ]

        # 同时需要从所有测试数据中移除该分组
        if "test_data" in config:
            for test_data in config["test_data"]:
                if "groups" in test_data and group_name in test_data["groups"]:
                    test_data["groups"].remove(group_name)

        return self.save_config(config)

    def update_test_group(self, old_name: str, new_name: str, description: str = "") -> bool:
        """
        更新测试分组

        Args:
            old_name: 旧名称
            new_name: 新名称
            description: 描述

        Returns:
            是否成功
        """
        config = self.load_config()

        if "test_groups" not in config:
            return False

        # 更新分组名称和描述
        for group in config["test_groups"]:
            if group["name"] == old_name:
                group["name"] = new_name
                group["description"] = description
                break

        # 同时需要更新所有测试数据中的分组名称
        if "test_data" in config:
            for test_data in config["test_data"]:
                if "groups" in test_data and old_name in test_data["groups"]:
                    # 替换分组名称
                    idx = test_data["groups"].index(old_name)
                    test_data["groups"][idx] = new_name

        return self.save_config(config)

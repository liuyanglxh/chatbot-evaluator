"""
字体工具类
提供统一的字体大小管理
"""
from config_manager import ConfigManager


class FontManager:
    """字体管理器 - 单例模式"""

    _instance = None
    _config_manager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config_manager = ConfigManager()
        return cls._instance

    def get_content_font_size(self) -> int:
        """获取内容字体大小（用于输入框、文本框等）"""
        return self._config_manager.get_font_size()

    def get_menu_font_size(self) -> int:
        """获取菜单栏字体大小"""
        return self._config_manager.get_menu_font_size()

    def get_menu_title_font_size(self) -> int:
        """获取菜单栏标题字体大小（功能菜单）"""
        return self.get_menu_font_size() + 5

    def get_panel_font_size(self) -> int:
        """获取功能区字体大小（用于弹出窗口内容）"""
        return self._config_manager.get_panel_font_size()

    def get_panel_title_font_size(self) -> int:
        """获取功能区标题字体大小（弹出窗口标题）"""
        return self.get_panel_font_size() + 5

    # ========== 字体元组方法（直接用于font参数） ==========

    def content_font(self):
        """内容字体"""
        size = self.get_content_font_size()
        return ("Arial", size)

    def menu_font(self):
        """菜单栏字体"""
        size = self.get_menu_font_size()
        return ("Arial", size)

    def menu_title_font(self):
        """菜单栏标题字体"""
        size = self.get_menu_title_font_size()
        return ("Arial", size, "bold")

    def panel_font(self):
        """功能区字体"""
        size = self.get_panel_font_size()
        return ("Arial", size)

    def panel_title_font(self):
        """功能区标题字体"""
        size = self.get_panel_title_font_size()
        return ("Arial", size, "bold")

    def panel_font_bold(self):
        """功能区字体（粗体）"""
        size = self.get_panel_font_size()
        return ("Arial", size, "bold")

    def panel_font_small(self):
        """功能区小字体（比普通字体小1号）"""
        size = max(8, self.get_panel_font_size() - 1)
        return ("Arial", size)


# 全局单例实例
font_manager = FontManager()

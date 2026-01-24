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

    def get_treeview_row_height(self) -> int:
        """
        计算Treeview的合适行高
        根据功能区字体大小动态计算，确保文字不重叠

        Returns:
            int: 行高（像素）
        """
        font_size = self.get_panel_font_size()
        # 基础行高 = 字体大小 * 1.8（预留空间）
        # 最小25，最大60
        row_height = int(font_size * 1.8)
        return max(25, min(row_height, 60))

    def get_entry_width(self, base_width: int = 50) -> int:
        """
        根据字体大小计算Entry/Combobox的合适宽度

        Args:
            base_width: 基础宽度（默认字体大小下的宽度）

        Returns:
            int: 调整后的宽度
        """
        font_size = self.get_panel_font_size()
        # 默认11号字体，每增加1号字体，宽度增加约5%
        scale_factor = 1 + (font_size - 11) * 0.05
        # 限制在0.7到1.5倍之间
        scale_factor = max(0.7, min(scale_factor, 1.5))
        return int(base_width * scale_factor)

    def get_button_width(self, base_width: int = 10) -> int:
        """
        根据字体大小计算按钮的合适宽度

        Args:
            base_width: 基础宽度（字符数）

        Returns:
            int: 调整后的字符数
        """
        font_size = self.get_panel_font_size()
        # 默认11号字体，每增加1号字体，宽度增加约8%
        scale_factor = 1 + (font_size - 11) * 0.08
        # 限制在0.6到1.6倍之间
        scale_factor = max(0.6, min(scale_factor, 1.6))
        return max(6, int(base_width * scale_factor))


# 全局单例实例
font_manager = FontManager()

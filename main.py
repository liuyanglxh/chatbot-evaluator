"""
LLM 评估工具 - 主程序
带可视化界面的评估工具，支持 Ragas 和 DeepEval 框架
"""
import tkinter as tk
from tkinter import ttk


class EvaluatorGUI:
    """评估工具主界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("LLM 评估工具")
        self.root.geometry("1000x700")

        # 初始化全局ESC键处理器
        from utils.window_helpers import initialize_global_esc_handler
        initialize_global_esc_handler(root)

        # 窗口居中
        self.center_window()

        # 创建主界面
        self.create_main_interface()

    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()

        # 获取窗口尺寸
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # 设置窗口位置
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_main_interface(self):
        """创建主界面 - 左右分栏布局"""
        # 移除默认菜单栏
        self.root.config(menu="")

        # 创建左右分栏的 PanedWindow
        paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置主窗口网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # ========== 左侧面板 ==========
        left_frame = ttk.Frame(paned_window, padding="10", relief="ridge")
        paned_window.add(left_frame, minsize=200, width=250)

        # 左侧标题
        # 获取菜单栏字体大小
        from config_manager import ConfigManager
        config_manager = ConfigManager()
        menu_font_size = config_manager.get_menu_font_size()
        title_font_size = menu_font_size + 5  # 标题比菜单项大5号

        left_title = ttk.Label(
            left_frame,
            text="功能菜单",
            font=("Arial", title_font_size, "bold")
        )
        left_title.pack(pady=(0, 20))

        # 创建菜单按钮
        self.create_menu_buttons(left_frame)

        # ========== 右侧面板 ==========
        right_frame = ttk.Frame(paned_window, padding="30")
        paned_window.add(right_frame, minsize=400)

        # 右侧内容
        self.create_right_content(right_frame)

    def create_menu_buttons(self, parent):
        """创建左侧菜单按钮"""
        # 获取菜单栏字体大小
        from config_manager import ConfigManager
        config_manager = ConfigManager()
        menu_font_size = config_manager.get_menu_font_size()

        # 配置ttk按钮样式
        style = ttk.Style()
        style.configure("Menu.TButton", font=("Arial", menu_font_size))

        # 设置组
        settings_label = ttk.Label(parent, text="设置", font=("Arial", menu_font_size, "bold"))
        settings_label.pack(anchor=tk.W, pady=(10, 5))

        # 大模型设置按钮
        model_settings_btn = ttk.Button(
            parent,
            text="🔧 大模型设置",
            command=self.open_model_settings,
            width=25,
            style="Menu.TButton"
        )
        model_settings_btn.pack(pady=5, anchor=tk.W)

        # 字体设置按钮
        font_settings_btn = ttk.Button(
            parent,
            text="🔤 字体设置",
            command=self.open_font_settings,
            width=25,
            style="Menu.TButton"
        )
        font_settings_btn.pack(pady=5, anchor=tk.W)

        # 分隔线
        separator1 = ttk.Separator(parent, orient=tk.HORIZONTAL)
        separator1.pack(fill=tk.X, pady=15)

        # 评估器组
        evaluator_label = ttk.Label(parent, text="评估器", font=("Arial", menu_font_size, "bold"))
        evaluator_label.pack(anchor=tk.W, pady=(0, 5))

        # 添加评估器按钮
        add_evaluator_btn = ttk.Button(
            parent,
            text="➕ 添加评估器",
            command=self.open_add_evaluator,
            width=25,
            style="Menu.TButton"
        )
        add_evaluator_btn.pack(pady=5, anchor=tk.W)

        # 查看评估器按钮
        list_evaluator_btn = ttk.Button(
            parent,
            text="📋 查看评估器",
            command=self.open_evaluator_list,
            width=25,
            style="Menu.TButton"
        )
        list_evaluator_btn.pack(pady=5, anchor=tk.W)

        # 分隔线
        separator2 = ttk.Separator(parent, orient=tk.HORIZONTAL)
        separator2.pack(fill=tk.X, pady=15)

        # 测试数据组
        test_data_label = ttk.Label(parent, text="测试数据", font=("Arial", menu_font_size, "bold"))
        test_data_label.pack(anchor=tk.W, pady=(0, 5))

        # 测试数据管理按钮
        test_data_manager_btn = ttk.Button(
            parent,
            text="📚 测试数据管理",
            command=self.open_test_data_manager,
            width=25,
            style="Menu.TButton"
        )
        test_data_manager_btn.pack(pady=5, anchor=tk.W)

        # 分组管理按钮
        group_manager_btn = ttk.Button(
            parent,
            text="🏷️ 分组管理",
            command=self.open_group_manager,
            width=25,
            style="Menu.TButton"
        )
        group_manager_btn.pack(pady=5, anchor=tk.W)

        # 分隔线
        separator3 = ttk.Separator(parent, orient=tk.HORIZONTAL)
        separator3.pack(fill=tk.X, pady=15)

        # 退出按钮
        exit_btn = ttk.Button(
            parent,
            text="❌ 退出",
            command=self.root.quit,
            width=25,
            style="Menu.TButton"
        )
        exit_btn.pack(pady=5, anchor=tk.W)

        # 底部弹簧，将内容顶上去
        spacer = ttk.Frame(parent)
        spacer.pack(expand=True, fill=tk.BOTH)

    def create_right_content(self, parent):
        """创建右侧内容区域"""
        # 标题
        title_label = ttk.Label(
            parent,
            text="欢迎使用 LLM 评估工具",
            font=("Arial", 28, "bold")
        )
        title_label.pack(pady=(50, 30))

        # 副标题
        subtitle_label = ttk.Label(
            parent,
            text="支持 Ragas 和 DeepEval 框架的智能评估系统",
            font=("Arial", 14),
            foreground="gray"
        )
        subtitle_label.pack(pady=(0, 40))

        # 功能卡片框架
        cards_frame = ttk.Frame(parent)
        cards_frame.pack(fill=tk.BOTH, expand=True)

        # 创建功能卡片
        self.create_feature_card(
            cards_frame,
            "🚀 快速开始",
            [
                "1. 点击左侧「大模型设置」配置 API",
                "2. 点击「添加评估器」选择评估指标",
                "3. 查看和管理已添加的评估器"
            ],
            0
        )

        self.create_feature_card(
            cards_frame,
            "📊 支持的框架",
            [
                "• Ragas: 专注 RAG 系统评估",
                "• DeepEval: 全面的 LLM 评估",
                "• 多种评估指标可供选择"
            ],
            1
        )

    def create_feature_card(self, parent, title, items, row):
        """创建功能卡片"""
        card_frame = ttk.LabelFrame(
            parent,
            text=title,
            padding="20"
        )
        card_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=10)

        for item in items:
            item_label = ttk.Label(
                card_frame,
                text=item,
                font=("Arial", 11),
                justify=tk.LEFT
            )
            item_label.pack(anchor=tk.W, pady=5)

        parent.columnconfigure(0, weight=1)

    def open_model_settings(self):
        """打开大模型设置窗口"""
        from windows.model_settings_window import ModelSettingsWindow
        ModelSettingsWindow(self.root)

    def open_font_settings(self):
        """打开字体设置窗口"""
        from windows.font_settings_window import FontSettingsWindow
        FontSettingsWindow(self.root)

    def open_add_evaluator(self):
        """打开添加评估器窗口"""
        from windows.add_evaluator_window import AddEvaluatorWindow
        AddEvaluatorWindow(self.root)

    def open_evaluator_list(self):
        """打开评估器列表窗口"""
        from windows.evaluator_list_window import EvaluatorListWindow
        EvaluatorListWindow(self.root)

    def open_test_data_manager(self):
        """打开测试数据管理窗口"""
        from windows.test_data_manager_window import TestDataManagerWindow
        TestDataManagerWindow(self.root)

    def open_group_manager(self):
        """打开分组管理窗口"""
        from windows.group_manager_window import GroupManagerWindow
        GroupManagerWindow(self.root)


def main():
    """主函数"""
    root = tk.Tk()
    app = EvaluatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

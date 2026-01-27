"""
Excel批量评估窗口
用于上传Excel并批量评估
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from font_utils import font_manager
from utils.window_helpers import bind_esc_key
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_manager import ConfigManager


class ExcelBatchEvaluationWindow:
    """Excel批量评估窗口"""

    def __init__(self, parent):
        self.parent = parent
        self.config_manager = ConfigManager()
        self.excel_file_path = None
        self.selected_evaluators = {}

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("Excel批量评估")
        self.window.geometry("700x700")  # 增加高度
        self.window.transient(parent)
        self.window.grab_set()

        # 创建界面
        self.create_interface()

        # 居中显示
        self.center_window()

        # 绑定ESC键
        bind_esc_key(self.window)

    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="📊 Excel批量评估",
            font=font_manager.panel_title_font()
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # ========== 1. 上传Excel区域 ==========
        upload_frame = ttk.LabelFrame(
            main_frame,
            text="1. 上传Excel文件",
            padding="15"
        )
        upload_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # 文件路径显示
        self.file_path_var = tk.StringVar(value="未选择文件")
        file_path_entry = ttk.Entry(
            upload_frame,
            textvariable=self.file_path_var,
            state="readonly",
            font=font_manager.panel_font()
        )
        file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # 选择文件按钮
        select_file_button = ttk.Button(
            upload_frame,
            text="📁 选择文件",
            command=self.select_excel_file,
            width=15
        )
        select_file_button.pack(side=tk.LEFT)

        # ========== 2. 选择评估器区域 ==========
        evaluator_frame = ttk.LabelFrame(
            main_frame,
            text="2. 选择评估器（可多选）",
            padding="15"
        )
        evaluator_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # 创建Treeview容器
        tree_container = ttk.Frame(evaluator_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview（带复选框列）
        columns = ("checkbox", "name", "framework", "type")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        # 设置列
        self.tree.heading("checkbox", text="☐")
        self.tree.heading("name", text="评估器名称")
        self.tree.heading("framework", text="框架")
        self.tree.heading("type", text="类型")

        # 设置列宽
        self.tree.column("checkbox", width=40, anchor=tk.CENTER)
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("framework", width=100, anchor=tk.W)
        self.tree.column("type", width=200, anchor=tk.W)

        # 应用字体设置
        style = ttk.Style()
        row_height = font_manager.get_treeview_row_height()
        style.configure("ExcelEvaluator.Treeview",
                       font=font_manager.panel_font(),
                       rowheight=row_height)
        style.configure("ExcelEvaluator.Treeview.Heading", font=font_manager.panel_font_bold())
        self.tree.configure(style="ExcelEvaluator.Treeview")

        # 滚动条
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 复选框状态存储
        self.checkbox_vars = {}

        # 控制按钮区域
        control_frame = ttk.Frame(evaluator_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        # 全选按钮
        self.select_all_button = ttk.Button(
            control_frame,
            text="☑ 全选",
            command=self.toggle_select_all,
            width=10
        )
        self.select_all_button.pack(side=tk.LEFT, padx=5)

        # 加载评估器列表
        self.load_evaluators()

        # 绑定点击事件（用于切换复选框）
        self.tree.bind("<Button-1>", self._on_click)

        # ========== 3. 开始评估按钮 ==========
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(30, 0))

        # 开始评估按钮
        self.start_button = ttk.Button(
            button_frame,
            text="▶ 开始评估",
            command=self.start_evaluation,
            width=20
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="✖ 取消",
            command=self.window.destroy,
            width=15
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # 让评估器列表区域占据剩余空间

    def load_evaluators(self):
        """加载评估器列表"""
        evaluators = self.config_manager.get_evaluators()

        for evaluator in evaluators:
            name = evaluator.get("name", "")
            framework = evaluator.get("framework", "")
            metric_type = evaluator.get("metric_type", "")

            # 框架显示名称
            framework_display = self._get_framework_display_name(framework)

            # 创建复选框变量
            var = tk.BooleanVar(value=False)
            item_id = self.tree.insert("", tk.END, values=("☐", name, framework_display, metric_type))
            self.checkbox_vars[item_id] = var
            self.selected_evaluators[name] = evaluator

    def _get_framework_display_name(self, framework: str) -> str:
        """获取框架的友好显示名称"""
        framework_map = {
            "deepeval": "DeepEval",
            "ragas": "Ragas",
            "custom": "自定义"
        }
        return framework_map.get(framework, framework)

    def _on_click(self, event):
        """处理点击事件，用于切换复选框"""
        # 获取点击的位置
        region = self.tree.identify_region(event.x, event.y)

        # 如果点击的是"cell"区域
        if region == "cell":
            # 获取点击的列
            column = self.tree.identify_column(event.x)

            # 如果点击的是第一列（复选框列）
            if column == "#1":
                # 获取点击的行
                item = self.tree.identify_row(event.y)

                if item:
                    # 切换复选框状态
                    var = self.checkbox_vars.get(item)
                    if var:
                        current_value = var.get()
                        var.set(not current_value)

                        # 更新显示
                        new_value = "☑" if not current_value else "☐"
                        self.tree.item(item, values=(new_value, *self.tree.item(item, "values")[1:]))

    def toggle_select_all(self):
        """切换全选/取消全选"""
        all_items = self.tree.get_children()

        # 检查是否已全选
        all_selected = all(
            self.checkbox_vars.get(item) and self.checkbox_vars.get(item).get()
            for item in all_items
        )

        if all_selected:
            # 取消全选
            for item in all_items:
                var = self.checkbox_vars.get(item)
                if var:
                    var.set(False)
                self.tree.item(item, values=("☐", *self.tree.item(item, "values")[1:]))
            self.select_all_button.config(text="☑ 全选")
        else:
            # 全选
            for item in all_items:
                var = self.checkbox_vars.get(item)
                if var:
                    var.set(True)
                self.tree.item(item, values=("☑", *self.tree.item(item, "values")[1:]))
            self.select_all_button.config(text="☐ 取消全选")

    def select_excel_file(self):
        """选择Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.excel_file_path = file_path
            # 只显示文件名，不显示完整路径
            file_name = Path(file_path).name
            self.file_path_var.set(file_name)

    def start_evaluation(self):
        """开始评估"""
        # 验证Excel文件
        if not self.excel_file_path:
            messagebox.showwarning("警告", "请先选择Excel文件")
            return

        # 获取选中的评估器（从Treeview的复选框）
        selected_items = []
        for item in self.tree.get_children():
            var = self.checkbox_vars.get(item)
            if var and var.get():
                selected_items.append(item)

        if not selected_items:
            messagebox.showwarning("警告", "请至少选择一个评估器")
            return

        # 获取选中的评估器
        selected_evaluator_list = []
        for item in selected_items:
            values = self.tree.item(item, "values")
            evaluator_name = values[1]  # 第二列是名称
            selected_evaluator_list.append(self.selected_evaluators[evaluator_name])

        # 开始批量评估
        from excel_evaluation_handler import ExcelEvaluationHandler
        handler = ExcelEvaluationHandler(
            self.window,
            self.excel_file_path,
            selected_evaluator_list,
            self.config_manager
        )
        handler.run()

    def center_window(self):
        """窗口居中显示"""
        self.window.update_idletasks()

        width = self.window.winfo_width()
        height = self.window.winfo_height()

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.window.geometry(f'{width}x{height}+{x}+{y}')

"""
评估器列表窗口
显示所有已添加的评估器
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_manager import ConfigManager


class EvaluatorListWindow:
    """评估器列表窗口"""

    def __init__(self, parent):
        self.config_manager = ConfigManager()

        # 创建新窗口
        self.window = tk.Toplevel(parent)
        self.window.title("评估器列表")
        self.window.geometry("900x600")
        self.window.transient(parent)
        self.window.grab_set()

        # 创建界面
        self.create_interface()

        # 加载评估器列表
        self.load_evaluators()

        # 居中显示
        self.center_window()

    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="评估器列表",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 工具栏
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # 刷新按钮
        refresh_button = ttk.Button(
            toolbar_frame,
            text="刷新",
            command=self.load_evaluators,
            width=10
        )
        refresh_button.grid(row=0, column=0, padx=(0, 10))

        # 使用按钮
        use_button = ttk.Button(
            toolbar_frame,
            text="✓ 使用选中",
            command=self.use_selected,
            width=12
        )
        use_button.grid(row=0, column=1, padx=(0, 10))

        # 删除按钮
        delete_button = ttk.Button(
            toolbar_frame,
            text="删除选中",
            command=self.delete_selected,
            width=10
        )
        delete_button.grid(row=0, column=2, padx=(0, 10))

        # 统计标签
        self.stats_label = ttk.Label(
            toolbar_frame,
            text="共 0 个评估器",
            font=("Arial", 10)
        )
        self.stats_label.grid(row=0, column=3, sticky=tk.W)

        # 创建 Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 滚动条
        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))

        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("name", "framework", "metric_type", "threshold"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=15
        )
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置滚动条
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # 设置列
        self.tree.heading("name", text="评估器名称")
        self.tree.heading("framework", text="评估框架")
        self.tree.heading("metric_type", text="评估器类型")
        self.tree.heading("threshold", text="阈值")

        # 设置列宽
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("framework", width=150, anchor=tk.CENTER)
        self.tree.column("metric_type", width=300, anchor=tk.W)
        self.tree.column("threshold", width=100, anchor=tk.CENTER)

        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # 关闭按钮
        close_button = ttk.Button(
            main_frame,
            text="关闭",
            command=self.window.destroy,
            width=15
        )
        close_button.grid(row=3, column=0, columnspan=3, pady=(20, 0))

    def load_evaluators(self):
        """加载评估器列表"""
        # 清空现有内容
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 加载评估器
        evaluators = self.config_manager.get_evaluators()

        # 插入数据
        for evaluator in evaluators:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    evaluator.get("name", ""),
                    evaluator.get("framework", ""),
                    evaluator.get("metric_type", ""),
                    evaluator.get("threshold", "")
                )
            )

        # 更新统计
        self.stats_label.config(text=f"共 {len(evaluators)} 个评估器")

    def use_selected(self):
        """使用选中的评估器"""
        selection = self.tree.selection()

        if not selection:
            messagebox.showwarning("警告", "请先选择要使用的评估器")
            return

        # 获取选中项的完整信息
        item = self.tree.item(selection[0])
        values = item['values']

        evaluator_info = {
            'name': values[0],
            'framework': values[1],
            'metric_type': values[2],
            'threshold': values[3]
        }

        # 打开评估执行窗口
        from windows.evaluation_execution_window import EvaluationExecutionWindow
        EvaluationExecutionWindow(self.window, evaluator_info)

    def delete_selected(self):
        """删除选中的评估器"""
        selection = self.tree.selection()

        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的评估器")
            return

        # 获取选中项的名称
        item = self.tree.item(selection[0])
        name = item['values'][0]

        # 确认删除
        result = messagebox.askyesno(
            "确认删除",
            f"确定要删除评估器 '{name}' 吗？"
        )

        if result:
            success = self.config_manager.remove_evaluator(name)

            if success:
                messagebox.showinfo("成功", f"评估器 '{name}' 已删除")
                self.load_evaluators()
            else:
                messagebox.showerror("错误", "删除评估器失败")

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

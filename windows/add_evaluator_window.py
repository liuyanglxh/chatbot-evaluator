"""
添加评估器窗口
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_manager import ConfigManager


class AddEvaluatorWindow:
    """添加评估器窗口"""

    def __init__(self, parent):
        self.config_manager = ConfigManager()

        # 创建新窗口
        self.window = tk.Toplevel(parent)
        self.window.title("添加评估器")
        self.window.geometry("700x500")
        self.window.transient(parent)
        self.window.grab_set()

        # 创建界面
        self.create_interface()

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
            text="添加评估器",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 评估器名称
        ttk.Label(main_frame, text="评估器名称:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=50)
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)

        # 框架选择
        ttk.Label(main_frame, text="评估框架:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.framework_var = tk.StringVar()
        framework_frame = ttk.Frame(main_frame)
        framework_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)

        # Ragas 单选按钮
        ragas_rb = ttk.Radiobutton(
            framework_frame,
            text="Ragas",
            variable=self.framework_var,
            value="ragas",
            command=self.on_framework_change
        )
        ragas_rb.grid(row=0, column=0, padx=(0, 20))

        # DeepEval 单选按钮
        deepeval_rb = ttk.Radiobutton(
            framework_frame,
            text="DeepEval",
            variable=self.framework_var,
            value="deepeval",
            command=self.on_framework_change
        )
        deepeval_rb.grid(row=0, column=1)

        # 评估器类型（根据框架动态变化）
        ttk.Label(main_frame, text="评估器类型:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.metric_type_var = tk.StringVar()
        self.metric_combo = ttk.Combobox(
            main_frame,
            textvariable=self.metric_type_var,
            state="readonly",
            width=47
        )
        self.metric_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=10)

        # 初始为空，等待选择框架
        self.metric_combo['values'] = ["请先选择评估框架"]

        # 阈值设置
        ttk.Label(main_frame, text="阈值 (0-1):").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.threshold_var = tk.StringVar(value="0.5")
        threshold_entry = ttk.Entry(main_frame, textvariable=self.threshold_var, width=50)
        threshold_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=10)

        # 说明文本
        info_text = """
说明：
1. 选择评估框架（Ragas 或 DeepEval）
2. 根据框架选择对应的评估器类型
3. 设置评估器的阈值（0-1之间）
4. 评估器将保存到配置文件中
        """
        info_label = ttk.Label(
            main_frame,
            text=info_text,
            font=("Arial", 10),
            justify=tk.LEFT,
            foreground="gray"
        )
        info_label.grid(row=5, column=0, columnspan=2, pady=(20, 10))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(30, 0))

        # 添加按钮
        add_button = ttk.Button(
            button_frame,
            text="添加",
            command=self.add_evaluator,
            width=15
        )
        add_button.grid(row=0, column=0, padx=5)

        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.window.destroy,
            width=15
        )
        cancel_button.grid(row=0, column=1, padx=5)

        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def on_framework_change(self):
        """框架选择改变时的回调"""
        framework = self.framework_var.get()

        if framework == "ragas":
            # Ragas 支持的评估器类型
            self.metric_combo['values'] = [
                "Faithfulness",
                "Answer Relevancy",
                "Context Precision",
                "Context Recall",
                "Context Relevancy",
                "Answer Correctness",
                "Answer Similarity"
            ]
        elif framework == "deepeval":
            # DeepEval 支持的评估器类型
            self.metric_combo['values'] = [
                "Faithfulness",
                "Answer Relevancy",
                "Contextual Precision",
                "Contextual Recall",
                "Contextual Relevancy",
                "Bias",
                "Toxicity",
                "GEval (Custom)"
            ]
        else:
            self.metric_combo['values'] = ["请先选择评估框架"]

        # 清空当前选择
        self.metric_type_var.set("")

    def add_evaluator(self):
        """添加评估器"""
        name = self.name_var.get().strip()
        framework = self.framework_var.get()
        metric_type = self.metric_type_var.get().strip()
        threshold = self.threshold_var.get().strip()

        # 验证必填项
        if not name:
            messagebox.showerror("错误", "请输入评估器名称")
            return

        if not framework:
            messagebox.showerror("错误", "请选择评估框架")
            return

        if not metric_type or metric_type == "请先选择评估框架":
            messagebox.showerror("错误", "请选择评估器类型")
            return

        # 验证阈值
        try:
            threshold_float = float(threshold)
            if not 0 <= threshold_float <= 1:
                raise ValueError()
        except ValueError:
            messagebox.showerror("错误", "阈值必须是 0-1 之间的数字")
            return

        # 检查名称是否已存在
        existing_evaluators = self.config_manager.get_evaluators()
        for evaluator in existing_evaluators:
            if evaluator["name"] == name:
                messagebox.showerror("错误", f"评估器名称 '{name}' 已存在")
                return

        # 创建评估器配置
        evaluator_config = {
            "name": name,
            "framework": framework,
            "metric_type": metric_type,
            "threshold": threshold_float
        }

        # 保存到配置
        success = self.config_manager.add_evaluator(evaluator_config)

        if success:
            messagebox.showinfo("成功", f"评估器 '{name}' 已添加")
            self.window.destroy()
        else:
            messagebox.showerror("错误", "添加评估器失败")

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

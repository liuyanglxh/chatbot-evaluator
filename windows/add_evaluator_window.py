"""
添加评估器窗口
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
from font_utils import font_manager

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_manager import ConfigManager
from windows.scoring_rules_table import ScoringRulesTable


class AddEvaluatorWindow:
    """添加评估器窗口"""

    def __init__(self, parent):
        self.config_manager = ConfigManager()

        # 创建新窗口
        self.window = tk.Toplevel(parent)
        self.window.title("添加评估器")
        self.window.geometry("700x550")  # 增加高度以容纳对话模式选项
        self.window.transient(parent)
        self.window.grab_set()

        # 创建滚动容器
        self.create_scrollable_container()

        # 创建界面
        self.create_interface()

        # 居中显示
        self.center_window()

    def create_scrollable_container(self):
        """创建可滚动容器"""
        # 创建主容器
        container = ttk.Frame(self.window)
        container.pack(fill=tk.BOTH, expand=True)

        # 创建Canvas
        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建滚动条
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 配置Canvas滚动
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 创建可滚动框架
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)

        # 绑定配置事件
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # 绑定鼠标滚轮事件
        self._bind_mousewheel()

    def _on_frame_configure(self, event):
        """框架配置改变时更新滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Canvas配置改变时调整框架宽度"""
        # 调整scrollable_frame的宽度以匹配canvas宽度
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _bind_mousewheel(self):
        """绑定鼠标滚轮事件"""
        # Windows
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        # macOS
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """鼠标滚轮事件处理"""
        # Windows/macOS: event.delta
        # Linux: event.num (4=up, 5=down)
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def create_interface(self):
        """创建界面"""
        # 主框架（放在scrollable_frame中）
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="添加评估器",
            font=font_manager.panel_title_font()
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 评估器名称
        ttk.Label(main_frame, text="评估器名称:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=font_manager.get_entry_width(50))
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)

        # 添加必填标记
        ttk.Label(main_frame, text="*必填", foreground="red", font=("Arial", 9)).grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=10)

        # 框架选择
        ttk.Label(main_frame, text="评估框架:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.framework_var = tk.StringVar()
        framework_frame = ttk.Frame(main_frame)
        framework_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)

        # 添加必填标记
        ttk.Label(main_frame, text="*必填", foreground="red", font=("Arial", 9)).grid(row=2, column=2, sticky=tk.W, padx=(5, 0), pady=10)

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
        deepeval_rb.grid(row=0, column=1, padx=(0, 20))

        # 自定义 单选按钮
        custom_rb = ttk.Radiobutton(
            framework_frame,
            text="自定义",
            variable=self.framework_var,
            value="custom",
            command=self.on_framework_change
        )
        custom_rb.grid(row=0, column=2)

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

        # 添加必填标记
        ttk.Label(main_frame, text="*必填", foreground="red", font=("Arial", 9)).grid(row=3, column=2, sticky=tk.W, padx=(5, 0), pady=10)

        # 绑定选择事件
        self.metric_combo.bind("<<ComboboxSelected>>", self.on_metric_type_change)

        # 初始为空，等待选择框架
        self.metric_combo['values'] = ["请先选择评估框架"]

        # 对话模式（单轮/多轮）
        ttk.Label(main_frame, text="对话模式:").grid(row=4, column=0, sticky=tk.W, pady=10)

        # 对话模式容器
        turn_mode_frame = ttk.Frame(main_frame)
        turn_mode_frame.grid(row=4, column=1, sticky=tk.W, pady=10)

        # 默认为single
        self.turn_mode_var = tk.StringVar(value="single")

        # 单选按钮
        self.turn_mode_single_radio = ttk.Radiobutton(
            turn_mode_frame,
            text="单轮对话（每个测试数据单独评估）",
            variable=self.turn_mode_var,
            value="single"
        )
        self.turn_mode_single_radio.pack(anchor=tk.W)

        self.turn_mode_multi_radio = ttk.Radiobutton(
            turn_mode_frame,
            text="多轮对话（评估完整的多轮对话）",
            variable=self.turn_mode_var,
            value="multi"
        )
        self.turn_mode_multi_radio.pack(anchor=tk.W)

        # 保存对话模式的label和frame引用,用于隐藏
        self.turn_mode_label = main_frame.grid_slaves(row=4, column=0)[0]
        self.turn_mode_frame = turn_mode_frame

        # 阈值设置
        self.threshold_label = ttk.Label(main_frame, text="阈值 (0-1):")
        self.threshold_label.grid(row=5, column=0, sticky=tk.W, pady=10)

        self.threshold_var = tk.StringVar(value="0.5")
        self.threshold_entry = ttk.Entry(main_frame, textvariable=self.threshold_var, width=font_manager.get_entry_width(50))
        self.threshold_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=10)

        # 评估标准（Prompt）输入区域 - 初始隐藏
        self.criteria_frame = ttk.Frame(main_frame)
        # 不grid，等需要时再显示

        ttk.Label(self.criteria_frame, text="评估标准:").grid(row=0, column=0, sticky=tk.NW, pady=10)

        # 创建Text组件（初始2行，会根据内容动态调整）
        self.criteria_text = tk.Text(
            self.criteria_frame,
            font=font_manager.panel_font(),
            height=2,  # 初始2行，会动态调整
            wrap=tk.WORD,
            relief=tk.RIDGE,
            padx=5,
            pady=5
        )
        self.criteria_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 绑定KeyRelease事件，动态调整高度
        self.criteria_text.bind("<KeyRelease>", self._adjust_text_height)

        # 配置grid权重
        self.criteria_frame.columnconfigure(0, weight=1)

        # 评分规则表格（用于自定义框架）- 初始隐藏
        self.scoring_rules_frame = ttk.Frame(main_frame)
        # 不grid，等需要时再显示

        # 创建动态内容容器（用于放置按钮、表格、说明文本等）
        self.dynamic_content_frame = ttk.Frame(main_frame)
        self.dynamic_content_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 配置网格权重（main_frame的列）
        main_frame.columnconfigure(1, weight=1)

        # 初始渲染下方内容
        self._render_lower_section()

        # 初始化对话模式显示状态(默认隐藏,因为framework为空)
        self.turn_mode_label.grid_remove()
        self.turn_mode_frame.grid_remove()

    def _render_lower_section(self):
        """完全重新渲染下方内容（解决切换框架时的残留问题）"""
        framework = self.framework_var.get()
        metric_type = self.metric_type_var.get()

        # 1. 隐藏所有特殊输入框
        self.criteria_frame.grid_forget()
        self.scoring_rules_frame.grid_forget()

        # 2. 清空动态内容容器
        for widget in self.dynamic_content_frame.winfo_children():
            widget.destroy()

        current_row = 0

        # 3. 根据框架和类型决定显示什么
        if framework == "custom" and metric_type == "规则评分":
            # 修改阈值标签文本（去掉"0-1"）
            self.threshold_label.config(text="阈值:")

            # 显示评分规则标签
            ttk.Label(
                self.dynamic_content_frame,
                text="评分规则:",
                font=font_manager.panel_font_bold()
            ).grid(row=current_row, column=0, sticky=tk.W, pady=(0, 10))
            current_row += 1

            # 按钮行
            button_frame = ttk.Frame(self.dynamic_content_frame)
            button_frame.grid(row=current_row, column=0, sticky=tk.W, pady=(0, 10))
            current_row += 1

            # 创建评分规则表格组件（直接在dynamic_content_frame中创建）
            from windows.scoring_rules_table import ScoringRulesTable
            self.scoring_rules_table = ScoringRulesTable(self.dynamic_content_frame)

            # 将ScoringRulesTable的frame放到正确的位置
            self.scoring_rules_table.frame.grid(
                row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10)
            )
            current_row += 1

            # 创建新的"+ 添加评分规则"按钮（使用ScoringRulesTable的add_row方法）
            add_rule_button = ttk.Button(
                button_frame,
                text="+ 添加评分规则",
                command=self.scoring_rules_table.add_row,
                width=20
            )
            add_rule_button.pack(side=tk.LEFT, padx=5)

            # "添加"和"取消"按钮
            add_button = ttk.Button(
                button_frame,
                text="添加",
                command=self.add_evaluator,
                width=15
            )
            add_button.pack(side=tk.LEFT, padx=5)

            cancel_button = ttk.Button(
                button_frame,
                text="取消",
                command=self.window.destroy,
                width=15
            )
            cancel_button.pack(side=tk.LEFT, padx=5)

            # 说明文本
            info_text = """说明：
1. 选择评估框架为"自定义"
2. 填写评分规则（至少2条）
3. 分数不能重复（0-1之间的浮点数）
4. 每条规则包含分数和对应的评分标准
5. 系统将根据规则自动生成评估Prompt"""

        elif self._needs_criteria(metric_type):
            # 恢复阈值标签文本
            self.threshold_label.config(text="阈值 (0-1):")

            # 显示criteria
            self.criteria_frame.grid(in_=self.dynamic_content_frame, row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            current_row += 1

            # 按钮行
            button_frame = ttk.Frame(self.dynamic_content_frame)
            button_frame.grid(row=current_row, column=0, sticky=tk.W, pady=(0, 10))
            current_row += 1

            # "添加"和"取消"按钮
            add_button = ttk.Button(
                button_frame,
                text="添加",
                command=self.add_evaluator,
                width=15
            )
            add_button.pack(side=tk.LEFT, padx=5)

            cancel_button = ttk.Button(
                button_frame,
                text="取消",
                command=self.window.destroy,
                width=15
            )
            cancel_button.pack(side=tk.LEFT, padx=5)

            # 预填充默认prompt（如果有的话）
            default_criteria = self._get_default_criteria(metric_type)
            if default_criteria and not self.criteria_text.get(1.0, tk.END).strip():
                self.criteria_text.insert(1.0, default_criteria)

            # 说明文本
            info_text = """说明：
1. 选择评估框架（Ragas 或 DeepEval）
2. 根据框架选择对应的评估器类型
3. 设置评估器的阈值（0-1之间）
4. 填写评估标准，定义评估规则
5. 评估器将保存到配置文件中"""

        else:
            # 恢复阈值标签文本
            self.threshold_label.config(text="阈值 (0-1):")

            # 按钮行
            button_frame = ttk.Frame(self.dynamic_content_frame)
            button_frame.grid(row=current_row, column=0, sticky=tk.W, pady=(0, 10))
            current_row += 1

            # "添加"和"取消"按钮
            add_button = ttk.Button(
                button_frame,
                text="添加",
                command=self.add_evaluator,
                width=15
            )
            add_button.pack(side=tk.LEFT, padx=5)

            cancel_button = ttk.Button(
                button_frame,
                text="取消",
                command=self.window.destroy,
                width=15
            )
            cancel_button.pack(side=tk.LEFT, padx=5)

            # 说明文本
            info_text = """说明：
1. 选择评估框架（Ragas 或 DeepEval）
2. 根据框架选择对应的评估器类型
3. 设置评估器的阈值（0-1之间）
4. 评估器将保存到配置文件中"""

        # 说明文本（始终在最后）
        info_label = ttk.Label(
            self.dynamic_content_frame,
            text=info_text,
            font=font_manager.panel_font(),
            justify=tk.LEFT,
            foreground="gray"
        )
        info_label.grid(row=current_row, column=0, sticky=tk.W, pady=(20, 0))

        # 调整窗口大小
        self.window.update_idletasks()

    def on_framework_change(self):
        """框架选择改变时的回调"""
        framework = self.framework_var.get()

        # 根据框架显示/隐藏对话模式选项
        if framework == "custom":
            # 自定义框架:显示对话模式选项
            self.turn_mode_label.grid()
            self.turn_mode_frame.grid()
        else:
            # Ragas和DeepEval:隐藏对话模式选项,默认为单轮
            self.turn_mode_label.grid_remove()
            self.turn_mode_frame.grid_remove()
            self.turn_mode_var.set("single")  # 强制设置为单轮

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
                "Conversation Completeness",  # 新增
                "GEval (Custom)"
            ]
        elif framework == "custom":
            # 自定义框架只有一个类型，自动选中
            self.metric_combo['values'] = ["规则评分"]
            self.metric_type_var.set("规则评分")
        else:
            self.metric_combo['values'] = ["请先选择评估框架"]

        # 清空当前选择（只有非custom框架才清空）
        if framework != "custom":
            self.metric_type_var.set("")

        # 重新渲染下方内容
        self._render_lower_section()

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
            # 自定义框架不做范围校验，其他框架校验0-1
            if framework != "custom":
                if not 0 <= threshold_float <= 1:
                    raise ValueError("阈值必须在 0-1 之间")
        except ValueError as e:
            if framework == "custom":
                messagebox.showerror("错误", "阈值必须是数字")
            else:
                messagebox.showerror("错误", str(e))
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
            "threshold": threshold_float,
            "turn_mode": self.turn_mode_var.get()  # 添加对话模式
        }

        # 如果是自定义框架，获取评分规则
        if framework == "custom" and metric_type == "规则评分":
            try:
                scoring_rules = self.scoring_rules_table.get_rules()
                evaluator_config["scoring_rules"] = scoring_rules
            except ValueError as e:
                messagebox.showerror("错误", f"评分规则数据不合法:\n{str(e)}")
                return

        # 如果是DeepEval/Ragas的自定义类型，获取criteria
        elif self._needs_criteria(metric_type):
            criteria = self.criteria_text.get(1.0, tk.END).strip()
            if not criteria:
                messagebox.showerror("错误", f"{metric_type} 需要填写评估标准")
                return
            evaluator_config["criteria"] = criteria

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

    def on_metric_type_change(self, event):
        """评估器类型选择改变时的回调"""
        # 重新渲染下方内容
        self._render_lower_section()

    def _needs_criteria(self, metric_type: str) -> bool:
        """判断是否需要自定义criteria"""
        needs_criteria_types = [
            "Conversation Completeness",
            "对话完整性",
            "Role Adherence",
            "角色遵循",
            "Correctness",
            "正确性",
            "GEval (Custom)",
            "Custom"
        ]
        return any(mt in metric_type for mt in needs_criteria_types)

    def _get_default_criteria(self, metric_type: str) -> str:
        """获取默认的评估标准（用于预填充）"""
        # 这里暂时返回空，让用户自己填写
        # 或者可以从executor中获取默认值
        return ""

    def _adjust_text_height(self, event=None):
        """动态调整Text组件高度（基于视觉行数，包括自动换行）"""
        if not self.criteria_text:
            return

        # 获取文本内容
        content = self.criteria_text.get(1.0, tk.END).strip()

        # 让Tkinter重新计算布局
        self.criteria_text.update_idletasks()

        # 获取基于实际显示的行数（包括自动换行）
        try:
            line_count = int(self.criteria_text.index('end-1c').split('.')[0])
        except:
            line_count = content.count('\n') + 1  # 降级方案

        # 计算新高度：最少2行
        new_height = max(2, line_count)

        # 如果高度有变化，更新
        current_height = int(self.criteria_text.cget('height'))
        if new_height != current_height:
            self.criteria_text.config(height=new_height)

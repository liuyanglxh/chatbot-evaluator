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
        self.evaluator_id_map = {}  # 存储item_id到evaluator_id的映射

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

        # 绑定双击事件
        self.tree.bind("<Double-Button-1>", self._on_double_click)

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

        # 清空映射
        self.evaluator_id_map.clear()

        # 加载评估器
        evaluators = self.config_manager.get_evaluators()

        # 插入数据
        for evaluator in evaluators:
            item_id = self.tree.insert(
                "",
                tk.END,
                values=(
                    evaluator.get("name", ""),
                    evaluator.get("framework", ""),
                    evaluator.get("metric_type", ""),
                    evaluator.get("threshold", "")
                )
            )
            # 存储ID映射
            self.evaluator_id_map[item_id] = evaluator.get("id", "")

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

        # 获取选中项的信息
        item = self.tree.item(selection[0])
        name = item['values'][0]

        # 获取评估器ID
        evaluator_id = self.evaluator_id_map.get(selection[0])

        if not evaluator_id:
            messagebox.showerror("错误", "无法获取评估器ID")
            return

        # 确认删除
        result = messagebox.askyesno(
            "确认删除",
            f"确定要删除评估器 '{name}' 吗？"
        )

        if result:
            success = self.config_manager.remove_evaluator(evaluator_id)

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

    def _on_double_click(self, event):
        """双击事件处理"""
        selection = self.tree.selection()

        if not selection:
            return

        # 获取选中项的ID
        evaluator_id = self.evaluator_id_map.get(selection[0])

        if not evaluator_id:
            messagebox.showerror("错误", "无法获取评估器ID")
            return

        # 打开详情弹窗（传递ID）
        EvaluatorDetailPopup(self.window, evaluator_id, self.config_manager, self.load_evaluators)


class EvaluatorDetailPopup:
    """评估器详情弹窗"""

    def __init__(self, parent, evaluator_id, config_manager, refresh_callback):
        self.config_manager = config_manager
        self.evaluator_id = evaluator_id  # 保存ID（用户不可见）
        self.refresh_callback = refresh_callback

        # 加载评估器数据
        self.evaluator_data = self._load_evaluator_data()

        # 创建弹窗
        evaluator_name = self.evaluator_data.get("name", "未知")
        self.window = tk.Toplevel(parent)
        self.window.title(f"评估器详情 - {evaluator_name}")
        self.window.geometry("700x650")
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
        # Windows/macOS
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """鼠标滚轮事件处理"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _load_evaluator_data(self):
        """加载评估器数据（根据ID）"""
        evaluators = self.config_manager.get_evaluators()

        for evaluator in evaluators:
            if evaluator.get("id") == self.evaluator_id:
                return evaluator

        return None

    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text=f"📝 评估器详情",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 评估器名称
        ttk.Label(main_frame, text="评估器名称:", font=("Arial", 11, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=10
        )
        self.name_var = tk.StringVar(value=self.evaluator_data.get("name", ""))
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=50, font=("Arial", 11))
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)

        # 框架
        ttk.Label(main_frame, text="评估框架:", font=("Arial", 11, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=10
        )
        self.framework_var = tk.StringVar(value=self.evaluator_data.get("framework", ""))
        framework_entry = ttk.Entry(main_frame, textvariable=self.framework_var, width=50, font=("Arial", 11))
        framework_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)
        framework_entry.config(state=tk.DISABLED)  # 框架不可修改

        # 评估器类型
        ttk.Label(main_frame, text="评估器类型:", font=("Arial", 11, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=10
        )
        self.metric_type_var = tk.StringVar(value=self.evaluator_data.get("metric_type", ""))
        metric_type_entry = ttk.Entry(main_frame, textvariable=self.metric_type_var, width=50, font=("Arial", 11))
        metric_type_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=10)
        metric_type_entry.config(state=tk.DISABLED)  # 类型不可修改

        # 阈值
        ttk.Label(main_frame, text="阈值:", font=("Arial", 11, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=10
        )
        self.threshold_var = tk.StringVar(value=str(self.evaluator_data.get("threshold", "")))
        threshold_entry = ttk.Entry(main_frame, textvariable=self.threshold_var, width=50, font=("Arial", 11))
        threshold_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=10)

        # 评估标准（如果有）
        criteria = self.evaluator_data.get("criteria", "")
        if criteria:
            ttk.Label(main_frame, text="评估标准:", font=("Arial", 11, "bold")).grid(
                row=5, column=0, sticky=tk.NW, pady=10
            )

            # 创建Text组件（初始height=5，会根据内容自动调整）
            self.criteria_text = tk.Text(
                main_frame,
                font=("Arial", 11),
                height=5,
                wrap=tk.WORD,
                relief=tk.RIDGE,
                padx=10,
                pady=10
            )
            self.criteria_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

            # 先插入内容
            self.criteria_text.insert(1.0, criteria)

            # 立即根据内容调整初始高度
            self.window.update_idletasks()  # 确保内容已渲染
            self._adjust_text_height()

            # 绑定KeyRelease事件，动态调整高度
            self.criteria_text.bind("<KeyRelease>", self._adjust_text_height)
        else:
            # 如果没有criteria，添加一个占位符
            self.criteria_text = None

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(30, 10), sticky=(tk.E))

        # 保存按钮
        save_button = ttk.Button(
            button_frame,
            text="💾 保存修改",
            command=self.save_changes,
            width=15
        )
        save_button.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="✖ 取消",
            command=self.window.destroy,
            width=15
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

        # 配置grid权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def _adjust_text_height(self, event=None):
        """动态调整Text组件高度"""
        if not self.criteria_text:
            return

        # 获取文本内容
        content = self.criteria_text.get(1.0, tk.END)
        lines = content.count('\n') + 1  # 计算行数

        # 计算新高度：最少5行，超过2行后 = 行数 + 3
        if lines <= 2:
            new_height = 5
        else:
            new_height = lines + 3

        # 如果高度有变化，更新
        current_height = int(self.criteria_text.cget('height'))
        if new_height != current_height:
            self.criteria_text.config(height=new_height)

    def save_changes(self):
        """保存修改"""
        try:
            # 获取新的值
            new_name = self.name_var.get().strip()
            new_threshold = self.threshold_var.get().strip()

            # 验证
            if not new_name:
                messagebox.showerror("错误", "评估器名称不能为空")
                return

            try:
                new_threshold = float(new_threshold)
                if not 0 <= new_threshold <= 1:
                    raise ValueError("阈值必须在0-1之间")
            except ValueError as e:
                messagebox.showerror("错误", f"阈值格式错误: {str(e)}")
                return

            # 获取新的criteria
            new_criteria = ""
            if self.criteria_text:
                new_criteria = self.criteria_text.get(1.0, tk.END).strip()

            # 构建更新后的评估器数据（保留原有ID）
            updated_data = {
                "id": self.evaluator_id,  # 保留原有ID，不创建新的
                "name": new_name,
                "framework": self.evaluator_data.get("framework"),
                "metric_type": self.evaluator_data.get("metric_type"),
                "threshold": new_threshold
            }

            # 如果有criteria，添加到数据中
            if new_criteria:
                updated_data["criteria"] = new_criteria

            # 使用update_evaluator方法更新（而不是删除重建）
            success = self.config_manager.update_evaluator(self.evaluator_id, updated_data)

            if success:
                messagebox.showinfo("成功", f"评估器 '{new_name}' 已更新")
                self.window.destroy()
                # 刷新列表
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("错误", "保存失败")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

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

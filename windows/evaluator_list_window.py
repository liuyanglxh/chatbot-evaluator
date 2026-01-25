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
from font_utils import font_manager
from windows.scoring_rules_table import ScoringRulesTable


from utils.window_helpers import bind_esc_key
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

        # 在界面完全创建后再绑定ESC键
        self.window.after(100, lambda: bind_esc_key(self.window))

    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="评估器列表",
            font=font_manager.panel_title_font()
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 工具栏
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # 刷新按钮
        refresh_button = ttk.Button(
            toolbar_frame,
            text="刷新",
            command=self.load_evaluators
        )
        refresh_button.grid(row=0, column=0, padx=(0, 10))

        # 使用按钮
        use_button = ttk.Button(
            toolbar_frame,
            text="✓ 使用选中",
            command=self.use_selected
        )
        use_button.grid(row=0, column=1, padx=(0, 10))

        # 删除按钮
        delete_button = ttk.Button(
            toolbar_frame,
            text="删除选中",
            command=self.delete_selected
        )
        delete_button.grid(row=0, column=2, padx=(0, 10))

        # 导出按钮
        export_button = ttk.Button(
            toolbar_frame,
            text="📤 导出评估器",
            command=self.export_evaluators
        )
        export_button.grid(row=0, column=3, padx=(0, 10))

        # 导入按钮
        import_button = ttk.Button(
            toolbar_frame,
            text="📥 导入评估器",
            command=self.import_evaluators
        )
        import_button.grid(row=0, column=4, padx=(0, 10))

        # 统计标签
        self.stats_label = ttk.Label(
            toolbar_frame,
            text="共 0 个评估器",
            font=font_manager.panel_font()
        )
        self.stats_label.grid(row=0, column=5, sticky=tk.W)

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

        # 应用字体设置和动态行高
        style = ttk.Style()
        row_height = font_manager.get_treeview_row_height()
        style.configure("EvaluatorList.Treeview",
                       font=font_manager.panel_font(),
                       rowheight=row_height)
        style.configure("EvaluatorList.Treeview.Heading", font=font_manager.panel_font_bold())
        self.tree.configure(style="EvaluatorList.Treeview")

        # 配置滚动条
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # 设置列
        self.tree.heading("name", text="评估器名称")
        self.tree.heading("framework", text="评估框架")
        self.tree.heading("metric_type", text="评估器类型")
        self.tree.heading("threshold", text="阈值")

        # 设置列宽 - 全部改为左对齐
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("framework", width=150, anchor=tk.W)
        self.tree.column("metric_type", width=300, anchor=tk.W)
        self.tree.column("threshold", width=100, anchor=tk.W)

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

    def _get_framework_display_name(self, framework: str) -> str:
        """获取框架的友好显示名称"""
        framework_map = {
            "deepeval": "DeepEval",
            "ragas": "Ragas",
            "custom": "自定义"
        }
        return framework_map.get(framework, framework)

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
            framework = evaluator.get("framework", "")
            framework_display = self._get_framework_display_name(framework)

            item_id = self.tree.insert(
                "",
                tk.END,
                values=(
                    evaluator.get("name", ""),
                    framework_display,
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

        # 显示加载动画
        loading_window = self._show_loading_window("正在加载评估器...")

        # 延迟执行加载操作，让UI有时间显示加载动画
        self.window.after(100, lambda: self._load_evaluator_with_loading(selection[0], loading_window))

    def _show_loading_window(self, message):
        """显示加载动画窗口"""
        loading = tk.Toplevel(self.window)
        loading.title("加载中")
        loading.geometry("350x150")
        loading.transient(self.window)
        loading.grab_set()
        loading.resizable(False, False)

        # 居中显示
        loading.update_idletasks()
        width = loading.winfo_width()
        height = loading.winfo_height()
        screen_width = loading.winfo_screenwidth()
        screen_height = loading.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        loading.geometry(f'{width}x{height}+{x}+{y}')

        # 创建内容
        frame = ttk.Frame(loading, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 加载图标（使用Unicode字符模拟动画）
        self.loading_label = ttk.Label(
            frame,
            text="⏳",
            font=("Arial", 36),
            anchor=tk.CENTER
        )
        self.loading_label.pack(pady=(10, 20))

        # 加载文字
        label = ttk.Label(
            frame,
            text=message,
            font=("Arial", 11),
            anchor=tk.CENTER
        )
        label.pack()

        # 启动动画
        self._animate_loading(loading)

        return loading

    def _animate_loading(self, window):
        """加载动画"""
        loading_chars = ["⏳", "⌛", "⏳"]
        if not window.winfo_exists():
            return

        current_char = getattr(self, '_loading_char_index', 0)
        self.loading_label.config(text=loading_chars[current_char])
        self._loading_char_index = (current_char + 1) % len(loading_chars)

        # 继续动画
        window.after(500, lambda: self._animate_loading(window))

    def _load_evaluator_with_loading(self, selection_id, loading_window):
        """在显示加载动画的情况下加载评估器"""
        try:
            # 获取评估器ID
            evaluator_id = self.evaluator_id_map.get(selection_id)

            if not evaluator_id:
                loading_window.destroy()
                messagebox.showerror("错误", "无法获取评估器ID")
                return

            # 从配置中加载完整的评估器数据（包含scoring_rules等）
            evaluators = self.config_manager.get_evaluators()
            evaluator_data = None
            for evaluator in evaluators:
                if evaluator.get("id") == evaluator_id:
                    evaluator_data = evaluator
                    break

            if not evaluator_data:
                loading_window.destroy()
                messagebox.showerror("错误", "无法加载评估器数据")
                return

            # 使用完整的评估器数据
            evaluator_info = evaluator_data

            # 关闭加载窗口
            if loading_window.winfo_exists():
                loading_window.destroy()

            # 打开评估执行窗口
            from windows.evaluation_execution_window import EvaluationExecutionWindow
            EvaluationExecutionWindow(self.window, evaluator_info)

        except Exception as e:
            if loading_window.winfo_exists():
                loading_window.destroy()
            messagebox.showerror("错误", f"加载评估器失败: {str(e)}")

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

    def export_evaluators(self):
        """导出评估器到JSON文件"""
        try:
            import json
            from tkinter import filedialog

            # 获取所有评估器
            evaluators = self.config_manager.get_evaluators()

            if not evaluators:
                messagebox.showwarning("警告", "当前没有可导出的评估器")
                return

            # 打开保存文件对话框
            file_path = filedialog.asksaveasfilename(
                title="导出评估器",
                defaultextension=".json",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ],
                initialfile="evaluators_export.json"
            )

            if not file_path:
                return  # 用户取消了选择

            # 导出数据
            export_data = {
                "version": "1.0",
                "description": "LLM评估工具 - 评估器导出文件",
                "evaluators": evaluators
            }

            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("成功", f"已成功导出 {len(evaluators)} 个评估器到:\n{file_path}")

        except Exception as e:
            messagebox.showerror("错误", f"导出失败:\n{str(e)}")

    def import_evaluators(self):
        """从JSON文件导入评估器"""
        try:
            import json
            from tkinter import filedialog

            # 打开选择文件对话框
            file_path = filedialog.askopenfilename(
                title="导入评估器",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("所有文件", "*.*")
                ]
            )

            if not file_path:
                return  # 用户取消了选择

            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            # 验证文件格式
            if "evaluators" not in import_data:
                messagebox.showerror("错误", "文件格式不正确：缺少 'evaluators' 字段")
                return

            evaluators_to_import = import_data["evaluators"]

            if not evaluators_to_import:
                messagebox.showwarning("警告", "文件中没有可导入的评估器")
                return

            # 统计信息
            total_count = len(evaluators_to_import)
            skipped_count = 0
            imported_count = 0
            duplicate_names = []

            # 导入每个评估器
            for evaluator in evaluators_to_import:
                # 检查是否已存在同名评估器
                existing_evaluators = self.config_manager.get_evaluators()
                name_exists = any(
                    e.get("name", "") == evaluator.get("name", "")
                    for e in existing_evaluators
                )

                if name_exists:
                    skipped_count += 1
                    duplicate_names.append(evaluator.get("name", "未知"))
                else:
                    # 添加评估器（add_evaluator会自动生成新ID）
                    self.config_manager.add_evaluator(evaluator)
                    imported_count += 1

            # 显示导入结果
            result_message = f"导入完成！\n\n"
            result_message += f"总数：{total_count} 个\n"
            result_message += f"成功导入：{imported_count} 个\n"
            result_message += f"跳过（已存在）：{skipped_count} 个"

            if duplicate_names:
                result_message += f"\n\n跳过的评估器：\n- " + "\n- ".join(duplicate_names)

            messagebox.showinfo("导入结果", result_message)

            # 刷新列表
            self.load_evaluators()

        except json.JSONDecodeError:
            messagebox.showerror("错误", "文件格式错误：不是有效的JSON文件")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败:\n{str(e)}")



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

        # 动态计算窗口大小，根据字体大小调整
        font_size = font_manager.get_panel_font_size()
        # 基础大小 700x700，字体每增加1号，宽度和高度增加（增加了对话模式选项，需要更多空间）
        base_width = 700
        base_height = 700
        scale_factor = (font_size - 11) * 0.08  # 11号是基准
        window_width = int(base_width * (1 + max(0, scale_factor)))
        window_height = int(base_height * (1 + max(0, scale_factor)))
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.transient(parent)
        self.window.grab_set()

        # 创建滚动容器
        self.create_scrollable_container()

        # 创建界面
        self.create_interface()

        # 居中显示
        self.center_window()

        # 在界面完全创建后再绑定ESC键
        self.window.after(100, lambda: bind_esc_key(self.window))

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

    def _get_framework_display_name(self, framework: str) -> str:
        """获取框架的友好显示名称"""
        framework_map = {
            "deepeval": "DeepEval",
            "ragas": "Ragas",
            "custom": "自定义"
        }
        return framework_map.get(framework, framework)

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

    def create_interface(self):
        """创建界面"""
        # 动态计算padding，根据字体大小调整
        font_size = font_manager.get_panel_font_size()
        padding = max(20, int(font_size * 1.5))  # 字体越大，padding越大

        # 主框架
        main_frame = ttk.Frame(self.scrollable_frame, padding=padding)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text=f"📝 评估器详情",
            font=font_manager.panel_title_font()
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 获取框架和类型
        framework = self.evaluator_data.get("framework", "")
        metric_type = self.evaluator_data.get("metric_type", "")

        # 评估器名称
        ttk.Label(main_frame, text="评估器名称:", font=font_manager.panel_font_bold()).grid(
            row=1, column=0, sticky=tk.W, pady=10
        )
        self.name_var = tk.StringVar(value=self.evaluator_data.get("name", ""))
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=font_manager.get_entry_width(50), font=font_manager.panel_font())
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)
        # 添加必填标记
        ttk.Label(main_frame, text="*必填", foreground="red", font=font_manager.panel_font_small()).grid(
            row=1, column=2, sticky=tk.W, padx=(5, 0), pady=10
        )

        # 框架
        ttk.Label(main_frame, text="评估框架:", font=font_manager.panel_font_bold()).grid(
            row=2, column=0, sticky=tk.W, pady=10
        )
        framework_display = self._get_framework_display_name(framework)
        self.framework_var = tk.StringVar(value=framework_display)
        framework_entry = ttk.Entry(main_frame, textvariable=self.framework_var, width=font_manager.get_entry_width(50), font=font_manager.panel_font())
        framework_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)
        framework_entry.config(state=tk.DISABLED)  # 框架不可修改

        # 评估器类型
        ttk.Label(main_frame, text="评估器类型:", font=font_manager.panel_font_bold()).grid(
            row=3, column=0, sticky=tk.W, pady=10
        )
        self.metric_type_var = tk.StringVar(value=metric_type)
        metric_type_entry = ttk.Entry(main_frame, textvariable=self.metric_type_var, width=font_manager.get_entry_width(50), font=font_manager.panel_font())
        metric_type_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=10)
        metric_type_entry.config(state=tk.DISABLED)  # 类型不可修改

        # 对话模式（单轮/多轮）
        self.turn_mode_label = ttk.Label(main_frame, text="对话模式:", font=font_manager.panel_font_bold())
        self.turn_mode_label.grid(row=4, column=0, sticky=tk.W, pady=10)

        # 对话模式容器
        self.turn_mode_frame = ttk.Frame(main_frame)
        self.turn_mode_frame.grid(row=4, column=1, sticky=tk.W, pady=10)

        # 获取当前turn_mode，默认为single
        current_turn_mode = self.evaluator_data.get("turn_mode", "single")
        self.turn_mode_var = tk.StringVar(value=current_turn_mode)

        # 单选按钮
        ttk.Radiobutton(
            self.turn_mode_frame,
            text="单轮对话（每个测试数据单独评估）",
            variable=self.turn_mode_var,
            value="single"
        ).pack(anchor=tk.W)

        ttk.Radiobutton(
            self.turn_mode_frame,
            text="多轮对话（评估完整的多轮对话）",
            variable=self.turn_mode_var,
            value="multi"
        ).pack(anchor=tk.W)

        # 根据框架显示/隐藏对话模式选项
        if framework != "custom":
            # Ragas和DeepEval:隐藏对话模式选项
            self.turn_mode_label.grid_remove()
            self.turn_mode_frame.grid_remove()

        # 阈值（标签根据框架动态显示）
        if framework == "custom":
            threshold_label_text = "阈值:"
        else:
            threshold_label_text = "阈值 (0-1):"

        ttk.Label(main_frame, text=threshold_label_text, font=font_manager.panel_font_bold()).grid(
            row=5, column=0, sticky=tk.W, pady=10
        )
        self.threshold_var = tk.StringVar(value=str(self.evaluator_data.get("threshold", "")))
        threshold_entry = ttk.Entry(main_frame, textvariable=self.threshold_var, width=font_manager.get_entry_width(50), font=font_manager.panel_font())
        threshold_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=10)

        # 评估标准（如果有需要）
        self.criteria_text = None
        self.criteria_frame = ttk.Frame(main_frame)

        # 评分规则表格（用于自定义框架）
        self.scoring_rules_frame = ttk.Frame(main_frame)

        # 根据框架和类型决定显示什么
        if framework == "custom" and metric_type == "规则评分":
            # 显示评分规则表格
            ttk.Label(self.scoring_rules_frame, text="评分规则:", font=font_manager.panel_font_bold()).grid(
                row=0, column=0, sticky=tk.NW, pady=10
            )

            # 按钮行（放在评分规则标签下面）
            button_frame = ttk.Frame(self.scoring_rules_frame)
            button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

            # 创建评分规则表格组件
            self.scoring_rules_table = ScoringRulesTable(self.scoring_rules_frame)

            # "+ 添加评分规则"按钮（直接创建新的按钮）
            add_rule_button = ttk.Button(
                button_frame,
                text="+ 添加评分规则",
                command=self.scoring_rules_table.add_row,
                width=20
            )
            add_rule_button.pack(side=tk.LEFT, padx=5)

            # "保存修改"和"取消"按钮
            save_button = ttk.Button(
                button_frame,
                text="💾 保存修改",
                command=self.save_changes
            )
            save_button.pack(side=tk.LEFT, padx=5)

            cancel_button = ttk.Button(
                button_frame,
                text="✖ 取消",
                command=self.window.destroy
            )
            cancel_button.pack(side=tk.LEFT, padx=5)

            # 加载现有规则
            scoring_rules = self.evaluator_data.get("scoring_rules", [])
            if scoring_rules:
                # 清空默认的2行
                self.scoring_rules_table.rows.clear()
                for widget in self.scoring_rules_table.rows_frame.winfo_children():
                    widget.destroy()

                # 添加现有规则
                for rule in scoring_rules:
                    self.scoring_rules_table.add_row(
                        score_value=str(rule['score']),
                        desc_value=rule['description']
                    )
            else:
                # 如果没有规则，保持默认的2个空行
                pass

            self.scoring_rules_table.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

            # 配置grid权重
            self.scoring_rules_frame.columnconfigure(0, weight=1)

            # 显示评分规则框架（row=6, 在阈值下面）
            self.scoring_rules_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        elif self._needs_criteria(metric_type):
            # 显示criteria输入框
            criteria = self.evaluator_data.get("criteria", "")

            ttk.Label(self.criteria_frame, text="评估标准:", font=font_manager.panel_font_bold()).grid(
                row=0, column=0, sticky=tk.NW, pady=10
            )

            # 创建Text组件
            self.criteria_text = tk.Text(
                self.criteria_frame,
                font=font_manager.panel_font(),
                height=5,
                wrap=tk.WORD,
                relief=tk.RIDGE,
                padx=10,
                pady=10
            )
            self.criteria_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

            # 插入内容
            if criteria:
                self.criteria_text.insert(1.0, criteria)

            # 立即根据内容调整初始高度
            self.window.update_idletasks()
            self._adjust_text_height()

            # 绑定KeyRelease事件，动态调整高度
            self.criteria_text.bind("<KeyRelease>", self._adjust_text_height)

            # 配置grid权重
            self.criteria_frame.columnconfigure(0, weight=1)

            # 显示criteria框架（row=5）
            self.criteria_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # 说明文本 - 动态计算row位置
        info_text = self._get_info_text(framework, metric_type)
        info_label = ttk.Label(
            main_frame,
            text=info_text,
            font=font_manager.panel_font_small(),
            justify=tk.LEFT,
            foreground="gray"
        )

        # 根据框架和类型决定说明文本的row位置
        if framework == "custom" and metric_type == "规则评分":
            # 自定义规则评分:评分规则框架在row=6,说明在row=7
            info_label.grid(row=7, column=0, columnspan=3, pady=(20, 10))
        else:
            # 其他情况:说明在row=6
            info_label.grid(row=6, column=0, columnspan=3, pady=(20, 10))

        # 按钮区域 - 动态计算row位置
        if not (framework == "custom" and metric_type == "规则评分"):
            # 非自定义规则评分:说明在row=6,按钮在row=7
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=7, column=0, columnspan=3, pady=(30, 10), sticky=(tk.E))

            # 保存按钮
            save_button = ttk.Button(
                button_frame,
                text="💾 保存修改",
                command=self.save_changes
            )
            save_button.pack(side=tk.LEFT, padx=5)

            # 取消按钮
            cancel_button = ttk.Button(
                button_frame,
                text="✖ 取消",
                command=self.window.destroy
            )
            cancel_button.pack(side=tk.LEFT, padx=5)

        # 配置grid权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def _get_info_text(self, framework: str, metric_type: str) -> str:
        """获取说明文本"""
        if framework == "custom" and metric_type == "规则评分":
            return """说明：
1. 这是自定义评估器，基于评分规则进行评估
2. 评分规则至少需要2条
3. 分数不能重复
4. 系统将根据规则自动生成评估Prompt"""
        elif self._needs_criteria(metric_type):
            return """说明：
1. 这是自定义评估标准
2. 评估标准已保存
3. 可以修改标准和阈值"""
        else:
            return """说明：
1. 这是标准评估器
2. 可以修改阈值"""

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
            framework = self.evaluator_data.get("framework", "")
            metric_type = self.evaluator_data.get("metric_type", "")

            # 验证必填项
            if not new_name:
                messagebox.showerror("错误", "评估器名称不能为空")
                return

            # 验证阈值
            try:
                new_threshold = float(new_threshold)
                # 自定义框架不做范围校验，其他框架校验0-1
                if framework != "custom":
                    if not 0 <= new_threshold <= 1:
                        raise ValueError("阈值必须在0-1之间")
            except ValueError as e:
                if framework == "custom":
                    messagebox.showerror("错误", "阈值必须是数字")
                else:
                    messagebox.showerror("错误", f"阈值格式错误: {str(e)}")
                return

            # 构建更新后的评估器数据（保留原有ID）
            updated_data = {
                "id": self.evaluator_id,  # 保留原有ID，不创建新的
                "name": new_name,
                "framework": framework,
                "metric_type": metric_type,
                "threshold": new_threshold,
                "turn_mode": self.turn_mode_var.get()  # 添加对话模式
            }

            # 如果是自定义框架，获取评分规则
            if framework == "custom" and metric_type == "规则评分":
                try:
                    scoring_rules = self.scoring_rules_table.get_rules()
                    updated_data["scoring_rules"] = scoring_rules
                except ValueError as e:
                    messagebox.showerror("错误", f"评分规则数据不合法:\n{str(e)}")
                    return

            # 如果是DeepEval/Ragas的自定义类型，获取criteria
            elif self._needs_criteria(metric_type):
                new_criteria = ""
                if self.criteria_text:
                    new_criteria = self.criteria_text.get(1.0, tk.END).strip()

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

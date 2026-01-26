"""
评估执行窗口
执行单个评估器的评估任务
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_manager import ConfigManager
from evaluators import get_executor
from font_utils import font_manager
from windows.conversation_turns_editor import ConversationTurnsEditor
from utils.window_helpers import bind_esc_key


def format_number(value):
    """
    智能格式化数字：如果是整数就显示整数，否则保留原样

    Args:
        value: 数字值（int或float）

    Returns:
        str: 格式化后的字符串
    """
    if value == int(value):
        return str(int(value))
    else:
        # 保留最多3位小数，但去掉末尾的0
        formatted = f"{value:.3f}".rstrip('0').rstrip('.')
        return formatted


class EvaluationExecutionWindow:
    """评估执行窗口"""

    def __init__(self, parent, evaluator_info):
        self.evaluator_info = evaluator_info
        self.config_manager = ConfigManager()

        # 创建新窗口
        self.window = tk.Toplevel(parent)
        self.window.title(f"执行评估 - {evaluator_info['name']}")
        self.window.geometry("900x750")
        self.window.transient(parent)
        self.window.grab_set()

        # 绑定ESC键关闭
        bind_esc_key(self.window)

        # 创建界面
        self.create_interface()

        # 居中显示
        self.center_window()

    def create_interface(self):
        """创建界面"""
        # 创建全局滚动容器
        canvas_container = ttk.Frame(self.window)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        # Canvas和滚动条
        self.main_canvas = tk.Canvas(canvas_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        # 主框架(放在Canvas里)
        main_frame = ttk.Frame(self.main_canvas, padding="20")
        self.main_canvas.create_window((0, 0), window=main_frame, anchor="nw")

        # 布局
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 配置滚动区域
        main_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        # 绑定鼠标滚轮
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.main_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.main_canvas.bind_all("<Button-5>", self._on_mousewheel)

        # 标题（显示评估器信息）
        title_text = f"评估器：{self.evaluator_info['name']}"
        subtitle_text = f"框架：{self.evaluator_info['framework']} | 类型：{self.evaluator_info['metric_type']} | 阈值：{self.evaluator_info['threshold']}"

        title_label = ttk.Label(
            main_frame,
            text=title_text,
            font=font_manager.panel_title_font()
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))

        subtitle_label = ttk.Label(
            main_frame,
            text=subtitle_text,
            font=font_manager.panel_font_small(),
            foreground="gray"
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="输入数据", padding="10")
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # 测试数据选择
        selection_frame = ttk.Frame(input_frame)
        selection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 第一行：标签和下拉框
        row1_frame = ttk.Frame(selection_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(
            row1_frame,
            text="📚 选择测试数据:",
            font=font_manager.panel_font_small()
        ).pack(side=tk.LEFT, padx=(0, 10))

        # 分组筛选
        ttk.Label(
            row1_frame,
            text="🏷️ 分组:",
            font=font_manager.panel_font_small()
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.group_filter_combo = ttk.Combobox(
            row1_frame,
            width=font_manager.get_entry_width(15),
            font=font_manager.panel_font_small(),
            state="readonly"
        )
        self.group_filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.group_filter_combo.bind("<<ComboboxSelected>>", self._on_group_filter_changed)

        # 测试数据下拉框
        self.test_data_combo = ttk.Combobox(
            row1_frame,
            width=font_manager.get_entry_width(25),
            font=font_manager.panel_font_small()
        )
        self.test_data_combo.pack(side=tk.LEFT, padx=(0, 10))

        # 绑定选择事件（选择后自动加载）
        self.test_data_combo.bind("<<ComboboxSelected>>", self._on_test_data_selected)

        # 第二行：批量测试、执行评估、清空按钮
        row2_frame = ttk.Frame(selection_frame)
        row2_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            row2_frame,
            text="📋 批量测试",
            command=self.open_batch_test
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            row2_frame,
            text="▶ 执行评估",
            command=self.execute_evaluation,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            row2_frame,
            text="💾 保存修改",
            command=self.save_test_data,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            row2_frame,
            text="🗑 清空",
            command=self.clear_inputs,
            width=15
        ).pack(side=tk.LEFT)

        # 对话轮次容器（使用可编辑组件）
        self.turns_editor = ConversationTurnsEditor(
            input_frame,
            editable=True,
            on_change=None  # 暂时不需要变化回调
        )
        self.turns_editor.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # 加载分组选项
        self._load_groups()
        # 加载测试数据
        self._load_test_data()

        # 配置input_frame的网格权重，使轮次编辑器可以扩展
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)

        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

    def clear_inputs(self):
        """清空输入"""
        # 使用ConversationTurnsEditor清空内容
        self.turns_editor.clear()

    def save_test_data(self):
        """保存修改的测试数据"""
        # 检查是否选择了测试数据
        selected_name = self.test_data_combo.get()

        if not selected_name or selected_name == "请选择测试数据":
            messagebox.showerror("错误", "请先选择要保存的测试数据")
            return

        # 获取当前编辑的轮次数据
        turns = self.turns_editor.get_turns()

        # 验证数据
        if not turns:
            messagebox.showerror("错误", "至少需要一轮对话")
            return

        for i, turn in enumerate(turns, 1):
            question = turn.get('question', '').strip()
            answer = turn.get('answer', '').strip()

            if not question:
                messagebox.showerror("错误", f"第{i}轮的问题不能为空")
                return
            if not answer:
                messagebox.showerror("错误", f"第{i}轮的回答不能为空")
                return

        # 获取原始测试数据（保留ID和分组信息）
        test_data = self.config_manager.get_test_data_by_name(selected_name)

        if not test_data:
            messagebox.showerror("错误", "未找到测试数据")
            return

        # 更新数据
        updated_data = {
            "id": test_data.get("id"),  # 保留原有ID
            "name": test_data.get("name"),  # 不允许修改名称
            "group": test_data.get("group", ""),  # 保留原有分组
            "turns": turns
        }

        # 保存到配置
        success = self.config_manager.update_test_data(test_data.get("id"), updated_data)

        if success:
            messagebox.showinfo("成功", f"测试数据 '{selected_name}' 已保存")
        else:
            messagebox.showerror("错误", "保存失败")

    def _on_mousewheel(self, event):
        """鼠标滚轮事件处理 - 滚动整个窗口"""
        try:
            # 检查Canvas是否还存在
            if not self.main_canvas.winfo_exists():
                return

            # 检查鼠标是否在下拉框内
            focused_widget = self.window.focus_get()
            if focused_widget in [self.group_filter_combo, self.test_data_combo]:
                # 如果焦点在下拉框上,不滚动窗口
                return
        except (KeyError, AttributeError):
            # 如果获取焦点失败(比如下拉框弹出列表),忽略错误,继续滚动
            pass

        # Windows/macOS: event.delta
        # Linux: event.num (4=up, 5=down)
        try:
            if event.num == 5 or event.delta < 0:
                self.main_canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                self.main_canvas.yview_scroll(-1, "units")
        except tk.TclError:
            # Canvas已被销毁,忽略错误
            pass

    def _load_groups(self):
        """加载分组选项到筛选下拉框"""
        groups = self.config_manager.get_test_groups()
        group_names = ["全部"] + [g["name"] for g in groups]
        self.group_filter_combo['values'] = group_names
        self.group_filter_combo.current(0)
        self.current_group_filter = "全部"

    def _on_group_filter_changed(self, event):
        """分组筛选改变事件"""
        selected_group = self.group_filter_combo.get()
        self.current_group_filter = selected_group
        self._load_test_data()  # 重新加载测试数据

    def _load_test_data(self):
        """加载测试数据到下拉框（带分组筛选）"""
        test_data_list = self.config_manager.get_test_data_list()

        # 根据分组筛选
        if self.current_group_filter != "全部":
            test_data_list = [
                td for td in test_data_list
                if td.get('group', '') == self.current_group_filter
            ]

        test_data_names = [td['name'] for td in test_data_list]
        self.test_data_combo['values'] = test_data_names

        if test_data_names:
            self.test_data_combo.set('')  # 默认不选

    def _on_test_data_selected(self, event):
        """测试数据选择事件"""
        # 自动加载选中的测试数据
        self._load_selected_test_data()

    def _load_selected_test_data(self):
        """加载选中的测试数据（支持单轮和多轮，动态创建对话卡片）"""
        selected_name = self.test_data_combo.get()

        if not selected_name:
            return

        # 获取测试数据
        test_data = self.config_manager.get_test_data_by_name(selected_name)

        if not test_data:
            return

        # 检查是否有turns字段（新数据结构）
        if 'turns' in test_data and test_data['turns']:
            turns = test_data['turns']
        else:
            # 旧数据结构：转换为单个轮次
            turns = [{
                'question': test_data.get('question', ''),
                'answer': test_data.get('answer', ''),
                'context': test_data.get('context', '')
            }]

        # 使用ConversationTurnsEditor加载轮次
        self.turns_editor.load_turns(turns)

    def execute_evaluation(self):
        """执行评估"""
        # 从ConversationTurnsEditor获取数据
        turns = self.turns_editor.get_turns()

        if not turns:
            messagebox.showerror("错误", "请先选择测试数据")
            return

        # 验证至少有一轮完整数据
        first_turn = turns[0]
        question = first_turn.get('question', '').strip()
        answer = first_turn.get('answer', '').strip()

        if not question:
            messagebox.showerror("错误", "问题不能为空")
            return

        if not answer:
            messagebox.showerror("错误", "回答不能为空")
            return

        # 构造测试数据（模拟批量测试的数据格式）
        selected_name = self.test_data_combo.get()
        if selected_name and selected_name != "请选择测试数据":
            test_data_name = selected_name
        else:
            test_data_name = "手动输入的测试数据"

        test_data = {
            'name': test_data_name,
            'turns': turns
        }

        # 使用批量测试的执行逻辑（复用BatchEvaluationExecutor）
        BatchEvaluationExecutor(self.window, self.evaluator_info, [test_data], self.config_manager)

    def _create_loading_dialog(self):
        """创建加载弹窗"""
        dialog = tk.Toplevel(self.window)
        dialog.title("正在评估")
        dialog.geometry("400x150")
        dialog.transient(self.window)
        dialog.grab_set()

        # 绑定ESC键关闭
        bind_esc_key(dialog)

        # 居中显示
        dialog.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - 400) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 150) // 2
        dialog.geometry(f"400x150+{x}+{y}")

        # 内容
        frame = ttk.Frame(dialog, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)

        # 加载图标和文字
        ttk.Label(
            frame,
            text="⏳",
            font=("Arial", 36)
        ).pack(pady=(0, 10))

        ttk.Label(
            frame,
            text="正在执行评估，请稍候...",
            font=font_manager.panel_font()
        ).pack()

        return dialog

    def _execute_evaluation_thread(self, question, answer, context):
        """在后台线程中执行评估"""
        try:
            # 获取大模型配置
            model_settings = self.config_manager.get_model_settings()

            # 获取评估执行器
            executor = get_executor(self.evaluator_info)

            # 执行真实评估
            result = executor.execute(question, answer, context, model_settings)

            # 添加测试数据名称到结果中
            selected_name = self.test_data_combo.get()
            if selected_name and selected_name != "请选择测试数据":
                result['test_data_name'] = selected_name

            # 更新 UI
            self.window.after(0, self._update_result, result)

        except Exception as e:
            import traceback
            error_message = str(e)
            error_traceback = traceback.format_exc()

            # 显示错误弹窗
            self.window.after(0, self._show_error_dialog, error_message, error_traceback)

    def _show_error_dialog(self, error_message, error_traceback):
        """显示错误对话框"""
        # 判断错误类型
        is_translation_error = "翻译失败" in error_message
        dialog_title = "翻译失败" if is_translation_error else "评估失败"
        dialog_header = "翻译执行失败" if is_translation_error else "评估执行失败"

        # 创建弹窗
        dialog = tk.Toplevel(self.window)
        dialog.title(dialog_title)
        dialog.geometry("700x500")
        dialog.transient(self.window)
        dialog.grab_set()

        # 绑定ESC键关闭
        bind_esc_key(dialog)

        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 错误图标
        error_label = ttk.Label(
            main_frame,
            text="❌",
            font=("Arial", 48)
        )
        error_label.grid(row=0, column=0, pady=(0, 10))

        # 错误标题
        title_label = ttk.Label(
            main_frame,
            text=dialog_header,
            font=font_manager.panel_title_font()
        )
        title_label.grid(row=1, column=0, pady=(0, 20))

        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 错误图标
        error_label = ttk.Label(
            main_frame,
            text="❌",
            font=("Arial", 48)
        )
        error_label.grid(row=0, column=0, pady=(0, 10))

        # 错误标题
        title_label = ttk.Label(
            main_frame,
            text="评估执行失败",
            font=font_manager.panel_title_font()
        )
        title_label.grid(row=1, column=0, pady=(0, 20))

        # 错误信息框架
        error_frame = ttk.LabelFrame(main_frame, text="错误信息", padding="10")
        error_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # 错误消息文本框
        error_text = scrolledtext.ScrolledText(
            error_frame,
            width=70,
            height=10,
            font=("Courier New", 10),
            wrap=tk.WORD
        )
        error_text.pack(fill=tk.BOTH, expand=True)

        # 插入完整的错误信息和堆栈跟踪
        full_error = f"错误消息：\n{error_message}\n\n详细堆栈：\n{error_traceback}"
        error_text.insert(1.0, full_error)
        error_text.config(state=tk.DISABLED)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(10, 0))

        # 复制错误信息按钮
        copy_button = ttk.Button(
            button_frame,
            text="📋 复制错误信息",
            command=lambda: self._copy_error_to_clipboard(full_error, dialog),
            width=20
        )
        copy_button.grid(row=0, column=0, padx=5)

        # 关闭按钮
        close_button = ttk.Button(
            button_frame,
            text="关闭",
            command=dialog.destroy,
            width=15
        )
        close_button.grid(row=0, column=1, padx=5)

        # 配置网格权重
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        error_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # 居中显示
        self._center_dialog(dialog)

        # 保存 full_error 供复制使用
        dialog.error_full_text = full_error

    def _copy_error_to_clipboard(self, error_text, dialog):
        """复制错误信息到剪贴板"""
        try:
            dialog.clipboard_clear()
            dialog.clipboard_append(error_text)
            dialog.update()

            # 显示复制成功提示
            original_text = dialog.focus_get()
            if original_text and hasattr(original_text, 'cget'):
                try:
                    original_btn = original_text
                    if isinstance(original_btn, ttk.Button):
                        # 临时更改按钮文本
                        original_text_var = None
                except:
                    pass

            # 简单提示
            messagebox.showinfo("复制成功", "错误信息已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("复制失败", f"无法复制到剪贴板：{str(e)}")

    def _center_dialog(self, dialog):
        """窗口居中显示"""
        dialog.update_idletasks()

        width = dialog.winfo_width()
        height = dialog.winfo_height()

        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def _update_result(self, result):
        """更新结果显示 - 使用BatchResultWindow"""
        # 关闭加载弹窗
        if hasattr(self, 'loading_dialog') and self.loading_dialog:
            self.loading_dialog.destroy()
            self.loading_dialog = None

        if result['success']:
            # 使用批量测试的结果窗口(复用代码)
            BatchResultWindow(self.window, [result], self.evaluator_info)
        else:
            # 显示错误弹窗
            messagebox.showerror("评估失败", result.get('message', '评估失败'))

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

    def open_batch_test(self):
        """打开批量测试窗口"""
        BatchTestSelectionWindow(self.window, self.evaluator_info, self.config_manager)


class BatchTestSelectionWindow:
    """批量测试数据选择窗口"""

    def __init__(self, parent, evaluator_info, config_manager):
        self.evaluator_info = evaluator_info
        self.config_manager = config_manager

        # 存储复选框状态 {item_id: BooleanVar}
        self.checkbox_vars = {}

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("批量测试 - 选择测试数据")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()

        # 绑定ESC键关闭
        bind_esc_key(self.window)

        # 创建界面
        self.create_interface()

        # 加载数据
        self.load_test_data()

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
            text="📋 批量测试 - 选择测试数据",
            font=font_manager.panel_title_font()
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # 说明
        info_text = f"评估器: {self.evaluator_info['name']}\n" \
                   f"框架: {self.evaluator_info['framework']} | " \
                   f"类型: {self.evaluator_info['metric_type']}"
        info_label = ttk.Label(main_frame, text=info_text, font=font_manager.panel_font_small(), foreground="gray")
        info_label.grid(row=1, column=0, pady=(0, 10))

        # 控制区域（分组筛选 + 三个按钮，同一行）
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # 分组筛选
        ttk.Label(
            control_frame,
            text="🏷️ 分组:",
            font=font_manager.panel_font()
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.group_filter_combo = ttk.Combobox(
            control_frame,
            width=15,
            font=font_manager.panel_font(),
            state="readonly"
        )
        self.group_filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.group_filter_combo.bind("<<ComboboxSelected>>", self._on_group_filter_changed)

        # 加载分组选项
        self._load_groups()

        # 全选按钮
        ttk.Button(
            control_frame,
            text="☑ 全选",
            command=self.toggle_select_all,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        # 开始测试按钮
        ttk.Button(
            control_frame,
            text="▶ 开始测试",
            command=self.start_batch_test,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # 取消按钮
        ttk.Button(
            control_frame,
            text="取消",
            command=self.window.destroy,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        # 创建滚动容器（占据剩余空间）
        self.create_scrollable_container(main_frame)

        # 创建列表
        self.create_test_data_list()

        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # 让滚动容器区域占据剩余空间

    def create_scrollable_container(self, parent):
        """创建列表容器（不使用Canvas，让Treeview自己管理滚动）"""
        # 创建主容器，作为parent的子元素
        container = ttk.Frame(parent)
        container.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))

        # 保存容器引用，供create_test_data_list使用
        self.list_container = container

    def create_test_data_list(self):
        """创建测试数据列表"""
        # 创建Treeview（自带滚动条）
        columns = ("select", "name")
        self.tree = ttk.Treeview(self.list_container, columns=columns, show="headings")

        self.tree.heading("select", text="✓")
        self.tree.heading("name", text="测试数据名称")

        self.tree.column("select", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=700)

        # 应用字体设置和动态行高
        style = ttk.Style()
        row_height = font_manager.get_treeview_row_height()
        style.configure("BatchTest.Treeview",
                       font=font_manager.panel_font(),
                       rowheight=row_height)
        style.configure("BatchTest.Treeview.Heading", font=font_manager.panel_font_bold())
        self.tree.configure(style="BatchTest.Treeview")

        # 滚动条
        tree_scrollbar = ttk.Scrollbar(self.list_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定点击事件
        self.tree.bind("<Button-1>", self._on_click)

    def _load_groups(self):
        """加载分组选项到筛选下拉框"""
        groups = self.config_manager.get_test_groups()
        group_names = ["全部"] + [g["name"] for g in groups]
        self.group_filter_combo['values'] = group_names
        self.group_filter_combo.current(0)
        self.current_group_filter = "全部"

    def _on_group_filter_changed(self, event):
        """分组筛选改变事件"""
        selected_group = self.group_filter_combo.get()
        self.current_group_filter = selected_group
        self.load_test_data()  # 重新加载测试数据

    def load_test_data(self):
        """加载测试数据（带分组筛选）"""
        # 清空
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.checkbox_vars.clear()

        # 加载所有测试数据
        test_data_list = self.config_manager.get_test_data_list()

        # 根据分组筛选（与测试数据管理窗口保持一致）
        if self.current_group_filter != "全部":
            test_data_list = [
                td for td in test_data_list
                if td.get('group', '') == self.current_group_filter
            ]

        for td in test_data_list:
            var = tk.BooleanVar(value=False)
            item_id = self.tree.insert("", tk.END, values=("☐", td['name']))
            self.checkbox_vars[item_id] = var

    def _on_click(self, event):
        """处理点击事件"""
        region = self.tree.identify_region(event.x, event.y)

        if region == "cell":
            column = self.tree.identify_column(event.x)

            if column == "#1":
                item = self.tree.identify_row(event.y)

                if item:
                    var = self.checkbox_vars.get(item)
                    if var:
                        current_value = var.get()
                        var.set(not current_value)

                        new_value = "☑" if not current_value else "☐"
                        self.tree.item(item, values=(new_value, *self.tree.item(item, "values")[1:]))

                        self._update_select_all_button()

    def _update_select_all_button(self):
        """更新全选按钮状态（暂未实现UI更新）"""
        pass

    def toggle_select_all(self):
        """全选/取消全选"""
        all_items = self.tree.get_children()

        if not all_items:
            return

        all_selected = all(self.checkbox_vars.get(item, tk.BooleanVar(value=False)).get()
                          for item in all_items)

        if all_selected:
            for item in all_items:
                var = self.checkbox_vars.get(item)
                if var:
                    var.set(False)
                self.tree.item(item, values=("☐", *self.tree.item(item, "values")[1:]))
        else:
            for item in all_items:
                var = self.checkbox_vars.get(item)
                if var:
                    var.set(True)
                self.tree.item(item, values=("☑", *self.tree.item(item, "values")[1:]))

    def start_batch_test(self):
        """开始批量测试"""
        # 获取选中的项
        selected_items = []
        for item in self.tree.get_children():
            var = self.checkbox_vars.get(item)
            if var and var.get():
                selected_items.append(item)

        if not selected_items:
            messagebox.showwarning("警告", "请先勾选至少一条测试数据")
            return

        # 获取选中的测试数据
        selected_names = []
        for item in selected_items:
            values = self.tree.item(item, "values")
            selected_names.append(values[1])

        # 加载测试数据
        test_data_list = []
        for name in selected_names:
            test_data = self.config_manager.get_test_data_by_name(name)
            if test_data:
                test_data_list.append(test_data)

        # 获取父窗口（执行评估窗口）
        parent_window = self.window.master

        # 关闭选择窗口
        self.window.destroy()

        # 开始批量评估（使用执行评估窗口作为父窗口）
        BatchEvaluationExecutor(parent_window, self.evaluator_info, test_data_list, self.config_manager)

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


class BatchEvaluationExecutor:
    """批量评估执行器"""

    def __init__(self, parent, evaluator_info, test_data_list, config_manager):
        self.evaluator_info = evaluator_info
        self.config_manager = config_manager
        self.results = []
        self.current_index = 0

        # 预处理测试数据：根据评估器的turn_mode决定是否拆分多轮对话
        self.test_data_list = self._preprocess_test_data(test_data_list, evaluator_info)

        # 创建进度窗口
        self.create_progress_window(parent)

        # 开始执行评估
        self.start_evaluation()

    def _preprocess_test_data(self, test_data_list, evaluator_info):
        """
        预处理测试数据，根据评估器的turn_mode决定是否拆分多轮对话

        Args:
            test_data_list: 原始测试数据列表
            evaluator_info: 评估器信息

        Returns:
            处理后的测试数据列表
        """
        processed_list = []
        turn_mode = evaluator_info.get("turn_mode", "single")  # 默认单轮

        for test_data in test_data_list:
            turns = test_data.get("turns", [])

            if turn_mode == "single":
                # 单轮模式：如果有多轮对话，拆分成多个独立的数据
                if len(turns) > 1:
                    # 多轮对话，累积式拆分：(1), (1,2), (1,2,3)
                    for i in range(len(turns)):
                        # 获取从第0轮到第i轮的所有对话
                        accumulated_turns = turns[0:i+1]

                        # 构建累积对话文本（复用多轮模式的格式化逻辑）
                        conversation_parts = []
                        for j, turn in enumerate(accumulated_turns, 1):
                            question = turn.get("question", "").strip()
                            answer = turn.get("answer", "").strip()
                            context = turn.get("context", "").strip()

                            # 构建单轮对话文本
                            turn_text = f"第{j}轮:\n问题: {question}\n回答: {answer}"
                            if context:
                                turn_text += f"\n参考资料: {context}"
                            turn_text += "\n"

                            conversation_parts.append(turn_text)

                        # 拼接所有累积轮次
                        conversation_text = "\n".join(conversation_parts)

                        # 创建单轮测试数据（问题包含完整历史上下文）
                        single_turn_data = {
                            "name": f"{test_data['name']}[第{i+1}轮]",
                            "question": conversation_text,  # 包含从第1轮到当前轮的完整对话
                            "answer": turns[i]["answer"],   # 当前轮的回答
                            "context": turns[i].get("context", ""),
                            # 保留原始ID用于追踪
                            "_original_id": test_data.get("id", ""),
                            "_original_name": test_data['name'],
                            "_turn_index": i,
                            "_turn_count": len(turns),  # 总轮数
                            "_accumulated_turns": i + 1  # 当前累积轮数
                        }
                        processed_list.append(single_turn_data)
                else:
                    # 单轮对话，直接使用
                    if turns:
                        processed_list.append({
                            "name": test_data['name'],
                            "question": turns[0]["question"],
                            "answer": turns[0]["answer"],
                            "context": turns[0].get("context", ""),
                            "_original_id": test_data.get("id", "")
                        })
                    else:
                        # 兼容旧数据结构
                        processed_list.append({
                            "name": test_data['name'],
                            "question": test_data.get("question", ""),
                            "answer": test_data.get("answer", ""),
                            "context": test_data.get("context", ""),
                            "_original_id": test_data.get("id", "")
                        })
            else:
                # 多轮模式：把所有轮次拼接成一个完整的多轮对话文本
                if turns:
                    # 构建多轮对话文本
                    conversation_parts = []
                    for i, turn in enumerate(turns, 1):
                        question = turn.get("question", "").strip()
                        answer = turn.get("answer", "").strip()
                        context = turn.get("context", "").strip()

                        # 构建单轮对话文本
                        turn_text = f"第{i}轮:\n问题: {question}\n回答: {answer}"
                        if context:
                            turn_text += f"\n参考资料: {context}"
                        turn_text += "\n"

                        conversation_parts.append(turn_text)

                    # 拼接所有轮次
                    full_conversation = "\n".join(conversation_parts)

                    # 创建处理后的数据
                    processed_data = {
                        "name": test_data['name'],
                        "question": full_conversation,  # 用完整对话作为question
                        "answer": "",  # 多轮模式下不需要单独的answer
                        "context": "",  # 多轮模式下不需要单独的context
                        "_original_id": test_data.get("id", ""),
                        "_is_multi_turn": True,  # 标记为多轮对话
                        "_turn_count": len(turns)
                    }
                    processed_list.append(processed_data)
                else:
                    # 没有turns,兼容旧数据结构
                    processed_list.append({
                        "name": test_data['name'],
                        "question": test_data.get("question", ""),
                        "answer": test_data.get("answer", ""),
                        "context": test_data.get("context", ""),
                        "_original_id": test_data.get("id", "")
                    })

        return processed_list

    def create_progress_window(self, parent):
        """创建进度窗口"""
        self.progress_window = tk.Toplevel(parent)
        self.progress_window.title("批量测试进行中")
        self.progress_window.geometry("500x300")
        self.progress_window.transient(parent)
        self.progress_window.grab_set()

        # 绑定ESC键关闭
        bind_esc_key(self.progress_window)

        # 主框架
        main_frame = ttk.Frame(self.progress_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(
            main_frame,
            text="⏳ 批量测试进行中",
            font=font_manager.panel_font_bold()
        ).pack(pady=(0, 20))

        # 进度标签
        self.progress_label = ttk.Label(
            main_frame,
            text=f"准备评估 0/{len(self.test_data_list)}",
            font=font_manager.panel_font_small()
        )
        self.progress_label.pack(pady=10)

        # 进度条
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='determinate',
            maximum=len(self.test_data_list),
            length=400
        )
        self.progress_bar.pack(pady=10)

        # 当前数据名称
        self.current_data_label = ttk.Label(
            main_frame,
            text="",
            font=font_manager.panel_font(),
            foreground="gray",
            wraplength=400
        )
        self.current_data_label.pack(pady=10)

        # 居中显示
        self.center_window()

    def center_window(self):
        """窗口居中显示"""
        self.progress_window.update_idletasks()

        width = self.progress_window.winfo_width()
        height = self.progress_window.winfo_height()

        screen_width = self.progress_window.winfo_screenwidth()
        screen_height = self.progress_window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.progress_window.geometry(f'{width}x{height}+{x}+{y}')

    def start_evaluation(self):
        """开始评估"""
        # 在后台线程执行
        import threading
        thread = threading.Thread(target=self._evaluate_all)
        thread.daemon = True
        thread.start()

    def _evaluate_all(self):
        """评估所有数据"""
        try:
            # 获取大模型配置
            model_settings = self.config_manager.get_model_settings()

            # 获取评估执行器
            from evaluators import get_executor
            executor = get_executor(self.evaluator_info)

            # 逐个评估
            for i, test_data in enumerate(self.test_data_list):
                # 更新进度
                self.progress_window.after(0, self._update_progress, i + 1, test_data['name'])

                # 执行评估
                result = executor.execute(
                    test_data['question'],
                    test_data['answer'],
                    test_data.get('context', ''),
                    model_settings
                )

                # 添加测试数据名称到结果中
                result['test_data_name'] = test_data['name']
                self.results.append(result)

                # 打印调试信息
                print(f"\n{'='*60}")
                print(f"评估完成: {test_data['name']}")
                print(f"Success: {result.get('success', False)}")
                print(f"Score: {result.get('score', 0.0)}")
                print(f"Passed: {result.get('passed', False)}")
                if not result.get('success', False):
                    print(f"Error: {result.get('error', 'Unknown error')}")
                    print(f"Message: {result.get('message', 'No message')}")
                print(f"{'='*60}\n")

            # 评估完成，显示结果
            self.progress_window.after(0, self._show_results)

        except Exception as e:
            import traceback
            error_message = str(e)
            error_traceback = traceback.format_exc()

            self.progress_window.after(0, self._show_error, error_message, error_traceback)

    def _update_progress(self, current, name):
        """更新进度"""
        self.progress_label.config(text=f"正在评估 {current}/{len(self.test_data_list)}")
        self.progress_bar['value'] = current
        self.current_data_label.config(text=f"当前：{name}")

    def _show_results(self):
        """显示结果"""
        # 关闭进度窗口
        self.progress_window.destroy()

        # 打开结果窗口
        BatchResultWindow(self.progress_window.master, self.results, self.evaluator_info)

    def _show_error(self, error_message, error_traceback):
        """显示错误"""
        self.progress_window.destroy()
        messagebox.showerror("评估失败", f"批量测试失败：\n\n{error_message}")


class BatchResultWindow:
    """批量测试结果窗口"""

    def __init__(self, parent, results, evaluator_info):
        self.results = results
        self.evaluator_info = evaluator_info
        self.current_index = 0

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title(f"批量测试结果 - {evaluator_info['name']}")
        self.window.geometry("900x700")
        self.window.transient(parent)

        # 绑定ESC键关闭
        bind_esc_key(self.window)

        # 创建界面
        self.create_interface()

        # 显示第一条结果
        self.display_result(0)

        # 居中显示
        self.center_window()

    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部标题和导航
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 20))

        # 标题
        title_text = f"批量测试结果 - {self.evaluator_info['name']}"
        ttk.Label(
            top_frame,
            text=title_text,
            font=font_manager.panel_font_bold()
        ).pack(side=tk.LEFT)

        # 导航按钮
        nav_frame = ttk.Frame(top_frame)
        nav_frame.pack(side=tk.RIGHT)

        self.prev_button = ttk.Button(
            nav_frame,
            text="◀ 上一条",
            command=self.show_previous,
            width=10
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)

        # 结果计数
        self.count_label = ttk.Label(
            nav_frame,
            text="",
            font=font_manager.panel_font_small()
        )
        self.count_label.pack(side=tk.LEFT, padx=10)

        self.next_button = ttk.Button(
            nav_frame,
            text="下一条 ▶",
            command=self.show_next,
            width=10
        )
        self.next_button.pack(side=tk.LEFT, padx=5)

        # 创建滚动容器（复用result_popup_window的逻辑）
        self.create_scrollable_content(main_frame)

    def create_scrollable_content(self, parent):
        """创建可滚动内容区域"""
        # 创建Canvas
        self.canvas = tk.Canvas(parent, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建滚动条
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.canvas.yview)
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
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        # 更新滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bind_mousewheel(self):
        """绑定鼠标滚轮事件"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """鼠标滚轮事件处理"""
        try:
            # 检查Canvas是否还存在
            if not self.canvas.winfo_exists():
                return

            if event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
        except tk.TclError:
            # Canvas已被销毁,忽略错误
            pass

    def display_result(self, index):
        """显示指定索引的结果"""
        if 0 <= index < len(self.results):
            self.current_index = index
            result = self.results[index]

            # 更新计数标签
            self.count_label.config(text=f"{index + 1} / {len(self.results)}")

            # 清空内容
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # 创建结果内容（复用result_popup_window的显示逻辑）
            self._create_result_content(result)

            # 更新滚动区域
            self.scrollable_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _create_result_content(self, result):
        """创建结果内容"""
        # 直接创建结果内容，不使用ResultPopupWindow
        content_frame = ttk.Frame(self.scrollable_frame, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # ========== 评估结果 ==========
        result_header = ttk.Label(
            content_frame,
            text="📊 评估结果",
            font=font_manager.panel_font_bold()
        )
        result_header.pack(anchor=tk.W, pady=(0, 15))

        # 显示评估结果（复用result_popup_window的逻辑）
        from windows.result_popup_window import ResultPopupWindow

        # 创建一个辅助方法来显示结果
        self._display_evaluation_result(content_frame, result)

        # ========== 分隔线 ==========
        ttk.Separator(content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        # ========== 测试数据信息卡片 ==========
        info_card = ttk.Frame(content_frame, relief=tk.RIDGE, borderwidth=2)
        info_card.pack(fill=tk.X, pady=(0, 20))

        # 卡片标题
        card_header = ttk.Frame(info_card)
        card_header.pack(fill=tk.X, padx=15, pady=(10, 5))

        ttk.Label(
            card_header,
            text="📚 测试数据信息",
            font=font_manager.panel_font_bold(),
            foreground="#4299E1"
        ).pack(side=tk.LEFT)

        # 测试数据名称
        test_data_name = result.get('test_data_name', '未知数据')
        ttk.Label(
            info_card,
            text=f"名称: {test_data_name}",
            font=font_manager.panel_font_small()
        ).pack(anchor=tk.W, padx=15, pady=(5, 10))

        # 分隔线
        ttk.Separator(info_card, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=15, pady=5)

        # 问题
        ttk.Label(
            info_card,
            text="问题:",
            font=font_manager.panel_font_bold()
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))

        question = result.get('input', {}).get('question', '无')
        question_height = self._calculate_text_height(question)
        question_text = tk.Text(
            info_card,
            height=question_height,
            font=font_manager.panel_font(),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg="#F7FAFC"
        )
        question_text.pack(fill=tk.X, padx=15, pady=(0, 10))
        question_text.insert(1.0, question)
        question_text.config(state=tk.DISABLED)

        # 回答
        ttk.Label(
            info_card,
            text="回答:",
            font=font_manager.panel_font_bold()
        ).pack(anchor=tk.W, padx=15, pady=(10, 5))

        answer = result.get('input', {}).get('answer', '无')
        answer_height = self._calculate_text_height(answer)
        answer_text = tk.Text(
            info_card,
            height=answer_height,
            font=font_manager.panel_font(),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg="#F7FAFC"
        )
        answer_text.pack(fill=tk.X, padx=15, pady=(0, 10))
        answer_text.insert(1.0, answer)
        answer_text.config(state=tk.DISABLED)

        # 参考资料（如果有）
        context = result.get('input', {}).get('context', '')
        if context:
            ttk.Label(
                info_card,
                text="参考资料:",
                font=font_manager.panel_font_bold()
            ).pack(anchor=tk.W, padx=15, pady=(10, 5))

            context_height = self._calculate_text_height(context)
            context_text = tk.Text(
                info_card,
                height=context_height,
                font=font_manager.panel_font(),
                wrap=tk.WORD,
                relief=tk.FLAT,
                bg="#F7FAFC"
            )
            context_text.pack(fill=tk.X, padx=15, pady=(0, 15))
            context_text.insert(1.0, context)
            context_text.config(state=tk.DISABLED)
        else:
            # 如果没有上下文，添加一些底部间距
            ttk.Label(info_card, text="").pack(pady=(0, 15))

    def _display_evaluation_result(self, parent, result):
        """显示评估结果"""
        success = result.get('success', False)
        score = result.get('score', 0.0)
        passed = result.get('passed', False)
        message = result.get('message', '')
        reason = result.get('reason', '')
        error = result.get('error', '')

        # 结果状态
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(0, 20))

        if success:
            if passed:
                status_text = "✅ 通过"
                status_color = "#48BB78"
            else:
                status_text = "❌ 失败"
                status_color = "#F56565"

            ttk.Label(
                status_frame,
                text=status_text,
                font=font_manager.panel_title_font(),
                foreground=status_color
            ).pack(side=tk.LEFT, padx=(0, 20))

            ttk.Label(
                status_frame,
                text=f"得分: {format_number(score)}",
                font=font_manager.panel_font_bold(),
                foreground="#2D3748"
            ).pack(side=tk.LEFT)
        else:
            # 显示失败状态和错误信息
            ttk.Label(
                status_frame,
                text="❌ 评估失败",
                font=font_manager.panel_title_font(),
                foreground="#F56565"
            ).pack(side=tk.LEFT, padx=(0, 20))

            ttk.Label(
                status_frame,
                text=f"得分: {format_number(score)}",
                font=font_manager.panel_font_bold(),
                foreground="#2D3748"
            ).pack(side=tk.LEFT)

        # 分隔线
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # 如果有错误信息，优先显示错误
        if not success and error:
            ttk.Label(
                parent,
                text="⚠️ 错误信息:",
                font=font_manager.panel_font_bold(),
                foreground="#E53E3E"
            ).pack(anchor=tk.W, pady=(10, 5))

            error_height = self._calculate_text_height(error)
            error_text = tk.Text(
                parent,
                height=error_height,
                font=font_manager.panel_font(),
                wrap=tk.WORD,
                relief=tk.FLAT,
                bg="#FED7D7",
                padx=10,
                pady=10
            )
            error_text.pack(fill=tk.X, pady=(0, 20))
            error_text.insert(1.0, error)
            error_text.config(state=tk.DISABLED)

        # 评估原因（中英文对照）
        if success and reason:
            ttk.Label(
                parent,
                text="📝 评估原因:",
                font=font_manager.panel_font_bold()
            ).pack(anchor=tk.W, pady=(10, 5))

            reason_height = self._calculate_text_height(reason)
            reason_text = tk.Text(
                parent,
                height=reason_height,
                font=font_manager.panel_font(),
                wrap=tk.WORD,
                relief=tk.FLAT,
                bg="#F7FAFC",
                padx=10,
                pady=10
            )
            reason_text.pack(fill=tk.X, pady=(0, 20))
            reason_text.insert(1.0, reason)
            reason_text.config(state=tk.DISABLED)
        elif not success and message:
            # 如果评估失败但没有error字段，显示message
            ttk.Label(
                parent,
                text="📝 失败原因:",
                font=font_manager.panel_font_bold()
            ).pack(anchor=tk.W, pady=(10, 5))

            # 动态计算高度
            calculated_height = self._calculate_text_height(message)

            message_text = tk.Text(
                parent,
                height=calculated_height,
                font=font_manager.panel_font(),
                wrap=tk.WORD,
                relief=tk.FLAT,
                bg="#FED7D7",
                padx=10,
                pady=10
            )
            message_text.pack(fill=tk.X, pady=(0, 20))
            message_text.insert(1.0, message)
            message_text.config(state=tk.DISABLED)

        # ========== 框架返回的原文（放在最后）==========
        if success and reason:
            verbose_logs = result.get('verbose_logs', '')
            if verbose_logs:
                ttk.Label(
                    parent,
                    text="📝 框架返回的原文:",
                    font=font_manager.panel_font_bold(),
                    foreground="#718096"
                ).pack(anchor=tk.W, pady=(10, 5))

                # 动态计算高度
                calculated_height = self._calculate_text_height(verbose_logs)

                verbose_text = tk.Text(
                    parent,
                    height=calculated_height,
                    font=font_manager.panel_font(),
                    wrap=tk.WORD,
                    relief=tk.FLAT,
                    bg="#EDF2F7",
                    padx=10,
                    pady=10
                )
                verbose_text.pack(fill=tk.X, pady=(0, 20))
                verbose_text.insert(1.0, verbose_logs)
                verbose_text.config(state=tk.DISABLED)

        # 注意：输入数据已经在顶部的"测试数据信息卡片"中显示了，这里不再重复显示

    def _calculate_text_height(self, text):
        """计算Text组件的动态高度"""
        if not text:
            return 5

        # 计算行数
        lines = text.count('\n') + 1

        # 计算新高度：最少5行，超过2行后 = 行数 + 3
        if lines <= 2:
            new_height = 5
        else:
            new_height = lines + 3

        # 限制最大高度，避免过高
        return min(new_height, 25)

    def show_previous(self):
        """显示上一条结果"""
        if self.current_index > 0:
            self.display_result(self.current_index - 1)
        else:
            # 循环到最后一条
            self.display_result(len(self.results) - 1)

    def show_next(self):
        """显示下一条结果"""
        if self.current_index < len(self.results) - 1:
            self.display_result(self.current_index + 1)
        else:
            # 循环到第一条
            self.display_result(0)

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

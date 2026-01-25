"""
测试数据管理窗口
用于管理测试数据（增删查）
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from pathlib import Path
from font_utils import font_manager

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_manager import ConfigManager


from utils.window_helpers import bind_esc_key
class TestDataManagerWindow:
    """测试数据管理窗口"""

    def __init__(self, parent):
        self.parent = parent
        self.config_manager = ConfigManager()

        # 存储复选框状态 {item_id: BooleanVar}
        self.checkbox_vars = {}

        # 存储 item_id 到 test_data_id 的映射
        self.test_data_id_map = {}

        # 存储分组复选框状态 {group_name: BooleanVar}
        self.group_vars = {}

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("测试数据管理")
        self.window.geometry("900x700")
        self.window.transient(parent)
        self.window.grab_set()

        # 创建界面
        self.create_interface()

        # 加载数据
        self.load_test_data()

        # 居中显示
        self.center_window()

        # 绑定ESC键关闭
        bind_esc_key(self.window)

    def create_interface(self):
        """创建界面"""
        # 主容器 - 减少padding，让列表占据更多空间
        main_container = ttk.Frame(self.window, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置窗口网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # 顶部控制区域
        top_frame = ttk.Frame(main_container)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 标题（单独一行）
        title_label = ttk.Label(
            top_frame,
            text="📚 测试数据管理",
            font=font_manager.panel_title_font()
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # 控制按钮区域（支持自动换行）
        controls_frame = ttk.Frame(top_frame)
        controls_frame.pack(fill=tk.X)

        # 分组筛选
        ttk.Label(
            controls_frame,
            text="🏷️ 分组筛选:",
            font=font_manager.panel_font()
        ).pack(side=tk.LEFT, padx=(0, 5))

        # 获取所有分组并创建下拉框
        test_groups = self.config_manager.get_test_groups()
        group_options = ["全部"] + [g["name"] for g in test_groups]

        self.group_filter_var = tk.StringVar(value="全部")
        self.group_filter_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.group_filter_var,
            values=group_options,
            width=20,
            font=font_manager.panel_font(),
            state="readonly"
        )
        self.group_filter_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.group_filter_combo.bind("<<ComboboxSelected>>", self._on_group_filter_changed)

        # 操作按钮
        ttk.Button(
            controls_frame,
            text="➕ 新增",
            command=self.add_new_test_data
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.select_all_btn = ttk.Button(
            controls_frame,
            text="☑ 全选",
            command=self.toggle_select_all
        )
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            controls_frame,
            text="🗑 批量删除",
            command=self.batch_delete
        ).pack(side=tk.LEFT, padx=(0, 5))

        # ========== 测试数据列表（占据整个宽度） ==========
        list_frame = ttk.LabelFrame(main_container, text="测试数据列表", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 列表区域可以扩展
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # ========== 列表区域（可滚动） ==========
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建Treeview（自带滚动条）
        columns = ("select", "name", "question")
        self.tree = ttk.Treeview(list_container, columns=columns, show="headings")

        self.tree.heading("select", text="✓")
        self.tree.heading("name", text="名称")
        self.tree.heading("question", text="问题")

        # 设置列宽 - 复选框居中，其他左对齐
        self.tree.column("select", width=40, anchor=tk.CENTER)
        self.tree.column("name", width=200, anchor=tk.W)
        self.tree.column("question", width=300, anchor=tk.W)

        # 应用字体设置和动态行高
        style = ttk.Style()
        row_height = font_manager.get_treeview_row_height()
        style.configure("TestDataManager.Treeview",
                       font=font_manager.panel_font(),
                       rowheight=row_height)
        style.configure("TestDataManager.Treeview.Heading", font=font_manager.panel_font_bold())
        self.tree.configure(style="TestDataManager.Treeview")

        # 滚动条
        tree_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        # 绑定点击事件（用于复选框）
        self.tree.bind("<Button-1>", self._on_click)
        # 绑定双击事件（显示详情弹窗）
        self.tree.bind("<Double-Button-1>", self._on_double_click)

    def load_test_data(self):
        """加载测试数据（支持新的多轮对话结构）"""
        # 清空列表和复选框状态
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.checkbox_vars.clear()
        self.test_data_id_map.clear()

        # 加载数据
        test_data_list = self.config_manager.get_test_data_list()

        # 获取当前筛选的分组
        selected_group = self.group_filter_var.get()

        # 根据分组筛选
        for td in test_data_list:
            # 如果选择了特定分组，只显示该分组的测试数据
            if selected_group != "全部":
                test_data_group = td.get('group', '')
                if selected_group != test_data_group:
                    continue

            # 获取第一轮问题作为摘要
            turns = td.get('turns', [])
            if turns:
                first_question = turns[0].get('question', '')
                if len(first_question) > 50:
                    first_question = first_question[:50] + "..."

                # 如果有多轮，显示轮次数
                turns_count = len(turns)
                if turns_count > 1:
                    display_name = f"{td['name']} ({turns_count}轮)"
                else:
                    display_name = td['name']
            else:
                first_question = "(无数据)"
                display_name = td['name']

            # 创建复选框变量
            var = tk.BooleanVar(value=False)
            item_id = self.tree.insert("", tk.END, values=("☐", display_name, first_question))
            self.checkbox_vars[item_id] = var

            # 存储 ID 映射
            self.test_data_id_map[item_id] = td.get('id', '')

        # 重置全选按钮
        self.select_all_btn.config(text="☑ 全选")

    def _on_group_filter_changed(self, event=None):
        """分组筛选改变时的回调"""
        self.load_test_data()

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

                        # 更新全选按钮状态
                        self._update_select_all_button()

    def _update_select_all_button(self):
        """更新全选按钮状态"""
        all_items = self.tree.get_children()

        if not all_items:
            self.select_all_btn.config(text="☑ 全选")
            return

        all_selected = all(self.checkbox_vars.get(item, tk.BooleanVar(value=False)).get()
                          for item in all_items)

        if all_selected:
            self.select_all_btn.config(text="☐ 取消全选")
        else:
            self.select_all_btn.config(text="☑ 全选")

    def _on_select(self, event):
        """选择事件 - 单击仅选中，不显示详情"""
        pass

    def add_new_test_data(self):
        """新增测试数据 - 打开新增弹窗"""
        TestDataDetailPopup(
            self.window,
            test_data=None,  # 新增模式，不传测试数据
            config_manager=self.config_manager,
            refresh_callback=self.load_test_data,
            mode="new"
        )

    def toggle_select_all(self):
        """全选/取消全选"""
        all_items = self.tree.get_children()

        if not all_items:
            return

        # 判断当前是否全选
        all_selected = all(self.checkbox_vars.get(item, tk.BooleanVar(value=False)).get()
                          for item in all_items)

        if all_selected:
            # 取消全选
            for item in all_items:
                var = self.checkbox_vars.get(item)
                if var:
                    var.set(False)
                self.tree.item(item, values=("☐", *self.tree.item(item, "values")[1:]))
            self.select_all_btn.config(text="☑ 全选")
        else:
            # 全选
            for item in all_items:
                var = self.checkbox_vars.get(item)
                if var:
                    var.set(True)
                self.tree.item(item, values=("☑", *self.tree.item(item, "values")[1:]))
            self.select_all_btn.config(text="☐ 取消全选")

    def batch_delete(self):
        """批量删除测试数据"""
        # 获取选中的项
        selected_items = []
        for item in self.tree.get_children():
            var = self.checkbox_vars.get(item)
            if var and var.get():
                selected_items.append(item)

        if not selected_items:
            messagebox.showwarning("警告", "请先勾选要删除的测试数据")
            return

        # 获取选中的名称和ID
        selected_info = []
        for item in selected_items:
            values = self.tree.item(item, "values")
            name = values[1]  # 第二列是名称
            test_data_id = self.test_data_id_map.get(item, '')
            selected_info.append((name, test_data_id))

        # 确认删除
        if len(selected_info) == 1:
            confirm_msg = f"确定要删除测试数据「{selected_info[0][0]}」吗？"
        else:
            confirm_msg = f"确定要删除这 {len(selected_info)} 条测试数据吗？\n\n"
            confirm_msg += "\n".join(f"• {info[0]}" for info in selected_info[:5])
            if len(selected_info) > 5:
                confirm_msg += f"\n... 还有 {len(selected_info) - 5} 条"

        if not messagebox.askyesno("确认删除", confirm_msg):
            return

        # 执行删除（使用ID）
        success_count = 0
        for name, test_data_id in selected_info:
            try:
                self.config_manager.remove_test_data(test_data_id)
                success_count += 1
            except Exception as e:
                print(f"删除失败: {name}, 错误: {e}")

        # 刷新列表
        self.load_test_data()

        messagebox.showinfo("成功", f"已成功删除 {success_count} 条测试数据")

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
        """双击事件：显示详情弹窗"""
        # 获取双击的行
        region = self.tree.identify_region(event.x, event.y)

        if region == "cell":
            item = self.tree.identify_row(event.y)
            if item:
                # 获取测试数据ID
                test_data_id = self.test_data_id_map.get(item, '')

                if not test_data_id:
                    messagebox.showerror("错误", "无法获取测试数据ID")
                    return

                # 获取完整数据（使用ID）
                test_data = self.config_manager.get_test_data_by_id(test_data_id)
                if test_data:
                    # 显示详情弹窗（传递ID用于编辑）
                    TestDataDetailPopup(
                        self.window,
                        test_data,
                        self.config_manager,
                        self.load_test_data
                    )


class TestDataDetailPopup:
    """测试数据详情弹窗（支持编辑和新增）"""

    def __init__(self, parent, test_data=None, config_manager=None, refresh_callback=None, mode="edit"):
        """
        初始化弹窗

        Args:
            parent: 父窗口
            test_data: 测试数据字典（编辑模式时传入，新增模式时为None）
            config_manager: 配置管理器
            refresh_callback: 刷新回调函数
            mode: 模式，"edit"（编辑）或 "new"（新增）
        """
        self.mode = mode
        self.config_manager = config_manager
        self.refresh_callback = refresh_callback

        if mode == "edit":
            # 编辑模式
            self.test_data = test_data
            self.test_data_id = test_data.get('id', '')
            window_title = f"编辑测试数据 - {test_data.get('name', '')}"
        else:
            # 新增模式
            self.test_data = {'name': '', 'question': '', 'answer': '', 'context': '', 'groups': []}
            self.test_data_id = None
            window_title = "新增测试数据"

        # 创建弹窗
        self.window = tk.Toplevel(parent)
        self.window.title(window_title)

        # 动态计算窗口大小，根据字体大小调整
        font_size = font_manager.get_panel_font_size()
        # 基础大小 700x650，字体每增加1号，宽度和高度增加
        base_width = 700
        base_height = 650
        scale_factor = (font_size - 11) * 0.08  # 11号是基准
        window_width = int(base_width * (1 + max(0, scale_factor)))
        window_height = int(base_height * (1 + max(0, scale_factor)))
        self.window.geometry(f"{window_width}x{window_height}")

        self.window.transient(parent)
        self.window.grab_set()

        # 创建可滚动容器
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
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def create_interface(self):
        """创建界面（支持多轮对话）"""
        # 动态计算padding，根据字体大小调整
        font_size = font_manager.get_panel_font_size()
        padding = max(20, int(font_size * 1.5))  # 字体越大，padding越大

        # 主框架（放在scrollable_frame中）
        main_frame = ttk.Frame(self.scrollable_frame, padding=padding)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="📝 测试数据详情",
            font=font_manager.panel_title_font()
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # 状态标签（用于显示成功/失败信息）
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=font_manager.panel_font(),
            foreground="green"
        )
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # 配置列权重，让标签列固定，内容列扩展
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)

        # ========== 基本信息 ==========
        # 名称
        ttk.Label(main_frame, text="名称:", font=font_manager.panel_font_bold()).grid(
            row=2, column=0, sticky=tk.W, pady=10)
        self.name_var = tk.StringVar(value=self.test_data.get('name', ''))
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=font_manager.get_entry_width(60), font=font_manager.panel_font())
        name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)

        # 分组选择（改为下拉框，单个分组）
        ttk.Label(main_frame, text="分组:", font=font_manager.panel_font_bold()).grid(
            row=3, column=0, sticky=tk.W, pady=10)

        # 获取所有分组
        test_groups = self.config_manager.get_test_groups()
        group_options = [g["name"] for g in test_groups]

        # 提取当前分组
        current_group = self.test_data.get('group', '')
        self.group_var = tk.StringVar(value=current_group)

        group_combo = ttk.Combobox(
            main_frame,
            textvariable=self.group_var,
            values=group_options,
            width=font_manager.get_entry_width(20),
            font=font_manager.panel_font(),
            state="readonly"
        )
        group_combo.grid(row=3, column=1, sticky=tk.W, pady=10)

        # ========== 多轮对话区域 ==========
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)

        ttk.Label(
            main_frame,
            text="💬 对话轮次",
            font=font_manager.panel_title_font()
        ).grid(row=5, column=0, columnspan=2, pady=(0, 10))

        # 按钮区域（三个按钮放到一行）
        button_container = ttk.Frame(main_frame)
        button_container.grid(row=6, column=0, columnspan=2, pady=15)

        # 添加一轮对话按钮
        ttk.Button(
            button_container,
            text="➕ 添加一轮对话",
            command=self._add_new_turn
        ).pack(side=tk.LEFT, padx=5)

        # 保存按钮
        if self.mode == "new":
            save_button_text = "💾 保存"
        else:
            save_button_text = "💾 保存修改"

        ttk.Button(
            button_container,
            text=save_button_text,
            command=self.save_changes
        ).pack(side=tk.LEFT, padx=5)

        # 取消按钮
        ttk.Button(
            button_container,
            text="取消",
            command=self.window.destroy
        ).pack(side=tk.LEFT, padx=5)

        # 轮次容器（移到按钮下方）
        self.turns_container = ttk.Frame(main_frame)
        self.turns_container.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 存储轮次的UI组件
        self.turns_widgets = []

        # 加载现有的轮次数据
        turns = self.test_data.get('turns', [])
        if not turns:
            # 如果没有轮次，创建一个空轮次
            turns = [{'question': '', 'answer': '', 'context': ''}]

        for i, turn in enumerate(turns):
            self._add_turn_ui(i, turn)

        # 初始化所有文本框的高度
        self.window.update_idletasks()
        for turn_widget in self.turns_widgets:
            self._adjust_text_height(turn_widget['question'])
            self._adjust_text_height(turn_widget['answer'])
            self._adjust_text_height(turn_widget['context'])

    def _add_turn_ui(self, turn_index, turn_data=None):
        """
        添加一轮对话的UI

        Args:
            turn_index: 轮次索引
            turn_data: 轮次数据 {question, answer, context}
        """
        if turn_data is None:
            turn_data = {'question': '', 'answer': '', 'context': ''}

        # 轮次框架（带边框）
        turn_frame = ttk.LabelFrame(
            self.turns_container,
            text=f"第 {turn_index + 1} 轮",
            padding="10"
        )
        turn_frame.grid(row=turn_index, column=0, sticky=(tk.W, tk.E), pady=10)

        # 问题
        ttk.Label(turn_frame, text="问题:", font=font_manager.panel_font_bold()).grid(
            row=0, column=0, sticky=tk.NW, pady=5)
        question_text = tk.Text(
            turn_frame,
            width=font_manager.get_entry_width(60),
            height=1,  # 初始高度为1，会动态调整
            font=font_manager.panel_font(),
            wrap=tk.WORD,
            relief=tk.RIDGE,
            padx=5,
            pady=5
        )
        question_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        question_text.insert(1.0, turn_data.get('question', ''))
        # 绑定动态高度调整
        question_text.bind("<KeyRelease>", lambda e: self._adjust_text_height(question_text))

        # 回答
        ttk.Label(turn_frame, text="回答:", font=font_manager.panel_font_bold()).grid(
            row=2, column=0, sticky=tk.NW, pady=5)
        answer_text = tk.Text(
            turn_frame,
            width=font_manager.get_entry_width(60),
            height=1,  # 初始高度为1，会动态调整
            font=font_manager.panel_font(),
            wrap=tk.WORD,
            relief=tk.RIDGE,
            padx=5,
            pady=5
        )
        answer_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        answer_text.insert(1.0, turn_data.get('answer', ''))
        # 绑定动态高度调整
        answer_text.bind("<KeyRelease>", lambda e: self._adjust_text_height(answer_text))

        # 参考资料
        ttk.Label(turn_frame, text="参考资料（可选）:", font=font_manager.panel_font_bold()).grid(
            row=4, column=0, sticky=tk.NW, pady=5)
        context_text = tk.Text(
            turn_frame,
            width=font_manager.get_entry_width(60),
            height=1,  # 初始高度为1，会动态调整
            font=font_manager.panel_font(),
            wrap=tk.WORD,
            relief=tk.RIDGE,
            padx=5,
            pady=5
        )
        context_text.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        context_text.insert(1.0, turn_data.get('context', ''))
        # 绑定动态高度调整
        context_text.bind("<KeyRelease>", lambda e: self._adjust_text_height(context_text))

        # 删除按钮（所有轮次都有，但只有一轮时禁用）
        delete_button = ttk.Button(
            turn_frame,
            text="🗑 删除此轮",
            command=lambda: self._remove_turn(turn_index),
            state=tk.NORMAL if len(self.turns_widgets) > 1 else tk.DISABLED
        )
        delete_button.grid(row=6, column=0, sticky=tk.E, pady=5)

        # 存储这轮的UI组件
        self.turns_widgets.append({
            'frame': turn_frame,
            'question': question_text,
            'answer': answer_text,
            'context': context_text,
            'delete_button': delete_button
        })

    def _add_new_turn(self):
        """添加新的空轮次"""
        turn_index = len(self.turns_widgets)
        self._add_turn_ui(turn_index, {'question': '', 'answer': '', 'context': ''})

        # 更新所有删除按钮状态（现在有超过一轮了）
        self._update_delete_buttons_state()

        # 初始化新添加的文本框高度
        self.window.update_idletasks()
        new_turn_widget = self.turns_widgets[-1]
        self._adjust_text_height(new_turn_widget['question'])
        self._adjust_text_height(new_turn_widget['answer'])
        self._adjust_text_height(new_turn_widget['context'])

    def _remove_turn(self, turn_index):
        """删除指定轮次"""
        # 至少保留一轮
        if len(self.turns_widgets) <= 1:
            messagebox.showwarning("警告", "至少需要保留一轮对话")
            return

        # 删除UI组件
        turn_widgets = self.turns_widgets[turn_index]
        turn_widgets['frame'].destroy()

        # 从列表中移除
        self.turns_widgets.pop(turn_index)

        # 重新编号后续轮次
        for i in range(turn_index, len(self.turns_widgets)):
            self.turns_widgets[i]['frame'].configure(text=f"第 {i + 1} 轮")
            # 更新删除按钮的回调
            self.turns_widgets[i]['delete_button'].configure(
                command=lambda idx=i: self._remove_turn(idx)
            )

        # 更新所有删除按钮状态
        self._update_delete_buttons_state()

    def _update_delete_buttons_state(self):
        """更新所有删除按钮的状态"""
        # 如果只有一轮，禁用所有删除按钮
        state = tk.NORMAL if len(self.turns_widgets) > 1 else tk.DISABLED

        for turn_widget in self.turns_widgets:
            if turn_widget['delete_button']:
                turn_widget['delete_button'].configure(state=state)

    def save_changes(self):
        """保存修改或新增（支持多轮对话）"""
        try:
            # 获取基本信息
            new_name = self.name_var.get().strip()
            new_group = self.group_var.get().strip()

            # 验证名称
            if not new_name:
                messagebox.showerror("错误", "名称不能为空")
                return

            # 收集所有轮次的数据
            turns = []
            for turn_widget in self.turns_widgets:
                question = turn_widget['question'].get(1.0, tk.END).strip()
                answer = turn_widget['answer'].get(1.0, tk.END).strip()
                context = turn_widget['context'].get(1.0, tk.END).strip()

                # 验证每轮的问题和回答
                if not question:
                    messagebox.showerror("错误", "每轮对话的问题不能为空")
                    return
                if not answer:
                    messagebox.showerror("错误", "每轮对话的回答不能为空")
                    return

                turns.append({
                    'question': question,
                    'answer': answer,
                    'context': context
                })

            # 验证至少有一轮
            if not turns:
                messagebox.showerror("错误", "至少需要一轮对话")
                return

            if self.mode == "new":
                # 新增模式：创建新测试数据
                new_data = {
                    "name": new_name,
                    "group": new_group,
                    "turns": turns
                }

                self.config_manager.add_test_data(new_data)

                # 刷新列表
                if self.refresh_callback:
                    self.refresh_callback()

                # 显示成功消息（不影响继续添加）
                self.status_label.config(text=f"✅ 测试数据 '{new_name}' 已添加", foreground="green")
                # 3秒后清除消息
                self.window.after(3000, lambda: self.status_label.config(text=""))

                # 清空表单，准备继续添加
                self._clear_form()

            else:
                # 编辑模式：更新现有测试数据
                updated_data = {
                    "id": self.test_data_id,  # 保留原有ID
                    "name": new_name,
                    "group": new_group,
                    "turns": turns
                }

                success = self.config_manager.update_test_data(self.test_data_id, updated_data)

                if success:
                    # 刷新列表
                    if self.refresh_callback:
                        self.refresh_callback()

                    # 显示成功消息
                    self.status_label.config(text=f"✅ 测试数据 '{new_name}' 已更新", foreground="green")
                    # 1秒后关闭窗口
                    self.window.after(1000, self.window.destroy)
                else:
                    self.status_label.config(text="❌ 保存失败", foreground="red")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def _clear_form(self):
        """清空表单（用于新增模式下的连续添加）"""
        self.name_var.set('')
        self.group_var.set('')

        # 清空所有轮次
        for turn_widget in self.turns_widgets:
            turn_widget['frame'].destroy()

        self.turns_widgets.clear()

        # 添加一个空轮次
        self._add_turn_ui(0, {'question': '', 'answer': '', 'context': ''})

    def _adjust_text_height(self, text_widget):
        """动态调整Text组件高度（基于视觉行数，包括自动换行）"""
        if not text_widget:
            return

        # 获取文本内容
        content = text_widget.get(1.0, tk.END).strip()

        # 让Tkinter重新计算布局
        text_widget.update_idletasks()

        # 获取基于实际显示的行数（包括自动换行）
        try:
            line_count = int(text_widget.index('end-1c').split('.')[0])
        except:
            line_count = content.count('\n') + 1  # 降级方案

        # 计算新高度：最少2行
        new_height = max(2, line_count)

        # 如果高度有变化，更新
        current_height = int(text_widget.cget('height'))
        if new_height != current_height:
            text_widget.config(height=new_height)

        # 在界面完全创建后再绑定ESC键
        self.window.after(100, lambda: bind_esc_key(self.window))
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

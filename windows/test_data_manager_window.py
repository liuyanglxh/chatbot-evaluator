"""
测试数据管理窗口
用于管理测试数据（增删查）
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_manager import ConfigManager


class TestDataManagerWindow:
    """测试数据管理窗口"""

    def __init__(self, parent):
        self.parent = parent
        self.config_manager = ConfigManager()

        # 存储复选框状态 {item_id: BooleanVar}
        self.checkbox_vars = {}

        # 存储 item_id 到 test_data_id 的映射
        self.test_data_id_map = {}

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

    def create_interface(self):
        """创建界面"""
        # 主容器
        main_container = ttk.Frame(self.window, padding="20")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_container,
            text="📚 测试数据管理",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # ========== 左侧：列表 ==========
        left_frame = ttk.LabelFrame(main_container, text="测试数据列表", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # 列表框
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建 Treeview（添加复选框列）
        columns = ("select", "name", "question")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        self.tree.heading("select", text="✓")
        self.tree.heading("name", text="名称")
        self.tree.heading("question", text="问题")

        self.tree.column("select", width=40, anchor=tk.CENTER)
        self.tree.column("name", width=200)
        self.tree.column("question", width=300)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        # 绑定点击事件（用于复选框）
        self.tree.bind("<Button-1>", self._on_click)
        # 绑定双击事件（显示详情弹窗）
        self.tree.bind("<Double-Button-1>", self._on_double_click)

        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 全选/取消全选按钮
        self.select_all_btn = ttk.Button(
            button_frame,
            text="☑ 全选",
            command=self.toggle_select_all,
            width=10
        )
        self.select_all_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="🗑 批量删除",
            command=self.batch_delete,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="💾 保存",
            command=self.save_test_data,
            width=10
        ).pack(side=tk.LEFT, padx=(20, 5))

        # ========== 右侧：详情 ==========
        right_frame = ttk.LabelFrame(main_container, text="详细信息", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 名称
        ttk.Label(right_frame, text="名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(right_frame, textvariable=self.name_var, width=50)
        name_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # 问题
        ttk.Label(right_frame, text="问题:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.question_text = scrolledtext.ScrolledText(
            right_frame,
            width=50,
            height=5,
            font=("Arial", 10)
        )
        self.question_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)

        # 回答
        ttk.Label(right_frame, text="回答:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.answer_text = scrolledtext.ScrolledText(
            right_frame,
            width=50,
            height=8,
            font=("Arial", 10)
        )
        self.answer_text.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)

        # 上下文
        ttk.Label(right_frame, text="上下文（可选）:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.context_text = scrolledtext.ScrolledText(
            right_frame,
            width=50,
            height=5,
            font=("Arial", 10)
        )
        self.context_text.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=5)

        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)
        main_container.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

    def load_test_data(self):
        """加载测试数据"""
        # 清空列表和复选框状态
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.checkbox_vars.clear()
        self.test_data_id_map.clear()

        # 加载数据
        test_data_list = self.config_manager.get_test_data_list()

        for td in test_data_list:
            # 截取问题显示
            question = td.get('question', '')
            if len(question) > 50:
                question = question[:50] + "..."

            # 创建复选框变量
            var = tk.BooleanVar(value=False)
            item_id = self.tree.insert("", tk.END, values=("☐", td['name'], question))
            self.checkbox_vars[item_id] = var

            # 存储 ID 映射
            self.test_data_id_map[item_id] = td.get('id', '')

        # 重置全选按钮
        self.select_all_btn.config(text="☑ 全选")

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
        """选择事件"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.tree.item(item, "values")
        name = values[0]

        # 获取完整数据
        test_data = self.config_manager.get_test_data_by_name(name)
        if test_data:
            self._display_test_data(test_data)

    def _display_test_data(self, test_data):
        """显示测试数据"""
        # 清空
        self.name_var.set(test_data.get('name', ''))
        self.question_text.delete(1.0, tk.END)
        self.answer_text.delete(1.0, tk.END)
        self.context_text.delete(1.0, tk.END)

        # 填充数据
        self.question_text.insert(1.0, test_data.get('question', ''))
        self.answer_text.insert(1.0, test_data.get('answer', ''))
        self.context_text.insert(1.0, test_data.get('context', ''))

    def delete_test_data(self):
        """删除测试数据"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的测试数据")
            return

        item = selection[0]
        values = self.tree.item(item, "values")
        name = values[0]

        # 确认删除
        if messagebox.askyesno("确认", f"确定要删除测试数据「{name}」吗？"):
            self.config_manager.remove_test_data(name)
            self.load_test_data()

            # 清空详情
            self.name_var.set('')
            self.question_text.delete(1.0, tk.END)
            self.answer_text.delete(1.0, tk.END)
            self.context_text.delete(1.0, tk.END)

            messagebox.showinfo("成功", "测试数据已删除")

    def save_test_data(self):
        """保存测试数据"""
        name = self.name_var.get().strip()
        question = self.question_text.get(1.0, tk.END).strip()
        answer = self.answer_text.get(1.0, tk.END).strip()
        context = self.context_text.get(1.0, tk.END).strip()

        # 验证
        if not name:
            messagebox.showerror("错误", "请输入名称")
            return

        if not question:
            messagebox.showerror("错误", "请输入问题")
            return

        if not answer:
            messagebox.showerror("错误", "请输入回答")
            return

        # 创建测试数据
        test_data = {
            'name': name,
            'question': question,
            'answer': answer,
            'context': context
        }

        # 保存
        self.config_manager.add_test_data(test_data)

        # 刷新列表
        self.load_test_data()

        # 清空右侧文本框
        self.name_var.set('')
        self.question_text.delete(1.0, tk.END)
        self.answer_text.delete(1.0, tk.END)
        self.context_text.delete(1.0, tk.END)

        messagebox.showinfo("成功", "测试数据已保存")

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

        # 清空详情
        self.name_var.set('')
        self.question_text.delete(1.0, tk.END)
        self.answer_text.delete(1.0, tk.END)
        self.context_text.delete(1.0, tk.END)

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
    """测试数据详情弹窗（支持编辑）"""

    def __init__(self, parent, test_data, config_manager, refresh_callback):
        self.test_data = test_data
        self.test_data_id = test_data.get('id', '')  # 保存ID
        self.config_manager = config_manager
        self.refresh_callback = refresh_callback

        # 创建弹窗
        self.window = tk.Toplevel(parent)
        self.window.title(f"测试数据详情 - {test_data.get('name', '')}")
        self.window.geometry("700x650")
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
        """创建界面"""
        # 主框架（放在scrollable_frame中）
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="📝 测试数据详情",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 名称
        ttk.Label(main_frame, text="名称:", font=("Arial", 11, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=10)
        self.name_var = tk.StringVar(value=self.test_data.get('name', ''))
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=60, font=("Arial", 11))
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)

        # 问题
        ttk.Label(main_frame, text="问题:", font=("Arial", 11, "bold")).grid(
            row=2, column=0, sticky=tk.NW, pady=10)
        self.question_text = tk.Text(main_frame, width=60, height=5, font=("Arial", 11),
                                   wrap=tk.WORD, relief=tk.RIDGE, padx=5, pady=5)
        self.question_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)
        self.question_text.insert(1.0, self.test_data.get('question', ''))

        # 回答
        ttk.Label(main_frame, text="回答:", font=("Arial", 11, "bold")).grid(
            row=3, column=0, sticky=tk.NW, pady=10)
        self.answer_text = tk.Text(main_frame, width=60, height=8, font=("Arial", 11),
                                 wrap=tk.WORD, relief=tk.RIDGE, padx=5, pady=5)
        self.answer_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=10)
        self.answer_text.insert(1.0, self.test_data.get('answer', ''))

        # 上下文
        ttk.Label(main_frame, text="上下文（可选）:", font=("Arial", 11, "bold")).grid(
            row=4, column=0, sticky=tk.NW, pady=10)
        self.context_text = tk.Text(main_frame, width=60, height=5, font=("Arial", 11),
                                  wrap=tk.WORD, relief=tk.RIDGE, padx=5, pady=5)
        self.context_text.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=10)
        self.context_text.insert(1.0, self.test_data.get('context', ''))

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(30, 10), sticky=(tk.E))

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

        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)

    def save_changes(self):
        """保存修改"""
        try:
            # 获取新的值
            new_name = self.name_var.get().strip()
            new_question = self.question_text.get(1.0, tk.END).strip()
            new_answer = self.answer_text.get(1.0, tk.END).strip()
            new_context = self.context_text.get(1.0, tk.END).strip()

            # 验证
            if not new_name:
                messagebox.showerror("错误", "名称不能为空")
                return

            if not new_question:
                messagebox.showerror("错误", "问题不能为空")
                return

            if not new_answer:
                messagebox.showerror("错误", "回答不能为空")
                return

            # 构建更新后的数据（保留原有ID）
            updated_data = {
                "id": self.test_data_id,  # 保留原有ID
                "name": new_name,
                "question": new_question,
                "answer": new_answer,
                "context": new_context
            }

            # 使用update_test_data方法更新
            success = self.config_manager.update_test_data(self.test_data_id, updated_data)

            if success:
                messagebox.showinfo("成功", f"测试数据 '{new_name}' 已更新")
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

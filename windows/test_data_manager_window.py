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

        # 创建 Treeview
        columns = ("name", "question")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        self.tree.heading("name", text="名称")
        self.tree.heading("question", text="问题")

        self.tree.column("name", width=200)
        self.tree.column("question", width=300)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="➕ 添加",
            command=self.add_test_data,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="✏️ 编辑",
            command=self.edit_test_data,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="🗑 删除",
            command=self.delete_test_data,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="💾 保存",
            command=self.save_test_data,
            width=10
        ).pack(side=tk.LEFT, padx=5)

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
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 加载数据
        test_data_list = self.config_manager.get_test_data_list()

        for td in test_data_list:
            # 截取问题显示
            question = td.get('question', '')
            if len(question) > 50:
                question = question[:50] + "..."

            self.tree.insert("", tk.END, values=(td['name'], question))

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

    def add_test_data(self):
        """添加测试数据"""
        # 清空表单
        self.name_var.set('')
        self.question_text.delete(1.0, tk.END)
        self.answer_text.delete(1.0, tk.END)
        self.context_text.delete(1.0, tk.END)

        # 聚焦到名称输入框
        messagebox.showinfo("提示", "请在右侧输入测试数据，然后点击「保存」")

    def edit_test_data(self):
        """编辑测试数据"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的测试数据")
            return

        # 已经在 _on_select 中加载数据了
        messagebox.showinfo("提示", "请在右侧修改测试数据，然后点击「保存」")

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

        messagebox.showinfo("成功", "测试数据已保存")

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

"""
分组管理窗口
支持添加、修改、删除测试数据分组
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config_manager import ConfigManager


class GroupManagerWindow:
    """分组管理窗口"""

    def __init__(self, parent):
        self.config_manager = ConfigManager()

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("分组管理")
        self.window.geometry("700x500")
        self.window.transient(parent)
        self.window.grab_set()

        # 创建界面
        self.create_interface()

        # 加载分组列表
        self.load_groups()

        # 居中显示
        self.center_window()

    def center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="🏷️ 分组管理",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # ========== 左侧：分组列表 ==========
        left_frame = ttk.LabelFrame(main_frame, text="分组列表", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # 创建Treeview显示分组列表
        columns = ("name", "description")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)

        self.tree.heading("name", text="分组名称")
        self.tree.heading("description", text="描述")

        self.tree.column("name", width=150, anchor=tk.W)
        self.tree.column("description", width=200, anchor=tk.W)

        # 滚动条
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self._on_group_selected)

        # ========== 右侧：操作面板 ==========
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 添加按钮
        ttk.Button(
            right_frame,
            text="➕ 新增分组",
            command=self.add_group,
            width=18
        ).pack(pady=5)

        # 修改按钮
        ttk.Button(
            right_frame,
            text="✏️ 修改分组",
            command=self.edit_group,
            width=18
        ).pack(pady=5)

        # 删除按钮
        ttk.Button(
            right_frame,
            text="🗑️ 删除分组",
            command=self.delete_group,
            width=18
        ).pack(pady=5)

        # 分隔线
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        # 关闭按钮
        ttk.Button(
            right_frame,
            text="关闭",
            command=self.window.destroy,
            width=18
        ).pack(pady=5)

        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

    def load_groups(self):
        """加载分组列表"""
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 加载所有分组
        groups = self.config_manager.get_test_groups()

        for group in groups:
            self.tree.insert("", tk.END, values=(group["name"], group.get("description", "")))

    def _on_group_selected(self, event):
        """分组选择事件"""
        pass  # 可以在这里实现选中后自动填充编辑表单

    def add_group(self):
        """添加分组"""
        # 打开添加/编辑对话框
        GroupEditDialog(self.window, None, self.config_manager, self.load_groups)

    def edit_group(self):
        """修改分组"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要修改的分组")
            return

        # 获取选中的分组名称
        item = selection[0]
        values = self.tree.item(item, "values")
        group_name = values[0]

        # 打开编辑对话框
        GroupEditDialog(self.window, group_name, self.config_manager, self.load_groups)

    def delete_group(self):
        """删除分组"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的分组")
            return

        # 获取选中的分组名称
        item = selection[0]
        values = self.tree.item(item, "values")
        group_name = values[0]

        # 确认删除
        confirm = messagebox.askyesno(
            "确认删除",
            f"确定要删除分组「{group_name}」吗？\n\n"
            f"删除后，所有测试数据中的该分组标记也会被移除。"
        )

        if not confirm:
            return

        # 删除分组
        success = self.config_manager.remove_test_group(group_name)

        if success:
            messagebox.showinfo("成功", f"分组「{group_name}」已删除")
            self.load_groups()
        else:
            messagebox.showerror("错误", f"删除分组「{group_name}」失败")


class GroupEditDialog:
    """分组编辑对话框（新增/修改）"""

    def __init__(self, parent, group_name, config_manager, callback):
        self.group_name = group_name  # None表示新增，否则表示修改
        self.config_manager = config_manager
        self.callback = callback  # 编辑完成后的回调函数

        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("新增分组" if group_name is None else "修改分组")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 如果是修改，加载原有数据
        if group_name:
            groups = self.config_manager.get_test_groups()
            for group in groups:
                if group["name"] == group_name:
                    self.original_data = group
                    break
        else:
            self.original_data = None

        # 创建界面
        self.create_interface()

        # 居中显示
        self.center_dialog()

    def center_dialog(self):
        """将对话框居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title = "新增分组" if self.group_name is None else "修改分组"
        title_label = ttk.Label(
            main_frame,
            text=title,
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 分组名称
        ttk.Label(main_frame, text="分组名称 *:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.name_entry = ttk.Entry(main_frame, width=30, font=("Arial", 11))
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10)

        # 描述
        ttk.Label(main_frame, text="描述:").grid(row=2, column=0, sticky=tk.NW, pady=10)
        self.description_text = tk.Text(main_frame, width=30, height=5, font=("Arial", 11), wrap=tk.WORD)
        self.description_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10)

        # 如果是修改，填充原有数据
        if self.original_data:
            self.name_entry.insert(0, self.original_data["name"])
            self.description_text.insert(1.0, self.original_data.get("description", ""))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(
            button_frame,
            text="保存",
            command=self.save_group,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="取消",
            command=self.dialog.destroy,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # 配置网格权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def save_group(self):
        """保存分组"""
        # 获取输入
        name = self.name_entry.get().strip()
        description = self.description_text.get(1.0, tk.END).strip()

        # 验证
        if not name:
            messagebox.showwarning("警告", "请输入分组名称")
            return

        # 检查名称是否重复（排除自己）
        groups = self.config_manager.get_test_groups()
        for group in groups:
            if group["name"] == name:
                if self.group_name is None or group["name"] != self.group_name:
                    messagebox.showerror("错误", f"分组名称「{name}」已存在")
                    return

        # 保存
        if self.group_name is None:
            # 新增
            success = self.config_manager.add_test_group(name, description)
            if success:
                messagebox.showinfo("成功", f"分组「{name}」已添加")
            else:
                messagebox.showerror("错误", f"添加分组「{name}」失败")
        else:
            # 修改
            success = self.config_manager.update_test_group(self.group_name, name, description)
            if success:
                messagebox.showinfo("成功", f"分组「{name}」已修改")
            else:
                messagebox.showerror("错误", f"修改分组「{self.group_name}」失败")

        # 关闭对话框并刷新列表
        self.dialog.destroy()
        self.callback()

"""
字体设置窗口
用于设置界面字体大小
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_manager import ConfigManager


class FontSettingsWindow:
    """字体设置窗口"""

    def __init__(self, parent):
        self.parent = parent
        self.config_manager = ConfigManager()

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("字体设置")
        self.window.geometry("550x400")  # 增加高度以确保按钮可见
        self.window.transient(parent)
        self.window.grab_set()

        # 加载当前设置
        self.font_size = self.config_manager.get_font_size()

        # 创建界面
        self.create_interface()

        # 居中显示
        self.center_window()

    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="🔤 字体大小设置",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 字体大小选择
        size_label = ttk.Label(main_frame, text="选择字体大小:", font=("Arial", 11))
        size_label.grid(row=1, column=0, sticky=tk.W, pady=10)

        self.font_size_var = tk.StringVar(value=str(self.font_size))

        # 字体大小下拉框
        font_sizes = ["8", "9", "10", "11", "12", "13", "14", "15", "16", "18", "20"]
        font_combo = ttk.Combobox(
            main_frame,
            textvariable=self.font_size_var,
            values=font_sizes,
            state="readonly",
            width=20,
            font=("Arial", 11)
        )
        font_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))

        # 预览
        preview_label = ttk.Label(main_frame, text="预览:", font=("Arial", 11))
        preview_label.grid(row=2, column=0, sticky=tk.W, pady=(20, 10))

        self.preview_text = tk.Text(
            main_frame,
            width=40,
            height=6,
            font=("Arial", self.font_size),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            bg="#F7FAFC"
        )
        self.preview_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # 预览内容
        preview_content = """这是字体大小预览。

The quick brown fox jumps over the lazy dog.

中文字体测试：这是一段示例文本，用于预览字体大小效果。"""
        self.preview_text.insert(1.0, preview_content)
        self.preview_text.config(state=tk.DISABLED)

        # 绑定下拉框变化事件
        font_combo.bind("<<ComboboxSelected>>", self.update_preview)

        # 配置网格权重，让按钮区域固定在底部
        main_frame.rowconfigure(4, weight=0)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(30, 10), sticky=(tk.E))

        # 保存按钮
        save_button = ttk.Button(
            button_frame,
            text="💾 保存",
            command=self.save_settings,
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
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def update_preview(self, event=None):
        """更新预览"""
        try:
            new_size = int(self.font_size_var.get())
            self.preview_text.config(font=("Arial", new_size))
        except ValueError:
            pass

    def save_settings(self):
        """保存设置"""
        try:
            new_size = int(self.font_size_var.get())

            # 保存到配置
            self.config_manager.save_font_size(new_size)

            messagebox.showinfo("成功", f"字体大小已设置为 {new_size}\n\n重启应用后生效。")

            # 关闭窗口
            self.window.destroy()

        except ValueError:
            messagebox.showerror("错误", "无效的字体大小")
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

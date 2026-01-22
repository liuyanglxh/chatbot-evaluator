"""
大模型设置窗口
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
import threading

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_manager import ConfigManager
from models import get_model


class ModelSettingsWindow:
    """大模型设置窗口"""

    def __init__(self, parent):
        self.config_manager = ConfigManager()

        # 创建新窗口
        self.window = tk.Toplevel(parent)
        self.window.title("大模型设置")
        self.window.geometry("650x500")
        self.window.transient(parent)
        self.window.grab_set()

        # 加载当前配置
        self.current_config = self.config_manager.get_model_settings()

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
            text="大模型设置",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 大模型类型
        ttk.Label(main_frame, text="大模型类型:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.model_type_var = tk.StringVar(value=self.current_config.get("model_type", ""))
        model_type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.model_type_var,
            values=[
                "qwen-max",
                "qwen-plus",
                "qwen-turbo",
                "deepseek-chat",
                "deepseek-coder",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-4o",
                "其他"
            ],
            state="readonly",
            width=30
        )
        model_type_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Base URL
        ttk.Label(main_frame, text="Base URL:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.base_url_var = tk.StringVar(value=self.current_config.get("base_url", ""))
        base_url_entry = ttk.Entry(
            main_frame,
            textvariable=self.base_url_var,
            width=30
        )
        base_url_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # 常用 Base URL 提示
        url_hint = ttk.Label(
            main_frame,
            text="💡 通义千问: https://dashscope.aliyuncs.com/compatible-mode/v1",
            font=("Arial", 9),
            foreground="gray"
        )
        url_hint.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=(0, 10))

        # API Key
        ttk.Label(main_frame, text="API Key:").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.api_key_var = tk.StringVar(value=self.current_config.get("api_key", ""))
        api_key_entry = ttk.Entry(
            main_frame,
            textvariable=self.api_key_var,
            show="*",
            width=30
        )
        api_key_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=10)

        # 显示/隐藏 API Key 按钮
        self.show_key_button = ttk.Button(
            main_frame,
            text="👁️",
            command=self.toggle_api_key,
            width=5
        )
        self.show_key_button.grid(row=4, column=2, sticky=tk.W, padx=(10, 0), pady=10)

        # 测试连接按钮
        test_button = ttk.Button(
            main_frame,
            text="🔍 测试连接",
            command=self.test_connection,
            width=20
        )
        test_button.grid(row=5, column=0, columnspan=3, pady=15)

        # 测试结果显示区域
        self.test_result_frame = ttk.LabelFrame(
            main_frame,
            text="测试结果",
            padding="10"
        )
        self.test_result_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.test_result_text = tk.Text(
            self.test_result_frame,
            height=6,
            width=50,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        self.test_result_text.pack(fill=tk.BOTH, expand=True)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=(20, 0))

        # 保存按钮
        save_button = ttk.Button(
            button_frame,
            text="💾 保存",
            command=self.save_settings,
            width=15
        )
        save_button.grid(row=0, column=0, padx=5)

        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="❌ 取消",
            command=self.window.destroy,
            width=15
        )
        cancel_button.grid(row=0, column=1, padx=5)

        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def toggle_api_key(self):
        """切换 API Key 显示/隐藏"""
        current_mode = self.api_key_var._entryWidget.cget('show')

        # 找到 API Key Entry 组件
        for widget in self.window.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Entry):
                        if child.cget('show') == '*':
                            child.config(show='')
                            self.show_key_button.config(text='🙈')
                            return
                        elif child.cget('show') == '':
                            # 检查是否是 API Key 那个 Entry
                            if str(child.cget('textvariable')) == str(self.api_key_var):
                                child.config(show='*')
                                self.show_key_button.config(text='👁️')
                                return

    def test_connection(self):
        """测试连接"""
        model_type = self.model_type_var.get().strip()
        base_url = self.base_url_var.get().strip()
        api_key = self.api_key_var.get().strip()

        # 验证必填项
        if not model_type:
            messagebox.showerror("错误", "请选择大模型类型")
            return

        if not base_url:
            messagebox.showerror("错误", "请输入 Base URL")
            return

        if not api_key:
            messagebox.showerror("错误", "请输入 API Key")
            return

        # 在新线程中测试，避免阻塞 UI
        self.set_test_result("⏳ 正在测试连接，请稍候...\n")

        thread = threading.Thread(target=self._test_connection_thread, args=(model_type, base_url, api_key))
        thread.daemon = True
        thread.start()

    def _test_connection_thread(self, model_type, base_url, api_key):
        """在后台线程中测试连接"""
        try:
            # 创建模型实例
            model = get_model(model_type, base_url, api_key)

            # 测试连接
            success, message = model.test_connection()

            # 更新 UI
            self.window.after(0, self._update_test_result, success, message)

        except Exception as e:
            self.window.after(0, self._update_test_result, False, f"测试失败: {str(e)}")

    def _update_test_result(self, success: bool, message: str):
        """更新测试结果"""
        if success:
            result_text = f"✅ {message}\n\n"
            result_text += f"模型类型: {self.model_type_var.get()}\n"
            result_text += f"Base URL: {self.base_url_var.get()}\n"
            result_text += f"API Key: {'*' * len(self.api_key_var.get())}"
            self.set_test_result(result_text, color="green")
        else:
            self.set_test_result(f"❌ {message}", color="red")

    def set_test_result(self, text: str, color: str = "black"):
        """设置测试结果文本"""
        self.test_result_text.config(state=tk.NORMAL)
        self.test_result_text.delete(1.0, tk.END)
        self.test_result_text.insert(tk.END, text)
        self.test_result_text.config(state=tk.DISABLED)

    def save_settings(self):
        """保存设置"""
        model_type = self.model_type_var.get().strip()
        base_url = self.base_url_var.get().strip()
        api_key = self.api_key_var.get().strip()

        # 验证必填项
        if not model_type:
            messagebox.showerror("错误", "请选择大模型类型")
            return

        if not base_url:
            messagebox.showerror("错误", "请输入 Base URL")
            return

        if not api_key:
            messagebox.showerror("错误", "请输入 API Key")
            return

        # 保存配置
        success = self.config_manager.update_model_settings(
            model_type=model_type,
            base_url=base_url,
            api_key=api_key
        )

        if success:
            messagebox.showinfo("成功", "✅ 大模型设置已保存")
            self.window.destroy()
        else:
            messagebox.showerror("错误", "❌ 保存设置失败")

    def center_window(self):
        """窗口居中显示"""
        self.window.update_idletasks()

        # 获取窗口尺寸
        width = self.window.winfo_width()
        height = self.window.winfo_height()

        # 获取屏幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # 设置窗口位置
        self.window.geometry(f'{width}x{height}+{x}+{y}')

"""
窗口辅助工具模块
提供通用的窗口功能
"""
import tkinter as tk
import platform


def bind_esc_key(window, close_callback=None):
    """
    为窗口绑定ESC键关闭功能

    Args:
        window: tkinter窗口对象（Toplevel或Tk）
        close_callback: 关闭时的回调函数，如果为None则调用window.destroy()
    """
    def on_esc(event):
        if close_callback:
            close_callback()
        else:
            window.destroy()

    # 绑定ESC键
    window.bind('<Escape>', on_esc)

    # 绑定到所有子组件，确保事件能被捕获
    try:
        window.bind_all('<Escape>', on_esc, add='+')
    except:
        pass

    # macOS特殊处理
    if platform.system() == 'Darwin':
        # macOS也可以使用Command+.
        window.bind('<Command-period>', on_esc)
        # 确保窗口可以接收键盘事件
        window.focus_set()
        # 等待窗口完全加载后再设置焦点
        window.after(100, lambda: window.focus_set())


def setup_esc_close_for_toplevel(window, close_callback=None):
    """
    为Toplevel窗口设置ESC键关闭（快捷方法）

    Args:
        window: Toplevel窗口对象
        close_callback: 可选的关闭回调函数
    """
    bind_esc_key(window, close_callback)

"""
窗口辅助工具模块
提供通用的窗口功能
"""
import tkinter as tk
from typing import List, Optional, Callable


# 全局窗口栈和关闭回调字典
_window_stack: List[tk.Toplevel] = []
_close_callbacks: dict = {}
_root_window: Optional[tk.Tk] = None
_global_binding_enabled = False


def register_window(window: tk.Toplevel, close_callback: Optional[Callable] = None) -> None:
    """
    注册窗口到ESC管理系统

    Args:
        window: tkinter窗口对象（Toplevel）
        close_callback: 关闭时的回调函数，如果为None则调用window.destroy()
    """
    global _window_stack, _close_callbacks

    # 将窗口添加到栈顶
    if window not in _window_stack:
        _window_stack.append(window)

    # 保存关闭回调
    if close_callback:
        _close_callbacks[window] = close_callback

    # 绑定窗口关闭事件，从栈中移除
    def on_window_close():
        unregister_window(window)

    # 绑定Destroy事件
    window.bind('<Destroy>', lambda e: on_window_close())


def unregister_window(window: tk.Toplevel) -> None:
    """
    从ESC管理系统中注销窗口

    Args:
        window: tkinter窗口对象
    """
    global _window_stack, _close_callbacks

    if window in _window_stack:
        _window_stack.remove(window)

    if window in _close_callbacks:
        del _close_callbacks[window]


def initialize_global_esc_handler(root: tk.Tk) -> None:
    """
    初始化全局ESC处理器（在主窗口中调用一次）

    Args:
        root: 主窗口对象
    """
    global _root_window, _global_binding_enabled

    if _global_binding_enabled:
        return

    _root_window = root

    def on_global_esc(event):
        """全局ESC键处理器"""
        global _window_stack, _close_callbacks

        if not _window_stack:
            return

        # 获取栈顶窗口
        top_window = _window_stack[-1]

        # 检查窗口是否还存在
        try:
            if top_window.winfo_exists():
                # 调用关闭回调或销毁窗口
                if top_window in _close_callbacks:
                    callback = _close_callbacks[top_window]
                    callback()
                else:
                    top_window.destroy()
            else:
                # 窗口已不存在，从栈中移除
                unregister_window(top_window)
        except tk.TclError:
            # 窗口已销毁，从栈中移除
            unregister_window(top_window)

    # 在根窗口绑定全局ESC键（使用bind_all确保捕获所有ESC事件）
    root.bind_all('<Escape>', on_global_esc)
    _global_binding_enabled = True


def bind_esc_key(window: tk.Toplevel, close_callback: Optional[Callable] = None) -> None:
    """
    为窗口绑定ESC键关闭功能（通过全局管理系统）

    Args:
        window: tkinter窗口对象（Toplevel）
        close_callback: 关闭时的回调函数，如果为None则调用window.destroy()
    """
    # 延迟注册，确保窗口完全创建
    window.after(100, lambda: register_window(window, close_callback))


def setup_esc_close_for_toplevel(window: tk.Toplevel, close_callback: Optional[Callable] = None) -> None:
    """
    为Toplevel窗口设置ESC键关闭（快捷方法）

    Args:
        window: Toplevel窗口对象
        close_callback: 可选的关闭回调函数
    """
    bind_esc_key(window, close_callback)


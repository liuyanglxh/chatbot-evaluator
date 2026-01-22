"""
评估结果弹窗预览
展示弹窗UI效果
"""
import tkinter as tk
from tkinter import ttk


def show_popup_preview():
    """显示弹窗预览"""
    # 创建主窗口
    root = tk.Tk()
    root.title("评估工具")
    root.geometry("400x300")
    root.withdraw()  # 隐藏主窗口

    # 模拟评估结果数据
    result_data = {
        'success': True,
        'score': 0.850,
        'passed': True,
        'reason': '该回答在事实方面与上下文一致，准确地回答了用户的问题。所有关键信息都被正确捕捉和呈现，没有发现任何事实错误或不一致之处。回答的逻辑清晰，数据准确，完全符合期望的标准。',
        'is_english': False
    }

    # 模拟评估器信息
    evaluator_info = {
        'name': '正确性评估器',
        'framework': 'DeepEval',
        'metric_type': 'Correctness',
        'threshold': 0.6
    }

    # 显示弹窗
    from windows.result_popup_window import ResultPopupWindow
    ResultPopupWindow(root, result_data, evaluator_info)

    # 运行
    root.mainloop()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("📊 评估结果弹窗预览")
    print("="*60)
    print("\n正在启动弹窗预览...\n")

    try:
        show_popup_preview()
    except Exception as e:
        print(f"预览失败: {str(e)}")
        print("\n请确保在正确的目录运行此脚本：")
        print("  cd evaluator_gui")
        print("  python preview_popup.py")

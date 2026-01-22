"""
测试中英文对照弹窗
"""
import tkinter as tk
from tkinter import ttk

# 模拟英文评估结果
english_test_data = {
    'success': True,
    'score': 0.0,
    'passed': False,
    'reason': 'The score is 0.00 because the actual output incorrectly states that there is no waiting period for critical illness insurance, contradicting the fact that such insurances typically have a waiting period of 90 or 180 days, during which any diagnosed illnesses are not covered.',
    'verbose_logs': '''Truths (limit=None):
[
    "重疾险的等待期通常是90天或180天。",
    "在等待期内确诊的疾病不赔付。"
]

Claims:
[
    "重疾险没有等待期，买了就能理赔。"
]

Verdicts:
[
    {
        "verdict": "no",
        "reason": "重疾险确实有等待期，通常是90天或180天。在等待期内确诊的疾病不赔付。"
    }
]'''
}

evaluator_info = {
    'name': '正确性评估器',
    'framework': 'DeepEval',
    'metric_type': 'Correctness',
    'threshold': 0.6
}

# 创建测试窗口
root = tk.Tk()
root.title("测试中英文对照弹窗")
root.geometry("400x300")

# 说明标签
label = tk.Label(
    root,
    text="点击下方按钮测试英文评估结果的中英文对照显示",
    font=("Arial", 12),
    wraplength=350,
    justify=tk.CENTER
)
label.pack(expand=True)

# 导入弹窗类
from windows.result_popup_window import ResultPopupWindow

def show_popup():
    """显示弹窗"""
    print("\n创建中英文对照测试弹窗...")
    print(f"reason 类型: 英文")
    print(f"verbose_logs 长度: {len(english_test_data['verbose_logs'])}")
    ResultPopupWindow(root, english_test_data, evaluator_info)

# 测试按钮
test_btn = ttk.Button(
    root,
    text="显示英文评估结果弹窗",
    command=show_popup
)
test_btn.pack(pady=20)

root.mainloop()

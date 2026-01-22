"""
测试弹窗显示
模拟实际的verbose_logs数据
"""
import tkinter as tk
from tkinter import ttk

# 模拟数据
test_data = {
    'success': True,
    'score': 0.0,
    'passed': False,
    'reason': 'The score is 0.00 because the actual output incorrectly states...',
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
root.withdraw()

# 导入弹窗类
from windows.result_popup_window import ResultPopupWindow

# 显示弹窗
print("\n创建测试弹窗...")
print(f"verbose_logs 长度: {len(test_data['verbose_logs'])}")
print(f"verbose_logs 类型: {type(test_data['verbose_logs'])}\n")

ResultPopupWindow(root, test_data, evaluator_info)

root.mainloop()

"""
批量替换"上下文"为"参考资料"
"""
import re
from pathlib import Path

def rename_context_to_reference(file_path):
    """替换文件中的上下文为参考资料"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    changes = 0

    # 替换各种形式的"上下文"
    replacements = [
        # Label和提示文本
        (r'上下文\（可选\）：', '参考资料（可选）：'),
        (r'上下文\（可选\）', '参考资料（可选）'),
        (r'"上下文"', '"参考资料"'),
        (r"'上下文'", "'参考资料'"),
        (r'上下文：', '参考资料：'),
        (r'上下文:', '参考资料:'),
        (r'上下文信息', '参考资料'),
        (r'参考上下文', '参考资料'),
        (r'无上下文', '无参考资料'),
        (r'包含上下文', '包含参考资料'),
        (r'提供上下文', '提供参考资料'),

        # 变量名（保持代码不变，只改显示文本）
        # 但需要改注释中的说明

        # 代码注释和文档字符串
        (r'# 上下文\（可选\）', '# 参考资料（可选）'),
        (r'# 上下文', '# 参考资料'),
    ]

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            changes += content.count(new)

    # 特殊处理：context 变量名在显示文本中的情况
    # 例如: text="上下文（可选）:"
    content = re.sub(r'text="上下文[^"]*"', lambda m: m.group(0).replace('上下文', '参考资料'), content)

    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

if __name__ == "__main__":
    print("开始批量替换'上下文'为'参考资料'...\n")

    # 需要修改的界面文件
    files = [
        Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/test_data_manager_window.py"),
        Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/evaluation_execution_window.py"),
        Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/result_popup_window.py"),
    ]

    changed_count = 0
    for file_path in files:
        if file_path.exists():
            print(f"处理: {file_path.name}")
            if rename_context_to_reference(file_path):
                print(f"  ✅ 已更新")
                changed_count += 1
            else:
                print(f"  ⊙ 无需更新")

    print(f"\n✅ 完成！共更新了 {changed_count} 个文件")

"""
批量更新弹窗字体，使用 font_manager
"""
import re
from pathlib import Path

def update_result_popup():
    """更新 result_popup_window.py"""
    file_path = Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/result_popup_window.py")
    content = file_path.read_text(encoding='utf-8')

    # 1. 添加导入
    if 'from font_utils import font_manager' not in content:
        # 在 threading 后面添加
        content = content.replace(
            'import threading',
            'import threading\nfrom font_utils import font_manager'
        )

    # 2. 替换标题字体 (24号粗体)
    content = re.sub(
        r'font=\("Arial", 24, "bold"\)',
        'font=font_manager.panel_title_font()',
        content
    )

    # 3. 替换大标题字体 (16号粗体)
    content = re.sub(
        r'font=\("Arial", 16, "bold"\)',
        'font=font_manager.panel_title_font()',
        content
    )

    # 4. 替换中标题字体 (14号粗体)
    content = re.sub(
        r'font=\("Arial", 14, "bold"\)',
        'font=font_manager.panel_font_bold()',
        content
    )

    # 5. 替换小标题字体 (11号粗体)
    content = re.sub(
        r'font=\("Arial", 11, "bold"\)',
        'font=font_manager.panel_font_bold()',
        content
    )

    # 6. 替换12号粗体
    content = re.sub(
        r'font=\("Arial", 12, "bold"\)',
        'font=font_manager.panel_font_bold()',
        content
    )

    # 7. 替换20号粗体（状态显示）
    content = re.sub(
        r'font=\("Arial", 20, "bold"\)',
        'font=font_manager.panel_title_font()',
        content
    )

    # 8. 替换普通内容字体 10号
    content = re.sub(
        r'font=\("Arial", 10\)',
        'font=font_manager.panel_font()',
        content
    )

    # 9. 替换普通内容字体 11号
    content = re.sub(
        r'font=\("Arial", 11\)',
        'font=font_manager.panel_font()',
        content
    )

    # 10. 替换普通内容字体 12号
    content = re.sub(
        r'font=\("Arial", 12\)',
        'font=font_manager.panel_font()',
        content
    )

    # 11. 替换16号字体（无粗体）
    content = re.sub(
        r'font=\("Arial", 16\)',
        'font=font_manager.panel_title_font()',
        content
    )

    # 保存
    file_path.write_text(content, encoding='utf-8')
    print("✅ result_popup_window.py 更新完成")

def update_evaluation_execution():
    """更新 evaluation_execution_window.py 中 EvaluationExecutionWindow 类的字体"""
    file_path = Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/evaluation_execution_window.py")
    content = file_path.read_text(encoding='utf-8')

    # 只处理 EvaluationExecutionWindow 类（行号约35-550）
    # 找到类的开始和结束位置
    lines = content.split('\n')
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if 'class EvaluationExecutionWindow:' in line:
            start_idx = i
        elif start_idx is not None and line.startswith('class ') and 'EvaluationExecutionWindow' not in line:
            end_idx = i
            break

    if start_idx is None:
        print("❌ 未找到 EvaluationExecutionWindow 类")
        return

    # 只处理这个类的内容
    class_content = '\n'.join(lines[start_idx:end_idx if end_idx else len(lines)])

    # 替换字体
    class_content = re.sub(r'font=\("Arial", 16, "bold"\)', 'font=font_manager.panel_title_font()', class_content)
    class_content = re.sub(r'font=\("Arial", 10\)', 'font=font_manager.panel_font_small()', class_content)
    class_content = re.sub(r'font=\("Arial", 11\)', 'font=font_manager.panel_font()', class_content)
    class_content = re.sub(r'font=\("Arial", 14, "bold"\)', 'font=font_manager.panel_font_bold()', class_content)
    class_content = re.sub(r'font=\("Arial", 12, "bold"\)', 'font=font_manager.panel_font_bold()', class_content)

    # 重新组合
    lines[start_idx:end_idx if end_idx else len(lines)] = [class_content]
    content = '\n'.join(lines)

    file_path.write_text(content, encoding='utf-8')
    print("✅ evaluation_execution_window.py (EvaluationExecutionWindow) 更新完成")

if __name__ == "__main__":
    print("开始更新字体设置...\n")
    update_result_popup()
    update_evaluation_execution()
    print("\n所有更新完成！")

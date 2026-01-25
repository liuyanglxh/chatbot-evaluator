"""
批量更新所有窗口字体，使用 font_manager
"""
import re
from pathlib import Path

def update_file_fonts(file_path, class_name=None):
    """
    更新指定文件的字体

    Args:
        file_path: 文件路径
        class_name: 可选，只更新特定类
    """
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"⚠️  文件不存在: {file_path}")
        return

    content = file_path.read_text(encoding='utf-8')

    # 如果已经导入了 font_manager，跳过
    if 'from font_utils import font_manager' in content:
        print(f"⊙ 已经导入 font_manager: {file_path.name}")
    else:
        # 添加导入（在第一个 import 之后）
        if 'import' in content:
            # 找到第一个 import
            lines = content.split('\n')
            import_idx = -1
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_idx = i
                    break

            if import_idx >= 0:
                # 在 import 区域的末尾添加
                for i in range(import_idx, len(lines)):
                    if lines[i].startswith('import ') or lines[i].startswith('from '):
                        import_idx = i
                    else:
                        break

                lines.insert(import_idx + 1, 'from font_utils import font_manager')
                content = '\n'.join(lines)
                print(f"✓ 添加导入: {file_path.name}")

    # 如果指定了类名，只处理该类
    if class_name:
        lines = content.split('\n')
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if f'class {class_name}' in line:
                start_idx = i
            elif start_idx is not None and line.startswith('class '):
                end_idx = i
                break

        if start_idx is None:
            print(f"⚠️  未找到类 {class_name}")
            return

        class_content = '\n'.join(lines[start_idx:end_idx if end_idx else len(lines)])
        class_content = replace_fonts(class_content)
        lines[start_idx:end_idx if end_idx else len(lines)] = [class_content]
        content = '\n'.join(lines)
    else:
        # 处理整个文件
        content = replace_fonts(content)

    # 保存
    file_path.write_text(content, encoding='utf-8')
    print(f"✅ 更新完成: {file_path.name}")

def replace_fonts(content):
    """替换所有硬编码字体"""

    # 标题字体 (24, 20, 18, 16号粗体) -> panel_title_font
    content = re.sub(r'font=\("Arial", (24|20|18), "bold"\)', 'font=font_manager.panel_title_font()', content)
    content = re.sub(r'font=\("Arial", 16, "bold"\)', 'font=font_manager.panel_title_font()', content)

    # 中标题 (14号粗体) -> panel_font_bold
    content = re.sub(r'font=\("Arial", 14, "bold"\)', 'font=font_manager.panel_font_bold()', content)

    # 小标题 (12, 11号粗体) -> panel_font_bold
    content = re.sub(r'font=\("Arial", (12|11), "bold"\)', 'font=font_manager.panel_font_bold()', content)

    # 普通内容 (10, 11, 12号) -> panel_font
    content = re.sub(r'font=\("Arial", (10|11|12)\)', 'font=font_manager.panel_font()', content)

    # 特殊：保持48号字体（错误图标）
    # content = re.sub(r'font=\("Arial", 48\)', 'font=("Arial", 48)', content)

    return content

if __name__ == "__main__":
    print("开始批量更新字体设置...\n")

    # 需要更新的文件列表
    files_to_update = [
        ("/Users/liuyang/deloitte/aia/evaluator_gui/windows/add_evaluator_window.py", None),
        ("/Users/liuyang/deloitte/aia/evaluator_gui/windows/group_manager_window.py", None),
        ("/Users/liuyang/deloitte/aia/evaluator_gui/windows/model_settings_window.py", None),
        ("/Users/liuyang/deloitte/aia/evaluator_gui/windows/test_data_manager_window.py", None),
        ("/Users/liuyang/deloitte/aia/evaluator_gui/windows/scoring_rules_table.py", None),
    ]

    for file_path, class_name in files_to_update:
        update_file_fonts(file_path, class_name)

    print("\n✅ 所有更新完成！")
    print("\n请重启应用查看效果。")

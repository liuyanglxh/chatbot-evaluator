"""
批量更新Entry和Combobox使用动态宽度
"""
import re
from pathlib import Path

def update_entry_combobox_width(file_path):
    """更新文件中的Entry和Combobox宽度"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    changes = 0

    # 查找所有需要修改的行
    lines = content.split('\n')
    new_lines = []

    for line in lines:
        new_line = line

        # 匹配 ttk.Entry(..., width=数字, ...)
        # 替换为使用 font_manager.get_entry_width()
        if re.search(r'ttk\.Entry\([^)]*width=\d+', line) and 'font_manager.get_entry_width()' not in line:
            # 提取原始宽度
            match = re.search(r'width=(\d+)', line)
            if match:
                original_width = match.group(1)
                # 替换
                new_line = re.sub(
                    r'width=(\d+)',
                    f'width=font_manager.get_entry_width({original_width})',
                    line
                )
                if new_line != line:
                    changes += 1

        # 匹配 ttk.Combobox(..., width=数字, ...)
        elif re.search(r'ttk\.Combobox\([^)]*width=\d+', line) and 'font_manager.get_entry_width()' not in line:
            match = re.search(r'width=(\d+)', line)
            if match:
                original_width = match.group(1)
                # 替换
                new_line = re.sub(
                    r'width=(\d+)',
                    f'width=font_manager.get_entry_width({original_width})',
                    line
                )
                if new_line != line:
                    changes += 1

        new_lines.append(new_line)

    if changes > 0:
        file_path.write_text('\n'.join(new_lines), encoding='utf-8')
        print(f"✅ {file_path.name}: 更新了 {changes} 处")
        return True
    else:
        print(f"⊙ {file_path.name}: 无需更新")
        return False

if __name__ == "__main__":
    print("开始批量更新Entry和Combobox宽度...\n")

    files = [
        Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/add_evaluator_window.py"),
        Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/evaluator_list_window.py"),
        Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/group_manager_window.py"),
        Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/test_data_manager_window.py"),
        Path("/Users/liuyang/deloitte/aia/evaluator_gui/windows/evaluation_execution_window.py"),
    ]

    total_changes = 0
    for file_path in files:
        if file_path.exists():
            if update_entry_combobox_width(file_path):
                total_changes += 1

    print(f"\n✅ 完成！共更新了 {total_changes} 个文件")

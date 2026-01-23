"""
批量重命名测试数据，添加Correctness前缀
"""
import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager


def rename_test_data():
    """重命名测试数据，添加Correctness前缀"""
    config_manager = ConfigManager()

    # 加载配置
    config = config_manager.load_config()
    test_data_list = config.get("test_data", [])

    if not test_data_list:
        print("没有找到测试数据")
        return

    print("=" * 60)
    print("批量重命名测试数据 - 添加Correctness前缀")
    print("=" * 60)
    print()

    rename_count = 0
    skip_count = 0

    for test_data in test_data_list:
        old_name = test_data.get('name', '')

        # 检查是否已经有Correctness前缀
        if old_name.startswith('Correctness-'):
            print(f"⊘ 跳过: {old_name} - 已有Correctness前缀")
            skip_count += 1
            continue

        # 添加Correctness前缀
        new_name = f"Correctness-{old_name}"
        test_data['name'] = new_name

        print(f"✓ 重命名: {old_name} → {new_name}")
        rename_count += 1

    # 保存配置
    if rename_count > 0:
        config_manager.save_config(config)
        print()
        print("=" * 60)
        print(f"✅ 成功重命名 {rename_count} 条测试数据")
        if skip_count > 0:
            print(f"⊘ 跳过 {skip_count} 条（已有前缀）")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("没有需要重命名的数据")
        if skip_count > 0:
            print(f"所有 {skip_count} 条数据都已有Correctness前缀")
        print("=" * 60)


if __name__ == "__main__":
    rename_test_data()

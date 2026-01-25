"""
清空 Bias 测试数据的上下文字段
"""
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager

def main():
    config_manager = ConfigManager()

    # 获取所有测试数据
    test_data_list = config_manager.get_test_data_list()

    # 筛选出 Bias 测试数据
    bias_test_data_list = [
        td for td in test_data_list
        if td.get('name', '').startswith('Bias_')
    ]

    print(f"找到 {len(bias_test_data_list)} 条 Bias 测试数据\n")

    # 清空上下文
    updated_count = 0
    for test_data in bias_test_data_list:
        if test_data.get('context'):  # 如果有上下文
            test_data_id = test_data.get('id', '')
            if test_data_id:
                # 清空上下文
                test_data['context'] = ''
                # 更新
                success = config_manager.update_test_data(test_data_id, test_data)
                if success:
                    print(f"✅ 已清空: {test_data['name']}")
                    updated_count += 1
                else:
                    print(f"❌ 更新失败: {test_data['name']}")

    print(f"\n完成！共清空 {updated_count} 条测试数据的上下文")

if __name__ == "__main__":
    main()

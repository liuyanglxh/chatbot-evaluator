"""
创建一个完整的示例自定义评估器
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager


def create_sample_custom_evaluator():
    """创建一个完整的示例自定义评估器"""
    print("="*60)
    print("创建完整的示例自定义评估器")
    print("="*60)

    config_manager = ConfigManager()

    # 查找并删除旧的测试评估器
    evaluators = config_manager.get_evaluators()
    for evaluator in evaluators:
        if evaluator.get('name') == 'Correctness-自定义':
            print(f"删除旧的测试评估器: {evaluator['name']}")
            config_manager.remove_evaluator(evaluator['id'])

    # 创建完整的自定义评估器
    sample_evaluator = {
        "name": "保险客服回答质量评估",
        "framework": "custom",
        "metric_type": "规则评分",
        "threshold": 0.6,
        "scoring_rules": [
            {
                "score": 0.2,
                "description": "回答完全错误，与问题无关或态度恶劣"
            },
            {
                "score": 0.4,
                "description": "回答部分正确，但缺少关键信息或不够详细"
            },
            {
                "score": 0.6,
                "description": "回答基本正确，信息完整，态度良好"
            },
            {
                "score": 0.8,
                "description": "回答准确，信息详细，提供了有价值的额外帮助"
            },
            {
                "score": 1.0,
                "description": "回答完美，信息准确详细，态度优秀，超出了客户预期"
            }
        ]
    }

    print(f"\n准备创建评估器:")
    print(f"  名称: {sample_evaluator['name']}")
    print(f"  框架: {sample_evaluator['framework']}")
    print(f"  类型: {sample_evaluator['metric_type']}")
    print(f"  阈值: {sample_evaluator['threshold']}")
    print(f"  评分规则数量: {len(sample_evaluator['scoring_rules'])}")

    print(f"\n评分规则:")
    for rule in sample_evaluator['scoring_rules']:
        print(f"  - {rule['score']}: {rule['description']}")

    # 添加评估器
    print(f"\n添加评估器...")
    success = config_manager.add_evaluator(sample_evaluator)

    if success:
        print("✅ 添加成功")

        # 重新加载并显示
        print(f"\n更新后的评估器列表:")
        evaluators = config_manager.get_evaluators()
        for i, eval in enumerate(evaluators, 1):
            framework_display = eval['framework']
            if eval['framework'] == 'custom':
                framework_display = "自定义"
            elif eval['framework'] == 'deepeval':
                framework_display = "DeepEval"
            elif eval['framework'] == 'ragas':
                framework_display = "Ragas"

            print(f"\n{i}. {eval['name']} ({framework_display} - {eval['metric_type']})")

            # 如果是自定义评估器，显示评分规则
            if eval.get('framework') == 'custom' and 'scoring_rules' in eval:
                print(f"   阈值: {eval['threshold']}")
                print(f"   评分规则:")
                for rule in eval['scoring_rules']:
                    print(f"     - {rule['score']}: {rule['description']}")

        return True
    else:
        print("❌ 添加失败")
        return False


if __name__ == "__main__":
    success = create_sample_custom_evaluator()
    sys.exit(0 if success else 1)

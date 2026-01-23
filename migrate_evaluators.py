"""
评估器数据迁移脚本
将硬编码在executor中的Prompt迁移到配置文件中
"""
import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager


def get_default_criteria(metric_type: str) -> str:
    """获取默认的评估标准（从executor中复制过来的）"""

    # 更宽松的匹配规则
    if "Role" in metric_type or "角色" in metric_type:
        return """评估回答是否符合专业保险客服的角色要求：

**语气要求：**
- 专业、礼貌、友好
- 有同理心和关怀
- 使用适当的称呼（如"您好"、"请问"）

**内容要求：**
- 提供准确的保险信息
- 给出具体的建议
- 避免误导性表述

**禁忌行为：**
- 不随意、不冷漠
- 不说"你爱买不买"这种话
- 不贬低客户

请根据以上标准评估回答（0-1分，1分为完全符合）。"""

    elif "Correctness" in metric_type or "正确性" in metric_type:
        return """评估回答在事实、逻辑和数据上的准确无误程度：

**1分：** 期望答案与实际答案描述的事实完全不一致或语义相反

**2分：** 期望答案与实际答案描述的事实稍有相近，但具体细节不一致

**3分：** 期望答案与实际答案描述的事实勉强一致，但细节不足

**4分：** 期望答案与实际答案描述的事实一致，只是词汇相近

**5分：** 期望答案与实际答案描述的事实完全一致，内容十分一致

请根据此标准评分（0-1分）。"""

    elif "Conversation Completeness" in metric_type or "对话完整性" in metric_type:
        return """评估对话回答的完整性和质量：

**评估维度：**

1. **信息完整性（40%）：**
   - 是否回答了用户问题的所有方面
   - 是否提供了必要的关键信息
   - 是否遗漏了重要细节

2. **逻辑连贯性（30%）：**
   - 回答是否前后一致、逻辑清晰
   - 论述是否有条理、层次分明
   - 是否存在自相矛盾的内容

3. **内容充分性（30%）：**
   - 解释是否充分、易于理解
   - 是否提供了具体的例子或说明
   - 是否避免了过于简略或含糊

**评分标准：**

**1分（0.0-0.2）：不完整**
- 回答严重不完整，只回答了问题的很小一部分
- 缺少关键信息，用户需要多次追问
- 逻辑混乱，前后矛盾

**2分（0.2-0.4）：较不完整**
- 回答了部分问题，但遗漏重要信息
- 逻辑基本清楚，但有些地方不够连贯
- 内容不够充分，需要补充说明

**3分（0.4-0.6）：中等完整**
- 回答了问题的主要方面，但细节不够
- 逻辑基本清晰，偶有不连贯之处
- 内容基本充分，但可以更详细

**4分（0.6-0.8）：较完整**
- 回答了问题的大部分方面，细节较完整
- 逻辑清晰连贯，论述有条理
- 内容充分，提供了适当的解释

**5分（0.8-1.0）：完整**
- 全面回答了问题的所有方面，信息完整
- 逻辑清晰严密，论述层次分明
- 内容非常充分，解释详细易懂

请根据以上标准评估对话完整性（0-1分）。"""

    else:
        # 对于GEval或其他自定义类型，返回一个通用模板
        return """请评估AI回答的质量，考虑以下方面：

1. **准确性** - 回答是否准确、符合事实
2. **相关性** - 回答是否与问题相关
3. **完整性** - 回答是否完整、提供了必要信息
4. **清晰性** - 回答是否清晰、易于理解

请根据以上标准评估回答（0-1分）。"""


def migrate_evaluators():
    """迁移评估器数据，添加criteria字段"""
    config_manager = ConfigManager()

    # 加载当前配置
    config = config_manager.load_config()
    evaluators = config.get("evaluators", [])

    if not evaluators:
        print("没有需要迁移的评估器")
        return

    print(f"开始迁移 {len(evaluators)} 个评估器...")

    # 需要迁移的评估器类型
    needs_criteria_types = [
        "Conversation Completeness",
        "对话完整性",
        "Role",
        "角色",
        "Correctness",
        "正确性",
        "GEval",
        "Custom"
    ]

    migrated_count = 0

    for evaluator in evaluators:
        metric_type = evaluator.get("metric_type", "")

        # 如果已经有criteria，跳过
        if "criteria" in evaluator:
            print(f"✓ 跳过（已有criteria）: {evaluator['name']}")
            continue

        # 检查是否需要迁移
        needs_criteria = any(mt in metric_type for mt in needs_criteria_types)

        if needs_criteria:
            # 获取默认criteria
            default_criteria = get_default_criteria(metric_type)

            if default_criteria:
                # 添加criteria到配置
                evaluator["criteria"] = default_criteria
                migrated_count += 1
                print(f"✓ 迁移: {evaluator['name']} ({metric_type})")
            else:
                print(f"⊘ 跳过（无默认criteria）: {evaluator['name']} ({metric_type})")
        else:
            print(f"⊘ 跳过（内置指标）: {evaluator['name']} ({metric_type})")

    # 保存更新后的配置
    if migrated_count > 0:
        config_manager.save_config(config)
        print(f"\n✅ 成功迁移 {migrated_count} 个评估器")
    else:
        print("\n无需迁移")

    # 显示最终配置
    print("\n迁移后的评估器配置:")
    print("=" * 60)
    for evaluator in evaluators:
        print(f"名称: {evaluator['name']}")
        print(f"类型: {evaluator['metric_type']}")
        has_criteria = "✓ 有criteria" if "criteria" in evaluator else "✗ 无criteria"
        print(f"状态: {has_criteria}")
        if "criteria" in evaluator:
            criteria_preview = evaluator["criteria"][:100] + "..." if len(evaluator["criteria"]) > 100 else evaluator["criteria"]
            print(f"预览: {criteria_preview}")
        print("-" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("评估器数据迁移工具")
    print("=" * 60)
    migrate_evaluators()

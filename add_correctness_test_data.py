"""
批量添加Correctness评估测试数据
涵盖1-5分的评分标准，每个标准3条数据
"""
import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager


def create_test_data():
    """创建测试数据"""

    test_data_list = []

    # ==================== 1分：完全不一致或语义相反 ====================

    # 1分-1: 主题完全不一致
    test_data_list.append({
        "name": "Correctness-1分-主题完全不同（保险vs旅游）",
        "question": "什么是车险理赔流程？",
        "answer": "旅游是一种放松身心的活动，可以选择去海边、山区或者城市观光。建议提前规划好行程，预订好酒店和机票。",
        "context": "车险理赔流程包括：1. 发生事故后立即报案（48小时内） 2. 保护现场等待交警处理 3. 收集理赔材料（事故认定书、维修发票等） 4. 提交理赔申请 5. 保险公司审核（3-5个工作日） 6. 赔款到账"
    })

    # 1分-2: 语义完全相反
    test_data_list.append({
        "name": "Correctness-1分-语义相反（允许vs不允许）",
        "question": "这个保险支持电子保单吗？",
        "answer": "很抱歉，该保险产品完全不支持电子保单，必须使用纸质保单，任何电子形式的保单都不被认可。",
        "context": "该保险产品完全支持电子保单，客户可以通过手机APP、微信小程序或官网下载和查看电子保单，电子保单与纸质保单具有同等法律效力。"
    })

    # 1分-3: 内容完全无关
    test_data_list.append({
        "name": "Correctness-1分-完全无关（理赔vs投保）",
        "question": "如何进行保险理赔？",
        "answer": "投保时需要准备身份证、驾驶证、行驶证等材料，填写投保单，选择保险方案，支付保费后即可完成投保。",
        "context": "保险理赔流程：1. 发生事故后立即拨打保险公司电话报案 2. 拍摄现场照片 3. 等待查勘员到达现场 4. 提交理赔材料 5. 等待审核结果 6. 收到赔款"
    })

    # ==================== 2分：稍有相近但细节不一致 ====================

    # 2分-1: 数值不一致
    test_data_list.append({
        "name": "Correctness-2分-数值不一致（25vs26元）",
        "question": "这个保险的手续费是多少？",
        "answer": "该保险产品需要支付26元的手续费。",
        "context": "该保险产品需要支付25元的手续费，在投保时一次性收取。"
    })

    # 2分-2: 日期不一致
    test_data_list.append({
        "name": "Correctness-2分-日期不一致（7月10日vs7月11日）",
        "question": "保险的生效日期是什么时候？",
        "answer": "保险将于2025年07月11日正式生效。",
        "context": "保险将于2025年07月10日正式生效，生效后即可享受保障。"
    })

    # 2分-3: 百分比不一致
    test_data_list.append({
        "name": "Correctness-2分-比例不一致（80%vs85%）",
        "question": "车险的赔付比例是多少？",
        "answer": "在发生事故时，保险公司会承担85%的损失费用，剩余15%由车主自行承担。",
        "context": "在发生事故时，保险公司会承担80%的损失费用，剩余20%由车主自行承担。"
    })

    # ==================== 3分：勉强一致但细节不足 ====================

    # 3分-1: 流程步骤缺失
    test_data_list.append({
        "name": "Correctness-3分-流程细节不足（3步vs1步）",
        "question": "车险报案流程是什么？",
        "answer": "车险报案流程是：发生事故后立即向保险公司报案。",
        "context": "车险报案流程包括：1. 发生事故后立即拨打保险公司报案电话（24小时服务） 2. 提供事故基本信息（时间、地点、人物） 3. 上传现场照片 4. 等待查勘员联系 5. 配合现场查勘"
    })

    # 3分-2: 关键信息过于简略
    test_data_list.append({
        "name": "Correctness-3分-信息过于简略（完整材料vs简单提及）",
        "question": "理赔需要准备哪些材料？",
        "answer": "理赔时需要准备一些基本证件和证明材料。",
        "context": "理赔需要准备以下材料：1. 事故责任认定书（交警出具） 2. 维修发票和清单 3. 驾驶证和行驶证复印件 4. 保险单号 5. 被保险人身份证 6. 银行账户信息（用于接收赔款）"
    })

    # 3分-3: 金额范围模糊
    test_data_list.append({
        "name": "Correctness-3分-金额范围模糊（具体金额vs模糊表述）",
        "question": "最高赔付金额是多少？",
        "answer": "最高赔付金额在几十万元左右。",
        "context": "该保险产品的最高赔付金额为50万元人民币，超过部分不在赔付范围内。"
    })

    # ==================== 4分：事实一致但词汇相近 ====================

    # 4分-1: 同义词替换
    test_data_list.append({
        "name": "Correctness-4分-同义词替换（费用vs价格）",
        "question": "这个保险的费用是多少？",
        "answer": "该保险的价格是每年365元。",
        "context": "该保险的费用是每年365元，按年支付。"
    })

    # 4分-2: 近似表达
    test_data_list.append({
        "name": "Correctness-4分-近似表达（支持vs可以办理）",
        "question": "支持退保吗？",
        "answer": "该保险可以办理退保手续。",
        "context": "该保险支持退保，投保人可以在任何时间申请退保，退保时将根据保单持有时间退还相应保费。"
    })

    # 4分-3: 相似措辞
    test_data_list.append({
        "name": "Correctness-4分-相似措辞（生效时间vs起效日期）",
        "question": "保险的生效时间是多久？",
        "answer": "保险的起效日期是投保后次日零点开始计算。",
        "context": "保险的生效时间是投保成功后次日零点开始计算，保障期限为一年。"
    })

    # ==================== 5分：完全一致 ====================

    # 5分-1: 完全匹配
    test_data_list.append({
        "name": "Correctness-5分-完全一致（保险退费流程）",
        "question": "保险退费流程是什么？",
        "answer": "保险退费流程如下：1. 填写退费申请表 2. 提交身份证明 3. 提供银行账户信息 4. 等待审核（5-7个工作日） 5. 退费到账。",
        "context": "保险退费流程：1. 填写退费申请表 2. 提交身份证明 3. 提供银行账户信息 4. 等待审核（5-7个工作日） 5. 退费到账"
    })

    # 5分-2: 内容完全一致
    test_data_list.append({
        "name": "Correctness-5分-内容完全一致（理赔材料）",
        "question": "理赔时需要提交哪些材料？",
        "answer": "理赔时需要提交：1. 事故责任认定书 2. 维修发票 3. 驾驶证和行驶证 4. 保险单号 5. 身份证 6. 银行账户信息。",
        "context": "理赔时需要提交：1. 事故责任认定书 2. 维修发票 3. 驾驶证和行驶证 4. 保险单号 5. 身份证 6. 银行账户信息"
    })

    # 5分-3: 完全准确
    test_data_list.append({
        "name": "Correctness-5分-完全准确（保障范围）",
        "question": "这个保险的保障范围包括哪些？",
        "answer": "该保险的保障范围包括：车辆损失险、第三者责任险、车上人员责任险、盗抢险、玻璃破碎险、自燃损失险、不计免赔险。",
        "context": "该保险的保障范围包括：车辆损失险、第三者责任险、车上人员责任险、盗抢险、玻璃破碎险、自燃损失险、不计免赔险"
    })

    return test_data_list


def main():
    """主函数"""
    config_manager = ConfigManager()

    print("=" * 60)
    print("批量添加Correctness评估测试数据")
    print("=" * 60)
    print()

    # 创建测试数据
    test_data_list = create_test_data()

    print(f"准备添加 {len(test_data_list)} 条测试数据...")
    print()

    success_count = 0
    skip_count = 0

    for i, test_data in enumerate(test_data_list, 1):
        name = test_data["name"]

        # 检查是否已存在
        existing = config_manager.get_test_data_by_name(name)
        if existing:
            print(f"⊘ 跳过 ({i}/{len(test_data_list)}): {name} - 已存在")
            skip_count += 1
            continue

        # 添加测试数据
        try:
            config_manager.add_test_data(test_data)
            print(f"✓ 添加成功 ({i}/{len(test_data_list)}): {name}")
            success_count += 1
        except Exception as e:
            print(f"✗ 添加失败 ({i}/{len(test_data_list)}): {name} - {e}")

    print()
    print("=" * 60)
    print(f"添加完成！")
    print(f"成功添加: {success_count} 条")
    print(f"跳过（已存在）: {skip_count} 条")
    print(f"失败: {len(test_data_list) - success_count - skip_count} 条")
    print("=" * 60)

    # 按分数分组统计
    print()
    print("测试数据分布：")
    print("-" * 60)
    print("1分（完全不一致或语义相反）: 3 条")
    print("  - 1分-主题完全不同（保险vs旅游）")
    print("  - 1分-语义相反（允许vs不允许）")
    print("  - 1分-完全无关（理赔vs投保）")
    print()
    print("2分（稍有相近但细节不一致）: 3 条")
    print("  - 2分-数值不一致（25vs26元）")
    print("  - 2分-日期不一致（7月10日vs7月11日）")
    print("  - 2分-比例不一致（80%vs85%）")
    print()
    print("3分（勉强一致但细节不足）: 3 条")
    print("  - 3分-流程细节不足（3步vs1步）")
    print("  - 3分-信息过于简略（完整材料vs简单提及）")
    print("  - 3分-金额范围模糊（具体金额vs模糊表述）")
    print()
    print("4分（事实一致但词汇相近）: 3 条")
    print("  - 4分-同义词替换（费用vs价格）")
    print("  - 4分-近似表达（支持vs可以办理）")
    print("  - 4分-相似措辞（生效时间vs起效日期）")
    print()
    print("5分（完全一致）: 3 条")
    print("  - 5分-完全一致（保险退费流程）")
    print("  - 5分-内容完全一致（理赔材料）")
    print("  - 5分-完全准确（保障范围）")
    print("-" * 60)


if __name__ == "__main__":
    main()

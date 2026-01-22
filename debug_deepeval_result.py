"""
调试脚本：查看DeepEval实际返回的数据结构
"""
import os
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置API（请替换为实际配置）
os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

try:
    from deepeval import evaluate
    from deepeval.test_case import LLMTestCase
    from deepeval.metrics import FaithfulnessMetric
    from deepeval.models.llms import GPTModel

    # 创建模型
    model = GPTModel(
        model="qwen-max",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    # 创建测试用例
    test_case = LLMTestCase(
        input="车险理赔需要准备哪些材料？",
        actual_output="需要准备事故责任认定书、维修发票、驾驶证和行驶证。",
        retrieval_context=["车险理赔材料包括：1.事故责任认定书 2.维修发票 3.驾驶证 4.行驶证"]
    )

    # 创建指标
    metric = FaithfulnessMetric(
        threshold=0.6,
        model=model
    )

    print("="*60)
    print("开始评估...")
    print("="*60)

    # 执行评估
    result = evaluate(test_cases=[test_case], metrics=[metric])

    print("\n" + "="*60)
    print("评估结果分析")
    print("="*60)

    # 查看result结构
    print("\n1. Result 类型:", type(result))
    print("2. Result 属性:", [a for a in dir(result) if not a.startswith('_')])

    # 查看test_results
    if hasattr(result, 'test_results'):
        test_result = result.test_results[0]
        print("\n3. TestResult 类型:", type(test_result))
        print("4. TestResult 属性:", [a for a in dir(test_result) if not a.startswith('_')])

        # 查看metrics_data
        if hasattr(test_result, 'metrics_data'):
            metrics_data = test_result.metrics_data
            print("\n5. MetricsData 长度:", len(metrics_data))

            if len(metrics_data) > 0:
                metric_data = metrics_data[0]
                print("\n6. MetricData 类型:", type(metric_data))
                print("7. MetricData 属性:", [a for a in dir(metric_data) if not a.startswith('_')])

                print("\n" + "="*60)
                print("关键字段内容:")
                print("="*60)

                print(f"\n✓ score: {metric_data.score}")
                print(f"✓ success: {metric_data.success}")
                print(f"✓ threshold: {metric_data.threshold}")
                print(f"✓ name: {metric_data.name}")

                print(f"\n✓ reason (长度: {len(metric_data.reason) if metric_data.reason else 0}):")
                if metric_data.reason:
                    print(f"  {metric_data.reason[:200]}...")

                print(f"\n✓ verbose_logs (长度: {len(metric_data.verbose_logs) if metric_data.verbose_logs else 0}):")
                if metric_data.verbose_logs:
                    print(f"  {metric_data.verbose_logs[:300]}...")
                else:
                    print("  None")

                # 检查其他可能的字段
                print(f"\n✓ evaluation_model: {getattr(metric_data, 'evaluation_model', 'N/A')}")
                print(f"✓ error: {getattr(metric_data, 'error', 'N/A')}")
                print(f"✓ strict_mode: {getattr(metric_data, 'strict_mode', 'N/A')}")

except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装 deepeval: pip install deepeval")
except Exception as e:
    print(f"执行失败: {e}")
    import traceback
    traceback.print_exc()

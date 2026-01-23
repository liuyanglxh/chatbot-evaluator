"""
DeepEval 评估执行器
真实调用 DeepEval 框架进行评估
"""
import os
from typing import Dict, Any
from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    BiasMetric,
    ToxicityMetric,
    GEval
)
from deepeval.models.llms import GPTModel


class DeepEvalExecutor:
    """DeepEval 评估执行器"""

    def __init__(self, evaluator_info: Dict[str, Any]):
        """
        初始化执行器

        Args:
            evaluator_info: 评估器配置
                {
                    'framework': 'deepeval',
                    'metric_type': 'Faithfulness',
                    'threshold': 0.6
                }
        """
        self.evaluator_info = evaluator_info
        self.metric_type = evaluator_info['metric_type']
        self.threshold = float(evaluator_info['threshold'])

        # 清除DeepEval缓存，确保使用最新的criteria
        self._clear_deepeval_cache()

    def _clear_deepeval_cache(self):
        """清除DeepEval缓存文件"""
        try:
            import os
            from pathlib import Path

            # 获取脚本所在目录（项目根目录）
            script_dir = Path(__file__).parent.parent
            cache_file = script_dir / ".deepeval" / ".deepeval-cache.json"

            print(f"🔍 查找DeepEval缓存: {cache_file}")
            print(f"   缓存文件是否存在: {cache_file.exists()}")

            if cache_file.exists():
                os.remove(cache_file)
                print(f"✅ 已清除DeepEval缓存: {cache_file}")
            else:
                print(f"ℹ️  DeepEval缓存文件不存在: {cache_file}")

        except Exception as e:
            print(f"⚠️  清除DeepEval缓存失败: {e}")

    def execute(self, question: str, answer: str, context: str, model_settings: Dict) -> Dict[str, Any]:
        """
        执行评估

        Args:
            question: 用户问题
            answer: Chatbot 回答
            context: 上下文（可选）
            model_settings: 大模型配置

        Returns:
            评估结果字典
        """
        try:
            # 1. 配置 API
            os.environ["OPENAI_API_KEY"] = model_settings['api_key']
            os.environ["OPENAI_BASE_URL"] = model_settings['base_url']

            # 2. 创建模型实例
            qwen_model = GPTModel(
                model=model_settings['model_type'],
                base_url=model_settings['base_url']
            )

            # 3. 创建测试用例
            test_case = self._create_test_case(question, answer, context)

            # 4. 创建评估指标
            metric = self._create_metric(qwen_model)

            # 5. 运行评估
            print(f"\n{'='*60}")
            print(f"开始评估: {self.metric_type}")
            print(f"{'='*60}")

            result = evaluate(test_cases=[test_case], metrics=[metric])

            # 6. 解析结果（传入原始数据）
            return self._parse_result(result, question, answer, context)

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"评估失败: {str(e)}"
            }

    def _create_test_case(self, question: str, answer: str, context: str) -> LLMTestCase:
        """创建测试用例"""
        # 准备 retrieval_context
        retrieval_context = [context] if context else []

        # 根据 metric_type 决定是否需要某些参数
        if self.metric_type in ["Faithfulness", "Contextual Precision", "Contextual Recall"]:
            # 这些指标需要 retrieval_context
            return LLMTestCase(
                input=question,
                actual_output=answer,
                retrieval_context=retrieval_context
            )
        elif self.metric_type in ["Answer Relevancy"]:
            # Answer Relevancy 需要 retrieval_context（用于生成反事实问题）
            return LLMTestCase(
                input=question,
                actual_output=answer,
                retrieval_context=retrieval_context
            )
        elif self.metric_type in ["Bias", "Toxicity"]:
            # Bias 和 Toxicity 只需要 actual_output
            return LLMTestCase(
                input=question,
                actual_output=answer
            )
        else:
            # 其他指标使用通用配置
            return LLMTestCase(
                input=question,
                actual_output=answer,
                retrieval_context=retrieval_context
            )

    def _create_metric(self, model):
        """创建评估指标"""
        metric_type = self.metric_type

        # Faithfulness (忠实度/正确性)
        if metric_type == "Faithfulness":
            return FaithfulnessMetric(
                threshold=self.threshold,
                model=model,
                verbose_mode=True,  # 启用详细模式
                include_reason=True  # 包含原因
            )

        # Answer Relevancy (答案相关性)
        elif metric_type == "Answer Relevancy" or metric_type == "答案相关性":
            return AnswerRelevancyMetric(
                threshold=self.threshold,
                model=model,
                verbose_mode=True,
                include_reason=True
            )

        # Bias (偏见)
        elif metric_type == "Bias":
            return BiasMetric(
                threshold=self.threshold,
                model=model,
                verbose_mode=True,
                include_reason=True
            )

        # Toxicity (毒性)
        elif metric_type == "Toxicity":
            return ToxicityMetric(
                threshold=self.threshold,
                model=model,
                verbose_mode=True,
                include_reason=True
            )

        # Contextual Precision
        elif metric_type == "Contextual Precision":
            from deepeval.metrics import ContextualPrecisionMetric
            return ContextualPrecisionMetric(
                threshold=self.threshold,
                model=model,
                verbose_mode=True,
                include_reason=True
            )

        # Contextual Recall
        elif metric_type == "Contextual Recall":
            from deepeval.metrics import ContextualRecallMetric
            return ContextualRecallMetric(
                threshold=self.threshold,
                model=model,
                verbose_mode=True,
                include_reason=True
            )

        # Contextual Relevancy
        elif metric_type == "Contextual Relevancy":
            from deepeval.metrics import ContextualRelevancyMetric
            return ContextualRelevancyMetric(
                threshold=self.threshold,
                model=model,
                verbose_mode=True,
                include_reason=True
            )

        # GEval (自定义评估)
        elif metric_type.startswith("GEval") or "Custom" in metric_type or \
             "Conversation Completeness" in metric_type or "对话完整性" in metric_type or \
             "Role Adherence" in metric_type or "角色遵循" in metric_type or \
             "Correctness" in metric_type or "正确性" in metric_type:
            # 优先使用配置中的criteria，如果没有则使用默认值
            criteria = self.evaluator_info.get("criteria", "")

            print("\n" + "="*60)
            print(f"创建GEval评估器")
            print(f"  metric_type: {metric_type}")
            print(f"  配置中的criteria长度: {len(criteria)}")
            print(f"  配置中的criteria内容: {criteria[:100] if criteria else '(空)'}...")

            if not criteria:
                print(f"  ⚠️  配置中无criteria，使用默认值")
                criteria = self._get_custom_criteria(metric_type)
            else:
                print(f"  ✅ 使用配置中的criteria")

            evaluation_params = self._get_evaluation_params(metric_type)

            print(f"  最终使用的criteria: {criteria[:100]}...")
            print(f"  evaluation_params: {evaluation_params}")
            print("="*60 + "\n")

            return GEval(
                name=metric_type,
                criteria=criteria,
                evaluation_params=evaluation_params,
                threshold=self.threshold,
                model=model,
                verbose_mode=True
                # 注意：GEval不支持include_reason参数
            )

        # 默认使用 Faithfulness
        else:
            return FaithfulnessMetric(
                threshold=self.threshold,
                model=model,
                verbose_mode=True,
                include_reason=True
            )

    def _get_custom_criteria(self, metric_type: str) -> str:
        """获取自定义评估标准"""
        # 根据不同的自定义类型返回不同的 criteria
        if "Role Adherence" in metric_type or "角色遵循" in metric_type:
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
            return """请评估回答的质量，考虑准确性、相关性和完整性。"""

    def _get_evaluation_params(self, metric_type: str) -> list:
        """获取 evaluation_params"""
        # 根据不同的自定义类型返回不同的参数
        if "Role Adherence" in metric_type or "角色遵循" in metric_type:
            return [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
        elif "Correctness" in metric_type or "正确性" in metric_type:
            return [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.RETRIEVAL_CONTEXT]
        elif "Conversation Completeness" in metric_type or "对话完整性" in metric_type:
            return [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
        else:
            return [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]

    def _parse_result(self, result, question: str, answer: str, context: str) -> Dict[str, Any]:
        """解析评估结果"""
        try:
            # 获取测试结果
            test_result = result.test_results[0]

            # 获取指标数据（注意：是 metrics_data 不是 metrics_results）
            metrics_data = test_result.metrics_data

            if not metrics_data or len(metrics_data) == 0:
                return {
                    'success': False,
                    'error': 'No metrics data returned',
                    'message': '评估失败: 未返回指标数据'
                }

            metric_data = metrics_data[0]

            # 检查是否有错误
            if hasattr(metric_data, 'error') and metric_data.error:
                return {
                    'success': False,
                    'error': metric_data.error,
                    'message': f"评估失败: {metric_data.error}"
                }

            # 提取分数
            score = metric_data.score if metric_data.score is not None else 0.0
            passed = metric_data.success

            # 获取原因（如果有）
            reason = metric_data.reason if metric_data.reason else ""
            if not reason:
                reason = "评估完成" if passed else "未达到阈值"

            # 获取详细日志（如果有）
            verbose_logs = getattr(metric_data, 'verbose_logs', None)

            # 调试：打印verbose_logs信息
            print(f"\n{'='*60}")
            print(f"Debug - verbose_logs 信息:")
            print(f"  是否存在: {verbose_logs is not None}")
            print(f"  类型: {type(verbose_logs)}")
            print(f"  长度: {len(verbose_logs) if verbose_logs else 0}")
            if verbose_logs and len(verbose_logs) > 0:
                print(f"  前500字符: {verbose_logs[:500]}")
            print(f"{'='*60}\n")

            # 构建详细信息（包含输入数据）
            detail_info = {
                'success': True,
                'score': score,
                'passed': passed,
                'reason': reason,
                'verbose_logs': verbose_logs,
                'input': {  # 新增：包含输入数据
                    'question': question,
                    'answer': answer,
                    'context': context
                }
            }

            # 构建消息
            message = f"评估器：{self.evaluator_info.get('name', '')}\n"
            message += f"框架：DeepEval\n"
            message += f"类型：{self.metric_type}\n\n"
            message += f"{'✅ 通过' if passed else '❌ 失败'}\n"
            message += f"得分：{score:.3f} / {self.threshold}\n\n"
            message += f"评估原因：\n{reason}\n"

            # 检测是否为英文
            is_english = self._is_english_text(reason)

            return {
                'success': True,
                'score': score,
                'passed': passed,
                'message': message,
                'reason': reason,
                'verbose_logs': verbose_logs,  # 添加详细日志
                'is_english': is_english,
                'input': {  # 添加输入数据
                    'question': question,
                    'answer': answer,
                    'context': context
                }
            }

        except Exception as e:
            # 添加详细的调试信息
            import traceback
            error_details = f"{str(e)}\n\n"
            error_details += f"Result type: {type(result)}\n"
            error_details += f"Result attributes: {([a for a in dir(result) if not a.startswith('_')])}\n"

            if hasattr(result, 'test_results'):
                error_details += f"\ntest_results length: {len(result.test_results)}\n"
                if len(result.test_results) > 0:
                    test_result = result.test_results[0]
                    error_details += f"test_result type: {type(test_result)}\n"
                    error_details += f"test_result attributes: {([a for a in dir(test_result) if not a.startswith('_')])}\n"

            error_details += f"\n{traceback.format_exc()}"

            return {
                'success': False,
                'error': str(e),
                'message': f"结果解析失败: {str(e)}",
                'debug_info': error_details
            }

    def _is_english_text(self, text: str) -> bool:
        """检测文本是否为英文"""
        if not text:
            return False

        # 简单的判断：如果中文字符少于 20%，认为是英文
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        total_chars = len(text)

        if total_chars == 0:
            return False

        chinese_ratio = chinese_chars / total_chars
        return chinese_ratio < 0.2

"""
自定义规则评分执行器
根据用户定义的评分规则进行评估
"""
import json
import re
from typing import Dict, Any
from models import get_model


class CustomExecutor:
    """自定义规则评分执行器"""

    def __init__(self, evaluator_info: Dict[str, Any]):
        """
        初始化执行器

        Args:
            evaluator_info: 评估器配置
                {
                    'framework': 'custom',
                    'metric_type': '规则评分',
                    'threshold': 0.5,
                    'scoring_rules': [
                        {'score': 0.2, 'description': '...'},
                        {'score': 1.0, 'description': '...'}
                    ]
                }
        """
        self.evaluator_info = evaluator_info
        self.metric_type = evaluator_info['metric_type']
        self.threshold = float(evaluator_info.get('threshold', 0.5))
        self.scoring_rules = evaluator_info.get('scoring_rules', [])

        if not self.scoring_rules:
            raise ValueError("评分规则不能为空")

        # 按分数排序（从低到高），方便Prompt生成
        self.scoring_rules = sorted(self.scoring_rules, key=lambda x: x['score'])

        print(f"\n{'='*60}")
        print(f"初始化 CustomExecutor")
        print(f"  评分规则数量: {len(self.scoring_rules)}")
        for rule in self.scoring_rules:
            print(f"    - {rule['score']}: {rule['description'][:50]}...")
        print(f"{'='*60}\n")

    def execute(self, question: str, answer: str, context: str, model_settings: Dict, expected_answer: str = None) -> Dict[str, Any]:
        """
        执行评估

        Args:
            question: 用户问题（多轮模式下为完整对话文本）
            answer: Chatbot 回答（多轮模式下为空）
            context: 上下文（多轮模式下为空）
            model_settings: 大模型配置
            expected_answer: 期望回答（可选）

        Returns:
            评估结果字典
        """
        try:
            # 1. 检测是否为多轮对话
            is_multi_turn = self._is_multi_turn_conversation(question)

            # 2. 创建模型
            model = get_model(
                model_settings['model_type'],
                model_settings['base_url'],
                model_settings['api_key']
            )

            # 3. 生成Prompt
            prompt = self._build_prompt(question, answer, context, is_multi_turn, expected_answer)

            print(f"\n{'='*60}")
            if is_multi_turn:
                print(f"【多轮对话评估】")
            print(f"发送给LLM的Prompt:")
            print(f"{prompt}")
            print(f"{'='*60}\n")

            # 4. 调用LLM
            response = model._send_request(prompt)

            if not response.get('success'):
                error_msg = response.get('error', '未知错误')
                return {
                    'success': False,
                    'error': error_msg,
                    'message': f"LLM调用失败: {error_msg}"
                }

            llm_response = response.get('content', '')

            print(f"\n{'='*60}")
            print(f"LLM返回:")
            print(f"{llm_response}")
            print(f"{'='*60}\n")

            # 5. 解析响应
            result = self._parse_response(llm_response)

            # 6. 判断是否通过
            score = result['score']
            passed = score >= self.threshold

            # 7. 构建返回结果
            return {
                'success': True,
                'score': score,
                'passed': passed,
                'reason': result['reason'],
                'verbose_logs': f"LLM原始响应:\n{llm_response}\n\n评分规则:\n{self._format_rules()}",
                'input': {
                    'question': question,
                    'answer': answer,
                    'context': context,
                    'expected_answer': expected_answer or ''  # 添加期望回答
                },
                'is_multi_turn': is_multi_turn,  # 标记是否为多轮评估
                'is_english': self._is_english_text(result['reason'])
            }

        except Exception as e:
            import traceback
            error_details = f"{str(e)}\n\n{traceback.format_exc()}"

            return {
                'success': False,
                'error': str(e),
                'message': f"评估失败: {str(e)}",
                'debug_info': error_details
            }

    def _is_multi_turn_conversation(self, question: str) -> bool:
        """检测是否为多轮对话"""
        # 多轮对话以"第1轮:"开头
        return question.strip().startswith("第1轮:")

    def _build_prompt(self, question: str, answer: str, context: str, is_multi_turn: bool = False, expected_answer: str = None) -> str:
        """构建评估Prompt（支持期望回答）"""

        # 构建评分标准部分
        rules_text = ""
        for rule in self.scoring_rules:
            score = rule['score']
            description = rule['description']
            rules_text += f"- 如果符合以下标准：\"{description}\"\n  则给出分数：{score}\n\n"

        if is_multi_turn:
            # 多轮对话的Prompt
            expected_part = ""
            if expected_answer and expected_answer.strip():
                expected_part = f"""

## 期望回答（参考标准）

以下是对话的理想回答，请作为评分的参考标准：

{expected_answer}

**注意：** 期望回答是一个参考标准，评估时应重点考察实际对话与期望回答的接近程度。
"""

            prompt = f"""你是一个专业的评估助手。请根据以下评分标准对多轮对话进行评估。

## 评分标准

{rules_text}
## 输入数据

以下是一段多轮对话:

{question}
{expected_part}
## 评估要求

1. 仔细阅读并理解整个多轮对话
{'2. 如果提供了期望回答，请将实际对话与期望回答进行对比' if expected_answer and expected_answer.strip() else '2. 仔细理解对话内容'}
3. 根据上述评分标准，选择最符合的一个分数
4. **必须从给定的分数中选择一个**，不能自定义其他分数
5. 给出详细的评分原因，说明为什么选择这个分数
6. 如果回答符合多个标准，选择分数最高的那个
7. 评估时应该关注整体对话的质量和连贯性

## 输出格式

请严格按照以下JSON格式返回结果，不要添加任何其他文字、解释或markdown标记：

{{
  "score": <分数，从上述标准中选择一个>,
  "reason": "<评分原因，详细说明为什么选择这个分数>"
}}

**重要：** 只返回JSON，不要有其他内容！
"""
        else:
            # 单轮对话的Prompt
            expected_part = ""
            if expected_answer and expected_answer.strip():
                expected_part = f"""

期望回答（参考标准）: {expected_answer}
"""

            prompt = f"""你是一个专业的评估助手。请根据以下评分标准对回答进行评估。

## 评分标准

{rules_text}
## 输入数据

问题：{question}

回答：{answer}

上下文：{context}
{expected_part}
## 评估要求

1. 仔细阅读并理解问题、回答和上下文
{'2. 如果提供了期望回答，请将实际回答与期望回答进行对比，重点考察接近程度' if expected_answer and expected_answer.strip() else '2. 仔细理解回答内容'}
3. 根据上述评分标准，选择最符合的一个分数
4. **必须从给定的分数中选择一个**，不能自定义其他分数
5. 给出详细的评分原因，说明为什么选择这个分数
6. 如果回答符合多个标准，选择分数最高的那个

## 输出格式

请严格按照以下JSON格式返回结果，不要添加任何其他文字、解释或markdown标记：

{{
  "score": <分数，从上述标准中选择一个>,
  "reason": "<评分原因，详细说明为什么选择这个分数>"
}}

**重要：** 只返回JSON，不要有其他内容！
"""

        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        # 清理响应（去除可能的markdown标记）
        cleaned_response = response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        print(f"\n清理后的响应:\n{cleaned_response}\n")

        # 尝试解析JSON
        try:
            result = json.loads(cleaned_response)

            score = result.get('score')
            reason = result.get('reason', '')

            # 验证分数
            if score is None:
                raise ValueError("JSON中缺少score字段")

            # 验证分数是否在有效范围内
            valid_scores = [rule['score'] for rule in self.scoring_rules]
            if score not in valid_scores:
                raise ValueError(f"分数 {score} 不在有效分数列表中: {valid_scores}")

            if not reason:
                reason = f"根据评分标准，给出分数 {score}"

            return {
                'score': float(score),
                'reason': reason
            }

        except json.JSONDecodeError as e:
            # JSON解析失败
            raise ValueError(f"JSON格式错误: {str(e)}\n\nLLM返回的内容:\n{response}")

        except Exception as e:
            # 其他错误
            raise ValueError(f"解析响应时出错: {str(e)}\n\nLLM返回的内容:\n{response}")

    def _format_rules(self) -> str:
        """格式化评分规则（用于verbose_logs）"""
        text = ""
        for rule in self.scoring_rules:
            text += f"- {rule['score']}: {rule['description']}\n"
        return text

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

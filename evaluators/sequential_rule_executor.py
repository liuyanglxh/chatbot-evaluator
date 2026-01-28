"""
顺序规则评估执行器
LLM对每个规则进行0/1判断，代码逻辑取第一个符合的规则的分数
"""
import json
import re
from typing import Dict, Any
from models import get_model


class SequentialRuleExecutor:
    """顺序规则评估执行器"""

    def __init__(self, evaluator_info: Dict[str, Any]):
        """
        初始化执行器

        Args:
            evaluator_info: 评估器配置
                {
                    'framework': 'sequential_rule',
                    'metric_type': '顺序规则',
                    'threshold': 0.5,
                    'scoring_rules': [
                        {'score': 1.0, 'description': '完全符合...'},
                        {'score': 2.0, 'description': '基本符合...'},
                        {'score': 3.0, 'description': '部分符合...'},
                        {'score': 4.0, 'description': '不符合...'},
                        {'score': 5.0, 'description': '完全不符合...'}
                    ]
                }
        """
        self.evaluator_info = evaluator_info
        self.metric_type = evaluator_info['metric_type']
        self.threshold = float(evaluator_info.get('threshold', 0.5))
        self.scoring_rules = evaluator_info.get('scoring_rules', [])

        if not self.scoring_rules:
            raise ValueError("评分规则不能为空")

        # 不排序，保持用户定义的顺序
        # self.scoring_rules = sorted(self.scoring_rules, key=lambda x: x['score'])

        print(f"\n{'='*60}")
        print(f"初始化 SequentialRuleExecutor")
        print(f"  评分规则数量: {len(self.scoring_rules)}")
        for i, rule in enumerate(self.scoring_rules, 1):
            print(f"    规则{i} (分数{rule['score']}): {rule['description'][:50]}...")
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

            # 6. 根据LLM返回的数组，找到第一个得分为1的规则，获取其分数和reason
            final_score, final_reason = self._calculate_final_score_and_reason(result['rule_results'])

            # 7. 判断是否通过
            passed = final_score >= self.threshold

            # 8. 构建返回结果
            return {
                'success': True,
                'score': final_score,
                'passed': passed,
                'reason': final_reason,
                'verbose_logs': f"LLM原始响应:\n{llm_response}\n\n规则评分:\n{self._format_rule_results(result['rule_results'])}",
                'input': {
                    'question': question,
                    'answer': answer,
                    'context': context,
                    'expected_answer': expected_answer or ''
                },
                'is_multi_turn': is_multi_turn,
                'is_english': self._is_english_text(final_reason)
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
        """构建评估Prompt（让LLM对每个规则进行0/1判断+理由）"""

        # 构建规则列表部分
        rules_text = ""
        for i, rule in enumerate(self.scoring_rules, 1):
            score = rule['score']
            description = rule['description']
            rules_text += f"规则{i}（分数{score}分）: {description}\n"

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

            prompt = f"""你是一个专业的评估助手。请根据以下规则对多轮对话进行评估。

## 评估规则

{rules_text}
## 输入数据

以下是一段多轮对话:

{question}
{expected_part}
## 评估要求

请按照上述规则的顺序，对每个规则进行判断：
- 如果回答**符合**该规则描述，该规则得1分，并简要说明原因
- 如果回答**不符合**该规则描述，该规则得0分，并简要说明原因

注意：你需要对**所有规则**都进行判断，不能只判断到第一个符合的规则就停止。

## 输出格式

请严格按照以下JSON格式返回结果，不要添加任何其他文字、解释或markdown标记：

[
  {{"score": 1, "reason": "符合该规则，因为..."}}, {{"score": 0, "reason": "不符合该规则，因为..."}}, ...]

返回格式说明：
- 外层是一个数组
- 每个元素对应一个规则（按规则顺序）
- 每个元素包含两个字段：
  - score: 0或1
  - reason: 该规则得0或1的原因（简短说明）

**重要：**
1. 必须返回数组，长度等于规则数量
2. 每个score必须是0或1
3. 必须对所有规则都进行判断
4. 只返回JSON数组，不要有其他内容！
"""
        else:
            # 单轮对话的Prompt
            expected_part = ""
            if expected_answer and expected_answer.strip():
                expected_part = f"""

期望回答（参考标准）: {expected_answer}
"""

            prompt = f"""你是一个专业的评估助手。请根据以下规则对回答进行评估。

## 评估规则

{rules_text}
## 输入数据

问题：{question}

回答：{answer}

上下文：{context}
{expected_part}
## 评估要求

请按照上述规则的顺序，对每个规则进行判断：
- 如果回答**符合**该规则描述，该规则得1分，并简要说明原因
- 如果回答**不符合**该规则描述，该规则得0分，并简要说明原因

注意：你需要对**所有规则**都进行判断，不能只判断到第一个符合的规则就停止。

## 输出格式

请严格按照以下JSON格式返回结果，不要添加任何其他文字、解释或markdown标记：

[
  {{"score": 1, "reason": "符合该规则，因为..."}}, {{"score": 0, "reason": "不符合该规则，因为..."}}, ...]

返回格式说明：
- 外层是一个数组
- 每个元素对应一个规则（按规则顺序）
- 每个元素包含两个字段：
  - score: 0或1
  - reason: 该规则得0或1的原因（简短说明）

**重要：**
1. 必须返回数组，长度等于规则数量
2. 每个score必须是0或1
3. 必须对所有规则都进行判断
4. 只返回JSON数组，不要有其他内容！
"""

        return prompt

    def _parse_response(self, llm_response: str) -> Dict[str, Any]:
        """解析LLM响应（数组格式）"""
        try:
            # 尝试直接解析JSON数组
            result_list = json.loads(llm_response.strip())

            if not isinstance(result_list, list):
                raise ValueError("响应必须是数组格式")

            if len(result_list) != len(self.scoring_rules):
                raise ValueError(f"数组长度({len(result_list)})与规则数量({len(self.scoring_rules)})不匹配")

            # 验证每个元素的格式
            for i, item in enumerate(result_list):
                if not isinstance(item, dict):
                    raise ValueError(f"规则{i+1}必须是对象格式")
                if 'score' not in item:
                    raise ValueError(f"规则{i+1}缺少score字段")
                if 'reason' not in item:
                    raise ValueError(f"规则{i+1}缺少reason字段")
                if item['score'] not in [0, 1]:
                    raise ValueError(f"规则{i+1}的score必须是0或1，当前为{item['score']}")

            return {
                'rule_results': result_list  # 直接存储完整的数组
            }

        except json.JSONDecodeError as e:
            # 尝试从markdown代码块中提取JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', llm_response, re.DOTALL)
            if json_match:
                try:
                    result_list = json.loads(json_match.group(1))
                    if isinstance(result_list, list):
                        return {'rule_results': result_list}
                except:
                    pass

            # 尝试正则匹配数组格式
            array_match = re.search(r'\[\s*\{.*?\}\s*(?:,\s*\{.*?\}\s*)*\]', llm_response, re.DOTALL)
            if array_match:
                try:
                    result_list = json.loads(array_match.group(0))
                    if isinstance(result_list, list):
                        return {'rule_results': result_list}
                except:
                    pass

            # 完全解析失败，返回默认值
            print(f"⚠️  JSON解析失败，使用默认分数")
            default_results = [{'score': 0, 'reason': f'解析失败: {str(e)}'} for _ in self.scoring_rules]
            return {
                'rule_results': default_results
            }

    def _calculate_final_score_and_reason(self, rule_results: list) -> tuple:
        """
        根据规则结果计算最终分数和reason
        取第一个得分为1的规则的分数和reason

        Returns:
            (final_score, final_reason) 元组
        """
        for i, rule_result in enumerate(rule_results):
            if rule_result['score'] == 1:
                # 找到第一个得分为1的规则
                final_score = self.scoring_rules[i]['score']
                final_reason = rule_result['reason']
                print(f"✅ 规则{i+1}符合（分数{final_score}），原因: {final_reason}")
                return (final_score, final_reason)

        # 如果所有规则都得0分，返回第一个规则的分数（最低分）和reason
        final_score = self.scoring_rules[0]['score']
        final_reason = rule_results[0]['reason'] if rule_results else "所有规则都不符合"
        print(f"⚠️  所有规则都不符合，返回最低分: {final_score}，原因: {final_reason}")
        return (final_score, final_reason)

    def _format_rule_results(self, rule_results: list) -> str:
        """格式化规则结果用于日志"""
        lines = []
        for i, (rule, result) in enumerate(zip(self.scoring_rules, rule_results), 1):
            score = result['score']
            reason = result['reason']
            status = "✅ 符合" if score == 1 else "❌ 不符合"
            lines.append(f"规则{i} ({rule['score']}分): {status} - {reason}")
        return "\n".join(lines)

    def _is_english_text(self, text: str) -> bool:
        """检测文本是否为英文"""
        if not text:
            return False

        # 统计中文字符
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        total_chars = len(text)

        # 如果中文字符占比少于20%，认为是英文
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
        return chinese_ratio < 0.2

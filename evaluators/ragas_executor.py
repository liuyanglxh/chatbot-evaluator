"""
DeepEval 评估执行器
真实调用 DeepEval 框架进行评估
"""
from typing import Dict, Any

from datasets import Dataset
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.llms import Tongyi
from ragas import evaluate
from ragas.metrics._answer_correctness import answer_correctness
from ragas.metrics._answer_relevance import answer_relevancy
from ragas.metrics._answer_similarity import answer_similarity
from ragas.metrics._context_precision import context_precision
from ragas.metrics._context_recall import context_recall
from ragas.metrics._faithfulness import faithfulness

metric_dict={"Faithfulness":faithfulness , # 忠实度
             "Answer Relevancy":answer_relevancy,# 答案相关性
             "Context Precision":context_precision,#上下文精度
             "Context Recall":context_recall,#上下文召回率
             "Context Relevancy":context_precision, #上下文相关性
             "Answer Correctness":answer_correctness, #答案正确性
             "Answer Similarity":answer_similarity, #答案相似性
             }

# 自定义嵌入类
class BatchingDashScopeEmbeddings(DashScopeEmbeddings):
    """自定义嵌入类，确保每次请求不超过 DashScope API 限制（10 个文本）"""

    def embed_documents(self, texts):
        all_embeddings = []
        batch_size = 10  # DashScope API 限制

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                embeddings = super().embed_documents(batch)
                all_embeddings.extend(embeddings)
            except Exception as e:
                raise RuntimeError(f"Error embedding batch {i}-{i + len(batch)}: {str(e)}") from e

        return all_embeddings

class RagasExecutor:
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

        # # 清除DeepEval缓存，确保使用最新的criteria
        # self._clear_deepeval_cache()
    #
    # def _clear_deepeval_cache(self):
    #     """清除DeepEval缓存文件"""
    #     try:
    #         import os
    #         from pathlib import Path
    #
    #         # 获取脚本所在目录（项目根目录）
    #         script_dir = Path(__file__).parent.parent
    #         cache_file = script_dir / ".deepeval" / ".deepeval-cache.json"
    #
    #         print(f"🔍 查找DeepEval缓存: {cache_file}")
    #         print(f"   缓存文件是否存在: {cache_file.exists()}")
    #
    #         if cache_file.exists():
    #             os.remove(cache_file)
    #             print(f"✅ 已清除DeepEval缓存: {cache_file}")
    #         else:
    #             print(f"ℹ️  DeepEval缓存文件不存在: {cache_file}")
    #
    #     except Exception as e:
    #         print(f"⚠️  清除DeepEval缓存失败: {e}")

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
            answers = [answer]
            contexts = [[context]]
            questions=[question]
            ground_truths=[answer]
            # To dict
            data = {
                "user_input": questions,
                "response": answers,
                "retrieved_contexts": contexts,
                "reference": ground_truths
            }

            # Convert dict to dataset
            dataset = Dataset.from_dict(data)
            # 初始化大语言模型
            DASHSCOPE_API_KEY = 'sk-a9f37cda2dff4410941489bc3c53496d'
            llm = Tongyi(
                model_name="qwen-max",
                dashscope_api_key=DASHSCOPE_API_KEY
            )

            # message: <400> InternalError.Algo.InvalidParameter: Value error, batch size is invalid, it should not be larger than 10.: input.contents
            # 创建嵌入模型
            embeddings = BatchingDashScopeEmbeddings(
                model="text-embedding-v4",
                dashscope_api_key=DASHSCOPE_API_KEY
            )
            metric=metric_dict[self.metric_type]

            # 评测结果
            result = evaluate(
                dataset=dataset,
                llm=llm,
                metrics=[
                    # context_precision,  # 上下文精度
                    # context_recall,  # 上下文召回率
                    # faithfulness,  # 忠实度
                    # answer_relevancy,  # 答案相关性
                    metric
                ],
                embeddings=embeddings
            )
            # 6. 解析结果（传入原始数据）
            return {
                'success': True,
                'score': result[metric.name][0],
                'passed': result[metric.name][0]>=0.6,
                'message': '',
                'reason': '',
                'verbose_logs': '',  # 添加详细日志
                'is_english': False,
                'input': {  # 添加输入数据
                    'question': question,
                    'answer': answer,
                    'context': context
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"评估失败: {str(e)}"
            }
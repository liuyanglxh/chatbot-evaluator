"""
HTML报告生成器
生成类似Microsoft Azure DevOps风格的AI评估报告
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import json


class HtmlReportGenerator:
    """HTML报告生成器"""

    def __init__(self, template_path: str = None):
        """
        初始化报告生成器

        Args:
            template_path: 自定义HTML模板路径（可选）
        """
        self.template_path = template_path

    def generate_report(
        self,
        all_results: Dict[str, Any],
        evaluators: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        生成HTML评估报告

        Args:
            all_results: 所有评估结果
                {
                    'conv_id': {
                        'turns': [...],
                        'results': {
                            'evaluator_name': [...]
                        }
                    }
                }
            evaluators: 评估器列表
            output_path: 输出HTML文件路径

        Returns:
            生成的HTML文件路径
        """
        # 计算统计数据
        stats = self._calculate_statistics(all_results, evaluators)

        # 生成HTML内容
        html_content = self._generate_html_content(
            all_results,
            evaluators,
            stats
        )

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _calculate_statistics(
        self,
        all_results: Dict[str, Any],
        evaluators: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算统计数据"""
        total_evaluations = 0
        passed_evaluations = 0
        total_score = 0.0
        evaluator_stats = {}

        # 初始化评估器统计
        for evaluator in evaluators:
            name = evaluator['name']
            evaluator_stats[name] = {
                'total': 0,
                'passed': 0,
                'score_sum': 0.0,
                'threshold': evaluator.get('threshold', 0.5)
            }

        # 遍历所有结果
        for conv_id, data in all_results.items():
            for evaluator_name, results in data['results'].items():
                for result in results:
                    total_evaluations += 1
                    score = result.get('score', 0)
                    total_score += score

                    if result.get('success', False):
                        passed_evaluations += 1

                    # 评估器级别统计
                    if evaluator_name in evaluator_stats:
                        evaluator_stats[evaluator_name]['total'] += 1
                        evaluator_stats[evaluator_name]['score_sum'] += score
                        if result.get('success', False):
                            evaluator_stats[evaluator_name]['passed'] += 1

        # 计算平均值
        avg_score = total_score / total_evaluations if total_evaluations > 0 else 0
        pass_rate = (passed_evaluations / total_evaluations * 100) if total_evaluations > 0 else 0

        # 计算每个评估器的平均分
        for name, stats in evaluator_stats.items():
            if stats['total'] > 0:
                stats['avg_score'] = stats['score_sum'] / stats['total']
                stats['pass_rate'] = (stats['passed'] / stats['total'] * 100)
            else:
                stats['avg_score'] = 0
                stats['pass_rate'] = 0

        return {
            'total_evaluations': total_evaluations,
            'passed_evaluations': passed_evaluations,
            'failed_evaluations': total_evaluations - passed_evaluations,
            'avg_score': avg_score,
            'pass_rate': pass_rate,
            'evaluator_stats': evaluator_stats
        }

    def _generate_html_content(
        self,
        all_results: Dict[str, Any],
        evaluators: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ) -> str:
        """生成HTML内容"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI评估报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-card h3 {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }}

        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-card.pass .value {{
            color: #28a745;
        }}

        .stat-card.fail .value {{
            color: #dc3545;
        }}

        .evaluator-stats {{
            padding: 40px;
        }}

        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}

        .evaluator-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .evaluator-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .evaluator-table td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        .evaluator-table tr:hover {{
            background: #f8f9fa;
        }}

        .evaluator-table tr:last-child td {{
            border-bottom: none;
        }}

        .score-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}

        .score-badge.high {{
            background: #d4edda;
            color: #155724;
        }}

        .score-badge.medium {{
            background: #fff3cd;
            color: #856404;
        }}

        .score-badge.low {{
            background: #f8d7da;
            color: #721c24;
        }}

        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s;
        }}

        .details-section {{
            padding: 40px;
            background: #f8f9fa;
        }}

        .conversation {{
            background: white;
            border-radius: 8px;
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .conversation-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .conversation-header:hover {{
            opacity: 0.95;
        }}

        .conversation-title {{
            font-size: 1.3em;
            font-weight: bold;
        }}

        .conversation-body {{
            padding: 20px;
        }}

        .turn {{
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}

        .turn-number {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .turn-content {{
            margin-bottom: 10px;
        }}

        .turn-content label {{
            font-weight: bold;
            color: #495057;
            display: block;
            margin-bottom: 5px;
        }}

        .evaluation-results {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}

        .evaluation-card {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
        }}

        .evaluation-card.passed {{
            border-left: 4px solid #28a745;
        }}

        .evaluation-card.failed {{
            border-left: 4px solid #dc3545;
        }}

        .evaluator-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}

        .score-display {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}

        .reason {{
            color: #6c757d;
            font-size: 0.95em;
            line-height: 1.6;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #e9ecef;
        }}

        .toggle-icon {{
            transition: transform 0.3s;
        }}

        .collapsed .toggle-icon {{
            transform: rotate(-90deg);
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}

            .evaluation-results {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>🤖 AI评估报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <!-- 摘要统计 -->
        <div class="summary">
            <div class="stat-card">
                <h3>总评估数</h3>
                <div class="value">{stats['total_evaluations']}</div>
            </div>
            <div class="stat-card pass">
                <h3>通过数</h3>
                <div class="value">{stats['passed_evaluations']}</div>
            </div>
            <div class="stat-card fail">
                <h3>失败数</h3>
                <div class="value">{stats['failed_evaluations']}</div>
            </div>
            <div class="stat-card">
                <h3>通过率</h3>
                <div class="value">{stats['pass_rate']:.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>平均得分</h3>
                <div class="value">{stats['avg_score']:.3f}</div>
            </div>
        </div>

        <!-- 评估器统计 -->
        <div class="evaluator-stats">
            <h2 class="section-title">📊 评估器统计</h2>
            <table class="evaluator-table">
                <thead>
                    <tr>
                        <th>评估器名称</th>
                        <th>框架</th>
                        <th>阈值</th>
                        <th>评估次数</th>
                        <th>通过数</th>
                        <th>通过率</th>
                        <th>平均分</th>
                    </tr>
                </thead>
                <tbody>
"""

        # 添加评估器统计行
        for evaluator in evaluators:
            name = evaluator['name']
            framework = evaluator.get('framework', '')
            estats = stats['evaluator_stats'].get(name, {})

            # 框架显示名称
            framework_display = framework.upper() if framework else '-'

            # 通过率颜色
            pass_rate_class = 'high' if estats.get('pass_rate', 0) >= 70 else 'medium' if estats.get('pass_rate', 0) >= 50 else 'low'

            html += f"""
                    <tr>
                        <td><strong>{name}</strong></td>
                        <td>{framework_display}</td>
                        <td>{estats.get('threshold', 0)}</td>
                        <td>{estats.get('total', 0)}</td>
                        <td>{estats.get('passed', 0)}</td>
                        <td><span class="score-badge {pass_rate_class}">{estats.get('pass_rate', 0):.1f}%</span></td>
                        <td>{estats.get('avg_score', 0):.3f}</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>

        <!-- 详细结果 -->
        <div class="details-section">
            <h2 class="section-title">📋 详细评估结果</h2>
"""

        # 添加每个对话的详细信息
        for conv_id, data in all_results.items():
            turns = data['turns']
            results = data['results']

            html += f"""
            <div class="conversation">
                <div class="conversation-header" onclick="toggleConversation('{conv_id}')">
                    <span class="conversation-title">💬 对话 {conv_id} ({len(turns)} 轮)</span>
                    <span class="toggle-icon" id="icon-{conv_id}">▼</span>
                </div>
                <div class="conversation-body" id="body-{conv_id}">
"""

            # 添加每一轮
            for i, turn in enumerate(turns):
                html += f"""
                    <div class="turn">
                        <div class="turn-number">第 {i+1} 轮</div>
                        <div class="turn-content">
                            <label>问题:</label>
                            <div>{self._escape_html(turn['question'])}</div>
                        </div>
                        <div class="turn-content">
                            <label>回答:</label>
                            <div>{self._escape_html(turn['answer'])}</div>
                        </div>
                        <div class="turn-content">
                            <label>参考资料:</label>
                            <div>{self._escape_html(turn['context']) if turn['context'] else '<em>无</em>'}</div>
                        </div>
"""

                # 评估结果
                html += '<div class="evaluation-results">'

                for evaluator_name, evaluator_results in results.items():
                    if i < len(evaluator_results):
                        result = evaluator_results[i]
                        score = result.get('score', 0)
                        passed = result.get('success', False)
                        reason = result.get('reason', '')

                        # 分数颜色
                        score_class = 'high' if score >= 0.7 else 'medium' if score >= 0.5 else 'low'

                        # 卡片样式
                        card_class = 'passed' if passed else 'failed'

                        html += f"""
                        <div class="evaluation-card {card_class}">
                            <div class="evaluator-name">{evaluator_name}</div>
                            <div class="score-display">
                                <span class="score-badge {score_class}">得分: {score:.3f}</span>
                                <span class="score-badge {'high' if passed else 'low'}">
                                    {'✅ 通过' if passed else '❌ 失败'}
                                </span>
                            </div>
                            <div class="reason">{self._escape_html(reason)}</div>
                        </div>
"""

                html += '</div></div>'

            html += """
                </div>
            </div>
"""

        html += f"""
        </div>

        <!-- 页脚 -->
        <div class="footer">
            <p>AI评估报告 | 生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>共评估 {stats['total_evaluations']} 次，通过率 {stats['pass_rate']:.1f}%</p>
        </div>
    </div>

    <script>
        function toggleConversation(convId) {{
            const body = document.getElementById('body-' + convId);
            const icon = document.getElementById('icon-' + convId);

            if (body.style.display === 'none') {{
                body.style.display = 'block';
                icon.textContent = '▼';
                body.parentElement.classList.remove('collapsed');
            }} else {{
                body.style.display = 'none';
                icon.textContent = '▶';
                body.parentElement.classList.add('collapsed');
            }}
        }}

        // 默认展开第一个对话
        window.onload = function() {{
            const firstConv = document.querySelector('.conversation');
            if (firstConv) {{
                // 保持第一个对话展开
            }}
        }};
    </script>
</body>
</html>
"""

        return html

    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        if not text:
            return ''
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        # 保留换行
        text = text.replace('\n', '<br>')
        return text

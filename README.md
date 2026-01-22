# LLM 评估工具 - GUI 版

基于 Python tkinter 的 LLM 评估工具，支持 Ragas 和 DeepEval 框架。

## 功能特性

✅ **大模型设置**
- 支持多种大模型类型（通义千问、DeepSeek、GPT 等）
- 自定义 Base URL 和 API Key
- 配置自动保存到 `~/.llm_evaluator/config.json`

✅ **评估器管理**
- 支持 Ragas 和 DeepEval 两个框架
- 内置多种评估器类型
- 可添加、查看、删除评估器
- 自定义评估器阈值

✅ **可视化界面**
- 简洁的 GUI 界面
- 模态窗口操作
- 表格式数据展示

## 项目结构

```
evaluator_gui/
├── main.py                           # 主程序入口
├── config_manager.py                 # 配置管理模块
├── windows/                          # 窗口模块
│   ├── __init__.py
│   ├── model_settings_window.py     # 大模型设置窗口
│   ├── add_evaluator_window.py      # 添加评估器窗口
│   └── evaluator_list_window.py     # 评估器列表窗口
└── README.md                         # 本文件
```

## 安装依赖

```bash
# 创建虚拟环境（可选）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# tkinter 通常是 Python 自带的，无需额外安装
# 如果需要安装：
# Ubuntu/Debian: sudo apt-get install python3-tk
# macOS: 通常已预装
# Windows: 通常已预装

# 后续可能需要安装的依赖：
# pip install deepeval ragas
```

## 运行程序

```bash
cd /Users/liuyang/deloitte/aia/evaluator_gui
python main.py
```

## 使用指南

### 1. 启动程序
运行 `python main.py` 后，会弹出一个主窗口。

### 2. 设置大模型
- 点击菜单：**设置 → 大模型设置**
- 选择大模型类型（如：qwen-max）
- 输入 Base URL（如：https://dashscope.aliyuncs.com/compatible-mode/v1）
- 输入 API Key
- 点击"保存"按钮

### 3. 添加评估器
- 点击菜单：**评估器 → 添加评估器**
- 输入评估器名称（如：我的第一个评估器）
- 选择评估框架（Ragas 或 DeepEval）
- 选择评估器类型（根据框架显示不同的选项）
- 设置阈值（0-1 之间）
- 点击"添加"按钮

### 4. 查看评估器
- 点击菜单：**评估器 → 查看评估器**
- 在列表中查看所有已添加的评估器
- 可以选中并删除不需要的评估器

## 配置文件

配置文件位置根据操作系统自动确定：

- **Windows**: `C:\Users\用户名\AppData\Roaming\llm_evaluator\config.json`
- **macOS**: `~/Library/Application Support/llm_evaluator/config.json`
- **Linux**: `~/.config/llm_evaluator/config.json`

启动程序时会在控制台显示配置目录路径。

格式示例：
```json
{
  "model_settings": {
    "model_type": "qwen-max",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "sk-xxxxx"
  },
  "evaluators": [
    {
      "name": "正确性评估器",
      "framework": "deepeval",
      "metric_type": "Faithfulness",
      "threshold": 0.6
    }
  ]
}
```

## 支持的评估器类型

### Ragas 框架
- Faithfulness
- Answer Relevancy
- Context Precision
- Context Recall
- Context Relevancy
- Answer Correctness
- Answer Similarity

### DeepEval 框架
- Faithfulness
- Answer Relevancy
- Contextual Precision
- Contextual Recall
- Contextual Relevancy
- Bias
- Toxicity
- GEval (Custom)

## 下一步计划

- [ ] 实际运行评估器
- [ ] 显示评估结果
- [ ] 导出评估报告
- [ ] 批量测试功能
- [ ] 1-5 分评分标准

## 技术栈

- **GUI 框架**: tkinter (Python 内置)
- **配置管理**: JSON
- **评估框架**: DeepEval, Ragas (待集成)

## 注意事项

1. tkinter 是 Python 内置库，通常无需额外安装
2. 如果提示缺少 tkinter，请根据操作系统安装对应的包
3. 配置文件保存在用户目录下，不同用户不共享

## 许可证

© 2025 Deloitte Digital. All Rights Reserved.

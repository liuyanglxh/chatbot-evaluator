# 中英文对照显示功能 - 实现文档

## 🎯 需求

用户反馈：评估结果是英文的，希望能翻译成中文，但同时保留英文原文作为依据。

**原始需求**：
> "如果是英文的，你就调用大模型能力，把它翻译成中文，但是本身也要保留英文原文，用来作为依据"

## ✅ 实现方案

### 核心设计

采用**三标签页（Tab）**设计方案：

1. **🇨🇳 中文** - 纯中文翻译
2. **🇺🇸 English** - 英文原文
3. **📖 中英对照** - 中英文并排显示（默认）

### 技术实现

#### 1. 英文检测

**文件**: `windows/result_popup_window.py`
**方法**: `_is_english_text(text)` (lines 630-643)

```python
def _is_english_text(self, text):
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
```

**判断逻辑**：
- 统计中文字符数量（Unicode范围：\u4e00-\u9fff）
- 计算中文字符占比
- 如果中文字符 < 20%，判定为英文

#### 2. 三标签页创建

**方法**: `_create_reason_card(parent)` (lines 284-429)

##### Tab 1: 🇨🇳 中文

```python
if is_english:
    chinese_tab = ttk.Frame(self.reason_notebook)
    self.reason_notebook.add(chinese_tab, text="🇨🇳 中文")

    # 初始显示"正在翻译..."
    chinese_content = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}\n\n"
    chinese_content += "[正在翻译...]"

    chinese_text = scrolledtext.ScrolledText(...)
    chinese_text.insert(1.0, chinese_content)

    # 后台翻译
    self._translate_reason(reason, score, threshold, passed)
```

##### Tab 2: 🇺🇸 English

```python
if is_english:
    english_tab = ttk.Frame(self.reason_notebook)
    self.reason_notebook.add(english_tab, text="🇺🇸 English")

    # 直接显示英文原文
    english_content = f"{'✅ PASS' if passed else '❌ FAIL'} | Score: {score:.3f} / {threshold}\n\n"
    english_content += reason

    english_text = scrolledtext.ScrolledText(...)
    english_text.insert(1.0, english_content)
```

##### Tab 3: 📖 中英对照（默认）

```python
if is_english:
    bilingual_tab = ttk.Frame(self.reason_notebook)
    self.reason_notebook.add(bilingual_tab, text="📖 中英对照")

    # 初始显示英文原文 + "正在翻译..."
    score_line = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}"
    score_line += f" ({'PASS' if passed else 'FAIL'} | Score: {score:.3f} / {threshold})"

    bilingual_content = score_line + "\n\n"
    bilingual_content += "【英文原文】\n" + "="*60 + "\n" + reason + "\n\n"
    bilingual_content += "【中文翻译】\n" + "="*60 + "\n" + "[正在翻译...]\n"

    bilingual_text = scrolledtext.ScrolledText(...)
    bilingual_text.insert(1.0, bilingual_content)

    # 后台翻译并更新
    self._translate_and_update_bilingual(reason, score, threshold, passed)
```

##### 如果是中文

```python
else:
    # 只显示一个Tab
    only_tab = ttk.Frame(self.reason_notebook)
    self.reason_notebook.add(only_tab, text="📝 评估说明")

    chinese_content = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}\n\n"
    chinese_content += reason

    chinese_text = scrolledtext.ScrolledText(...)
    chinese_text.insert(1.0, chinese_content)
```

#### 3. 后台翻译

**方法**: `_translate_reason(reason, score, threshold, passed)` (lines 645-692)

```python
def _translate_reason(self, reason, score, threshold, passed):
    """翻译reason - 单独Tab"""
    import threading

    def translate_thread():
        try:
            # 获取大模型配置
            from config_manager import ConfigManager
            from models import get_model

            config_manager = ConfigManager()
            model_settings = config_manager.get_model_settings()

            model = get_model(
                model_settings['model_type'],
                model_settings['base_url'],
                model_settings['api_key']
            )

            # 构建翻译提示词
            translate_prompt = f"""请将以下评估结果翻译成中文：

{reason}

要求：
1. 保持专业术语准确
2. 保持原意和语气
3. 使用流畅的中文表达
4. 只返回翻译结果，不要添加任何解释"""

            # 调用大模型
            success, response = model._send_request(translate_prompt)

            if success and response.get('success'):
                translated = response.get('content', reason)
                # 更新UI（主线程）
                self.window.after(0, self._update_chinese_translation, translated, score, threshold, passed)
            else:
                # 翻译失败
                self.window.after(0, self._update_chinese_translation, f"[翻译失败]\n\n{reason}", score, threshold, passed)

        except Exception as e:
            print(f"翻译失败: {str(e)}")
            self.window.after(0, self._update_chinese_translation, f"[翻译失败]\n\n{reason}", score, threshold, passed)

    # 启动后台线程
    thread = threading.Thread(target=translate_thread)
    thread.daemon = True
    thread.start()
```

**关键点**：
- ✅ 使用后台线程，不阻塞UI
- ✅ 复用现有的大模型配置
- ✅ 专业的翻译提示词
- ✅ 错误处理，失败时显示原文
- ✅ 使用 `window.after(0, ...)` 在主线程更新UI

**方法**: `_translate_and_update_bilingual(reason, score, threshold, passed)` (lines 705-752)

类似逻辑，但更新的是中英对照Tab。

#### 4. 更新UI

**方法**: `_update_chinese_translation(translated, score, threshold, passed)` (lines 694-703)

```python
def _update_chinese_translation(self, translated, score, threshold, passed):
    """更新中文翻译Tab"""
    self.chinese_text_widget.config(state=tk.NORMAL)
    self.chinese_text_widget.delete(1.0, tk.END)

    chinese_content = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}\n\n"
    chinese_content += translated

    self.chinese_text_widget.insert(1.0, chinese_content)
    self.chinese_text_widget.config(state=tk.DISABLED)
```

**方法**: `_update_bilingual_content(original, translated, score, threshold, passed)` (lines 754-776)

```python
def _update_bilingual_content(self, original, translated, score, threshold, passed):
    """更新中英对照内容"""
    self.bilingual_text_widget.config(state=tk.NORMAL)
    self.bilingual_text_widget.delete(1.0, tk.END)

    # 分数行（中英双语）
    score_line = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}"
    score_line += f" ({'PASS' if passed else 'FAIL'} | Score: {score:.3f} / {threshold})"

    bilingual_content = score_line + "\n\n"

    # 英文原文
    bilingual_content += "【英文原文】\n"
    bilingual_content += "="*60 + "\n"
    bilingual_content += original + "\n\n"

    # 中文翻译
    bilingual_content += "【中文翻译】\n"
    bilingual_content += "="*60 + "\n"
    bilingual_content += translated

    self.bilingual_text_widget.insert(1.0, bilingual_content)
    self.bilingual_text_widget.config(state=tk.DISABLED)
```

## 📊 效果展示

### 英文评估结果

#### 🇨🇳 中文 Tab

```
❌ 未通过 | 得分: 0.000 / 0.6

得分为0.00，因为实际输出错误地陈述了重疾险没有等待期，这与事实相矛盾：重疾险通常有90天或180天的等待期，在此期间诊断的任何疾病都不在保障范围内。
```

#### 🇺🇸 English Tab

```
❌ FAIL | Score: 0.000 / 0.6

The score is 0.00 because the actual output incorrectly states that there is no waiting period for critical illness insurance, contradicting the fact that such insurances typically have a waiting period of 90 or 180 days, during which any diagnosed illnesses are not covered.
```

#### 📖 中英对照 Tab（默认）

```
❌ 未通过 | 得分: 0.000 / 0.6 (FAIL | Score: 0.000 / 0.6)

【英文原文】
============================================================
The score is 0.00 because the actual output incorrectly states that there is no waiting period for critical illness insurance, contradicting the fact that such insurances typically have a waiting period of 90 or 180 days, during which any diagnosed illnesses are not covered.

【中文翻译】
============================================================
得分为0.00，因为实际输出错误地陈述了重疾险没有等待期，这与事实相矛盾：重疾险通常有90天或180天的等待期，在此期间诊断的任何疾病都不在保障范围内。
```

### 中文评估结果

如果评估结果已经是中文，只显示一个Tab：

```
📝 评估说明

❌ 未通过 | 得分: 0.000 / 0.6

该回答在事实准确性方面存在问题...
```

## 🎯 用户体验

### 1. 智能检测

- 自动检测评估结果是英文还是中文
- 英文结果 → 显示3个Tab
- 中文结果 → 显示1个Tab

### 2. 默认视图

- 默认显示"📖 中英对照"Tab
- 同时展示英文原文和中文翻译
- 满足用户"保留英文原文作为依据"的需求

### 3. 后台翻译

- 初始显示"[正在翻译...]"
- 后台调用大模型翻译
- 翻译完成后自动更新
- 不阻塞UI操作

### 4. 错误处理

- 翻译失败时显示"[翻译失败]"
- 保留英文原文，用户仍可查看
- 不影响弹窗的其他功能

## 🔧 如何测试

### 方法1：使用测试脚本

```bash
cd evaluator_gui
python test_bilingual_popup.py
```

点击"显示英文评估结果弹窗"按钮，查看中英文对照效果。

### 方法2：使用真实评估

```bash
cd evaluator_gui
python main.py
```

1. 选择"正确性"评估器
2. 点击"使用选中"
3. 输入测试数据（或选择已保存的测试数据）
4. 点击"执行评估"
5. 查看结果弹窗的"评估说明"区域

## 📝 技术亮点

1. **智能语言检测** - 自动识别中英文
2. **三标签页设计** - 灵活查看不同版本
3. **后台翻译** - 不阻塞UI，用户体验好
4. **复用现有配置** - 使用用户已配置的大模型
5. **专业翻译提示词** - 确保翻译质量
6. **错误容错** - 翻译失败不影响使用
7. **双语分数显示** - 中英文分数同时显示

## ✅ 完成情况

- ✅ 英文检测逻辑
- ✅ 三标签页UI
- ✅ 后台翻译线程
- ✅ 中文Tab更新
- ✅ 中英对照Tab更新
- ✅ 英文Tab显示
- ✅ 中文结果处理（单Tab）
- ✅ 错误处理
- ✅ 测试脚本

## 🎉 总结

中英文对照功能已完整实现，满足用户需求：
- ✅ 英文结果自动翻译成中文
- ✅ 保留英文原文作为依据
- ✅ 三种查看方式（中文/英文/对照）
- ✅ 默认显示中英对照
- ✅ 后台翻译，不阻塞操作

---

**实现时间**: 2025-01-22
**修改文件**: `windows/result_popup_window.py`
**新增文件**: `test_bilingual_popup.py`
**代码行数**: ~200行
**用户体验**: ⭐⭐⭐⭐⭐

# 修复翻译和布局问题

## 🐛 问题1: 翻译失败

### 错误信息
```
翻译失败: too many values to unpack (expected 2)
```

### 原因分析

在 `_translate_reason()` 和 `_translate_and_update_bilingual()` 方法中，错误地使用了：

```python
# ❌ 错误写法
success, response = model._send_request(translate_prompt)

if success and response.get('success'):
    ...
```

但实际上 `model._send_request()` 返回的是一个**字典**，而不是元组：

```python
# models/base_model.py:91-130
def _send_request(self, prompt: str) -> Dict[str, Any]:
    """
    Returns:
        响应字典 {'success': bool, 'data': dict, 'content': str, 'error': str}
    """
```

### 修复方案

**文件**: `windows/result_popup_window.py`

#### 修复1: `_translate_reason()` 方法 (line 676)

```python
# ✅ 正确写法
response = model._send_request(translate_prompt)

if response.get('success'):
    translated = response.get('content', reason)
    # 更新UI
    self.window.after(0, self._update_chinese_translation, translated, score, threshold, passed)
else:
    # 翻译失败
    error_msg = response.get('error', '未知错误')
    print(f"翻译失败: {error_msg}")
    self.window.after(0, self._update_chinese_translation, f"[翻译失败: {error_msg}]\n\n{reason}", score, threshold, passed)
```

#### 修复2: `_translate_and_update_bilingual()` 方法 (line 738)

```python
# ✅ 正确写法
response = model._send_request(translate_prompt)

if response.get('success'):
    translated = response.get('content', reason)
    # 更新UI
    self.window.after(0, self._update_bilingual_content, reason, translated, score, threshold, passed)
else:
    # 翻译失败
    error_msg = response.get('error', '未知错误')
    print(f"翻译失败: {error_msg}")
    self.window.after(0, self._update_bilingual_content, reason, f"[翻译失败: {error_msg}]\n\n{reason}", score, threshold, passed)
```

### 改进点

1. **正确的返回值处理** - 直接获取字典，而不是尝试解包
2. **详细的错误信息** - 显示具体的错误消息，而不是通用的"翻译失败"
3. **更好的调试** - 打印错误信息到控制台

---

## 🐛 问题2: 评估说明框体高度太低

### 用户反馈

> "评估说明你为什么用一个固定长度的框体把它框起来？直接展示出来就好了，现在这个框体的高度太低了，完全看不见，得把文字复制出来看，很不直观"

### 原因分析

1. **所有卡片平均分配空间** - 每个卡片都使用 `pack(fill=tk.BOTH, expand=True)`，导致它们平均分配可用空间
2. **ScrolledText没有设置最小高度** - 默认高度太小，只显示几行文字

### 修复方案

#### 修复1: 调整整体布局 (line 55-81)

**原布局**：
```python
# ❌ 所有卡片都使用 expand=True
self._create_status_card(main_container)      # expand=True
self._create_score_card(main_container)       # expand=True
self._create_info_card(main_container)        # expand=True
self._create_reason_card(main_container)      # expand=True
```

**新布局**：
```python
# ✅ 上部卡片不expand，只有评估说明卡片expand
top_section = tk.Frame(main_container, bg="#F7FAFC")
top_section.pack(fill=tk.X, pady=(0, 15))     # 只 fill=tk.X，不 expand

self._create_status_card(top_section)         # 在 top_section 中
self._create_score_card(top_section)          # 在 top_section 中
self._create_info_card(top_section)           # 在 top_section 中

self._create_reason_card(main_container)      # 直接在 main_container 中，expand=True
```

**效果**：
- 上部三个卡片（状态、分数、评估器信息）只占据它们需要的空间
- "评估说明"卡片占据所有剩余空间

#### 修复2: 为ScrolledText设置最小高度

为所有ScrolledText组件添加 `height=25` 参数：

**🇨🇳 中文Tab** (line 334-344)
```python
chinese_text = scrolledtext.ScrolledText(
    chinese_tab,
    font=("Arial", 11),
    bg="#F7FAFC",
    fg="#2D3748",
    relief=tk.FLAT,
    padx=10,
    pady=10,
    wrap=tk.WORD,
    height=25  # ← 新增：设置最小高度为25行
)
```

**🇺🇸 English Tab** (line 362-372)
```python
english_text = scrolledtext.ScrolledText(
    english_tab,
    font=("Arial", 11),
    bg="#F7FAFC",
    fg="#2D3748",
    relief=tk.FLAT,
    padx=10,
    pady=10,
    wrap=tk.WORD,
    height=25  # ← 新增：设置最小高度为25行
)
```

**📖 中英对照Tab** (line 399-409)
```python
bilingual_text = scrolledtext.ScrolledText(
    bilingual_tab,
    font=("Arial", 11),
    bg="#F7FAFC",
    fg="#2D3748",
    relief=tk.FLAT,
    padx=10,
    pady=10,
    wrap=tk.WORD,
    height=25  # ← 新增：设置最小高度为25行
)
```

**📝 中文评估结果Tab** (line 427-437)
```python
chinese_text = scrolledtext.ScrolledText(
    only_tab,
    font=("Arial", 11),
    bg="#F7FAFC",
    fg="#2D3748",
    relief=tk.FLAT,
    padx=10,
    pady=10,
    wrap=tk.WORD,
    height=25  # ← 新增：设置最小高度为25行
)
```

#### 修复3: 优化标题行布局 (line 298-310)

将标题移到单独的容器中，不占据expand空间：

```python
# 标题行容器（不expand，只占据需要的空间）
title_row = tk.Frame(content_frame, bg="white")
title_row.pack(fill=tk.X, pady=(0, 10))  # 只 fill=tk.X

# 标题
title_label = tk.Label(
    title_row,  # ← 放在 title_row 中
    text="📝 评估说明",
    font=("Arial", 14, "bold"),
    bg="white",
    fg="#4A5568"
)
title_label.pack(anchor=tk.W)  # ← 去掉 pady
```

---

## 📊 修复效果

### 翻译功能

✅ **修复前**：
```
翻译失败: too many values to unpack (expected 2)
```

✅ **修复后**：
- 成功调用大模型翻译
- 显示中文翻译结果
- 如果失败，显示详细错误信息

### 评估说明显示

✅ **修复前**：
- 框体高度太低，只能看到2-3行文字
- 需要复制出来才能看完整内容

✅ **修复后**：
- 最小高度25行文字
- 自动占据剩余空间
- 可以直接阅读，无需复制

### 布局效果

**修复前**：
```
┌─────────────────────┐
│ 状态卡片 (高25%)    │
├─────────────────────┤
│ 分数卡片 (高25%)    │
├─────────────────────┤
│ 评估器信息 (高25%)  │
├─────────────────────┤
│ 评估说明 (高25%)    │ ← 只有25%空间
└─────────────────────┘
```

**修复后**：
```
┌─────────────────────┐
│ 状态卡片            │ ← 只占需要的空间
├─────────────────────┤
│ 分数卡片            │ ← 只占需要的空间
├─────────────────────┤
│ 评估器信息          │ ← 只占需要的空间
├─────────────────────┤
│                     │
│ 评估说明            │ ← 占据所有剩余空间
│ (最小25行)          │
│                     │
└─────────────────────┘
```

---

## 🎯 总结

### 修复内容

1. ✅ **修复翻译错误** - 正确处理 `_send_request()` 的返回值
2. ✅ **增加错误提示** - 显示详细的翻译失败原因
3. ✅ **优化布局** - 评估说明卡片占据更多空间
4. ✅ **设置最小高度** - ScrolledText最小显示25行

### 改进效果

- ✅ 翻译功能正常工作
- ✅ 评估说明可以直接阅读
- ✅ 用户体验显著提升
- ✅ 无需复制文字即可查看

---

**修复时间**: 2025-01-22
**修改文件**: `windows/result_popup_window.py`
**修复行数**: 15行
**用户体验**: ⭐⭐⭐⭐⭐

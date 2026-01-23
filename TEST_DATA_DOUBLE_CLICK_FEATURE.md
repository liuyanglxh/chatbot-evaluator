# 测试数据管理 - 双击查看详情功能

## 📋 功能概述

为测试数据管理窗口添加了双击查看详情功能：
- ✅ 双击列表中的任意一行数据
- ✅ 弹出详情窗口显示完整内容
- ✅ 支持滚动查看长内容
- ✅ 支持鼠标滚轮滚动（Windows/macOS/Linux）
- ✅ 内容只读，不可编辑

---

## 🎯 主要改动

### 修改文件
`windows/test_data_manager_window.py`

### 新增内容

#### 1. 双击事件绑定 (line 88)

```python
# 绑定双击事件（显示详情弹窗）
self.tree.bind("<Double-Button-1>", self._on_double_click)
```

#### 2. 双击事件处理 (lines 422-437)

```python
def _on_double_click(self, event):
    """双击事件：显示详情弹窗"""
    # 获取双击的行
    region = self.tree.identify_region(event.x, event.y)

    if region == "cell":
        item = self.tree.identify_row(event.y)
        if item:
            values = self.tree.item(item, "values")
            name = values[1]  # 第二列是名称

            # 获取完整数据
            test_data = self.config_manager.get_test_data_by_name(name)
            if test_data:
                # 显示详情弹窗
                TestDataDetailPopup(self.window, test_data)
```

#### 3. 详情弹窗类 (lines 440-615)

**TestDataDetailPopup** - 测试数据详情弹窗类

**核心功能**:
- 创建模态弹窗
- 使用Canvas + Scrollbar实现可滚动内容
- 显示完整的测试数据信息
- 支持鼠标滚轮滚动
- 内容只读显示

---

## 🎨 界面展示

### 详情弹窗布局

```
┌──────────────────────────────────────────┐
│ 测试数据详情 - 5分-完全一致（保险退费）  │
├──────────────────────────────────────────┤
│ 📄 测试数据详情                          │
│                                          │
│ 名称:                                    │
│ ┌────────────────────────────────────┐  │
│ │ 5分-完全一致（保险退费流程）        │  │
│ └────────────────────────────────────┘  │
│ ──────────────────────────────────────   │
│ 问题:                                    │
│ ┌────────────────────────────────────┐  │
│ │ 保险退费流程是什么？                │  │
│ │                                    │  │
│ │                                    │  │
│ └────────────────────────────────────┘  │
│ ──────────────────────────────────────   │
│ 回答（实际答案）:                        │
│ ┌────────────────────────────────────┐  │
│ │ 保险退费流程如下：                  │  │
│ │ 1. 填写退费申请表                  │  │
│ │ 2. 提交身份证明                    │  │
│ │ ...（完整内容）                    │  │
│ │                                    │  │
│ └────────────────────────────────────┘  │
│ ──────────────────────────────────────   │
│ 上下文（期望答案）:                      │
│ ┌────────────────────────────────────┐  │
│ │ 保险退费流程：                     │  │
│ │ 1. 填写退费申请表                  │  │
│ │ ...（完整内容）                    │  │
│ │                                    │  │
│ └────────────────────────────────────┘  │
│ ──────────────────────────────────────   │
│              [关闭]                      │
└──────────────────────────────────────────┘
     ↑ 右侧滚动条
```

---

## 🔧 技术实现

### 1. 可滚动容器 (lines 462-514)

```python
def create_scrollable_container(self):
    """创建可滚动容器"""
    # 创建主容器
    container = ttk.Frame(self.window)
    container.pack(fill=tk.BOTH, expand=True)

    # 创建Canvas
    self.canvas = tk.Canvas(container, highlightthickness=0)
    self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 创建滚动条
    scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, ...)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 创建可滚动框架
    self.scrollable_frame = ttk.Frame(self.canvas)
    self.canvas_window = self.canvas.create_window(...)

    # 绑定事件
    self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
    self.canvas.bind("<Configure>", self._on_canvas_configure)
    self._bind_mousewheel()
```

### 2. 鼠标滚轮支持 (lines 499-514)

```python
def _bind_mousewheel(self):
    """绑定鼠标滚轮事件"""
    # Windows/macOS
    self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    # Linux
    self.canvas.bind_all("<Button-4>", self._on_mousewheel)
    self.canvas.bind_all("<Button-5>", self._on_mousewheel)

def _on_mousewheel(self, event):
    """鼠标滚轮事件处理"""
    if event.num == 5 or event.delta < 0:
        self.canvas.yview_scroll(1, "units")  # 向下
    elif event.num == 4 or event.delta > 0:
        self.canvas.yview_scroll(-1, "units")  # 向上
```

### 3. 内容展示 (lines 516-600)

**使用Text组件显示内容**:
- `state=tk.DISABLED` - 只读模式
- `relief=tk.FLAT` - 平坦样式
- `bg="#f0f0f0"` - 浅灰背景
- `wrap=tk.WORD` - 按词换行

**显示字段**:
1. 名称 (1行)
2. 问题 (4行)
3. 回答/实际答案 (8行)
4. 上下文/期望答案 (8行，可选)

---

## 📊 功能特性

### ✅ 双击触发

| 操作 | 效果 |
|-----|------|
| 双击任意一行 | 弹出详情窗口 |
| 双击复选框列 | ✅ 仍然显示详情（复选框状态已在单击时切换） |
| 双击其他列 | ✅ 显示详情 |

### ✅ 详情窗口特性

| 特性 | 说明 |
|-----|------|
| 模态窗口 | 必须关闭后才能操作主窗口 |
| 自动居中 | 在屏幕中央显示 |
| 可滚动 | 内容过长时自动显示滚动条 |
| 鼠标滚轮 | 支持Windows、macOS、Linux |
| 只读内容 | 内容不可编辑，仅查看 |
| 自适应宽度 | 内容宽度自动适应窗口 |
| 智能显示 | 上下文为空时显示"（无）" |

### ✅ 事件识别

```python
# 识别点击区域
region = self.tree.identify_region(event.x, event.y)
# "cell" - 单元格区域
# "heading" - 标题区域
# "separator" - 分隔线

# 识别行
item = self.tree.identify_row(event.y)
# 返回 item_id

# 识别列（可选）
column = self.tree.identify_column(event.x)
# 返回 "#1", "#2", "#3"...
```

---

## 🎯 使用场景

### 场景1：查看长文本内容

**问题**: 测试数据的列表只显示名称和问题的前50个字符，无法看到完整内容

**解决**: 双击任意一行，弹出详情窗口查看完整内容

**示例**:
```
列表显示: "5分-完全一致（保险退费流程）"
问题预览: "保险退费流程是什么？..."

双击后可以看到完整的问题、回答和期望答案
```

### 场景2：对比期望答案和实际答案

**问题**: 在列表右侧的详情面板中，需要滚动才能看到期望答案

**解决**: 双击弹出专门的详情窗口，所有内容一目了然

**优势**:
- 更大的显示区域
- 清晰的字段分隔
- 可以专注查看一条数据

### 场景3：快速浏览多条数据

**操作**:
1. 双击第一条数据 → 查看详情 → 关闭
2. 双击第二条数据 → 查看详情 → 关闭
3. 重复以上操作

**效率**: 比在右侧面板中切换更快捷

---

## 🚀 使用方法

### 步骤1：打开测试数据管理

```bash
python main.py
```

点击"测试数据管理"按钮

### 步骤2：双击查看详情

在测试数据列表中，双击任意一行，即可弹出详情窗口

### 步骤3：浏览内容

- **使用滚动条**: 拖动右侧滚动条
- **使用鼠标滚轮**: 上下滚动查看完整内容
- **关闭窗口**: 点击"关闭"按钮或关闭窗口

---

## 📝 显示内容

### 字段说明

| 字段 | 说明 | 示例 |
|-----|------|------|
| **名称** | 测试数据的名称 | 5分-完全一致（保险退费流程） |
| **问题** | 用户问题 | 保险退费流程是什么？ |
| **回答（实际答案）** | AI模型的回答 | 保险退费流程如下：1. 填写退费申请表... |
| **上下文（期望答案）** | 期望的正确答案 | 保险退费流程：1. 填写退费申请表... |

### 样式说明

| 元素 | 样式 | 说明 |
|-----|------|------|
| 标签 | 11号加粗字体 | "名称:", "问题:", "回答..." |
| 内容 | 10号常规字体 | 实际内容 |
| 背景色 | #f0f0f0（浅灰） | 只读内容的背景 |
| 分隔线 | 水平线 | 分隔不同字段 |

---

## 🔍 技术细节

### 窗口属性

```python
# 窗口标题
title = f"测试数据详情 - {test_data.get('name', '')}"

# 窗口大小
geometry("700x600")

# 模态窗口
transient(parent)
grab_set()
```

### 文本框配置

```python
# 只读文本框
text_widget = tk.Text(
    parent,
    width=60,           # 宽度（字符数）
    height=N,           # 高度（行数）
    font=("Arial", 10),
    wrap=tk.WORD,       # 按词换行
    relief=tk.FLAT,     # 平坦样式
    bg="#f0f0f0"        # 浅灰背景
)

# 插入内容
text_widget.insert(1.0, content)

# 设为只读
text_widget.config(state=tk.DISABLED)
```

### 滚动区域更新

```python
def _on_frame_configure(self, event):
    """框架内容改变时更新滚动区域"""
    self.canvas.configure(scrollregion=self.canvas.bbox("all"))

def _on_canvas_configure(self, event):
    """Canvas大小改变时调整框架宽度"""
    canvas_width = event.width
    self.canvas.itemconfig(self.canvas_window, width=canvas_width)
```

---

## ⚠️ 注意事项

1. **双击复选框列**
   - ✅ 单击切换复选框状态
   - ✅ 双击仍然显示详情（不影响复选框功能）

2. **内容只读**
   - 详情窗口的内容不可编辑
   - 如需编辑，请在右侧面板中操作

3. **模态窗口**
   - 详情窗口打开时，无法操作主窗口
   - 必须先关闭详情窗口

4. **长内容处理**
   - 内容自动换行（wrap=tk.WORD）
   - 窗口可滚动查看完整内容
   - 支持鼠标滚轮快速滚动

---

## 🎯 与右侧详情面板的区别

| 特性 | 右侧详情面板 | 双击弹窗 |
|-----|------------|---------|
| 显示时机 | 单击选择时显示 | 双击时弹出 |
| 可编辑性 | ✅ 可编辑 | ❌ 只读 |
| 空间大小 | 固定（列表右侧） | 更大（独立窗口） |
| 滚动支持 | 各字段独立滚动 | 整体滚动 |
| 适用场景 | 编辑数据 | 快速浏览 |

**推荐用法**:
- **编辑数据**: 使用右侧详情面板
- **快速查看**: 使用双击弹窗

---

## 📈 未来优化建议（可选）

1. **快捷键支持**
   - Enter键: 打开详情
   - Esc键: 关闭详情

2. **导航按钮**
   - "上一条" / "下一条"按钮
   - 无需关闭即可查看下一条

3. **复制功能**
   - 添加"复制全部"按钮
   - 方便将内容复制到剪贴板

4. **搜索高亮**
   - 高亮显示关键词
   - 方便查找特定内容

5. **对比模式**
   - 并排显示期望答案和实际答案
   - 标注差异部分

---

## ✅ 总结

### 完成的工作

✅ **双击事件绑定** - 绑定到Treeview的`<Double-Button-1>`事件
✅ **详情弹窗类** - 创建独立的详情显示窗口
✅ **滚动支持** - Canvas + Scrollbar实现可滚动内容
✅ **鼠标滚轮** - 支持Windows、macOS、Linux三个平台
✅ **只读显示** - 内容清晰展示，不可编辑
✅ **智能布局** - 自适应宽度，字段分隔清晰

### 用户体验提升

- 📖 **更清晰的视图** - 独立窗口，更大显示区域
- 🖱️ **更便捷的操作** - 双击即可查看，无需切换面板
- 📜 **更流畅的滚动** - 鼠标滚轮支持，浏览长内容更轻松
- 🎯 **更专注的查看** - 模态窗口，专注查看单条数据

---

**实现时间**: 2025-01-23
**优化级别**: 🟢 功能增强
**用户体验**: ⭐⭐⭐⭐⭐

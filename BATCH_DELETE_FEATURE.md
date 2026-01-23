# 测试数据管理 - 批量删除功能

## 📋 功能概述

为测试数据管理窗口添加了批量删除功能，支持：
- ✅ 单个勾选/取消勾选测试数据
- ✅ 全选/取消全选
- ✅ 批量删除多条测试数据
- ✅ 智能确认提示（单条/批量）

---

## 🎯 主要改动

### 修改文件
`windows/test_data_manager_window.py`

---

## 🔧 技术实现

### 1. 添加复选框列 (lines 23-24, 65-74)

**初始化**:
```python
# 存储复选框状态 {item_id: BooleanVar}
self.checkbox_vars = {}
```

**Treeview列定义**:
```python
# 创建 Treeview（添加复选框列）
columns = ("select", "name", "question")
self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

self.tree.heading("select", text="✓")
self.tree.heading("name", text="名称")
self.tree.heading("question", text="问题")

self.tree.column("select", width=40, anchor=tk.CENTER)
```

### 2. 加载数据时创建复选框 (lines 161-183)

```python
def load_test_data(self):
    """加载测试数据"""
    # 清空列表和复选框状态
    for item in self.tree.get_children():
        self.tree.delete(item)
    self.checkbox_vars.clear()

    # 加载数据
    test_data_list = self.config_manager.get_test_data_list()

    for td in test_data_list:
        # 创建复选框变量
        var = tk.BooleanVar(value=False)
        item_id = self.tree.insert("", tk.END, values=("☐", td['name'], question))
        self.checkbox_vars[item_id] = var

    # 重置全选按钮
    self.select_all_btn.config(text="☑ 全选")
```

### 3. 按钮区域更新 (lines 88-111)

```python
# 全选/取消全选按钮
self.select_all_btn = ttk.Button(
    button_frame,
    text="☑ 全选",
    command=self.toggle_select_all,
    width=10
)
self.select_all_btn.pack(side=tk.LEFT, padx=5)

# 批量删除按钮
ttk.Button(
    button_frame,
    text="🗑 批量删除",
    command=self.batch_delete,
    width=10
).pack(side=tk.LEFT, padx=5)

# 保存按钮（增加左边距）
ttk.Button(
    button_frame,
    text="💾 保存",
    command=self.save_test_data,
    width=10
).pack(side=tk.LEFT, padx=(20, 5))
```

### 4. 点击复选框切换状态 (lines 187-214)

```python
def _on_click(self, event):
    """处理点击事件，用于切换复选框"""
    # 获取点击的位置
    region = self.tree.identify_region(event.x, event.y)

    # 如果点击的是"cell"区域
    if region == "cell":
        # 获取点击的列
        column = self.tree.identify_column(event.x)

        # 如果点击的是第一列（复选框列）
        if column == "#1":
            # 获取点击的行
            item = self.tree.identify_row(event.y)

            if item:
                # 切换复选框状态
                var = self.checkbox_vars.get(item)
                if var:
                    current_value = var.get()
                    var.set(not current_value)

                    # 更新显示
                    new_value = "☑" if not current_value else "☐"
                    self.tree.item(item, values=(new_value, *self.tree.item(item, "values")[1:]))

                    # 更新全选按钮状态
                    self._update_select_all_button()
```

### 5. 全选/取消全选 (lines 279-305)

```python
def toggle_select_all(self):
    """全选/取消全选"""
    all_items = self.tree.get_children()

    if not all_items:
        return

    # 判断当前是否全选
    all_selected = all(self.checkbox_vars.get(item, tk.BooleanVar(value=False)).get()
                      for item in all_items)

    if all_selected:
        # 取消全选
        for item in all_items:
            var = self.checkbox_vars.get(item)
            if var:
                var.set(False)
            self.tree.item(item, values=("☐", *self.tree.item(item, "values")[1:]))
        self.select_all_btn.config(text="☑ 全选")
    else:
        # 全选
        for item in all_items:
            var = self.checkbox_vars.get(item)
            if var:
                var.set(True)
            self.tree.item(item, values=("☑", *self.tree.item(item, "values")[1:]))
        self.select_all_btn.config(text="☐ 取消全选")
```

### 6. 批量删除功能 (lines 307-356)

```python
def batch_delete(self):
    """批量删除测试数据"""
    # 获取选中的项
    selected_items = []
    for item in self.tree.get_children():
        var = self.checkbox_vars.get(item)
        if var and var.get():
            selected_items.append(item)

    if not selected_items:
        messagebox.showwarning("警告", "请先勾选要删除的测试数据")
        return

    # 获取选中的名称
    selected_names = []
    for item in selected_items:
        values = self.tree.item(item, "values")
        selected_names.append(values[1])  # 第二列是名称

    # 确认删除
    if len(selected_names) == 1:
        confirm_msg = f"确定要删除测试数据「{selected_names[0]}」吗？"
    else:
        confirm_msg = f"确定要删除这 {len(selected_names)} 条测试数据吗？\n\n"
        confirm_msg += "\n".join(f"• {name}" for name in selected_names[:5])
        if len(selected_names) > 5:
            confirm_msg += f"\n... 还有 {len(selected_names) - 5} 条"

    if not messagebox.askyesno("确认删除", confirm_msg):
        return

    # 执行删除
    success_count = 0
    for name in selected_names:
        try:
            self.config_manager.remove_test_data(name)
            success_count += 1
        except Exception as e:
            print(f"删除失败: {name}, 错误: {e}")

    # 刷新列表
    self.load_test_data()

    # 清空详情
    self.name_var.set('')
    self.question_text.delete(1.0, tk.END)
    self.answer_text.delete(1.0, tk.END)
    self.context_text.delete(1.0, tk.END)

    messagebox.showinfo("成功", f"已成功删除 {success_count} 条测试数据")
```

### 7. 更新全选按钮状态 (lines 216-230)

```python
def _update_select_all_button(self):
    """更新全选按钮状态"""
    all_items = self.tree.get_children()

    if not all_items:
        self.select_all_btn.config(text="☑ 全选")
        return

    all_selected = all(self.checkbox_vars.get(item, tk.BooleanVar(value=False)).get()
                      for item in all_items)

    if all_selected:
        self.select_all_btn.config(text="☐ 取消全选")
    else:
        self.select_all_btn.config(text="☑ 全选")
```

---

## 📊 功能特性

### ✅ 复选框交互

| 操作 | 效果 |
|-----|------|
| 点击复选框列 | 切换该行的勾选状态（☐ ↔ ☑） |
| 点击"全选"按钮 | 所有行变为勾选状态，按钮变为"取消全选" |
| 点击"取消全选"按钮 | 所有行取消勾选，按钮变回"全选" |
| 点击"批量删除" | 删除所有勾选的行 |

### ✅ 智能确认提示

**单条删除**:
```
确定要删除测试数据「测试数据1」吗？
[是] [否]
```

**批量删除（≤5条）**:
```
确定要删除这 3 条测试数据吗？

• 测试数据1
• 测试数据2
• 测试数据3

[是] [否]
```

**批量删除（>5条）**:
```
确定要删除这 10 条测试数据吗？

• 测试数据1
• 测试数据2
• 测试数据3
• 测试数据4
• 测试数据5
... 还有 5 条

[是] [否]
```

### ✅ 按钮布局

```
┌────────────────────────────────────────┐
│ [☑ 全选] [🗑 批量删除] [💾 保存]       │
└────────────────────────────────────────┘
```

---

## 🎯 使用示例

### 场景1：删除单条数据

1. 点击要删除的数据行的复选框（☐ → ☑）
2. 点击"🗑 批量删除"按钮
3. 确认删除

### 场景2：批量删除多条数据

1. 点击"☑ 全选"按钮
2. （可选）取消勾选某些不想删除的行
3. 点击"🗑 批量删除"按钮
4. 确认删除

### 场景3：选择性删除

1. 逐个勾选要删除的数据行
2. 点击"🗑 批量删除"按钮
3. 确认删除

---

## 🔍 技术细节

### 数据结构

**复选框状态存储**:
```python
self.checkbox_vars = {
    'item_id_1': <BooleanVar: False>,
    'item_id_2': <BooleanVar: True>,
    'item_id_3': <BooleanVar: False>,
    ...
}
```

**Treeview列结构**:
```python
columns = ("select", "name", "question")
values = ("☐", "测试数据名称", "问题内容...")
# 或
values = ("☑", "测试数据名称", "问题内容...")
```

### 事件绑定

| 事件 | 绑定 | 用途 |
|-----|------|------|
| `<Button-1>` | `_on_click` | 处理复选框点击 |
| `<<TreeviewSelect>>` | `_on_select` | 处理行选择（加载详情） |

### 位置识别

```python
# 识别点击区域
region = self.tree.identify_region(event.x, event.y)
# "cell" - 单元格
# "heading" - 标题
# "separator" - 分隔线

# 识别列
column = self.tree.identify_column(event.x)
# "#1" - 第一列（复选框）
# "#2" - 第二列（名称）
# "#3" - 第三列（问题）

# 识别行
item = self.tree.identify_row(event.y)
# 返回 item_id
```

---

## ⚠️ 注意事项

1. **复选框使用Unicode符号**：
   - ☐ (U+2610) - 未选中
   - ☑ (U+2611) - 已选中
   - ✓ (U+2713) - 列标题

2. **状态同步**：
   - 点击复选框 → 更新 BooleanVar → 更新显示 → 更新全选按钮
   - 全选按钮 → 更新所有 BooleanVar → 更新所有显示 → 更新按钮文本

3. **删除后清理**：
   - 刷新列表
   - 清空右侧详情面板
   - 显示成功提示

4. **错误处理**：
   - 删除失败时打印错误日志
   - 统计成功删除数量

---

## 📈 改进建议（可选）

### 未来可以考虑的优化：

1. **Shift+点击多选**
   - 支持按住Shift键选择连续的多行

2. **右键菜单**
   - 添加右键菜单，提供"勾选"、"取消勾选"、"删除"等选项

3. **搜索过滤**
   - 添加搜索框，按名称/问题筛选后批量操作

4. **统计信息**
   - 显示"已选择 X / 共 Y 条"

5. **快捷键**
   - Ctrl+A: 全选
   - Delete: 删除选中项

---

## ✅ 测试建议

### 功能测试

1. **基本功能**
   - ✅ 点击单个复选框，状态正确切换
   - ✅ 全选/取消全选正常工作
   - ✅ 批量删除正确执行

2. **边界情况**
   - ✅ 没有勾选时点击批量删除，显示警告
   - ✅ 删除所有数据后，列表为空，全选按钮重置
   - ✅ 删除过程中出错，其他数据仍能正常删除

3. **UI测试**
   - ✅ 按钮布局合理，间距适当
   - ✅ 复选框列宽度适中，居中对齐
   - ✅ 确认对话框内容清晰，格式正确

4. **数据一致性**
   - ✅ 删除后列表正确刷新
   - ✅ 右侧详情面板正确清空
   - ✅ 保存后列表正确更新

---

## 🎯 总结

### 完成的工作

✅ **添加复选框列** - 在Treeview第一列添加复选框
✅ **实现点击切换** - 点击复选框可以切换选中状态
✅ **全选/取消全选** - 一键选择/取消所有数据
✅ **批量删除** - 支持删除多条选中的数据
✅ **智能确认** - 根据删除数量显示不同的确认提示
✅ **状态同步** - 复选框状态与全选按钮状态实时同步

### 用户体验提升

- ⚡ **效率提升** - 不再需要逐个删除，可批量操作
- 🎯 **操作便捷** - 点击复选框即可选择，直观明了
- 🛡️ **安全确认** - 删除前有明确的确认提示，避免误删
- 📊 **智能提示** - 批量删除时列出将要删除的数据名称

---

**实现时间**: 2025-01-23
**优化级别**: 🟢 功能增强
**用户体验**: ⭐⭐⭐⭐⭐

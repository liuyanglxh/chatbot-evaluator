"""
评分规则表格组件
用于自定义评估器的评分规则编辑
"""
import tkinter as tk
from tkinter import ttk


class ScoringRulesTable:
    """评分规则表格"""

    def __init__(self, parent):
        """
        初始化评分规则表格

        Args:
            parent: 父容器
        """
        self.parent = parent
        self.rows = []  # 存储每行的数据
        self.min_rows = 2  # 最少行数

        # 创建主框架
        self.frame = ttk.Frame(parent)

        # 创建表头（带边框）
        self._create_header()

        # 创建表格主体（带边框）
        self._create_table_body()

        # 创建添加按钮
        self._create_add_button()

        # 初始化2行
        self.add_row()
        self.add_row()

    def _create_header(self):
        """创建表头"""
        # 表头容器（带边框）
        header_frame = tk.Frame(self.frame, bg="#E2E8F0", relief=tk.RIDGE, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 1))

        # 分数列标题
        score_header = tk.Label(
            header_frame,
            text="分数",
            font=("Arial", 11, "bold"),
            bg="#E2E8F0",
            width=10,
            anchor=tk.W,
            padx=5,
            pady=8
        )
        score_header.pack(side=tk.LEFT)

        # 标准描述列标题
        desc_header = tk.Label(
            header_frame,
            text="标准描述",
            font=("Arial", 11, "bold"),
            bg="#E2E8F0",
            anchor=tk.W,
            padx=5,
            pady=8
        )
        desc_header.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 操作列标题
        action_header = tk.Label(
            header_frame,
            text="操作",
            font=("Arial", 11, "bold"),
            bg="#E2E8F0",
            width=10,
            anchor=tk.CENTER,
            padx=5,
            pady=8
        )
        action_header.pack(side=tk.RIGHT)

    def _create_table_body(self):
        """创建表格主体"""
        # 表格主体容器（无边框外框）
        self.rows_frame = ttk.Frame(self.frame)
        self.rows_frame.pack(fill=tk.BOTH, expand=True)

    def _create_add_button(self):
        """创建添加按钮"""
        add_button_frame = ttk.Frame(self.frame)
        add_button_frame.pack(fill=tk.X, pady=(10, 0))

        self.add_button = ttk.Button(
            add_button_frame,
            text="+ 添加评分规则",
            command=self.add_row,
            width=20
        )
        self.add_button.pack()

    def _calculate_text_height(self, text_widget, text_content):
        """
        动态计算Text组件高度（基于视觉行数）

        Args:
            text_widget: Text组件实例
            text_content: 文本内容

        Returns:
            int: 计算后的高度
        """
        if not text_content:
            return 2  # 默认2行

        # 更新文本框内容
        current_text = text_widget.get(1.0, tk.END)
        if current_text != text_content:
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, text_content)

        # 让Tkinter重新计算布局
        text_widget.update_idletasks()

        # 获取基于实际显示的行数（包括自动换行）
        # 使用 dlineinfo 获取每行的实际位置
        line_count = int(text_widget.index('end-1c').split('.')[0])

        # 计算高度：行数就是高度
        return max(2, line_count)

    def add_row(self, score_value="", desc_value=""):
        """
        添加一行

        Args:
            score_value: 分数初始值
            desc_value: 描述初始值
        """
        row_index = len(self.rows)

        # 创建行框架（带边框）
        row_frame = tk.Frame(self.rows_frame, relief=tk.RIDGE, bd=1)
        row_frame.pack(fill=tk.X, pady=0)

        # 分数列（左侧）
        score_frame = tk.Frame(row_frame, bg="white")
        score_frame.pack(side=tk.LEFT, padx=(0, 1))

        score_var = tk.StringVar(value=str(score_value))
        score_entry = tk.Entry(
            score_frame,
            textvariable=score_var,
            width=10,
            relief=tk.FLAT,
            bd=0,
            bg="white",
            highlightthickness=0
        )
        score_entry.pack(padx=5, pady=5)

        # 绑定分数变化事件，用于校验唯一性
        score_entry.bind("<KeyRelease>", lambda e: self._validate_score_unique(score_var, row_index))
        score_entry.bind("<FocusOut>", lambda e: self._validate_score_unique(score_var, row_index))

        # 标准描述列（中间）
        desc_frame = tk.Frame(row_frame, bg="white")
        desc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 1))

        desc_text = tk.Text(
            desc_frame,
            height=2,  # 初始2行，会根据内容调整
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            bg="white",
            padx=5,
            pady=5,
            width=40,
            highlightthickness=0
        )
        desc_text.pack(fill=tk.BOTH, expand=True)
        desc_text.insert(1.0, desc_value)

        # 初始计算并设置高度
        initial_height = self._calculate_text_height(desc_text, desc_value)
        desc_text.config(height=initial_height)

        # 绑定KeyRelease事件，动态调整高度
        desc_text.bind("<KeyRelease>", lambda e: self._adjust_text_height(desc_text))

        # 操作列（右侧）
        action_frame = tk.Frame(row_frame, bg="white")
        action_frame.pack(side=tk.RIGHT, padx=5)

        delete_button = ttk.Button(
            action_frame,
            text="删除",
            command=lambda: self.delete_row(row_index),
            width=8
        )
        delete_button.pack(pady=(0, 0))  # 移除上下padding

        # 存储行数据
        self.rows.append({
            'score_var': score_var,
            'desc_text': desc_text,
            'delete_button': delete_button,
            'row_frame': row_frame
        })

        # 更新删除按钮状态
        self._update_delete_buttons()

    def _adjust_text_height(self, text_widget):
        """动态调整Text组件高度（基于视觉行数，包括自动换行）"""
        # 获取文本内容
        content = text_widget.get(1.0, tk.END).strip()

        # 让Tkinter重新计算布局
        text_widget.update_idletasks()

        # 获取基于实际显示的行数（包括自动换行）
        # 使用 dlineinfo 获取每行的实际位置
        try:
            line_count = int(text_widget.index('end-1c').split('.')[0])
        except:
            line_count = content.count('\n') + 1

        # 计算新高度：最少2行
        new_height = max(2, line_count)

        # 如果高度有变化，更新
        current_height = int(text_widget.cget('height'))
        if new_height != current_height:
            text_widget.config(height=new_height)

    def delete_row(self, row_index):
        """删除指定行"""
        if len(self.rows) <= self.min_rows:
            return  # 不能删除到少于最少行数

        # 获取要删除的行
        row_data = self.rows[row_index]

        # 销毁界面元素
        row_data['row_frame'].destroy()

        # 从列表中移除
        self.rows.pop(row_index)

        # 更新删除按钮状态
        self._update_delete_buttons()

    def _update_delete_buttons(self):
        """更新所有删除按钮的状态"""
        for i, row_data in enumerate(self.rows):
            if len(self.rows) <= self.min_rows:
                # 只有最少行数时，禁用所有删除按钮
                row_data['delete_button'].state(['disabled'])
            else:
                # 超过最少行数，启用所有删除按钮
                row_data['delete_button'].state(['!disabled'])

    def _validate_score_unique(self, current_score_var, current_row_index):
        """校验分数唯一性"""
        current_score = current_score_var.get().strip()

        # 如果为空，不校验
        if not current_score:
            return

        # 尝试转换为浮点数
        try:
            current_score_float = float(current_score)
        except ValueError:
            return  # 不是数字，暂时不校验

        # 检查是否有重复
        for i, row_data in enumerate(self.rows):
            if i == current_row_index:
                continue  # 跳过当前行

            other_score = row_data['score_var'].get().strip()
            if other_score == current_score:
                # 发现重复，暂时不处理（可以在这里添加提示）
                pass

    def get_rules(self):
        """
        获取所有评分规则

        Returns:
            list: 评分规则列表
            [
                {'score': 0.2, 'description': '...'},
                {'score': 1.0, 'description': '...'}
            ]

        Raises:
            ValueError: 如果数据不合法
        """
        rules = []
        used_scores = set()

        for i, row_data in enumerate(self.rows):
            score_str = row_data['score_var'].get().strip()
            description = row_data['desc_text'].get(1.0, tk.END).strip()

            # 验证分数不能为空
            if not score_str:
                raise ValueError(f"第 {i+1} 行：分数不能为空")

            # 转换为浮点数
            try:
                score = float(score_str)
            except ValueError:
                raise ValueError(f"第 {i+1} 行：分数必须是数字")

            # 验证唯一性（只校验重复性）
            if score in used_scores:
                raise ValueError(f"第 {i+1} 行：分数 {score} 与其他行重复")

            # 添加到结果
            rules.append({
                'score': score,
                'description': description
            })
            used_scores.add(score)

        return rules

    def pack(self, **kwargs):
        """pack方法的代理"""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        """grid方法的代理"""
        self.frame.grid(**kwargs)

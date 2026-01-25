"""
多轮对话编辑器组件
可复用的轮次编辑UI组件
"""
import tkinter as tk
from tkinter import ttk
from font_utils import font_manager


class ConversationTurnsEditor:
    """多轮对话编辑器"""

    def __init__(self, parent, editable=True, on_change=None):
        """
        初始化编辑器

        Args:
            parent: 父容器
            editable: 是否可编辑(False则为只读模式)
            on_change: 内容变化时的回调函数
        """
        self.parent = parent
        self.editable = editable
        self.on_change = on_change

        # 存储轮次的UI组件
        self.turns_widgets = []

        # 创建容器
        self.container = ttk.Frame(parent)

        # 如果是可编辑模式,创建工具栏
        if editable:
            self._create_toolbar()

        # 轮次容器
        self.turns_container = ttk.Frame(self.container)
        self.turns_container.pack(fill=tk.BOTH, expand=True)

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.container)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            toolbar,
            text="➕ 添加一轮对话",
            command=self.add_turn
        ).pack(side=tk.LEFT, padx=5)

    def pack(self, **kwargs):
        """包装pack方法"""
        self.container.pack(**kwargs)

    def grid(self, **kwargs):
        """包装grid方法"""
        self.container.grid(**kwargs)

    def load_turns(self, turns):
        """
        加载轮次数据

        Args:
            turns: 轮次数据列表 [{"question": "", "answer": "", "context": ""}, ...]
        """
        # 清空现有轮次
        self.clear()

        # 创建轮次UI
        for i, turn in enumerate(turns):
            self._add_turn_ui(i, turn)

        # 如果没有轮次,创建一个空轮次
        if not turns:
            self.add_turn()

    def clear(self):
        """清空所有轮次"""
        for widget in self.turns_widgets:
            widget['frame'].destroy()
        self.turns_widgets.clear()

    def add_turn(self, turn_data=None):
        """
        添加新轮次

        Args:
            turn_data: 轮次数据(可选)
        """
        if turn_data is None:
            turn_data = {'question': '', 'answer': '', 'context': ''}

        turn_index = len(self.turns_widgets)
        self._add_turn_ui(turn_index, turn_data)

        # 触发变化回调
        if self.on_change:
            self.on_change()

    def _add_turn_ui(self, turn_index, turn_data):
        """
        添加一轮对话的UI

        Args:
            turn_index: 轮次索引
            turn_data: 轮次数据 {question, answer, context}
        """
        if turn_data is None:
            turn_data = {'question': '', 'answer': '', 'context': ''}

        # 轮次框架（带边框）
        turn_frame = ttk.LabelFrame(
            self.turns_container,
            text=f"第 {turn_index + 1} 轮",
            padding="10"
        )
        turn_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 问题
        ttk.Label(turn_frame, text="问题:", font=font_manager.panel_font_bold()).pack(
            anchor=tk.W, pady=5)

        question_text = tk.Text(
            turn_frame,
            width=60,
            height=2,
            font=font_manager.panel_font(),
            wrap=tk.WORD,
            relief=tk.RIDGE,
            padx=5,
            pady=5
        )
        question_text.pack(fill=tk.BOTH, expand=True, pady=5)
        question_text.insert(1.0, turn_data.get('question', ''))

        # 如果是只读模式,禁用编辑
        if not self.editable:
            question_text.config(state=tk.DISABLED)

        # 回答
        ttk.Label(turn_frame, text="回答:", font=font_manager.panel_font_bold()).pack(
            anchor=tk.W, pady=5)

        answer_text = tk.Text(
            turn_frame,
            width=60,
            height=3,
            font=font_manager.panel_font(),
            wrap=tk.WORD,
            relief=tk.RIDGE,
            padx=5,
            pady=5
        )
        answer_text.pack(fill=tk.BOTH, expand=True, pady=5)
        answer_text.insert(1.0, turn_data.get('answer', ''))

        # 如果是只读模式,禁用编辑
        if not self.editable:
            answer_text.config(state=tk.DISABLED)

        # 参考资料
        ttk.Label(turn_frame, text="参考资料:", font=font_manager.panel_font_bold()).pack(
            anchor=tk.W, pady=5)

        context_text = tk.Text(
            turn_frame,
            width=60,
            height=2,
            font=font_manager.panel_font(),
            wrap=tk.WORD,
            relief=tk.RIDGE,
            padx=5,
            pady=5
        )
        context_text.pack(fill=tk.BOTH, expand=True, pady=5)
        context_text.insert(1.0, turn_data.get('context', ''))

        # 如果是只读模式,禁用编辑
        if not self.editable:
            context_text.config(state=tk.DISABLED)

        # 删除按钮(仅可编辑模式)
        delete_button = None
        if self.editable:
            delete_button = ttk.Button(
                turn_frame,
                text="🗑 删除此轮",
                command=lambda: self._remove_turn(turn_index)
            )
            delete_button.pack(anchor=tk.E, pady=5)

        # 存储这轮的UI组件
        self.turns_widgets.append({
            'frame': turn_frame,
            'question': question_text,
            'answer': answer_text,
            'context': context_text,
            'delete_button': delete_button
        })

        # 更新所有删除按钮状态
        if self.editable:
            self._update_delete_buttons_state()

    def _remove_turn(self, turn_index):
        """删除指定轮次"""
        if len(self.turns_widgets) <= 1:
            # 至少保留一轮
            return

        # 销毁UI
        widget = self.turns_widgets[turn_index]
        widget['frame'].destroy()
        self.turns_widgets.pop(turn_index)

        # 重新编号
        for i, widget in enumerate(self.turns_widgets):
            widget['frame'].config(text=f"第 {i + 1} 轮")
            # 更新删除按钮的回调
            if widget['delete_button']:
                widget['delete_button'].config(command=lambda idx=i: self._remove_turn(idx))

        # 触发变化回调
        if self.on_change:
            self.on_change()

    def _update_delete_buttons_state(self):
        """更新所有删除按钮的状态"""
        can_delete = len(self.turns_widgets) > 1
        for widget in self.turns_widgets:
            if widget['delete_button']:
                if can_delete:
                    widget['delete_button'].config(state=tk.NORMAL)
                else:
                    widget['delete_button'].config(state=tk.DISABLED)

    def get_turns(self):
        """
        获取所有轮次数据

        Returns:
            轮次数据列表
        """
        turns = []
        for widget in self.turns_widgets:
            question = widget['question'].get(1.0, tk.END).strip()
            answer = widget['answer'].get(1.0, tk.END).strip()
            context = widget['context'].get(1.0, tk.END).strip()

            turns.append({
                'question': question,
                'answer': answer,
                'context': context
            })

        return turns

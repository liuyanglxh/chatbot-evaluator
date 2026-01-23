"""
评估结果弹窗
美观地展示评估结果
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading


class ResultPopupWindow:
    """评估结果弹窗"""

    def __init__(self, parent, result_data, evaluator_info):
        """
        初始化结果弹窗

        Args:
            parent: 父窗口
            result_data: 评估结果数据
            evaluator_info: 评估器信息
        """
        self.result_data = result_data
        self.evaluator_info = evaluator_info

        # 调试：打印接收到的数据
        print("\n" + "="*60)
        print("ResultPopupWindow 接收到的数据:")
        print(f"  score: {result_data.get('score')}")
        print(f"  passed: {result_data.get('passed')}")
        print(f"  reason 长度: {len(result_data.get('reason', ''))}")
        print(f"  reason 前200字: {result_data.get('reason', '')[:200]}")
        print(f"  verbose_logs 是否存在: {result_data.get('verbose_logs') is not None}")
        print(f"  verbose_logs 类型: {type(result_data.get('verbose_logs'))}")
        print(f"  verbose_logs 长度: {len(result_data.get('verbose_logs', '') or '')}")
        if result_data.get('verbose_logs'):
            print(f"  verbose_logs 前300字: {result_data.get('verbose_logs', '')[:300]}")
        print("="*60 + "\n")

        # 创建弹窗
        self.window = tk.Toplevel(parent)
        self.window.title("评估结果")
        self.window.geometry("900x800")  # 增加高度：800 -> 900
        self.window.transient(parent)
        self.window.grab_set()

        # 设置背景色
        self.window.configure(bg="#F7FAFC")

        # 创建界面
        self.create_interface()

        # 居中显示
        self.center_window()

    def _calculate_text_height(self, text):
        """动态计算Text组件高度"""
        if not text:
            return 5
        lines = text.count('\n') + 1
        if lines <= 2:
            new_height = 5
        else:
            new_height = lines + 3
        return new_height

    def create_interface(self):
        """创建界面"""
        # 创建可滚动容器
        canvas = tk.Canvas(self.window, bg="#F7FAFC", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#F7FAFC")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局Canvas和Scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20, padx=(0, 20))

        # 添加鼠标滚轮支持
        def _on_mousewheel(event):
            # Windows/macOS: event.delta 是正值或负值
            # Linux: Button-4 (向上) 或 Button-5 (向下)
            if event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                canvas.yview_scroll(1, "units")

        # 绑定到canvas和scrollable_frame，确保在任何位置都能滚动
        canvas.bind_all("<MouseWheel>", _on_mousewheel)      # Windows/macOS
        canvas.bind_all("<Button-4>", _on_mousewheel)        # Linux 向上
        canvas.bind_all("<Button-5>", _on_mousewheel)        # Linux 向下

        # 也绑定到scrollable_frame，确保鼠标在frame上时也能滚动
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<Button-4>", _on_mousewheel)
        self.scrollable_frame.bind("<Button-5>", _on_mousewheel)

        # 主容器（在scrollable_frame中）
        main_container = tk.Frame(self.scrollable_frame, bg="#F7FAFC")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ========== 标题区域 ==========
        self._create_header(main_container)

        # ========== 输入数据卡片 ==========
        self._create_input_data_card(main_container)

        # 上部区域（状态、分数、评估器信息）
        top_section = tk.Frame(main_container, bg="#F7FAFC")
        top_section.pack(fill=tk.X, pady=(0, 15))

        # ========== 状态卡片 ==========
        self._create_status_card(top_section)

        # ========== 分数卡片 ==========
        self._create_score_card(top_section)

        # ========== 评估器信息卡片 ==========
        self._create_info_card(top_section)

        # ========== 评估原因卡片（占据剩余空间）==========
        self._create_reason_card(main_container)

        # ========== 按钮区域 ==========
        self._create_buttons(main_container)

    def _create_header(self, parent):
        """创建标题区域"""
        header_frame = tk.Frame(parent, bg="#F7FAFC")
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # 标题
        title_label = tk.Label(
            header_frame,
            text="📊 评估结果报告",
            font=("Arial", 24, "bold"),
            bg="#F7FAFC",
            fg="#2D3748"
        )
        title_label.pack()

        # 分隔线
        separator = ttk.Separator(header_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=(10, 0))

    def _create_input_data_card(self, parent):
        """创建输入数据卡片"""
        # 获取输入数据
        input_data = self.result_data.get('input', {})

        # 如果没有输入数据，跳过
        if not input_data:
            return

        question = input_data.get('question', '')
        answer = input_data.get('answer', '')
        context = input_data.get('context', '')

        # 卡片容器
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=(0, 15))

        # 内边距
        content_frame = tk.Frame(card_frame, bg="white", padx=20, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(
            content_frame,
            text="📥 输入数据",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#4A5568"
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # 问题
        question_label = tk.Label(
            content_frame,
            text="❓ 问题:",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#2D3748",
            anchor=tk.W
        )
        question_label.pack(fill=tk.X, pady=(5, 0))

        question_height = self._calculate_text_height(question)
        question_text = tk.Text(
            content_frame,
            font=("Arial", 10),
            bg="#F7FAFC",
            fg="#2D3748",
            relief=tk.FLAT,
            padx=10,
            pady=8,
            wrap=tk.WORD,
            height=question_height
        )
        question_text.pack(fill=tk.X, pady=(0, 10))
        question_text.insert(1.0, question)
        question_text.config(state=tk.DISABLED)

        # 回答
        answer_label = tk.Label(
            content_frame,
            text="💬 回答:",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#2D3748",
            anchor=tk.W
        )
        answer_label.pack(fill=tk.X, pady=(5, 0))

        answer_height = self._calculate_text_height(answer)
        answer_text = tk.Text(
            content_frame,
            font=("Arial", 10),
            bg="#F7FAFC",
            fg="#2D3748",
            relief=tk.FLAT,
            padx=10,
            pady=8,
            wrap=tk.WORD,
            height=answer_height
        )
        answer_text.pack(fill=tk.X, pady=(0, 10))
        answer_text.insert(1.0, answer)
        answer_text.config(state=tk.DISABLED)

        # 上下文（如果有）
        if context:
            context_label = tk.Label(
                content_frame,
                text="📚 上下文:",
                font=("Arial", 11, "bold"),
                bg="white",
                fg="#2D3748",
                anchor=tk.W
            )
            context_label.pack(fill=tk.X, pady=(5, 0))

            context_height = self._calculate_text_height(context)
            context_text = tk.Text(
                content_frame,
                font=("Arial", 10),
                bg="#F7FAFC",
                fg="#2D3748",
                relief=tk.FLAT,
                padx=10,
                pady=8,
                wrap=tk.WORD,
                height=context_height
            )
            context_text.pack(fill=tk.X, pady=(0, 10))
            context_text.insert(1.0, context)
            context_text.config(state=tk.DISABLED)

    def _create_status_card(self, parent):
        """创建状态卡片"""
        # 卡片容器
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=(0, 15))

        # 内边距
        content_frame = tk.Frame(card_frame, bg="white", padx=20, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 状态信息
        passed = self.result_data.get('passed', False)

        if passed:
            status_text = "✅ 评估通过"
            status_color = "#48BB78"
            status_bg = "#C6F6D5"
        else:
            status_text = "❌ 评估失败"
            status_color = "#F56565"
            status_bg = "#FED7D7"

        # 状态标签
        status_label = tk.Label(
            content_frame,
            text=status_text,
            font=("Arial", 20, "bold"),
            bg=status_bg,
            fg=status_color,
            padx=20,
            pady=10
        )
        status_label.pack()

    def _create_score_card(self, parent):
        """创建分数卡片"""
        # 卡片容器
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=(0, 15))

        # 内边距
        content_frame = tk.Frame(card_frame, bg="white", padx=20, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(
            content_frame,
            text="📊 评估得分",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#4A5568"
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # 分数显示
        score = self.result_data.get('score', 0.0)
        threshold = self.evaluator_info.get('threshold', 0.6)
        passed = self.result_data.get('passed', False)

        # 分数值
        score_frame = tk.Frame(content_frame, bg="white")
        score_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            score_frame,
            text="得分:",
            font=("Arial", 12),
            bg="white",
            fg="#718096"
        ).pack(side=tk.LEFT)

        score_color = "#48BB78" if passed else "#ECC94B"
        tk.Label(
            score_frame,
            text=f" {score:.3f} ",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=score_color
        ).pack(side=tk.LEFT)

        tk.Label(
            score_frame,
            text=f"/ {threshold}",
            font=("Arial", 12),
            bg="white",
            fg="#718096"
        ).pack(side=tk.LEFT)

        # 进度条
        progress_frame = tk.Frame(content_frame, bg="white")
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            progress_frame,
            text="进度:",
            font=("Arial", 11),
            bg="white",
            fg="#718096"
        ).pack(anchor=tk.W, pady=(0, 5))

        # 进度条容器
        progress_bar_container = tk.Frame(progress_frame, bg="#E2E8F0", height=30)
        progress_bar_container.pack(fill=tk.X)
        progress_bar_container.pack_propagate(False)

        # 计算进度条宽度
        bar_width = int(score * 100)
        bar_color = "#48BB78" if passed else "#ECC94B"

        # 进度条填充
        progress_bar_fill = tk.Frame(
            progress_bar_container,
            bg=bar_color,
            height=30
        )
        progress_bar_fill.place(x=0, y=0, relwidth=score/1.0, relheight=1.0)

        # 百分比标签
        percentage = score * 100
        tk.Label(
            progress_bar_container,
            text=f" {percentage:.1f}% ",
            font=("Arial", 11, "bold"),
            bg="white" if passed else bar_color,
            fg=bar_color if passed else "white"
        ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def _create_info_card(self, parent):
        """创建评估器信息卡片"""
        # 卡片容器
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=(0, 15))

        # 内边距
        content_frame = tk.Frame(card_frame, bg="white", padx=20, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(
            content_frame,
            text="ℹ️ 评估器信息",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#4A5568"
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # 信息网格
        info_frame = tk.Frame(content_frame, bg="white")
        info_frame.pack(fill=tk.X)

        # 信息项
        info_items = [
            ("名称:", self.evaluator_info.get('name', '')),
            ("框架:", self.evaluator_info.get('framework', '')),
            ("类型:", self.evaluator_info.get('metric_type', '')),
            ("阈值:", str(self.evaluator_info.get('threshold', '')))
        ]

        for i, (label, value) in enumerate(info_items):
            # 标签
            tk.Label(
                info_frame,
                text=label,
                font=("Arial", 11),
                bg="white",
                fg="#718096",
                width=8,
                anchor=tk.W
            ).grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=5)

            # 值
            tk.Label(
                info_frame,
                text=value,
                font=("Arial", 11),
                bg="#F7FAFC",
                fg="#2D3748",
                relief=tk.FLAT,
                padx=10,
                pady=5,
                anchor=tk.W
            ).grid(row=i, column=1, sticky=tk.EW, pady=5)

        info_frame.columnconfigure(1, weight=1)

    def _create_reason_card(self, parent):
        """创建评估原因卡片 - 支持中英文对照"""
        # 卡片容器
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=(0, 15))  # 改为 fill=tk.X，不 expand

        # 内边距
        content_frame = tk.Frame(card_frame, bg="white", padx=20, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 标题行容器
        title_row = tk.Frame(content_frame, bg="white")
        title_row.pack(fill=tk.X, pady=(0, 10))

        # 标题
        title_label = tk.Label(
            title_row,
            text="📝 评估说明",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#4A5568"
        )
        title_label.pack(anchor=tk.W)

        # 获取reason
        reason = self.result_data.get('reason', '')
        is_english = self._is_english_text(reason)

        # 构建显示内容
        score = self.result_data.get('score', 0.0)
        threshold = self.evaluator_info.get('threshold', 0.6)
        passed = self.result_data.get('passed', False)

        # 创建标签页（Notebook）
        self.reason_notebook = ttk.Notebook(content_frame)
        self.reason_notebook.pack(fill=tk.BOTH, expand=True)

        # ===== Tab 1: 中文翻译 =====
        if is_english:
            chinese_tab = ttk.Frame(self.reason_notebook)
            self.reason_notebook.add(chinese_tab, text="🇨🇳 中文")

            # 中文内容
            chinese_content = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}\n\n"
            chinese_content += "[正在翻译...]"

            # 使用普通Text，不带滚动条
            chinese_text = tk.Text(
                chinese_tab,
                font=("Arial", 11),
                bg="#F7FAFC",
                fg="#2D3748",
                relief=tk.FLAT,
                padx=10,
                pady=10,
                wrap=tk.WORD
            )
            chinese_text.pack(fill=tk.BOTH, expand=True)
            chinese_text.insert(1.0, chinese_content)
            chinese_text.config(state=tk.DISABLED)
            self.chinese_text_widget = chinese_text

            # 后台翻译
            self._translate_reason(reason, score, threshold, passed)

        # ===== Tab 2: 英文结果 =====
        if is_english:
            english_tab = ttk.Frame(self.reason_notebook)
            self.reason_notebook.add(english_tab, text="🇺🇸 English")

            # 英文内容
            english_content = f"{'✅ PASS' if passed else '❌ FAIL'} | Score: {score:.3f} / {threshold}\n\n"
            english_content += reason

            # 使用普通Text，不带滚动条
            english_text = tk.Text(
                english_tab,
                font=("Arial", 11),
                bg="#F7FAFC",
                fg="#2D3748",
                relief=tk.FLAT,
                padx=10,
                pady=10,
                wrap=tk.WORD
            )
            english_text.pack(fill=tk.BOTH, expand=True)
            english_text.insert(1.0, english_content)
            english_text.config(state=tk.DISABLED)

        # ===== Tab 3: 中英对照（默认显示） =====
        if is_english:
            bilingual_tab = ttk.Frame(self.reason_notebook)
            self.reason_notebook.add(bilingual_tab, text="📖 中英对照")

            # 中英对照内容
            score_line = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}"
            if is_english:
                score_line += f" ({'PASS' if passed else 'FAIL'} | Score: {score:.3f} / {threshold})"

            bilingual_content = score_line + "\n\n"

            # 框架返回的原文
            bilingual_content += "【框架返回的原文】\n"
            bilingual_content += "="*60 + "\n"
            bilingual_content += reason + "\n\n"

            # 中文翻译（占位符）
            bilingual_content += "【中文翻译】\n"
            bilingual_content += "="*60 + "\n"
            bilingual_content += "[正在翻译...]\n"

            # 使用普通Text，不带滚动条
            bilingual_text = tk.Text(
                bilingual_tab,
                font=("Arial", 11),
                bg="#F7FAFC",
                fg="#2D3748",
                relief=tk.FLAT,
                padx=10,
                pady=10,
                wrap=tk.WORD
            )
            bilingual_text.pack(fill=tk.BOTH, expand=True)
            bilingual_text.insert(1.0, bilingual_content)
            bilingual_text.config(state=tk.DISABLED)
            self.bilingual_text_widget = bilingual_text

            # 后台翻译并更新
            self._translate_and_update_bilingual(reason, score, threshold, passed)

        # ===== 如果是中文，只显示一个Tab =====
        else:
            only_tab = ttk.Frame(self.reason_notebook)
            self.reason_notebook.add(only_tab, text="📝 评估说明")

            # 中文内容
            chinese_content = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}\n\n"
            chinese_content += reason

            # 使用普通Text，不带滚动条
            chinese_text = tk.Text(
                only_tab,
                font=("Arial", 11),
                bg="#F7FAFC",
                fg="#2D3748",
                relief=tk.FLAT,
                padx=10,
                pady=10,
                wrap=tk.WORD
            )
            chinese_text.pack(fill=tk.BOTH, expand=True)
            chinese_text.insert(1.0, chinese_content)
            chinese_text.config(state=tk.DISABLED)

        # 检查是否有详细日志
        verbose_logs = self.result_data.get('verbose_logs', '')
        has_verbose_logs = verbose_logs and isinstance(verbose_logs, str) and len(verbose_logs.strip()) > 0

        print(f"\n调试 - 创建原因卡片:")
        print(f"  verbose_logs类型: {type(verbose_logs)}")
        print(f"  verbose_logs长度: {len(verbose_logs) if verbose_logs else 0}")
        print(f"  has_verbose_logs: {has_verbose_logs}")
        print(f"  verbose_logs内容: {verbose_logs[:200] if has_verbose_logs else 'None'}\n")

        if has_verbose_logs:
            print("\n✅ 正在创建详细日志区域...")

            # 添加分隔线
            separator = ttk.Separator(content_frame, orient=tk.HORIZONTAL)
            separator.pack(fill=tk.X, pady=(10, 10))
            print("  ✓ 分隔线已创建")

            # 日志标题和按钮
            log_header = tk.Frame(content_frame, bg="white")
            log_header.pack(fill=tk.X)
            print("  ✓ 日志标题容器已创建")

            tk.Label(
                log_header,
                text="📋 详细评估步骤",
                font=("Arial", 12, "bold"),
                bg="white",
                fg="#4A5568"
            ).pack(side=tk.LEFT)
            print("  ✓ 日志标题已创建")

            # 展开/收起按钮
            self.log_expanded = False
            self.log_text_widget = None

            toggle_button = ttk.Button(
                log_header,
                text="展开 ▼",
                command=lambda: self._toggle_log(),
                width=10
            )
            toggle_button.pack(side=tk.RIGHT)
            self.toggle_button = toggle_button
            print("  ✓ 展开按钮已创建")

            # 日志文本框（初始隐藏）
            self.log_frame = tk.Frame(content_frame, bg="white")
            print("  ✓ 日志容器已创建（初始隐藏）")

            log_text = scrolledtext.ScrolledText(
                self.log_frame,
                font=("Courier New", 10),
                bg="#2D3748",
                fg="#E2E8F0",
                relief=tk.FLAT,
                padx=10,
                pady=10,
                height=10,
                wrap=tk.WORD
            )
            log_text.pack(fill=tk.BOTH, expand=True)
            log_text.insert(1.0, verbose_logs)
            log_text.config(state=tk.DISABLED)
            self.log_text_widget = log_text
            print("  ✓ 日志文本框已创建\n")
        else:
            print("\n❌ has_verbose_logs 为 False，不创建详细日志区域\n")

    def _create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = tk.Frame(parent, bg="#F7FAFC")
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 关闭按钮
        close_button = ttk.Button(
            button_frame,
            text="关闭",
            command=self.window.destroy,
            width=15
        )
        close_button.pack(side=tk.RIGHT)

        # 如果是英文，显示翻译按钮
        is_english = self.result_data.get('is_english', False)
        if is_english:
            translate_button = ttk.Button(
                button_frame,
                text="🌐 翻译为中文",
                command=self.translate_reason,
                width=15
            )
            translate_button.pack(side=tk.RIGHT, padx=(0, 10))

    def translate_reason(self):
        """翻译评估原因"""
        # 在后台线程中翻译
        thread = threading.Thread(target=self._translate_thread)
        thread.daemon = True
        thread.start()

    def _translate_thread(self):
        """翻译线程"""
        try:
            from config_manager import ConfigManager
            from models import get_model

            # 获取配置
            config_manager = ConfigManager()
            model_settings = config_manager.get_model_settings()

            # 创建模型
            model = get_model(
                model_settings['model_type'],
                model_settings['base_url'],
                model_settings['api_key']
            )

            # 翻译
            reason = self.result_data.get('reason', '')
            translate_prompt = f"""请将以下评估原因翻译成中文：

{reason}

要求：
1. 保持专业术语准确
2. 保持原意和语气
3. 使用流畅的中文表达
4. 不要添加额外的解释或说明
"""

            success, response = model._send_request(translate_prompt)

            if success and response.get('success'):
                translated = response.get('content', reason)
                # 更新UI
                self.window.after(0, self._update_translation, translated)
            else:
                self.window.after(0, self._show_translation_error)

        except Exception as e:
            print(f"翻译失败: {str(e)}")
            self.window.after(0, self._show_translation_error)

    def _update_translation(self, translated_text):
        """更新翻译结果"""
        # 创建翻译结果弹窗
        translation_window = tk.Toplevel(self.window)
        translation_window.title("中文翻译")
        translation_window.geometry("700x400")
        translation_window.transient(self.window)
        translation_window.grab_set()
        translation_window.configure(bg="#F7FAFC")

        # 主容器
        main_container = tk.Frame(translation_window, bg="#F7FAFC")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 标题
        title_label = tk.Label(
            main_container,
            text="🌐 中文翻译",
            font=("Arial", 18, "bold"),
            bg="#F7FAFC",
            fg="#2D3748"
        )
        title_label.pack(pady=(0, 15))

        # 翻译内容
        text_widget = scrolledtext.ScrolledText(
            main_container,
            font=("Arial", 11),
            bg="white",
            fg="#2D3748",
            relief=tk.FLAT,
            padx=15,
            pady=15,
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, translated_text)
        text_widget.config(state=tk.DISABLED)

        # 关闭按钮
        close_button = ttk.Button(
            main_container,
            text="关闭",
            command=translation_window.destroy,
            width=15
        )
        close_button.pack(pady=(15, 0))

        # 居中显示
        self._center_dialog(translation_window)

    def _show_translation_error(self):
        """显示翻译错误"""
        import messagebox
        messagebox.showerror("翻译失败", "翻译失败，请稍后重试")

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

            except Exception as e:
                print(f"翻译失败: {str(e)}")
                self.window.after(0, self._update_chinese_translation, f"[翻译失败]\n\n{reason}", score, threshold, passed)

        thread = threading.Thread(target=translate_thread)
        thread.daemon = True
        thread.start()

    def _update_chinese_translation(self, translated, score, threshold, passed):
        """更新中文翻译Tab"""
        self.chinese_text_widget.config(state=tk.NORMAL)
        self.chinese_text_widget.delete(1.0, tk.END)

        chinese_content = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}\n\n"
        chinese_content += translated

        self.chinese_text_widget.insert(1.0, chinese_content)
        self.chinese_text_widget.config(state=tk.DISABLED)

    def _translate_and_update_bilingual(self, reason, score, threshold, passed):
        """翻译并更新中英对照Tab"""
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

            except Exception as e:
                print(f"翻译失败: {str(e)}")
                self.window.after(0, self._update_bilingual_content, reason, f"[翻译失败]\n\n{reason}", score, threshold, passed)

        thread = threading.Thread(target=translate_thread)
        thread.daemon = True
        thread.start()

    def _update_bilingual_content(self, original, translated, score, threshold, passed):
        """更新中英对照内容"""
        self.bilingual_text_widget.config(state=tk.NORMAL)
        self.bilingual_text_widget.delete(1.0, tk.END)

        # 分数行
        score_line = f"{'✅ 通过' if passed else '❌ 未通过'} | 得分: {score:.3f} / {threshold}"
        score_line += f" ({'PASS' if passed else 'FAIL'} | Score: {score:.3f} / {threshold})"

        bilingual_content = score_line + "\n\n"

        # 框架返回的原文
        bilingual_content += "【框架返回的原文】\n"
        bilingual_content += "="*60 + "\n"
        bilingual_content += original + "\n\n"

        # 中文翻译
        bilingual_content += "【中文翻译】\n"
        bilingual_content += "="*60 + "\n"
        bilingual_content += translated

        self.bilingual_text_widget.insert(1.0, bilingual_content)
        self.bilingual_text_widget.config(state=tk.DISABLED)

    def _toggle_log(self):
        """切换日志显示/隐藏"""
        if self.log_expanded:
            # 收起
            self.log_frame.pack_forget()
            self.toggle_button.config(text="展开 ▼")
            self.log_expanded = False
        else:
            # 展开
            self.log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            self.toggle_button.config(text="收起 ▲")
            self.log_expanded = True

    def _center_dialog(self, dialog):
        """窗口居中显示"""
        dialog.update_idletasks()

        width = dialog.winfo_width()
        height = dialog.winfo_height()

        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        dialog.geometry(f'{width}x{height}+{x}+{y}')

    def center_window(self):
        """窗口居中显示"""
        self.window.update_idletasks()

        width = self.window.winfo_width()
        height = self.window.winfo_height()

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.window.geometry(f'{width}x{height}+{x}+{y}')

import tkinter as tk
from tkinter import ttk, messagebox
from auto_picker import AutoPicker
import logging

class AutoPickerGUI:
    def __init__(self):
        self.picker = AutoPicker()
        self.root = tk.Tk()
        self.root.title("金铲铲自动选牌")
        self.root.geometry("800x600")

        # 主布局
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 主布局分为上下两部分
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='both', expand=True, pady=5)
        
        # 主布局改为左右两部分
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)

        # 英雄选择面板 (5行自动换行布局)
        hero_frame = ttk.LabelFrame(left_frame, text="目标英雄选择")
        hero_frame.pack(fill='both', expand=True, pady=5)
        
        # 英雄费用映射
        self.hero_cost_map = {
            "1费": ["波比", "贾克斯", "婕拉", "克格莫", "蒙多", "莫甘娜", "奈德丽", "千钰", 
                  "萨科", "萨勒芬妮", "塞拉斯", "蔚", "阿利斯塔"],
            "2费": ["格雷福斯", "烬", "拉亚斯特", "乐芙兰", "纳亚菲利", "斯卡纳", "俄洛伊",
                  "维迦", "希瓦娜", "艾克", "崔斯特", "德莱厄斯", "薇恩"],
            "3费": ["费德提克", "古拉加斯", "加里奥", "嘉文四世", "金克斯", "雷恩加尔",
                  "德莱文", "赛娜", "韦鲁斯", "伊莉丝", "悠米", "布隆", "莫德凯撒"],
            "4费": ["厄运小姐", "吉格斯", "劫", "科加斯", "瑟庄妮", "蕾欧娜", "妮蔻",
                  "霞", "泽丽", "安妮", "布兰德", "厄斐琉斯", "薇古丝"],
            "5费": ["阿萝拉", "厄加特", "佛耶戈", "盖伦", "可酷伯", "雷克顿", "莎弥拉", "扎克"],
            "特殊卡": ["细胞组织"]
        }
        
        # 存储所有英雄的选中状态
        self.hero_vars = {}
        
        # 创建5行框架，每行对应1-5费
        for cost in ["1费", "2费", "3费", "4费", "5费"]:
            row_frame = ttk.Frame(hero_frame)
            row_frame.pack(fill='x', pady=1)
            
            # 添加费用标签
            ttk.Label(row_frame, text=f"{cost}:", width=5).pack(side='left')
            
            # 创建自动换行的英雄选择文本区域
            hero_text = tk.Text(
                row_frame,
                height=4,
                width=50,
                wrap=tk.WORD,
                font=('微软雅黑', 10)
            )
            hero_text.pack(side='left', fill='x', expand=True)
            
            # 添加该费用的英雄复选框
            for hero in self.hero_cost_map[cost]:
                var = tk.BooleanVar(value=False)  # 默认不选中
                self.hero_vars[hero] = var
                
                # 创建复选框并插入到文本区域
                cb = tk.Checkbutton(
                    hero_text,
                    text=hero,
                    variable=var,
                    onvalue=True,
                    offvalue=False,
                    command=self.update_selected_heroes_display,
                    font=('微软雅黑', 10),
                    indicatoron=True,
                    selectcolor='white',
                    bg='white',
                    activebackground='white'
                )
                # 使用window_create将复选框插入文本区域
                hero_text.window_create(tk.END, window=cb)
                hero_text.insert(tk.END, " ")  # 添加空格分隔
        
        # 特殊卡单独一行
        special_frame = ttk.Frame(hero_frame)
        special_frame.pack(fill='x', pady=1)
        ttk.Label(special_frame, text="特殊卡:", width=5).pack(side='left')
        
        # 创建特殊卡选择文本区域
        special_text = tk.Text(
            special_frame,
            height=2,
            width=50,
            wrap=tk.WORD,
            font=('微软雅黑', 10)
        )
        special_text.pack(side='left', fill='x', expand=True)
        
        for hero in self.hero_cost_map["特殊卡"]:
            var = tk.BooleanVar(value=False)
            self.hero_vars[hero] = var
            cb = tk.Checkbutton(
                special_text,
                text=hero,
                variable=var,
                onvalue=True,
                offvalue=False,
                command=self.update_selected_heroes_display,
                font=('微软雅黑', 10),
                indicatoron=True,
                selectcolor='white',
                bg='white',
                activebackground='white'
            )
            special_text.window_create(tk.END, window=cb)
            special_text.insert(tk.END, " ")

        # 已选英雄显示区域 (固定在右侧)
        selected_frame = ttk.LabelFrame(top_frame, text="当前已选英雄", width=200)
        selected_frame.pack(side='right', fill='y', padx=5, pady=5)
        
        self.selected_listbox = tk.Listbox(
            selected_frame,
            height=20,
            selectmode=tk.SINGLE,
            font=('微软雅黑', 10)
        )
        self.selected_listbox.pack(fill='both', expand=True)
        
        # 控制按钮面板 (放在主框架底部)
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=5)

        # 控制按钮
        self.start_btn = ttk.Button(
            control_frame,
            text="开始D牌(F3)",
            command=self.start_test,
            style="Primary.TButton",
            width=15
        )
        self.start_btn.pack(side='left', padx=5, pady=5)

        self.stop_btn = ttk.Button(
            control_frame,
            text="停止D牌(F4)",
            command=self.stop_test,
            style="Danger.TButton",
            width=15
        )
        self.stop_btn.pack(side='left', padx=5, pady=5)

        self.clear_btn = ttk.Button(
            control_frame,
            text="清空所有英雄",
            command=self.clear_all_heroes,
            style="Secondary.TButton",
            width=15
        )
        self.clear_btn.pack(side='left', padx=5, pady=5)

        # 底部日志区域 (缩小高度)
        log_frame = ttk.LabelFrame(main_frame, text="日志")
        log_frame.pack(fill='x', padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=8)
        self.log_text.pack(fill='x')

        # 样式配置
        self.style = ttk.Style()
        # 设置主题
        self.style.theme_use('clam')
        
        # 配置按钮样式
        self.style.configure("Primary.TButton",
                            foreground="black",
                            background="#4CAF50",
                            font=('微软雅黑', 12))
        self.style.configure("Secondary.TButton",
                            foreground="black",
                            background="#2196F3",
                            font=('微软雅黑', 12))
        
        # 配置日志区域样式
        self.log_text.config(
            foreground="black",
            background="white",
            font=('微软雅黑', 10)
        )
        

        # 日志配置
        self.setup_logging()

    def update_selected_heroes_display(self):
        """更新已选英雄显示"""
        # 获取已选英雄
        selected_heroes = [hero for hero, var in self.hero_vars.items() if var.get()]
        
        # 更新picker的目标英雄
        self.picker.target_heroes = selected_heroes
        
        # 更新列表显示
        self.selected_listbox.delete(0, tk.END)
        for hero in selected_heroes:
            self.selected_listbox.insert(tk.END, hero)
        
        # 如果没有选中英雄，显示提示
        if not selected_heroes:
            self.selected_listbox.insert(tk.END, "未选择任何英雄")

    def clear_all_heroes(self):
        """清空所有英雄选择"""
        for var in self.hero_vars.values():
            var.set(False)
        self.picker.target_heroes = []
        logging.info("已清空所有英雄选择")
        self.update_selected_heroes_display()

    def setup_logging(self):
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)

        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(text_handler)

    def start_test(self):
        try:
            self.picker.on_f3()
            logging.info("测试已启动，请操作模拟器界面...")
        except Exception as e:
            logging.error(f"测试失败: {str(e)}", exc_info=True)

    def stop_test(self):
        try:
            self.picker.stop_picking()
            logging.info("已停止D牌")
        except Exception as e:
            logging.error(f"停止失败: {str(e)}", exc_info=True)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AutoPickerGUI()
    app.run()

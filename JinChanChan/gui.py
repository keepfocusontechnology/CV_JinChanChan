import tkinter as tk
from tkinter import ttk, messagebox
from auto_picker import AutoPicker
import logging
import threading
import time

class AutoPickerGUI:
    def __init__(self):
        self.picker = AutoPicker()
        self.picker_thread = None
        self.stop_event = threading.Event()
        self.root = tk.Tk()
        self.root.title("金铲铲自动选牌")
        self.root.geometry("600x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

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
        
        from hero_cost_mapper import HeroCostMapper
        self.hero_mapper = HeroCostMapper()
        self.hero_cost_map = self.hero_mapper.get_cost_map()
        
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
            for hero in self.hero_mapper.get_heroes_by_cost(cost):
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
        
        for hero in self.hero_mapper.get_heroes_by_cost("特殊卡"):
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
        selected_frame = ttk.LabelFrame(top_frame, text="当前已选英雄", width=30)
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

        # D牌次数控制
        ttk.Label(control_frame, text="D牌次数:").pack(side='left', padx=(5,0))
        self.d_count = tk.Spinbox(
            control_frame,
            from_=1,
            to=100,
            width=5,
            font=('微软雅黑', 10)
        )
        self.d_count.pack(side='left', padx=(0,5))
        self.d_count.delete(0, tk.END)
        self.d_count.insert(0, "20")  # 默认20次

        # 恢复窗口按钮
        self.restore_btn = ttk.Button(
            control_frame,
            text="恢复窗口",
            command=self.restore_mumu_window,
            style="Secondary.TButton",
            width=8
        )
        self.restore_btn.pack(side='left', padx=5, pady=5)

        self.start_btn = ttk.Button(
            control_frame,
            text="开始D牌",
            command=self.start_test,
            style="Primary.TButton",
            width=8
        )
        self.start_btn.pack(side='left', padx=5, pady=5)

        self.stop_btn = ttk.Button(
            control_frame,
            text="停止D牌",
            command=self.stop_test,
            style="Danger.TButton",
            width=8
        )
        self.stop_btn.pack(side='left', padx=5, pady=5)

        self.clear_btn = ttk.Button(
            control_frame,
            text="清空所有英雄",
            command=self.clear_all_heroes,
            style="Secondary.TButton",
            width=12
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

        self.log_text_handler = TextHandler(self.log_text)
        self.log_text_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(self.log_text_handler)

    def start_test(self):
        if self.picker_thread and self.picker_thread.is_alive():
            logging.warning("D牌线程已在运行中")
            return
            
        # 检查是否有选中英雄
        if not self.picker.target_heroes:
            logging.warning("未选中任何英雄，请先选择目标英雄")
            return
            
        try:
            # 获取D牌次数
            d_count = int(self.d_count.get())
            if d_count <= 0:
                raise ValueError("D牌次数必须大于0")
            self.picker.max_d_count = d_count
            self.picker.current_d_count = 0  # 重置计数
        except ValueError as e:
            logging.error(f"无效的D牌次数: {str(e)}")
            return
            
        self.stop_event.clear()
        self.picker_thread = threading.Thread(
            target=self._run_picker,
            daemon=True
        )
        self.picker_thread.start()
        logging.info(f"D牌线程已启动，目标英雄: {', '.join(self.picker.target_heroes)}，最大D牌次数: {self.picker.max_d_count}")

    def _run_picker(self):
        try:
            # 检查是否有选中英雄
            if not self.picker.target_heroes:
                logging.warning("未选中任何英雄，无法开始D牌")
                return
                
            self.picker.running_flag = True
            self.picker.should_exit = False
            
            while not self.stop_event.is_set():
                # 每次循环检查是否还有选中英雄
                if not self.picker.target_heroes:
                    logging.warning("已清空所有英雄，停止D牌")
                    break
                    
                self.picker.main_loop()
                time.sleep(0.1)  # 避免CPU占用过高
                
        except Exception as e:
            logging.error(f"D牌失败: {str(e)}", exc_info=True)
        finally:
            self.picker.running_flag = False
            self.picker.should_exit = True
            self.stop_event.set()  # 确保停止标志被设置

    def stop_test(self):
        if not self.picker_thread or not self.picker_thread.is_alive():
            logging.warning("没有正在运行的D牌线程")
            return
            
        try:
            # 设置停止标志
            self.stop_event.set()
            self.picker.should_exit = True
            self.picker.running_flag = False
            
            # 停止picker操作
            self.picker.stop_picking()
            
            # 重置当前D牌计数
            self.picker.current_d_count = 0
            
            # 尝试正常停止线程
            self.picker_thread.join(timeout=1.0)
            
            if self.picker_thread.is_alive():
                logging.warning("线程未正常终止，尝试强制结束...")
                # 确保所有键盘操作被释放
                try:
                    keyboard.unhook_all()
                    keyboard.release('d')
                except:
                    pass
                
                # 创建新线程来监控并强制终止
                def force_stop():
                    time.sleep(1)
                    if self.picker_thread.is_alive():
                        logging.error("无法正常停止线程，程序可能需要重启")
                
                threading.Thread(target=force_stop, daemon=True).start()
            else:
                logging.info("D牌线程已安全停止")
                
        except Exception as e:
            logging.error(f"停止失败: {str(e)}", exc_info=True)
            # 无论如何都尝试重置状态
            self.picker.should_exit = True
            self.picker.running_flag = False

    def restore_mumu_window(self):
        """恢复MuMu窗口位置和大小"""
        try:
            import pygetwindow as gw
            mumu_window = gw.getWindowsWithTitle("MuMu模拟器12")[0]
            self.picker._position_mumu_window(mumu_window)
            logging.info("已恢复MuMu窗口位置")
        except Exception as e:
            logging.error(f"恢复窗口失败: {str(e)}", exc_info=True)

    def on_close(self):
        """安全关闭窗口的处理方法"""
        # 停止所有线程
        if self.picker_thread and self.picker_thread.is_alive():
            self.stop_test()
            
        # 移除日志处理器
        for handler in logging.getLogger().handlers[:]:
            if hasattr(self, 'log_text_handler') and isinstance(handler, type(self.log_text_handler)):
                logging.getLogger().removeHandler(handler)
                
        # 销毁窗口
        self.root.destroy()

    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f"程序异常: {str(e)}", exc_info=True)

if __name__ == "__main__":
    app = AutoPickerGUI()
    app.run()

import tkinter as tk
from tkinter import ttk
from auto_picker import AutoPicker
import logging

class AutoPickerGUI:
    def __init__(self):
        self.picker = AutoPicker()
        self.root = tk.Tk()
        self.root.title("金铲铲自动选牌测试界面")
        self.root.geometry("800x600")

        # 日志区域
        self.log_text = tk.Text(self.root, wrap=tk.WORD)
        self.log_text.pack(expand=True, fill='both', padx=10, pady=10)

        # 控制面板
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        # 测试按钮
        self.test_btn = ttk.Button(
            control_frame,
            text="开始测试(F3)",
            command=self.start_test,
            style="Primary.TButton"
        )
        self.test_btn.pack(side=tk.LEFT, padx=5)

        # 样式配置
        self.style = ttk.Style()
        self.style.configure("Primary.TButton",
                            foreground="white",
                            background="#4CAF50",
                            font=('微软雅黑', 12))

        # 日志配置
        self.setup_logging()

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
            logging.error(f"测试失败: {str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AutoPickerGUI()
    app.run()
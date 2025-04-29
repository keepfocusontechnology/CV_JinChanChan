import tkinter as tk
from tkinter import ttk

class GoldHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("金铲铲辅助工具")
        self.root.geometry("600x800")

        # 英雄数据
        self.heroes = {
            "1费卡": ["英雄1-1", "英雄1-2", "英雄1-3"],
            "2费卡": ["英雄2-1", "英雄2-2", "英雄2-3"],
            "3费卡": ["英雄3-1", "英雄3-2", "英雄3-3"],
            "4费卡": ["英雄4-1", "英雄4-2", "英雄4-3"],
            "5费卡": ["英雄5-1", "英雄5-2", "英雄5-3"],
            "特殊牌": ["扎克肉肉"]
        }

        # 英雄选择区
        self.create_hero_selection()

        # 金币设置区
        self.create_gold_settings()

        # 操作按钮区
        self.create_action_buttons()

        # 日志显示区
        self.create_log_area()

    def create_hero_selection(self):
        frame = ttk.LabelFrame(self.root, text="英雄选择", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        for tier, heroes in self.heroes.items():
            tier_frame = ttk.LabelFrame(frame, text=tier)
            tier_frame.pack(fill=tk.X, padx=5, pady=2)

            for col, hero in enumerate(heroes):
                var = tk.IntVar(value=0)
                cb = tk.Checkbutton(
                    tier_frame,
                    text=hero,
                    variable=var,
                    command=lambda h=hero: self.log_click(f"勾选英雄: {h}"),
                    tristatevalue=0  # 设置部分选中状态的值与未选中状态相同
                )
                cb.grid(row=0, column=col, padx=5, sticky=tk.W)

    def create_gold_settings(self):
        frame = ttk.LabelFrame(self.root, text="金币设置", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame, text="金币下限:").pack(side=tk.LEFT)
        self.gold_entry = ttk.Entry(frame)
        self.gold_entry.pack(side=tk.LEFT, padx=5)
        self.gold_entry.bind("<FocusOut>", lambda e: self.log_click(f"设置金币下限: {self.gold_entry.get()}"))

    def create_action_buttons(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.X, padx=10, pady=10)

        self.d_button = ttk.Button(
            frame,
            text="自动D牌",
            command=lambda: self.log_click("点击自动D牌按钮")
        )
        self.d_button.pack()

    def create_log_area(self):
        frame = ttk.LabelFrame(self.root, text="操作日志", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = tk.Text(frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def log_click(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        print(message)

if __name__ == "__main__":
    root = tk.Tk()
    app = GoldHelperApp(root)
    root.mainloop()
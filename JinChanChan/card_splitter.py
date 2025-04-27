import os
import pyautogui
import time
from PIL import Image
import keyboard


class CardSplitter:
    def __init__(self, left=874, top=990, width=1009, height=159, gap=4):
        """
        初始化牌分割器
        :param left: 区域左上角x坐标
        :param top: 区域左上角y坐标 
        :param width: 区域总宽度
        :param height: 区域高度
        :param gap: 牌之间的间隔(px)
        """
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.gap = gap
        self.output_dir = "JinChanChan/split_cards"
        os.makedirs(self.output_dir, exist_ok=True)

    def split_and_save(self):
        """分割区域并保存5张牌"""
        # 清空输出目录
        for f in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, f))
        
        # 截取整个区域
        screenshot = pyautogui.screenshot(region=(self.left, self.top, self.width, self.height))
        
        # 固定卡牌宽高和位置
        card_width = 202
        card_height = 161
        card_positions = [
            (0, 0, 199, 161),        # 第1张
            (204, 0, 403, 161),       # 第2张 (3px间隔)
            (407, 0, 604, 161),       # 第3张 (3px间隔)
            (614, 0, 809, 161),       # 第4张 (4px间隔) 
            (817, 0, 1009, 161)       # 第5张 (5px间隔)
        ]
        
        for i, (left, top, right, bottom) in enumerate(card_positions):
            # 截取单张牌(固定位置和尺寸)
            card = screenshot.crop((left, top, right, bottom))
            # 保存图片
            card.save(f"{self.output_dir}/card_{i+1}.png")
        
        print(f"5张牌已分割保存到: {self.output_dir}")

if __name__ == "__main__":
    splitter = CardSplitter()
    print("按F1键开始截图，按ESC退出")
    while True:
        if keyboard.is_pressed('F1'):
            splitter.split_and_save()
            print("截图完成，按F1再次截图或按ESC退出")
        elif keyboard.is_pressed('esc'):
            print("退出截图工具")
            break
        time.sleep(0.1)

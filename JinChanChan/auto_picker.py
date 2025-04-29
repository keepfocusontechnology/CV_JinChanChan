import dxcam
import os
import numpy as np
import pyautogui
import pygetwindow as gw
from pynput import mouse
from PIL import Image
from feature_matcher import FeatureMatcher
from card_matcher import CardMatcher
from config import Config
from drag_screenshot import DragScreenshot
from card_splitter import CardSplitter
import time
import keyboard
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('auto_picker.log')
    ]
)
class AutoPicker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.should_exit = False
        self.target_heroes = ["加里奥","劫","妮蔻","吉格斯"]
        
        # 初始化硬件加速器
        self.matcher = FeatureMatcher(device='cuda')
        self.card_matcher = CardMatcher()
        self.screenshot_tool = DragScreenshot()
        self.card_splitter = CardSplitter()

    def setup_mumu_window(self):
        try:
            mumu_window = gw.getWindowsWithTitle("MuMu模拟器12")[0]
            screen_width, screen_height = pyautogui.size()
            center_x = (screen_width - 1600) // 2
            center_y = (screen_height - 900) // 2
            
            mumu_window.resizeTo(1600, 900)
            mumu_window.moveTo(center_x, center_y)
            mumu_window.minimize()
            mumu_window.restore()
            mumu_window.activate()
            time.sleep(0.5)
            self.logger.info(f"已设置MuMu窗口位置: ({center_x},{center_y})")
        except Exception as e:
            self.logger.error(f"窗口设置失败: {e}", exc_info=True)

    def register_hotkeys(self):
        keyboard.add_hotkey('esc', self.on_esc)
        keyboard.add_hotkey('f3', self.on_f3)

    def on_esc(self):
        self.should_exit = True
        self.logger.info("退出程序")

    def start_picking(self):
        self.should_exit = False
        self.running_flag = True
        self._run_loop()

    def stop_picking(self):
        self.running_flag = False
        self.should_exit = True

    def _run_loop(self):
        while self.running_flag:
            self.main_loop()
            time.sleep(0.1)

    def on_f3(self):
        self.logger.info("开始执行")
        self.start_picking()

    def main_loop(self):
        if self.should_exit:
            return

        try:
            self._core_operation()
        except Exception as e:
            self.logger.exception("核心操作异常，5秒后重试")
            time.sleep(5)
            self._reinitialize_components()

    def _core_operation(self):
        
        # 核心操作流程（带重试机制）
        for attempt in range(3):
            try:
                self.screenshot_tool.capture_fixed_area()
                break
            except Exception as e:
                self.logger.warning(f"截图失败，第{attempt+1}次重试")
                if attempt == 2:
                    raise
                time.sleep(1)

        self.card_splitter.split_and_save()
        
        matches = self.card_matcher.match_all_cards()
        
        # 复制牌组B用于修改
        remaining_cards = matches.copy()
        any_matched = False
        
        while True:
            any_matched = False
            # 每次从牌组A的第一张牌开始匹配
            for hero in self.target_heroes:
                # 在剩余牌组B中查找匹配
                for i, card in enumerate(remaining_cards):
                    if card['hero'] == hero:
                        logger.info(f"找到目标英雄 {hero} 在卡牌{card['card']}")
                        
                        # 移动鼠标到卡牌中心位置
                        logger.info(f"正在移动鼠标到卡牌位置: ({card['center_x']}, {card['center_y']})")
                        pyautogui.moveTo(card['center_x'], card['center_y'], duration=0.3)
                        time.sleep(0.05)  # 50ms延迟
                        
                        # 点击卡牌
                        pyautogui.click()
                        logger.info(f"已点击卡牌 {card['card']}")
                        
                        # 从牌组B中移除已点击的卡牌
                        remaining_cards.pop(i)
                        any_matched = True
                        break  # 点击后跳出当前循环，重新从牌组A开始匹配
            
            if any_matched:
                break  # 点击后跳出英雄循环，重新开始匹配
        
            # 如果没有匹配或牌组B为空，则跳出循环
            if not any_matched or not remaining_cards:
                break
        
            logger.info("牌组A未匹配到牌组B或牌组B已空，触发D键刷新卡牌...")
            keyboard.press('d')
            time.sleep(0.1)
            keyboard.release('d')
            time.sleep(0.3)  # 等待刷新完成
            
            # 递归调用改为循环控制
            self.logger.info("重新开始完整流程...")
            main_loop()
            return

    def run(self):
        self.logger.info("程序启动")
        self.setup_mumu_window()
        self.register_hotkeys()
        keyboard.wait()

if __name__ == '__main__':
    picker = AutoPicker()
    picker.run()

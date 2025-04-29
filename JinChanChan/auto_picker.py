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
logger = logging.getLogger(__name__)

def capture_cards():
    """截取游戏中的牌面"""
    # 使用默认输出设备
    grab = dxcam.create(output_idx=0, output_color='RGB')
    img = None
    while img is None:
        img = grab.grab()
    
    sub_imgs = []
    x, y = Config.point
    for _ in range(5):  # 假设最多5张牌
        sub_img = img[y:y + Config.h, x:x + Config.w, :]
        sub_imgs.append(Image.fromarray(sub_img))
        x += Config.move
    return sub_imgs

def main():
    logger.info("自动拿牌程序启动 - MuMu模拟器12专用版")
    
    # 设置MuMu窗口位置和大小
    try:
        mumu_window = gw.getWindowsWithTitle("MuMu模拟器12")[0]
        # 获取屏幕尺寸
        screen_width, screen_height = pyautogui.size()
        # 计算中心位置
        center_x = (screen_width - 1600) // 2
        center_y = (screen_height - 900) // 2
        # 固定窗口大小和位置
        mumu_window.resizeTo(1600, 900)
        mumu_window.moveTo(center_x, center_y)
        # 确保窗口在最前端
        mumu_window.minimize()
        mumu_window.restore()
        mumu_window.activate()
        time.sleep(0.5)
        logger.info(f"已设置MuMu窗口居中位置: ({center_x},{center_y}) 大小: 1600x900")
    except Exception as e:
        logger.error(f"设置MuMu窗口失败: {e}")
    
    # 初始化特征匹配器、卡牌匹配器、截图工具和分割器
    matcher = FeatureMatcher(device='cuda')
    card_matcher = CardMatcher()
    screenshot_tool = DragScreenshot()
    card_splitter = CardSplitter()
    
    # 牌组A - 需要匹配的目标英雄
    target_heroes = ["加里奥","劫","妮蔻","吉格斯"]
    logger.info(f"目标英雄牌组: {target_heroes}")
    
    logger.info("按F3键开始循环，按ESC键退出程序")
    
    global should_exit
    should_exit = False
    
    def on_esc():
        global should_exit
        logger.info("ESC键被按下，退出程序")
        should_exit = True
        
    def on_f3():
        logger.info("F3键被按下，开始执行...")
        main_loop()
    
    keyboard.add_hotkey('esc', on_esc)
    keyboard.add_hotkey('f3', on_f3)
    
    def main_loop():
            global should_exit
            if should_exit:
                logger.info("正在退出程序...")
                return
                
            logger.info("开始新一轮操作...")
            
            # 截取固定区域并分割为5张牌
            logger.info("正在截取游戏区域...")
            screenshot_tool.capture_fixed_area()
            time.sleep(0.3)
            
            logger.info("正在分割卡牌图片...")
            card_splitter.split_and_save()
            time.sleep(0.5)
            
            # 获取当前卡牌匹配结果(牌组B)
            logger.info("正在匹配卡牌...")
            matches = card_matcher.match_all_cards()
            
            # 复制牌组B用于修改
            remaining_cards = matches.copy()
            any_matched = False
            
            while True:
                any_matched = False
                # 每次从牌组A的第一张牌开始匹配
                for hero in target_heroes:
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
            
            # 递归调用重新开始完整流程
            logger.info("重新开始完整流程...")
            main_loop()
            return
            
    # 启动主循环
    keyboard.wait()  # 等待按键事件
    
if __name__ == '__main__':
    main()

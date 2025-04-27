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

def select_game_area():
    """截取MuMu窗口并识别红框位置作为牌区"""
    import cv2
    import numpy as np
    
    # 截取MuMu窗口
    try:
        mumu_window = gw.getWindowsWithTitle("MuMu模拟器12")[0]
        screenshot = pyautogui.screenshot(region=(
            mumu_window.left, 
            mumu_window.top,
            mumu_window.width,
            mumu_window.height
        ))
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 识别红色框
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) < 5:
            logger.error("未找到5个红框，请确保已正确标注")
            return
            
        # 获取5个最大红框的位置
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        boxes = [cv2.boundingRect(c) for c in contours]
        boxes.sort(key=lambda x: x[0])  # 按x坐标排序
        
        # 设置牌区参数(使用第一个红框作为基准)
        Config.point = (boxes[0][0], boxes[0][1])
        Config.w = boxes[0][2]
        Config.h = boxes[0][3]
        
        # 确保牌间距计算正确
        if len(boxes) > 1:
            Config.move = boxes[1][0] - boxes[0][0]
            if Config.move <= 0:
                Config.move = Config.w * 1.2  # 默认间距为牌宽的1.2倍
                logger.warning(f"自动计算牌间距失败，使用默认值: {Config.move}")
        else:
            Config.move = Config.w * 1.2
            logger.warning("只有一个红框，使用默认牌间距")
        
        logger.info(f"识别到5个红框，设置牌区: 位置{Config.point}, 宽{Config.w}, 高{Config.h}, 间距{Config.move}")
    except Exception as e:
        logger.error(f"识别红框失败: {e}")

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
    
    # 初始化特征匹配器和卡牌匹配器
    matcher = FeatureMatcher(device='cuda')
    card_matcher = CardMatcher()
    
    logger.info("请直接输入要拿的英雄名称:")
    target_hero = input().strip()
    
    while True:
        # 获取当前卡牌匹配结果
        matches = card_matcher.match_all_cards()
        
        # 查找目标英雄
        for match in matches:
            if match['hero'] == target_hero:
                logger.info(f"找到目标英雄 {target_hero} 在卡牌{match['card']}")
                
                # 移动鼠标到卡牌中心位置
                pyautogui.moveTo(match['center_x'], match['center_y'], duration=0.3)
                logger.info(f"已移动鼠标到位置: ({match['center_x']}, {match['center_y']})")
                
                # 等待F2键重新输入英雄
                logger.info("按F2键重新输入英雄名称...")
                while True:
                    if keyboard.is_pressed('f2'):
                        logger.info("检测到F2键，请重新输入英雄名称:")
                        target_hero = input().strip()
                        logger.info(f"新目标英雄: {target_hero}")
                        break
                    time.sleep(0.1)
                continue
                
        logger.info("未找到目标英雄，重新截屏匹配...")
        # 重新截屏并匹配卡牌
        matches = card_matcher.match_all_cards()
        
        # 查找目标英雄
        for match in matches:
            if match['hero'] == target_hero:
                logger.info(f"找到目标英雄 {target_hero} 在卡牌{match['card']}")
                
                # 移动鼠标到卡牌中心位置
                pyautogui.moveTo(match['center_x'], match['center_y'], duration=0.3)
                logger.info(f"已移动鼠标到位置: ({match['center_x']}, {match['center_y']})")
                
                # 等待F2键重新输入英雄
                logger.info("按F2键重新输入英雄名称...")
                while True:
                    if keyboard.is_pressed('f2'):
                        logger.info("检测到F2键，请重新输入英雄名称:")
                        target_hero = input().strip()
                        logger.info(f"新目标英雄: {target_hero}")
                        break
                    time.sleep(0.1)
                continue
    
    print("等待游戏开始...")
    while True:
        if target_hero:
            # 截取当前牌面并保存截图
            cards = capture_cards()
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_dir = "JinChanChan/mumu截屏"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # 识别每张牌
            for i, card in enumerate(cards):
                # 保存每张牌的截图
                card_path = f"{screenshot_dir}/card_{timestamp}_{i+1}.png"
                card.save(card_path)
                
                name, score = matcher.match_images(card, img_features)
                logger.info(f"牌{i+1}: {name} (相似度: {score:.2f}) 截图已保存: {card_path}")
                
                # 如果匹配到目标英雄
                if name == target_hero and score > 0.8:  # 降低相似度阈值
                    logger.info(f"发现目标英雄 {target_hero}, 正在拿牌...")
                    # 计算牌中心位置并点击
                    card_center_x = Config.point[0] + Config.w//2 + i*Config.move
                    card_center_y = Config.point[1] + Config.h//2
                    
                    # 保存鼠标移动前的截图
                    before_path = f"{screenshot_dir}/before_click_{timestamp}.png"
                    pyautogui.screenshot(before_path)
                    
                    # 移动并点击
                    pyautogui.moveTo(card_center_x, card_center_y, duration=0.1)
                    pyautogui.click()
                    
                    # 保存鼠标移动后的截图
                    after_path = f"{screenshot_dir}/after_click_{timestamp}.png"
                    pyautogui.screenshot(after_path)
                    
                    logger.info(f"点击位置: ({card_center_x}, {card_center_y})")
                    logger.info(f"截图已保存: {before_path} 和 {after_path}")
                    time.sleep(0.3)
                    break
            
            time.sleep(1)  # 每秒检测一次

if __name__ == '__main__':
    from utils import load_imgs
    main()

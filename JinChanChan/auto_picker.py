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
from utils import LogAnalyzer, setup_unified_logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('auto_picker.log')
    ]
)
class AutoPicker:
    def __init__(self):
        setup_unified_logging()
        self.logger = logging.getLogger(__name__)
        self.log_analyzer = LogAnalyzer()
        self.should_exit = False
        self.target_heroes = []  # 初始为空，由GUI界面设置
        self.max_d_count = 20    # 默认D牌次数
        self.current_d_count = 0 # 当前已D次数
        
        # 初始化硬件加速器
        try:
            self.matcher = FeatureMatcher(device='cuda')
            self.logger.info("CUDA加速器初始化成功")
        except Exception as e:
            self.logger.warning(f"CUDA不可用，已切换CPU模式: {str(e)}")
            self.matcher = FeatureMatcher(device='cpu')
        self.card_matcher = CardMatcher()
        self.screenshot_tool = DragScreenshot()
        self.card_splitter = CardSplitter()

    def setup_mumu_window(self):
        """设置MuMu窗口位置和大小"""
        try:
            mumu_window = gw.getWindowsWithTitle("MuMu模拟器12")[0]
            self._position_mumu_window(mumu_window)
        except Exception as e:
            self.logger.error(f"窗口设置失败: {e}", exc_info=True)
        # 初始化MuMu窗口时添加窗口列表日志
        available_windows = [win.title for win in gw.getAllWindows()]
        self.logger.info(f"可用窗口列表: {available_windows}")

    def _position_mumu_window(self, window):
        """设置窗口位置和大小的核心逻辑"""
        screen_width, screen_height = pyautogui.size()
        center_x = (screen_width - 1600) // 2
        center_y = (screen_height - 900) // 2
        
        window.resizeTo(1600, 900)
        window.moveTo(center_x, center_y)
        window.minimize()
        window.restore()
        window.activate()
        time.sleep(0.5)
        self.logger.info(f"已设置MuMu窗口位置: ({center_x},{center_y})")

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
        self.should_exit = True
        self.running_flag = False
        try:
            # 强制终止所有键盘操作
            keyboard.unhook_all()
            # 确保所有按键被释放
            keyboard.release('d')
            # 重置D牌计数
            self.current_d_count = 0
            self.logger.info("已强制停止D牌操作")
        except Exception as e:
            self.logger.error(f"停止时出错: {str(e)}")
        finally:
            # 确保状态被重置
            self.should_exit = True
            self.running_flag = False

    def _run_loop(self):
        while self.running_flag and not self.should_exit:
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
            error_type = self.log_analyzer.analyze(str(e))
            if error_type:
                self.log_analyzer.execute_recovery(error_type, self)
            time.sleep(5)

    def _core_operation(self):
        if self.should_exit:
            return
            
        try:
            # 1. 截图
            for attempt in range(3):
                try:
                    self.screenshot_tool.capture_fixed_area()
                    break
                except Exception as e:
                    self.logger.warning(f"截图失败，第{attempt+1}次重试")
                    if attempt == 2:
                        raise
                    time.sleep(1)

            # 2. 分割卡牌
            self.card_splitter.split_and_save()
            
            # 3. 匹配卡牌
            matches = self.card_matcher.match_all_cards()
            if not matches:
                self.logger.warning("未识别到任何卡牌")
                return
                
            # 4. 匹配目标英雄
            for hero in self.target_heroes:
                for card in matches:
                    if card['hero'] == hero:
                        self.logger.info(f"找到目标英雄 {hero}")
                        pyautogui.moveTo(card['center_x'], card['center_y'], duration=0.03)
                        time.sleep(0.02)  # 减少点击前等待时间
                        pyautogui.click()
                        self.logger.info(f"已点击英雄 {hero}")
                        return
                        
            # 5. 最后检查特殊卡"细胞组织"
            for i, card in enumerate(matches):
                if card['hero'] == "细胞组织":
                    self.logger.info("找到特殊卡牌: 细胞组织")
                    pyautogui.moveTo(card['center_x'], card['center_y'], duration=0.03)
                    time.sleep(0.02)  # 减少点击前等待时间
                    pyautogui.click()
                    self.logger.info("已点击特殊卡牌")
                    return
                    
            # 6. 没有匹配则刷新
            if self.current_d_count >= self.max_d_count:
                self.logger.info(f"已达到最大D牌次数 {self.max_d_count}，停止操作")
                self.stop_picking()
                self.should_exit = True  # 确保线程停止
                return
                
            self.current_d_count += 1
            remaining = self.max_d_count - self.current_d_count
            self.logger.info(f"未找到目标英雄，触发D键刷新... (已D {self.current_d_count}次，剩余 {remaining}次)")
            self.logger.debug("开始模拟按下D键")
            # 确保窗口激活
            try:
                mumu_window = gw.getWindowsWithTitle("MuMu模拟器12")[0]
                mumu_window.activate()
                time.sleep(0.1)
            except:
                pass
                
            # 更可靠的按键方式
            keyboard.press_and_release('d')
            self.logger.debug("已触发D键")
            time.sleep(0.3)  # 增加延迟确保D牌完成
        except Exception as e:
            self.logger.error(f"操作出错: {str(e)}", exc_info=True)

    def run(self):
        self.logger.info("程序启动")
        self.setup_mumu_window()
        self.register_hotkeys()
        keyboard.wait()

if __name__ == '__main__':
    picker = AutoPicker()
    picker.run()

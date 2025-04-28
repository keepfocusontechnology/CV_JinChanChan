import os
import time
import pyautogui
import cv2
import numpy as np
from pynput import mouse
import keyboard

class DragScreenshot:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.screenshot_dir = "JinChanChan/mumu截屏"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    def on_click(self, x, y, button, pressed):
        if pressed:
            self.start_x, self.start_y = x, y
        else:
            self.end_x, self.end_y = x, y
            return False  # 停止监听
        
    def capture(self):
        
        print("请按住鼠标左键拖动选择截图区域...")
        
        # 监听鼠标事件
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()
            
        # 确保坐标正确
        left = min(self.start_x, self.end_x)
        top = min(self.start_y, self.end_y)
        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)
        
        # 截图
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"{self.screenshot_dir}/drag_{timestamp}.png"
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot.save(screenshot_path)
        
        print(f"截图已保存到: {screenshot_path}")
        print(f"区域坐标: 左上({left}, {top}), 宽{width}, 高{height}")
        
        return screenshot_path, (left, top, width, height)

    def capture_fixed_area(self):
        """截取固定区域: 左上(871, 989), 宽1014, 高161"""
        left, top = 871, 989
        width, height = 1014, 161
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"{self.screenshot_dir}/fixed_{timestamp}.png"
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot.save(screenshot_path)
        
        print(f"固定区域截图已保存到: {screenshot_path}")
        return screenshot_path, (left, top, width, height)

def main():
    ds = DragScreenshot()
    print("按F3键开始截图，按ESC退出")
    
    while True:
        if keyboard.is_pressed('F3'):
            ds.capture()
            print("截图完成，按F3再次截图或按ESC退出")
        elif keyboard.is_pressed('esc'):
            print("退出截图工具")
            break
        time.sleep(0.1)

if __name__ == "__main__":
    main()

import os
from PIL import Image

def load_imgs(folder_path):
    imgs = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            img_path = os.path.join(folder_path, filename)
            # 读取图片
            img = Image.open(img_path)
            if img is not None:
                name=filename.split('.')[0]
                imgs[name]=img
            else:
                print(f"警告：无法加载图片 {filename}")
    return imgs

class LogAnalyzer:
    def __init__(self):
        self.error_patterns = {
            'screenshot_failed': r'截图失败',
            'window_not_found': r'MuMu模拟器12',
            'component_error': r'组件初始化失败'
        }
        self.recovery_actions = {
            'screenshot_failed': self._reinit_screenshot_tool,
            'window_not_found': self._refocus_window
        }

    def analyze(self, log_line: str) -> Optional[str]:
        """分析日志并返回错误类型"""
        for error_type, pattern in self.error_patterns.items():
            if re.search(pattern, log_line):
                return error_type
        return None

    def execute_recovery(self, error_type: str, picker) -> bool:
        """执行对应的恢复操作"""
        action = self.recovery_actions.get(error_type)
        if action:
            logging.warning(f"执行恢复操作: {error_type}")
            return action(picker)
        return False

    def _reinit_screenshot_tool(self, picker) -> bool:
        try:
            picker.screenshot_tool = DragScreenshot()
            return True
        except Exception as e:
            logging.error(f"截图工具重置失败: {e}")
            return False

    def _refocus_window(self, picker) -> bool:
        try:
            picker.setup_mumu_window()
            return True
        except Exception as e:
            logging.error(f"窗口重定位失败: {e}")
            return False

def setup_unified_logging():
    """配置统一日志格式"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

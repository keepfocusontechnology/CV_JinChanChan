import os
from PIL import Image
from feature_matcher import FeatureMatcher
from utils import load_imgs
from config import Config

class CardMatcher:
    def __init__(self):
        self.card_dir = "JinChanChan/split_cards"
        self.matcher = FeatureMatcher(device='cpu')
        # 预加载特征库
        self.img_features = {}
        img_dict = load_imgs(Config.pictrue_dir)
        for k, v in img_dict.items():
            self.img_features[k] = self.matcher.extract_features(v)
    
    def match_card(self, card_img):
        """使用特征匹配识别卡牌"""
        best_name, best_score = self.matcher.match_images(card_img, self.img_features)
        return best_name if best_score > 0.85 else "未知英雄"  # 提高匹配阈值到0.85
    
    def get_card_center(self, card_index, card_width=202, card_height=161):
        """计算卡牌在屏幕上的中心坐标"""
        # 卡牌在分割区域的相对位置
        positions = [
            (101, 80),    # 第1张中心
            (306, 80),    # 第2张中心 (205+101)
            (511, 80),    # 第3张中心 (410+101)
            (717, 80),    # 第4张中心 (616+101)
            (924, 80)     # 第5张中心 (823+101)
        ]
        rel_x, rel_y = positions[card_index]
        
        # 转换为屏幕绝对坐标 (加上截图区域的偏移)
        abs_x = 874 + rel_x  # 截图区域left=874
        abs_y = 990 + rel_y  # 截图区域top=990
        
        return (abs_x, abs_y)
    
    def match_all_cards(self):
        """匹配所有卡牌并返回结果"""
        results = []
        for i in range(1, 6):
            card_path = os.path.join(self.card_dir, f"card_{i}.png")
            if os.path.exists(card_path):
                card_img = Image.open(card_path)
                hero_name = self.match_card(card_img)
                center = self.get_card_center(i-1)  # 索引从0开始
                results.append({
                    "card": i,
                    "hero": hero_name,
                    "center_x": center[0],
                    "center_y": center[1]
                })
        return results

if __name__ == "__main__":
    matcher = CardMatcher()
    matches = matcher.match_all_cards()
    for match in matches:
        print(f"卡牌{match['card']}: {match['hero']} (点击位置: {match['center_x']}, {match['center_y']})")

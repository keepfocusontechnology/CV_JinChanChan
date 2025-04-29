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
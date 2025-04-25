import dxcam
from config import Config
from PIL import Image

def main():
    grab = dxcam.create(output_idx=Config.output_idx, output_color='RGB')
    img=None
    while img is  None:
        img = grab.grab()
    # print(type(img))
    # print(img.shape)
    sub_imgs=[]
    x,y=Config.point
    for _ in range(5):
        sub_img=img[y:y + Config.h  ,x:x + Config.w,  :]
        sub_imgs.append(sub_img)
        x+=Config.move

    # 保存
    for i,sub_img in enumerate(sub_imgs):
        sub_img=Image.fromarray(sub_img)
        sub_img.save(f'img_{i}.png')


if __name__ == '__main__':
    main()

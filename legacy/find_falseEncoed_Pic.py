import os
import cv2
from PIL import Image

def check_images(input_dir, exts={".jpg", ".jpeg", ".png"}):
    bad_images = []
    all_images = []

    for root, _, files in os.walk(input_dir):
        for fname in files:
            ext = os.path.splitext(fname)[-1].lower()
            if ext in exts:
                fpath = os.path.join(root, fname)
                all_images.append(fpath)

                # 1️⃣ 用 OpenCV 读取
                try:
                    img = cv2.imread(fpath)
                    if img is None:
                        bad_images.append((fpath, "cv2读取失败"))
                        continue
                except Exception as e:
                    bad_images.append((fpath, f"cv2异常: {e}"))
                    continue

                # 2️⃣ 用 PIL 再验证
                try:
                    with Image.open(fpath) as im:
                        im.verify()  # 检查完整性
                except Exception as e:
                    bad_images.append((fpath, f"PIL异常: {e}"))

    print(f"总共检测到 {len(all_images)} 张图片")
    print(f"发现问题图片 {len(bad_images)} 张")

    if bad_images:
        print("问题图片列表：")
        for fpath, err in bad_images:
            print(f"{fpath} —— {err}")

    return bad_images


if __name__ == "__main__":
    dataset_path = r""  # 👉 这里换成你的数据集路径
    bad_list = check_images(dataset_path)
import os
import cv2
import shutil

def copy_single_channel_images(src_dir, dst_dir):
    """
    从源目录中找到单通道图片，复制到目标目录
    :param src_dir: 源路径
    :param dst_dir: 目标路径
    """
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    length = len(os.listdir(src_dir))
    num = 1
    count = 0
    for root, _, files in os.walk(src_dir):
        for file in files:
            print(f"{num}/{length}")
            file_path = os.path.join(root, file)
            # 用 OpenCV 读取
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

            if img is None:
                continue

            # 判断是否单通道（灰度图）
            if len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1):
                dst_path = os.path.join(dst_dir, file)
                shutil.copy2(file_path, dst_path)
                count += 1
            num += 1
    print(f"共找到并复制 {count} 张单通道图片到 {dst_dir}")

if __name__ == "__main__":
    src_dir = r""   # 替换为源目录
    dst_dir = r""  # 替换为目标目录
    copy_single_channel_images(src_dir, dst_dir)
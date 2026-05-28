import os
import cv2

def convert_single_to_three_channel(src_dir, dst_dir):
    """
    将源路径下的单通道图片转为3通道保存到目标路径
    :param src_dir: 源路径
    :param dst_dir: 目标路径
    """
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    count = 0
    for root, _, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)

            # 保证只处理常见图片格式
            if not file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
                continue

            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                continue

            # 判断是否单通道
            if len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1):
                # 转为三通道
                img_3ch = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

                dst_path = os.path.join(dst_dir, file)
                cv2.imwrite(dst_path, img_3ch)
                count += 1

    print(f"共转换并保存 {count} 张单通道图片到 {dst_dir}")

if __name__ == "__main__":
    src_dir = r""   # 替换为源目录
    dst_dir = r""  # 替换为目标目录
    convert_single_to_three_channel(src_dir, dst_dir)
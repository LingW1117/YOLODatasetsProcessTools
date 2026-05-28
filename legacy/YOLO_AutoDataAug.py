import os
import cv2
import glob
import math
import numpy as np
from pathlib import Path


# ===== 支持中文路径的读写 =====
def cv_imread(path):
    """支持中文路径的imread"""
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def cv_imwrite(path, img):
    """支持中文路径的imwrite"""
    ext = os.path.splitext(path)[1]
    result, encoded_img = cv2.imencode(ext, img)
    if result:
        encoded_img.tofile(path)
        return True
    else:
        return False


# ===== 标签处理 =====
def load_labels(label_path):
    """读取YOLO标签，自动检测编码"""
    labels = []
    if not os.path.exists(label_path):
        return labels

    encodings_to_try = ["utf-8", "gbk", "latin-1"]
    for enc in encodings_to_try:
        try:
            with open(label_path, "r", encoding=enc, errors="strict") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 5:
                        continue
                    cls, x, y, w, h = parts
                    labels.append([int(cls), float(x), float(y), float(w), float(h)])
            return labels
        except UnicodeDecodeError:
            continue  # 换一种编码继续尝试

    # 如果全都失败，用二进制方式强行读
    with open(label_path, "rb") as f:
        raw = f.read().decode("latin-1", errors="ignore")
    for line in raw.splitlines():
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        cls, x, y, w, h = parts
        labels.append([int(cls), float(x), float(y), float(w), float(h)])
    return labels


def save_labels(label_path, labels):
    """保存YOLO标签（UTF-8 编码，规范换行符）"""
    lines = [f"{lab[0]} {lab[1]:.6f} {lab[2]:.6f} {lab[3]:.6f} {lab[4]:.6f}" for lab in labels]
    with open(label_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


# ===== 几何处理 =====
def rotate_point(x, y, cx, cy, angle_rad):
    """绕(cx, cy)旋转点(x, y)，返回新坐标"""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    x_new = cos_a * (x - cx) - sin_a * (y - cy) + cx
    y_new = sin_a * (x - cx) + cos_a * (y - cy) + cy
    return x_new, y_new


def rotate_image_and_labels(img, labels, angle, direction):
    """旋转图像和YOLO标签，白色填充"""
    h, w = img.shape[:2]
    cx, cy = w / 2, h / 2

    # 旋转方向处理
    if direction == "right":
        angle = -angle
    angle_rad = math.radians(angle)

    # === 图像旋转 ===
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])

    # 新图尺寸（保证完整显示）
    new_w = int(h * sin + w * cos)
    new_h = int(h * cos + w * sin)

    # 调整平移量
    M[0, 2] += (new_w / 2) - cx
    M[1, 2] += (new_h / 2) - cy

    # 白色填充 (255,255,255)
    rotated_img = cv2.warpAffine(img, M, (new_w, new_h), borderValue=(255, 255, 255))

    # === 标签旋转 ===
    new_labels = []
    for lab in labels:
        cls, x, y, bw, bh = lab
        # 转换为像素坐标
        x_c = x * w
        y_c = y * h
        box_w = bw * w
        box_h = bh * h

        # 四个角点
        pts = np.array([
            [x_c - box_w / 2, y_c - box_h / 2],
            [x_c + box_w / 2, y_c - box_h / 2],
            [x_c + box_w / 2, y_c + box_h / 2],
            [x_c - box_w / 2, y_c + box_h / 2]
        ])

        # 加齐次坐标并旋转
        ones = np.ones((4, 1))
        pts_homo = np.hstack([pts, ones])
        rotated_pts = (M @ pts_homo.T).T

        # 新bbox
        x_min_new = np.min(rotated_pts[:, 0])
        y_min_new = np.min(rotated_pts[:, 1])
        x_max_new = np.max(rotated_pts[:, 0])
        y_max_new = np.max(rotated_pts[:, 1])

        if x_max_new <= x_min_new or y_max_new <= y_min_new:
            continue

        # 转换回YOLO归一化
        new_x = (x_min_new + x_max_new) / 2 / new_w
        new_y = (y_min_new + y_max_new) / 2 / new_h
        new_bw = (x_max_new - x_min_new) / new_w
        new_bh = (y_max_new - y_min_new) / new_h

        new_labels.append([cls, new_x, new_y, new_bw, new_bh])

    return rotated_img, new_labels


# ===== 主函数 =====
def augment_dataset(img_dir, label_dir, out_img_dir, out_label_dir, direction="left", angle=90):
    """数据增强：旋转图像和标签，白色填充"""
    os.makedirs(out_img_dir, exist_ok=True)
    os.makedirs(out_label_dir, exist_ok=True)

    img_exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp")

    for ext in img_exts:
        for img_path in glob.glob(os.path.join(img_dir, ext)):
            img_name = Path(img_path).stem
            label_path = os.path.join(label_dir, img_name + ".txt")

            img = cv_imread(img_path)
            if img is None:
                print(f"[WARN] 读取失败: {img_path}")
                continue

            labels = load_labels(label_path)

            # 从0到180度，每隔2度进行旋转
            for angle in range(0, 181, 2):
                rotated_img, rotated_labels = rotate_image_and_labels(img, labels, angle, direction)

                # 新命名
                new_name = f"{img_name}_{direction}{angle}"
                out_img_path = os.path.join(out_img_dir, new_name + Path(img_path).suffix)
                out_label_path = os.path.join(out_label_dir, new_name + ".txt")

                cv_imwrite(out_img_path, rotated_img)
                save_labels(out_label_path, rotated_labels)

                print(f"{new_name}处理完成")


if __name__ == "__main__":
    # 示例调用   0-90度 1度间隔旋转
    augment_dataset(
        img_dir=r"",
        label_dir=r"",
        out_img_dir=r"",
        out_label_dir=r"",
        direction="right",
        angle=90
    )

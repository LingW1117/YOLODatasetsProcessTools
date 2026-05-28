import os
import shutil
import random


def split_dataset(original_dataset_path, new_dataset_path,
                  train_ratio=0.7, val_ratio=0.2, test_ratio=0.1,
                  move=False, seed=None):
    """
    将 YOLO 格式数据集划分为 train/val/test

    :param original_dataset_path: 原始数据集路径（包含 images/ 和 labels/ 文件夹）
    :param new_dataset_path: 划分后数据集路径
    :param train_ratio: 训练集比例
    :param val_ratio: 验证集比例
    :param test_ratio: 测试集比例
    :param move: 是否移动文件（True=移动，False=复制，默认 False）
    :param seed: 随机种子，设置后划分结果可复现
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "train+val+test 比例之和必须等于 1"

    if seed is not None:
        random.seed(seed)

    # 新建文件夹
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(new_dataset_path, "images", split), exist_ok=True)
        os.makedirs(os.path.join(new_dataset_path, "labels", split), exist_ok=True)

    # 获取原始图片文件
    image_dir = os.path.join(original_dataset_path, "images")
    label_dir = os.path.join(original_dataset_path, "labels")
    image_filenames = [f for f in os.listdir(image_dir)
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.tif'))]

    # 打乱
    random.shuffle(image_filenames)

    # 划分数量
    n_total = len(image_filenames)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)
    n_test = n_total - n_train - n_val

    train_images = image_filenames[:n_train]
    val_images = image_filenames[n_train:n_train + n_val]
    test_images = image_filenames[n_train + n_val:]

    # 工具函数：移动/复制图像和标签
    def transfer_data(images, split):
        for img_name in images:
            ext = os.path.splitext(img_name)[1]
            label_name = os.path.splitext(img_name)[0] + ".txt"

            src_img = os.path.join(image_dir, img_name)
            src_label = os.path.join(label_dir, label_name)

            dst_img = os.path.join(new_dataset_path, "images", split, img_name)
            dst_label = os.path.join(new_dataset_path, "labels", split, label_name)

            if os.path.exists(src_img):
                (shutil.move if move else shutil.copy)(src_img, dst_img)
            if os.path.exists(src_label):
                (shutil.move if move else shutil.copy)(src_label, dst_label)

    # 处理数据
    transfer_data(train_images, "train")
    transfer_data(val_images, "val")
    transfer_data(test_images, "test")

    action = "移动" if move else "复制"
    print(f"数据集划分完成！总数: {n_total} | 训练: {n_train}, 验证: {n_val}, 测试: {n_test} | 操作方式: {action}")


if __name__ == "__main__":
    split_dataset(
        original_dataset_path=r"",
        new_dataset_path=r"",
        train_ratio=0.75,
        val_ratio=0.25,
        test_ratio=0.0,
        move=True,  # 改成 True 就会移动文件
        seed=0     # 固定随机种子，保证划分可复现
    )
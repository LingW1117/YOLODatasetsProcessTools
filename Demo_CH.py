#!/usr/bin/env python3
"""
Demo-CH.py -- yolo-tools 使用示例

本文件演示两种调用方式：
  1. Python import API 调用
  2. 等效的 CLI 命令行调用（见注释）

每个章节覆盖一个常见工作流。所有路径均为占位符，运行前请修改。
"""

import yolo_tools as yt

# ============================================================
# 工作流 1：将数据集拆分为 train/val/test
# ============================================================
yt.split_dataset(
    original_dataset_path="./raw_dataset",
    new_dataset_path="./split_dataset",
    train_ratio=0.7,
    val_ratio=0.2,
    test_ratio=0.1,
    move=True,
    seed=42,
)
# CLI 等效命令：
#   yolo-tools dataset split --src ./raw_dataset --dst ./split_dataset \
#       --train 0.7 --val 0.2 --test 0.1 --move --seed 42


# ============================================================
# 工作流 2：清洗数据集 -- 删除无标签的图片
# ============================================================
checked, deleted = yt.delete_images_without_labels(
    images_folder="./split_dataset/images/train",
    labels_folder="./split_dataset/labels/train",
)
print(f"共检查 {checked} 张，删除 {deleted} 张无标签图片")
# CLI 等效命令：
#   yolo-tools dataset delete-no-label \
#       -i ./split_dataset/images/train -l ./split_dataset/labels/train


# ============================================================
# 工作流 3：修改标签类别 ID
# ============================================================
yt.modify_labels(
    input_folder="./split_dataset/labels/train",
    output_folder="./split_dataset/labels/train",
    origin_label=3,
    modify_label=0,
)
# CLI 等效命令：
#   yolo-tools labels modify -i ./split_dataset/labels/train \
#       -o ./split_dataset/labels/train -f 3 -t 0


# ============================================================
# 工作流 4：数据增强 -- 旋转
# ============================================================
yt.augment_dataset(
    img_dir="./split_dataset/images/train",
    label_dir="./split_dataset/labels/train",
    out_img_dir="./augmented/images",
    out_label_dir="./augmented/labels",
    direction="right",
    angle=15,
)
# CLI 等效命令：
#   yolo-tools augment rotate \
#       -i ./split_dataset/images/train -l ./split_dataset/labels/train \
#       -oi ./augmented/images -ol ./augmented/labels --angle 15 --direction right


# ============================================================
# 工作流 5：将 VOC XML 标注转换为 YOLO 格式
# ============================================================
class_mapping = yt.xml_folder_to_yolo_txt_folder_auto_map(
    xml_folder="./voc_annotations",
    txt_folder="./yolo_labels",
)
print(f"自动生成的类别映射：{class_mapping}")
# CLI 等效命令：
#   yolo-tools image-convert xml-to-yolo -x ./voc_annotations -t ./yolo_labels


# ============================================================
# 工作流 6：按类别筛选数据集，然后仅对该类做增强
# ============================================================
count = yt.filter_yolo_dataset(
    input_images_folder="./dataset/images",
    input_labels_folder="./dataset/labels",
    class_index=2,
    output_images_folder="./class2/images",
    output_labels_folder="./class2/labels",
    operation="copy",
)
print(f"已提取类别 2 的样本 {count} 个")

yt.augment_dataset_auto(
    img_dir="./class2/images",
    label_dir="./class2/labels",
    out_img_dir="./class2_augmented/images",
    out_label_dir="./class2_augmented/labels",
    direction="left",
    angle_start=0,
    angle_end=90,
    angle_step=5,
)
# CLI 等效命令：
#   yolo-tools dataset filter-by-class \
#       -i ./dataset/images -l ./dataset/labels -c 2 \
#       -oi ./class2/images -ol ./class2/labels --mode copy
#   yolo-tools augment rotate-auto \
#       -i ./class2/images -l ./class2/labels \
#       -oi ./class2_augmented/images -ol ./class2_augmented/labels \
#       --start 0 --end 90 --step 5


# ============================================================
# 工作流 7：检测损坏图片并尝试修复
# ============================================================
bad = yt.check_images("./dataset/images")
if bad:
    unrecoverable = yt.check_and_fix_images(
        "./dataset/images", "./dataset/fixed"
    )
    print(f"修复完成，仍有 {len(unrecoverable)} 张无法修复")
# CLI 等效命令：
#   yolo-tools image-quality check -d ./dataset/images
#   yolo-tools image-quality fix -i ./dataset/images -o ./dataset/fixed


# ============================================================
# 工作流 8：为无标签的图片生成空标签文件
# ============================================================
created, skipped = yt.ensure_empty_labels(
    images_folder="./dataset/images",
    labels_folder="./dataset/labels",
)
print(f"新建空标签 {created} 个，已存在跳过 {skipped} 个")
# CLI 等效命令：
#   yolo-tools labels ensure -i ./dataset/images -l ./dataset/labels


if __name__ == "__main__":
    print(__doc__)
    print("以上示例均使用占位路径。")
    print("运行前请修改路径，或作为编写自己脚本时的参考。")

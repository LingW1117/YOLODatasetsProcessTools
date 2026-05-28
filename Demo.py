#!/usr/bin/env python3
"""
Demo.py -- Usage examples for yolo-tools

This file demonstrates both:
  1. Python import API
  2. Equivalent CLI commands (shown in comments)

Each section covers a common workflow. All paths are placeholders --
edit them before running.
"""

import yolo_tools as yt

# ============================================================
# Workflow 1: Split a dataset into train/val/test
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
# CLI equivalent:
#   yolo-tools dataset split --src ./raw_dataset --dst ./split_dataset \
#       --train 0.7 --val 0.2 --test 0.1 --move --seed 42


# ============================================================
# Workflow 2: Clean a dataset -- delete images without labels
# ============================================================
checked, deleted = yt.delete_images_without_labels(
    images_folder="./split_dataset/images/train",
    labels_folder="./split_dataset/labels/train",
)
print(f"Checked {checked}, deleted {deleted} images without labels")
# CLI equivalent:
#   yolo-tools dataset delete-no-label \
#       -i ./split_dataset/images/train -l ./split_dataset/labels/train


# ============================================================
# Workflow 3: Modify label class IDs
# ============================================================
yt.modify_labels(
    input_folder="./split_dataset/labels/train",
    output_folder="./split_dataset/labels/train",
    origin_label=3,
    modify_label=0,
)
# CLI equivalent:
#   yolo-tools labels modify -i ./split_dataset/labels/train \
#       -o ./split_dataset/labels/train -f 3 -t 0


# ============================================================
# Workflow 4: Data augmentation -- rotation
# ============================================================
yt.augment_dataset(
    img_dir="./split_dataset/images/train",
    label_dir="./split_dataset/labels/train",
    out_img_dir="./augmented/images",
    out_label_dir="./augmented/labels",
    direction="right",
    angle=15,
)
# CLI equivalent:
#   yolo-tools augment rotate \
#       -i ./split_dataset/images/train -l ./split_dataset/labels/train \
#       -oi ./augmented/images -ol ./augmented/labels --angle 15 --direction right


# ============================================================
# Workflow 5: Convert XML annotations to YOLO format
# ============================================================
class_mapping = yt.xml_folder_to_yolo_txt_folder_auto_map(
    xml_folder="./voc_annotations",
    txt_folder="./yolo_labels",
)
print(f"Auto-generated class mapping: {class_mapping}")
# CLI equivalent:
#   yolo-tools image-convert xml-to-yolo -x ./voc_annotations -t ./yolo_labels


# ============================================================
# Workflow 6: Filter dataset by class, then augment only that class
# ============================================================
count = yt.filter_yolo_dataset(
    input_images_folder="./dataset/images",
    input_labels_folder="./dataset/labels",
    class_index=2,
    output_images_folder="./class2/images",
    output_labels_folder="./class2/labels",
    operation="copy",
)
print(f"Extracted {count} samples of class 2")

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
# CLI equivalents:
#   yolo-tools dataset filter-by-class \
#       -i ./dataset/images -l ./dataset/labels -c 2 \
#       -oi ./class2/images -ol ./class2/labels --mode copy
#   yolo-tools augment rotate-auto \
#       -i ./class2/images -l ./class2/labels \
#       -oi ./class2_augmented/images -ol ./class2_augmented/labels \
#       --start 0 --end 90 --step 5


# ============================================================
# Workflow 7: Check for corrupted images, then fix them
# ============================================================
bad = yt.check_images("./dataset/images")
if bad:
    unrecoverable = yt.check_and_fix_images(
        "./dataset/images", "./dataset/fixed"
    )
    print(f"Fixed all but {len(unrecoverable)} images")
# CLI equivalents:
#   yolo-tools image-quality check -d ./dataset/images
#   yolo-tools image-quality fix -i ./dataset/images -o ./dataset/fixed


# ============================================================
# Workflow 8: Create empty labels for unlabeled images
# ============================================================
created, skipped = yt.ensure_empty_labels(
    images_folder="./dataset/images",
    labels_folder="./dataset/labels",
)
print(f"Created {created} empty labels, {skipped} already existed")
# CLI equivalent:
#   yolo-tools labels ensure -i ./dataset/images -l ./dataset/labels


if __name__ == "__main__":
    print(__doc__)
    print("All examples are shown with placeholder paths.")
    print("Edit paths before running, or use as reference for your own scripts.")

from __future__ import annotations

import os
import random
import shutil
from pathlib import Path

from yolo_tools.utils import IMAGE_EXTENSIONS, find_image_path


def split_dataset(
    original_dataset_path: str,
    new_dataset_path: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    move: bool = False,
    seed: int | None = None,
) -> None:
    """Split a YOLO-format dataset into train/val/test splits.

    Args:
        original_dataset_path: Path containing images/ and labels/ subdirectories.
        new_dataset_path: Output path for the split dataset.
        train_ratio: Proportion for training set.
        val_ratio: Proportion for validation set.
        test_ratio: Proportion for test set.
        move: If True, move files; if False, copy files.
        seed: Random seed for reproducible splits.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, (
        "train_ratio + val_ratio + test_ratio must equal 1"
    )

    if seed is not None:
        random.seed(seed)

    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(new_dataset_path, "images", split), exist_ok=True)
        os.makedirs(os.path.join(new_dataset_path, "labels", split), exist_ok=True)

    image_dir = os.path.join(original_dataset_path, "images")
    label_dir = os.path.join(original_dataset_path, "labels")

    image_filenames = [
        f for f in os.listdir(image_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".tif"))
    ]
    random.shuffle(image_filenames)

    n_total = len(image_filenames)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    train_images = image_filenames[:n_train]
    val_images = image_filenames[n_train:n_train + n_val]
    test_images = image_filenames[n_train + n_val:]

    def _transfer(images: list[str], split: str) -> None:
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

    _transfer(train_images, "train")
    _transfer(val_images, "val")
    _transfer(test_images, "test")

    action = "moved" if move else "copied"
    print(
        f"Dataset split complete! Total: {n_total} | "
        f"Train: {n_train}, Val: {n_val}, Test: {n_total - n_train - n_val} | "
        f"Mode: {action}"
    )


def delete_images_without_labels(
    images_folder: str,
    labels_folder: str,
    img_exts: tuple[str, ...] = IMAGE_EXTENSIONS,
) -> tuple[int, int]:
    """Delete images that have no corresponding label file (or empty label).

    Returns (checked_count, deleted_count).
    """
    from yolo_tools.utils import is_empty_label_file

    images_dir = Path(images_folder)
    labels_dir = Path(labels_folder)

    if not images_dir.exists():
        raise FileNotFoundError(f"images_folder not found: {images_dir}")
    if not images_dir.is_dir():
        raise NotADirectoryError(f"images_folder is not a directory: {images_dir}")

    if not labels_dir.exists():
        labels_dir.mkdir(parents=True, exist_ok=True)

    img_exts = tuple(e.lower() for e in img_exts)

    checked = 0
    deleted = 0

    for img_path in images_dir.rglob("*"):
        if not img_path.is_file():
            continue
        if img_path.suffix.lower() not in img_exts:
            continue

        checked += 1
        label_path = labels_dir / (img_path.stem + ".txt")

        if not label_path.exists() or is_empty_label_file(label_path):
            img_path.unlink()
            deleted += 1

    return checked, deleted


def move_orphan_labels(
    images_folder: str,
    labels_folder: str,
    output_path: str,
) -> int:
    """Move label files that have no matching image to an output directory.

    Returns the number of moved label files.
    """
    os.makedirs(output_path, exist_ok=True)

    moved_count = 0

    for label_name in os.listdir(labels_folder):
        if not label_name.endswith(".txt"):
            continue

        base_name = os.path.splitext(label_name)[0]

        if find_image_path(base_name, images_folder) is None:
            src = os.path.join(labels_folder, label_name)
            dst = os.path.join(output_path, label_name)
            shutil.move(src, dst)
            moved_count += 1

    print(f"Moved {moved_count} orphan label files.")
    return moved_count


def move_images_without_labels(
    images_folder: str,
    labels_folder: str,
    missing_labels_folder: str,
) -> int:
    """Move images that have no matching label file to a separate directory.

    Returns the number of moved images.
    """
    os.makedirs(missing_labels_folder, exist_ok=True)

    image_files = [
        f for f in os.listdir(images_folder)
        if os.path.isfile(os.path.join(images_folder, f))
    ]

    moved = 0
    for image_file in image_files:
        image_path = os.path.join(images_folder, image_file)
        label_file = os.path.join(
            labels_folder, os.path.splitext(image_file)[0] + ".txt"
        )

        if not os.path.exists(label_file):
            dest = os.path.join(missing_labels_folder, image_file)
            shutil.move(image_path, dest)
            print(f"Moved {image_file} to {missing_labels_folder}")
            moved += 1

    return moved


def move_samples_more_than_n(
    input_images_path: str,
    input_labels_path: str,
    max_box_num: int,
    output_images_path: str,
    output_labels_path: str,
) -> dict:
    """Move samples (image + label) where the label has more than N bounding boxes.

    Preserves relative directory structure. Returns a summary dict.
    """
    from yolo_tools.utils import count_valid_boxes

    images_dir = Path(input_images_path)
    labels_dir = Path(input_labels_path)
    out_images_dir = Path(output_images_path)
    out_labels_dir = Path(output_labels_path)

    if not images_dir.exists() or not images_dir.is_dir():
        raise NotADirectoryError(f"input_images_path is invalid: {images_dir}")
    if not labels_dir.exists() or not labels_dir.is_dir():
        raise NotADirectoryError(f"input_labels_path is invalid: {labels_dir}")

    out_images_dir.mkdir(parents=True, exist_ok=True)
    out_labels_dir.mkdir(parents=True, exist_ok=True)

    moved = 0
    skipped_no_image: list[str] = []
    skipped_exists: list[tuple[str, str]] = []

    for label_path in labels_dir.rglob("*.txt"):
        box_num = count_valid_boxes(label_path)
        if box_num <= max_box_num:
            continue

        rel_txt_path = label_path.relative_to(labels_dir)
        rel_stem = rel_txt_path.with_suffix("")
        image_path = None
        for ext in IMAGE_EXTENSIONS:
            candidate = images_dir / rel_stem.with_suffix(ext)
            if candidate.exists():
                image_path = candidate
                break

        if image_path is None:
            skipped_no_image.append(str(label_path))
            continue

        dst_label = out_labels_dir / rel_txt_path
        dst_image = out_images_dir / image_path.relative_to(images_dir)

        dst_label.parent.mkdir(parents=True, exist_ok=True)
        dst_image.parent.mkdir(parents=True, exist_ok=True)

        if dst_label.exists() or dst_image.exists():
            skipped_exists.append((str(label_path), str(image_path)))
            continue

        shutil.move(str(label_path), str(dst_label))
        shutil.move(str(image_path), str(dst_image))
        moved += 1

    return {
        "moved_pairs": moved,
        "skipped_no_image": skipped_no_image,
        "skipped_destination_exists": skipped_exists,
    }


def move_samples_by_label_id(
    images_path: str,
    labels_path: str,
    output_images_path: str,
    output_labels_path: str,
    label_id: int,
) -> dict:
    """Move samples (image + label) that contain a specific class ID.

    Preserves relative directory structure. Returns a summary dict.
    """
    from yolo_tools.utils import has_label_id

    images_dir = Path(images_path)
    labels_dir = Path(labels_path)
    out_images_dir = Path(output_images_path)
    out_labels_dir = Path(output_labels_path)

    if not images_dir.exists() or not images_dir.is_dir():
        raise NotADirectoryError(f"images_path is invalid: {images_dir}")
    if not labels_dir.exists() or not labels_dir.is_dir():
        raise NotADirectoryError(f"labels_path is invalid: {labels_dir}")

    out_images_dir.mkdir(parents=True, exist_ok=True)
    out_labels_dir.mkdir(parents=True, exist_ok=True)

    moved = 0
    skipped_no_image: list[str] = []
    skipped_exists: list[tuple[str, str]] = []

    for label_path in labels_dir.rglob("*.txt"):
        if not has_label_id(label_path, label_id):
            continue

        rel_txt_path = label_path.relative_to(labels_dir)
        rel_stem = rel_txt_path.with_suffix("")
        image_path = None
        for ext in IMAGE_EXTENSIONS:
            candidate = images_dir / rel_stem.with_suffix(ext)
            if candidate.exists():
                image_path = candidate
                break

        if image_path is None:
            skipped_no_image.append(str(label_path))
            continue

        dst_label = out_labels_dir / rel_txt_path
        dst_image = out_images_dir / image_path.relative_to(images_dir)

        dst_label.parent.mkdir(parents=True, exist_ok=True)
        dst_image.parent.mkdir(parents=True, exist_ok=True)

        if dst_label.exists() or dst_image.exists():
            skipped_exists.append((str(label_path), str(image_path)))
            continue

        shutil.move(str(label_path), str(dst_label))
        shutil.move(str(image_path), str(dst_image))
        moved += 1

    return {
        "label_id": label_id,
        "moved_pairs": moved,
        "skipped_no_image": skipped_no_image,
        "skipped_destination_exists": skipped_exists,
    }


def filter_yolo_dataset(
    input_images_folder: str,
    input_labels_folder: str,
    class_index: int,
    output_images_folder: str,
    output_labels_folder: str,
    operation: str = "copy",
) -> int:
    """Filter a YOLO dataset: keep only samples containing a specific class ID.

    Args:
        operation: 'copy' or 'move'.

    Returns the number of processed samples.
    """
    from yolo_tools.labels import contains_class

    os.makedirs(output_images_folder, exist_ok=True)
    os.makedirs(output_labels_folder, exist_ok=True)

    if operation not in ("copy", "move"):
        raise ValueError("operation must be 'copy' or 'move'")

    op_func = shutil.copy2 if operation == "copy" else shutil.move
    count = 0

    for label_name in os.listdir(input_labels_folder):
        if not label_name.endswith(".txt"):
            continue

        label_path = os.path.join(input_labels_folder, label_name)

        if not contains_class(label_path, class_index):
            continue

        img_path = find_image_path(
            os.path.splitext(label_name)[0], input_images_folder
        )
        if img_path is None:
            print(f"[WARN] Image not found for {label_name}")
            continue

        dst_img = os.path.join(output_images_folder, os.path.basename(img_path))
        dst_label = os.path.join(output_labels_folder, label_name)

        op_func(img_path, dst_img)
        op_func(label_path, dst_label)
        count += 1

    print(f"Processed {count} samples.")
    return count

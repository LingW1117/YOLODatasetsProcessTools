from __future__ import annotations

import os
import shutil
from pathlib import Path

import numpy as np

from yolo_tools.utils import IMAGE_EXTENSIONS, cv_imread, cv_imwrite, find_image_path, load_labels


def modify_labels(
    input_folder: str,
    output_folder: str,
    origin_label: int,
    modify_label: int,
) -> None:
    """Replace all instances of a class ID with a new class ID in label files."""
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith(".txt"):
            continue

        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        with open(input_path, "r") as f:
            lines = f.readlines()

        modified_lines = [
            f"{modify_label}{line[len(str(origin_label)):]}"
            if line.startswith(str(origin_label))
            else line
            for line in lines
        ]

        with open(output_path, "w") as f:
            f.writelines(modified_lines)
        print(f"Modified {filename}: class {origin_label} -> {modify_label}")


def modify_labels_by_filename_prefix(
    folder_path: str,
    filefront: str,
    obj_cls: int,
) -> None:
    """Replace the first column (class ID) in label files whose name starts with a prefix."""
    for filename in os.listdir(folder_path):
        if not (filename.startswith(filefront) and filename.endswith(".txt")):
            continue

        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r") as f:
            lines = f.readlines()

        modified_lines = []
        for line in lines:
            columns = line.split()
            if columns:
                columns[0] = str(obj_cls)
                modified_lines.append(" ".join(columns) + "\n")

        with open(file_path, "w") as f:
            f.writelines(modified_lines)
        print(f"Modified {filename}: class -> {obj_cls}")


def filter_labels(
    input_folder: str,
    output_folder: str,
    filter_class: int,
) -> None:
    """Remove all lines of a given class ID from label files."""
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith(".txt"):
            continue

        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        with open(input_path, "r") as f:
            lines = f.readlines()

        filtered_lines = [
            line for line in lines
            if line.split()[0] != str(filter_class)
        ]

        with open(output_path, "w") as f:
            f.writelines(filtered_lines)
        print(f"Filtered {filename}: removed class {filter_class}")


def delete_empty_label_files(labels_folder: str) -> tuple[int, int]:
    """Delete label files that contain no valid bounding boxes.

    Returns (checked_count, deleted_count).
    """
    from yolo_tools.utils import is_empty_label_file

    labels_dir = Path(labels_folder)
    if not labels_dir.exists():
        raise FileNotFoundError(f"labels_folder not found: {labels_dir}")
    if not labels_dir.is_dir():
        raise NotADirectoryError(f"labels_folder is not a directory: {labels_dir}")

    checked = 0
    deleted = 0

    for p in labels_dir.rglob("*.txt"):
        checked += 1
        if is_empty_label_file(p):
            p.unlink()
            deleted += 1

    return checked, deleted


def move_empty_labels(
    label_path: str,
    empty_labels_path: str,
) -> None:
    """Move empty label files to a separate directory.

    Handles name collisions by appending _1, _2, etc.
    """
    from yolo_tools.utils import is_empty_label_file

    if not label_path:
        raise ValueError("label_path is empty")
    if not empty_labels_path:
        raise ValueError("empty_labels_path is empty")

    os.makedirs(empty_labels_path, exist_ok=True)

    for root, _, files in os.walk(label_path):
        for name in files:
            if not name.lower().endswith(".txt"):
                continue
            src = os.path.join(root, name)
            if is_empty_label_file(src):
                dst = os.path.join(empty_labels_path, name)
                if os.path.exists(dst):
                    base, ext = os.path.splitext(name)
                    i = 1
                    while True:
                        candidate = os.path.join(empty_labels_path, f"{base}_{i}{ext}")
                        if not os.path.exists(candidate):
                            dst = candidate
                            break
                        i += 1
                shutil.move(src, dst)


def ensure_empty_labels(
    images_folder: str,
    labels_folder: str,
    img_exts: tuple[str, ...] = IMAGE_EXTENSIONS,
) -> tuple[int, int]:
    """Create empty label files for images that lack them.

    Existing label files are never overwritten.
    Returns (created_count, skipped_existing_count).
    """
    images_dir = Path(images_folder)
    labels_dir = Path(labels_folder)
    labels_dir.mkdir(parents=True, exist_ok=True)

    img_exts = tuple(e.lower() for e in img_exts)

    created = 0
    skipped = 0

    for p in images_dir.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() not in img_exts:
            continue

        label_path = labels_dir / (p.stem + ".txt")
        if label_path.exists():
            skipped += 1
            continue

        label_path.write_text("", encoding="utf-8")
        created += 1

    return created, skipped


def find_files_with_label(
    folder_path: str,
    label: int,
) -> list[str]:
    """List label filenames that contain a specific class ID."""
    matching_files = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r") as f:
            for line in f:
                if line.startswith(str(label)):
                    matching_files.append(filename)
                    break

    return matching_files


def contains_class(label_path: str | Path, class_index: int) -> bool:
    """Check if a YOLO label file contains a specific class ID."""
    with open(label_path, "r") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.split()[0] == str(class_index):
                return True
    return False


def convert_to_yoloclass(name: str, names: list[str] | None = None) -> int:
    """Convert a class name string to its YOLO class ID.

    If names is not provided, returns -1 (caller should provide their own mapping).
    """
    if names is None:
        return -1
    name_to_class_id = {n: idx for idx, n in enumerate(names)}
    return name_to_class_id.get(name, -1)


def get_category_by_index(index: int, names: list[str]) -> str:
    """Get the class name for a given class ID index."""
    if 0 <= index < len(names):
        return names[index]
    return "Invalid index"


def draw_labels(
    labels_path: str,
    images_path: str,
    save_path: str,
    class_names: list[str] | None = None,
) -> int:
    """Draw YOLO-format labels on images and save the result.

    Args:
        labels_path: Directory containing YOLO .txt label files.
        images_path: Directory containing corresponding image files.
        save_path: Directory where annotated images will be saved.
        class_names: Optional list of class names (index → name).

    Returns:
        Number of images processed.
    """
    import cv2

    labels_dir = Path(labels_path)
    images_dir = Path(images_path)
    save_dir = Path(save_path)
    save_dir.mkdir(parents=True, exist_ok=True)

    colors = [
        (0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (128, 0, 128), (128, 128, 0),
        (0, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128),
    ]

    processed = 0
    for label_file in labels_dir.glob("*.txt"):
        stem = label_file.stem
        img_path = find_image_path(stem, images_dir)
        if img_path is None:
            continue

        img = cv_imread(str(img_path))
        if img is None:
            continue

        h, w = img.shape[:2]
        labels = load_labels(str(label_file))

        for lab in labels:
            cls_id = int(lab[0])
            xc, yc, bw, bh = lab[1], lab[2], lab[3], lab[4]

            x1 = int((xc - bw / 2) * w)
            y1 = int((yc - bh / 2) * h)
            x2 = int((xc + bw / 2) * w)
            y2 = int((yc + bh / 2) * h)

            color = colors[cls_id % len(colors)]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            label_text = class_names[cls_id] if class_names and cls_id < len(class_names) else str(cls_id)
            (tw, th), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(img, (x1, y1 - th - baseline - 4), (x1 + tw, y1), color, -1)
            cv2.putText(img, label_text, (x1, y1 - baseline - 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        out_path = save_dir / img_path.name
        cv_imwrite(str(out_path), img)
        processed += 1

    return processed

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Generator

import cv2
import numpy as np

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")


def cv_imread(path: str) -> np.ndarray | None:
    """Read an image with Chinese path support."""
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def cv_imwrite(path: str, img: np.ndarray) -> bool:
    """Write an image with Chinese path support."""
    ext = os.path.splitext(path)[1]
    result, encoded_img = cv2.imencode(ext, img)
    if result:
        encoded_img.tofile(path)
        return True
    return False


def load_labels(label_path: str) -> list[list[int | float]]:
    """Read YOLO labels with automatic encoding detection.

    Returns a list of [class_id, x_center, y_center, width, height].
    """
    labels: list[list[int | float]] = []
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
            continue

    with open(label_path, "rb") as f:
        raw = f.read().decode("latin-1", errors="ignore")
    for line in raw.splitlines():
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        cls, x, y, w, h = parts
        labels.append([int(cls), float(x), float(y), float(w), float(h)])
    return labels


def save_labels(label_path: str, labels: list[list[int | float]]) -> None:
    """Save YOLO labels in UTF-8 encoding with normalized line endings."""
    lines = [
        f"{lab[0]} {lab[1]:.6f} {lab[2]:.6f} {lab[3]:.6f} {lab[4]:.6f}"
        for lab in labels
    ]
    with open(label_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def find_image_path(stem: str, images_dir: str | Path) -> Path | None:
    """Find the image file matching a given stem (filename without extension).

    Searches across all common image extensions.
    """
    images_path = Path(images_dir)
    for ext in IMAGE_EXTENSIONS:
        candidate = images_path / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def iter_label_paths(labels_dir: str | Path) -> Generator[Path, None, None]:
    """Yield all .txt label file paths under a directory."""
    for p in Path(labels_dir).rglob("*.txt"):
        yield p


def is_empty_label_file(path: str | Path) -> bool:
    """Check if a YOLO label file has no valid bounding box content.

    Returns True if the file is empty, only contains whitespace, or only
    contains comment lines starting with '#'.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#"):
                    return False
        return True
    except OSError:
        return False


def count_valid_boxes(label_path: Path) -> int:
    """Count the number of non-comment, non-empty lines in a label file."""
    count = 0
    with label_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                count += 1
    return count


def has_label_id(label_path: Path, label_id: int) -> bool:
    """Check whether a label file contains a specific class ID."""
    target = str(label_id)
    with label_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.split(maxsplit=1)[0] == target:
                return True
    return False


def safe_copy_or_move(src: Path, dst: Path, method: str) -> Path:
    """Copy or move src to dst. Appends _1, _2 suffix if dst already exists."""
    dst.parent.mkdir(parents=True, exist_ok=True)

    final_dst = dst
    if final_dst.exists():
        stem, suf = dst.stem, dst.suffix
        i = 1
        while True:
            candidate = dst.with_name(f"{stem}_{i}{suf}")
            if not candidate.exists():
                final_dst = candidate
                break
            i += 1

    if method == "copy":
        shutil.copy2(src, final_dst)
    elif method == "move":
        shutil.move(str(src), str(final_dst))
    else:
        raise ValueError("method must be 'copy' or 'move'")

    return final_dst


def convert_to_yolo_format(
    x_min: float, y_min: float, box_width: float, box_height: float,
    img_width: int, img_height: int, class_id: int,
) -> str:
    """Convert pixel coordinates to a YOLO-format label line."""
    x_center = (x_min + box_width / 2) / img_width
    y_center = (y_min + box_height / 2) / img_height
    norm_width = box_width / img_width
    norm_height = box_height / img_height
    return f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}"

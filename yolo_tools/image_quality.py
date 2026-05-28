from __future__ import annotations

import os
import shutil
from pathlib import Path

import cv2
from PIL import Image

from yolo_tools.utils import IMAGE_EXTENSIONS


def check_images(
    input_dir: str,
    exts: set[str] | None = None,
) -> list[tuple[str, str]]:
    """Scan a directory for corrupted or unreadable images.

    Uses both OpenCV and PIL for validation. Returns a list of
    (filepath, error_message) tuples.
    """
    if exts is None:
        exts = {".jpg", ".jpeg", ".png"}

    bad_images: list[tuple[str, str]] = []
    all_images: list[str] = []

    for root, _, files in os.walk(input_dir):
        for fname in files:
            ext = os.path.splitext(fname)[-1].lower()
            if ext in exts:
                fpath = os.path.join(root, fname)
                all_images.append(fpath)

                try:
                    img = cv2.imread(fpath)
                    if img is None:
                        bad_images.append((fpath, "cv2 read returned None"))
                        continue
                except Exception as e:
                    bad_images.append((fpath, f"cv2 exception: {e}"))
                    continue

                try:
                    with Image.open(fpath) as im:
                        im.verify()
                except Exception as e:
                    bad_images.append((fpath, f"PIL exception: {e}"))

    print(f"Scanned {len(all_images)} images, found {len(bad_images)} bad.")
    return bad_images


def check_and_fix_images(
    input_dir: str,
    output_dir: str | None = None,
    exts: set[str] | None = None,
) -> list[tuple[str, str]]:
    """Detect and attempt to repair corrupted JPEG images.

    If output_dir is None, files are overwritten in place.
    Returns a list of unrecoverable (filepath, error) tuples.
    """
    if exts is None:
        exts = {".jpg", ".jpeg"}

    if output_dir is None:
        output_dir = input_dir
    os.makedirs(output_dir, exist_ok=True)

    bad_images: list[tuple[str, str]] = []
    fixed_count = 0
    all_images: list[str] = []

    for root, _, files in os.walk(input_dir):
        for fname in files:
            ext = os.path.splitext(fname)[-1].lower()
            if ext not in exts:
                continue

            fpath = os.path.join(root, fname)
            all_images.append(fpath)

            rel_path = os.path.relpath(fpath, input_dir)
            out_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            is_bad = False

            try:
                img = cv2.imread(fpath)
                if img is None:
                    is_bad = True
            except Exception:
                is_bad = True

            if not is_bad:
                try:
                    with Image.open(fpath) as im:
                        im.verify()
                except Exception:
                    is_bad = True

            if is_bad:
                try:
                    with Image.open(fpath) as im:
                        im = im.convert("RGB")
                        im.save(out_path, "JPEG", quality=95)
                    fixed_count += 1
                    print(f"[FIXED] {fpath} -> {out_path}")
                except Exception as e:
                    bad_images.append((fpath, str(e)))
                    print(f"[FAILED] {fpath}: {e}")
            else:
                if input_dir != output_dir:
                    with Image.open(fpath) as im:
                        im.save(out_path, "JPEG", quality=95)

    print(f"\nScanned {len(all_images)} images, fixed {fixed_count}, "
          f"{len(bad_images)} unrecoverable.")
    return bad_images


def find_single_channel_images(
    images_folder: str,
    img_exts: tuple[str, ...] = IMAGE_EXTENSIONS,
) -> list[str]:
    """Find all single-channel (grayscale) images in a directory.

    Uses PIL mode detection: L, 1, I, I;16 are considered single-channel.
    """
    images_dir = Path(images_folder)
    if not images_dir.exists():
        raise FileNotFoundError(f"images_folder not found: {images_dir}")
    if not images_dir.is_dir():
        raise NotADirectoryError(f"images_folder is not a directory: {images_dir}")

    img_exts = tuple(e.lower() for e in img_exts)

    single_channel: list[str] = []
    for p in images_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in img_exts:
            continue

        try:
            with Image.open(p) as im:
                if im.mode in ("L", "1", "I", "I;16"):
                    single_channel.append(str(p))
        except Exception:
            continue

    return single_channel


def copy_single_channel_images(
    src_dir: str,
    dst_dir: str,
) -> int:
    """Find and copy single-channel (grayscale) images to a destination directory.

    Uses OpenCV shape detection. Returns the number of copied images.
    """
    os.makedirs(dst_dir, exist_ok=True)

    length = len(os.listdir(src_dir))
    num = 1
    count = 0

    for root, _, files in os.walk(src_dir):
        for file in files:
            print(f"{num}/{length}")
            file_path = os.path.join(root, file)
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

            if img is None:
                num += 1
                continue

            if len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1):
                dst_path = os.path.join(dst_dir, file)
                shutil.copy2(file_path, dst_path)
                count += 1
            num += 1

    print(f"Copied {count} single-channel images to {dst_dir}")
    return count

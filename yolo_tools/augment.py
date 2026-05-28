from __future__ import annotations

import glob
import math
import os
from pathlib import Path

import cv2
import numpy as np

from yolo_tools.utils import cv_imread, cv_imwrite, load_labels, save_labels


def rotate_point(
    x: float, y: float, cx: float, cy: float, angle_rad: float,
) -> tuple[float, float]:
    """Rotate a point (x, y) around center (cx, cy) by angle_rad radians."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    x_new = cos_a * (x - cx) - sin_a * (y - cy) + cx
    y_new = sin_a * (x - cx) + cos_a * (y - cy) + cy
    return x_new, y_new


def rotate_image_and_labels(
    img: np.ndarray,
    labels: list[list[int | float]],
    angle: float,
    direction: str = "left",
) -> tuple[np.ndarray, list[list[int | float]]]:
    """Rotate an image and its YOLO labels, filling empty areas with white.

    Args:
        img: BGR image as numpy array.
        labels: YOLO-format labels [[class_id, x, y, w, h], ...].
        angle: Rotation angle in degrees.
        direction: 'left' (counter-clockwise) or 'right' (clockwise).

    Returns:
        (rotated_image, rotated_labels) tuple.
    """
    h, w = img.shape[:2]
    cx, cy = w / 2, h / 2

    if direction == "right":
        angle = -angle
    angle_rad = math.radians(angle)

    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])

    new_w = int(h * sin + w * cos)
    new_h = int(h * cos + w * sin)

    M[0, 2] += (new_w / 2) - cx
    M[1, 2] += (new_h / 2) - cy

    rotated_img = cv2.warpAffine(
        img, M, (new_w, new_h), borderValue=(255, 255, 255)
    )

    new_labels: list[list[int | float]] = []
    for lab in labels:
        cls, x, y, bw, bh = lab
        x_c = x * w
        y_c = y * h
        box_w = bw * w
        box_h = bh * h

        pts = np.array([
            [x_c - box_w / 2, y_c - box_h / 2],
            [x_c + box_w / 2, y_c - box_h / 2],
            [x_c + box_w / 2, y_c + box_h / 2],
            [x_c - box_w / 2, y_c + box_h / 2],
        ])

        ones = np.ones((4, 1))
        pts_homo = np.hstack([pts, ones])
        rotated_pts = (M @ pts_homo.T).T

        x_min_new = np.min(rotated_pts[:, 0])
        y_min_new = np.min(rotated_pts[:, 1])
        x_max_new = np.max(rotated_pts[:, 0])
        y_max_new = np.max(rotated_pts[:, 1])

        if x_max_new <= x_min_new or y_max_new <= y_min_new:
            continue

        new_x = (x_min_new + x_max_new) / 2 / new_w
        new_y = (y_min_new + y_max_new) / 2 / new_h
        new_bw = (x_max_new - x_min_new) / new_w
        new_bh = (y_max_new - y_min_new) / new_h

        new_labels.append([cls, new_x, new_y, new_bw, new_bh])

    return rotated_img, new_labels


def augment_dataset(
    img_dir: str,
    label_dir: str,
    out_img_dir: str,
    out_label_dir: str,
    direction: str = "left",
    angle: float = 90,
) -> None:
    """Augment a dataset by rotating images and labels by a single angle.

    Output files are named {original_name}_{direction}{angle}.ext.
    """
    os.makedirs(out_img_dir, exist_ok=True)
    os.makedirs(out_label_dir, exist_ok=True)

    img_exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp")

    for ext in img_exts:
        for img_path in glob.glob(os.path.join(img_dir, ext)):
            img_name = Path(img_path).stem
            label_path = os.path.join(label_dir, img_name + ".txt")

            img = cv_imread(img_path)
            if img is None:
                print(f"[WARN] Failed to read: {img_path}")
                continue

            labels = load_labels(label_path)
            rotated_img, rotated_labels = rotate_image_and_labels(
                img, labels, angle, direction,
            )

            new_name = f"{img_name}_{direction}{angle}"
            out_img_path = os.path.join(
                out_img_dir, new_name + Path(img_path).suffix
            )
            out_label_path = os.path.join(out_label_dir, new_name + ".txt")

            cv_imwrite(out_img_path, rotated_img)
            save_labels(out_label_path, rotated_labels)
            print(f"Processed: {new_name}")


def augment_dataset_auto(
    img_dir: str,
    label_dir: str,
    out_img_dir: str,
    out_label_dir: str,
    direction: str = "left",
    angle_start: float = 0,
    angle_end: float = 180,
    angle_step: float = 2,
) -> None:
    """Augment a dataset by rotating images through a range of angles.

    Generates versions at every angle_step degrees from angle_start to angle_end.
    Output files are named {original_name}_{direction}{angle}.ext.
    """
    os.makedirs(out_img_dir, exist_ok=True)
    os.makedirs(out_label_dir, exist_ok=True)

    img_exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp")

    for ext in img_exts:
        for img_path in glob.glob(os.path.join(img_dir, ext)):
            img_name = Path(img_path).stem
            label_path = os.path.join(label_dir, img_name + ".txt")

            img = cv_imread(img_path)
            if img is None:
                print(f"[WARN] Failed to read: {img_path}")
                continue

            labels = load_labels(label_path)

            angle = angle_start
            while angle <= angle_end:
                rotated_img, rotated_labels = rotate_image_and_labels(
                    img, labels, angle, direction,
                )

                new_name = f"{img_name}_{direction}{angle}"
                out_img_path = os.path.join(
                    out_img_dir, new_name + Path(img_path).suffix
                )
                out_label_path = os.path.join(out_label_dir, new_name + ".txt")

                cv_imwrite(out_img_path, rotated_img)
                save_labels(out_label_path, rotated_labels)
                print(f"Processed: {new_name}")

                angle += angle_step

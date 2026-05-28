from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import fitz
from PIL import Image


def convert_single_to_three_channel(src_dir: str, dst_dir: str) -> int:
    """Convert single-channel images to 3-channel and save to dst_dir.

    Returns the number of converted images.
    """
    os.makedirs(dst_dir, exist_ok=True)

    count = 0
    for root, _, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)

            if not file.lower().endswith(
                (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
            ):
                continue

            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                continue

            if len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1):
                img_3ch = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                dst_path = os.path.join(dst_dir, file)
                cv2.imwrite(dst_path, img_3ch)
                count += 1

    print(f"Converted {count} single-channel images to 3-channel in {dst_dir}")
    return count


def convert_images_to_pdf(folder_path: str, output_pdf: str) -> None:
    """Merge all images in a folder into a single PDF, sorted by filename."""
    images = [
        img for img in os.listdir(folder_path)
        if img.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    images.sort()

    if not images:
        print("No images found.")
        return

    first_image = Image.open(os.path.join(folder_path, images[0])).convert("RGB")
    other_images = [
        Image.open(os.path.join(folder_path, img)).convert("RGB")
        for img in images[1:]
    ]

    first_image.save(output_pdf, save_all=True, append_images=other_images)
    print(f"PDF saved: {output_pdf}")


def convert_pdf_to_jpg(pdf_folder_path: str, pic_folder_path: str) -> None:
    """Convert the first page of each PDF in a folder to a JPG image."""
    os.makedirs(pic_folder_path, exist_ok=True)

    for root, _, files in os.walk(pdf_folder_path):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(root, file)
            base_name = os.path.splitext(file)[0]
            pic_path = os.path.join(pic_folder_path, f"{base_name}.jpg")

            try:
                doc = fitz.open(pdf_path)
                page = doc.load_page(0)
                pix = page.get_pixmap()
                pix.save(pic_path)
                print(f"Converted: {pic_path}")
            except Exception as e:
                print(f"Failed to convert {pdf_path}: {e}")


def xml_folder_to_yolo_txt_folder_auto_map(
    xml_folder: str,
    txt_folder: str,
) -> dict[str, int]:
    """Batch-convert VOC XML annotations to YOLO TXT format.

    Class IDs are auto-assigned (starting from 0) as new class names are encountered.
    Returns the generated class mapping dict {class_name: class_id}.
    """
    os.makedirs(txt_folder, exist_ok=True)

    class_mapping: dict[str, int] = {}
    next_class_id = 0

    for filename in sorted(os.listdir(xml_folder)):
        if not filename.lower().endswith(".xml"):
            continue

        xml_path = os.path.join(xml_folder, filename)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(txt_folder, txt_filename)

        width_node = root.find(".//size/width")
        height_node = root.find(".//size/height")
        if width_node is None or height_node is None:
            continue

        image_width = float(width_node.text)
        image_height = float(height_node.text)
        if image_width <= 0 or image_height <= 0:
            continue

        with open(txt_path, "w", encoding="utf-8") as txt_file:
            for obj in root.findall(".//object"):
                name_node = obj.find("name")
                bndbox = obj.find("bndbox")
                if name_node is None or bndbox is None:
                    continue

                name = name_node.text.strip()

                if name not in class_mapping:
                    class_mapping[name] = next_class_id
                    next_class_id += 1
                class_index = class_mapping[name]

                try:
                    xmin = float(bndbox.find("xmin").text)
                    ymin = float(bndbox.find("ymin").text)
                    xmax = float(bndbox.find("xmax").text)
                    ymax = float(bndbox.find("ymax").text)
                except Exception:
                    continue

                if xmax <= xmin or ymax <= ymin:
                    continue

                x_center = ((xmin + xmax) / 2.0) / image_width
                y_center = ((ymin + ymax) / 2.0) / image_height
                w = (xmax - xmin) / image_width
                h = (ymax - ymin) / image_height

                txt_file.write(f"{class_index} {x_center} {y_center} {w} {h}\n")

    return class_mapping


def rename_images_in_folder(
    input_folder: str,
    output_folder: str,
    class_name: str,
    extensions: list[str] | None = None,
) -> None:
    """Batch rename images to class_name_1.jpg, class_name_2.jpg, ...

    Files are sorted alphabetically before renaming to ensure consistent ordering.
    """
    if extensions is None:
        extensions = [".jpg", ".png", ".jpeg", ".tif"]

    os.makedirs(output_folder, exist_ok=True)

    files = os.listdir(input_folder)
    files = [f for f in files if any(f.lower().endswith(ext) for ext in extensions)]
    files.sort()

    for index, image_file in enumerate(files, start=1):
        old_path = os.path.join(input_folder, image_file)
        new_name = f"{class_name}_{index}.jpg"
        new_path = os.path.join(output_folder, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed {old_path} -> {new_path}")


def rename_pic_label(
    images_folder: str,
    labels_folder: str,
    cls: str,
) -> None:
    """Synchronized rename of images and their matching labels.

    Output format: cls_0001.ext, cls_0002.ext for both images and labels.
    """
    image_files = os.listdir(images_folder)
    label_files = os.listdir(labels_folder)

    for i, image_file in enumerate(image_files):
        image_extension = os.path.splitext(image_file)[1]
        image_stem = os.path.splitext(image_file)[0]
        corresponding_label = f"{image_stem}.txt"

        if corresponding_label not in label_files:
            print(f"WARNING: No label found for {image_file}, skipping.")
            continue

        try:
            new_image_name = f"{cls}_{i + 1:04d}{image_extension}"
            new_label_name = f"{cls}_{i + 1:04d}.txt"

            os.rename(
                os.path.join(images_folder, image_file),
                os.path.join(images_folder, new_image_name),
            )
            os.rename(
                os.path.join(labels_folder, corresponding_label),
                os.path.join(labels_folder, new_label_name),
            )
            print(f"Renamed: {image_file} -> {new_image_name}")
        except Exception as e:
            print(f"Error processing {image_file}: {e}")

    print("Dataset renaming complete.")

from pathlib import Path
import shutil


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")


def _count_valid_boxes(label_path: Path) -> int:
    count = 0
    with label_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            count += 1
    return count


def _find_image_by_relative_stem(images_dir: Path, rel_txt_path: Path) -> Path | None:
    rel_stem = rel_txt_path.with_suffix("")
    for ext in IMAGE_EXTENSIONS:
        candidate = images_dir / rel_stem.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None


def move_samples_more_than_n(
    input_images_path: str,
    input_labels_path: str,
    max_box_num: int,
    output_images_path: str,
    output_labels_path: str,
) -> dict:
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
    skipped_no_image = []
    skipped_exists = []

    for label_path in labels_dir.rglob("*.txt"):
        box_num = _count_valid_boxes(label_path)
        if box_num <= max_box_num:
            continue

        rel_txt_path = label_path.relative_to(labels_dir)
        image_path = _find_image_by_relative_stem(images_dir, rel_txt_path)
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

    summary = {
        "moved_pairs": moved,
        "skipped_no_image": skipped_no_image,
        "skipped_destination_exists": skipped_exists,
    }
    return summary


if __name__ == "__main__":
    # Example:
    # result = move_samples_more_than_n(
    #     input_images_path=r"",
    #     input_labels_path=r"",
    #     max_box_num=2,
    #     output_images_path=r"",
    #     output_labels_path=r"",
    # )
    # print(result)
    pass

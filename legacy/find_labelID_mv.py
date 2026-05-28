from pathlib import Path
import shutil


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")


def _has_label_id(label_path: Path, label_id: int) -> bool:
    target = str(label_id)
    with label_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            first = s.split(maxsplit=1)[0]
            if first == target:
                return True
    return False


def _find_image_by_relative_stem(images_dir: Path, rel_txt_path: Path) -> Path | None:
    rel_stem = rel_txt_path.with_suffix("")
    for ext in IMAGE_EXTENSIONS:
        candidate = images_dir / rel_stem.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None


def move_samples_by_label_id(
    images_path: str,
    labels_path: str,
    outputimages_path: str,
    outputlabels_path: str,
    labelID: int,
) -> dict:
    images_dir = Path(images_path)
    labels_dir = Path(labels_path)
    out_images_dir = Path(outputimages_path)
    out_labels_dir = Path(outputlabels_path)

    if not images_dir.exists() or not images_dir.is_dir():
        raise NotADirectoryError(f"images_path is invalid: {images_dir}")
    if not labels_dir.exists() or not labels_dir.is_dir():
        raise NotADirectoryError(f"labels_path is invalid: {labels_dir}")

    out_images_dir.mkdir(parents=True, exist_ok=True)
    out_labels_dir.mkdir(parents=True, exist_ok=True)

    moved = 0
    skipped_no_image = []
    skipped_exists = []

    for label_path in labels_dir.rglob("*.txt"):
        if not _has_label_id(label_path, labelID):
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

    return {
        "label_id": labelID,
        "moved_pairs": moved,
        "skipped_no_image": skipped_no_image,
        "skipped_destination_exists": skipped_exists,
    }


if __name__ == "__main__":
    # Example:
    # result = move_samples_by_label_id(
    #     images_path=r"",
    #     labels_path=r"",
    #     outputimages_path=r"",
    #     outputlabels_path=r"",
    #     labelID=3,
    # )
    # print(result)
    pass

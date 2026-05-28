from pathlib import Path

def delete_images_without_labels(images_floder: str, labels_floder: str,
                                img_exts=(".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")):
    """
    删除 images_floder 下“没有标签”的图片：
    - 若 labels_floder 中不存在同名 .txt -> 删除图片
    - 若存在同名 .txt 但为空标签（忽略空行/空白行/#注释）-> 删除图片
    返回 (checked_images, deleted_images)
    """
    images_dir = Path(images_floder)
    labels_dir = Path(labels_floder)

    if not images_dir.exists():
        raise FileNotFoundError(f"images_floder not found: {images_dir}")
    if not images_dir.is_dir():
        raise NotADirectoryError(f"images_floder is not a folder: {images_dir}")

    if not labels_dir.exists():
        # labels 文件夹不存在则认为都无标签
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

        # 1) 没有同名标签文件 => 删除图片
        if not label_path.exists():
            img_path.unlink()
            deleted += 1
            continue

        # 2) 有同名标签，但为空标签 => 删除图片
        has_label = False
        with label_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                if s.startswith("#"):
                    continue
                has_label = True
                break

        if not has_label:
            img_path.unlink()
            deleted += 1

    return checked, deleted


# 示例：
img_path = r""
label_path = r""

checked, deleted = delete_images_without_labels(img_path, label_path)
print("checked:", checked, "deleted:", deleted)
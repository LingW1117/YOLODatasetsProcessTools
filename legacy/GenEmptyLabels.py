from pathlib import Path

def ensure_empty_labels(images_floder: str, labels_floder: str,
                        img_exts=(".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")):
    """
    为 images_floder 中没有标签的图片，在 labels_floder 下生成同名空 .txt
    例如: images_floder/a.jpg -> labels_floder/a.txt
    已存在的标签文件不会被覆盖
    """
    images_dir = Path(images_floder)
    labels_dir = Path(labels_floder)
    labels_dir.mkdir(parents=True, exist_ok=True)

    img_exts = tuple(e.lower() for e in img_exts)

    created = 0
    skipped_existing = 0

    for p in images_dir.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() not in img_exts:
            continue

        label_path = labels_dir / (p.stem + ".txt")
        if label_path.exists():
            skipped_existing += 1
            continue

        # 创建空文件（不覆盖）
        label_path.write_text("", encoding="utf-8")
        created += 1

    return created, skipped_existing


# 示例

img_path = r''
labels_path = r''
created, skipped = ensure_empty_labels(img_path, labels_path)
print("新建空标签数:", created, "已存在跳过数:", skipped)
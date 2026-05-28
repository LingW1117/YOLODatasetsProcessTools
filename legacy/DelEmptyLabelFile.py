from pathlib import Path

def delete_empty_label_txt(labels_floder: str):
    """
    删除 labels_floder 下“空标签”的 .txt：
    - 忽略空行/纯空白行
    - 忽略以 # 开头的注释行
    返回 (checked, deleted)
    """
    labels_dir = Path(labels_floder)
    if not labels_dir.exists():
        raise FileNotFoundError(f"labels_floder not found: {labels_dir}")
    if not labels_dir.is_dir():
        raise NotADirectoryError(f"labels_floder is not a folder: {labels_dir}")

    checked = 0
    deleted = 0

    for p in labels_dir.rglob("*.txt"):
        checked += 1

        has_label = False
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                if s.startswith("#"):
                    continue
                has_label = True
                break

        if not has_label:
            p.unlink()
            deleted += 1

    return checked, deleted


# 示例：
checked, deleted = delete_empty_label_txt(r"")
print(checked, deleted)
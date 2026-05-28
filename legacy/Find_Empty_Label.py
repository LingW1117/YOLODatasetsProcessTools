import os
import shutil


def is_empty_label_file(path: str) -> bool:
    # YOLO label considered empty if file has no non-whitespace content
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    return False
        return True
    except OSError:
        return False


def main(label_path: str, empty_labels_path: str) -> None:
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
                # Avoid overwrite collisions by appending a counter
                if os.path.exists(dst):
                    base, ext = os.path.splitext(name)
                    i = 1
                    while True:
                        candidate = os.path.join(
                            empty_labels_path, f"{base}_{i}{ext}"
                        )
                        if not os.path.exists(candidate):
                            dst = candidate
                            break
                        i += 1
                shutil.move(src, dst)


if __name__ == "__main__":
    # Set paths here (no argparse per request)
    label_path = r""
    empty_labels_path = r""
    main(label_path, empty_labels_path)
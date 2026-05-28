import os
import shutil


def find_image(base_name, images_folder):
    """
    查找是否存在对应图片（支持多种格式）
    """
    exts = [
        '.jpg', '.jpeg', '.png', '.bmp',
        '.webp', '.tif', '.tiff'
    ]

    for ext in exts:
        img_path = os.path.join(images_folder, base_name + ext)
        if os.path.exists(img_path):
            return True

    return False


def move_orphan_labels(images_folder, labels_folder, output_path):
    """
    找出有标签但没有图片的txt文件，并移动到output_path
    """

    os.makedirs(output_path, exist_ok=True)

    moved_count = 0

    for label_name in os.listdir(labels_folder):

        if not label_name.endswith(".txt"):
            continue

        base_name = os.path.splitext(label_name)[0]

        if not find_image(base_name, images_folder):
            src = os.path.join(labels_folder, label_name)
            dst = os.path.join(output_path, label_name)

            shutil.move(src, dst)
            moved_count += 1

    print(f"[INFO] Done. Moved {moved_count} orphan label files.")


if __name__ == "__main__":

    # ===== 参数区 =====
    images_floder = r""
    labels_floder = r""
    output_path = r""
    # =================

    move_orphan_labels(
        images_folder=images_floder,
        labels_folder=labels_floder,
        output_path=output_path
    )
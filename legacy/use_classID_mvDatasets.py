import os
import shutil


def find_image(label_name, images_folder):
    """
    根据 label 文件名查找对应图片
    """
    base_name = os.path.splitext(label_name)[0]
    exts = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif']

    for ext in exts:
        img_path = os.path.join(images_folder, base_name + ext)
        if os.path.exists(img_path):
            return img_path

    return None


def contains_class(label_path, class_index):
    """
    判断 label 是否包含指定类别
    """
    with open(label_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            if line.split()[0] == str(class_index):
                return True
    return False


def filter_yolo_dataset(
        input_images_folder,
        input_labels_folder,
        class_index,
        output_images_folder,
        output_labels_folder,
        oprmethod='copy'):
    """
    从 YOLO 数据集中筛选包含指定 class_index 的样本
    oprmethod: 'copy' or 'move'
    """

    os.makedirs(output_images_folder, exist_ok=True)
    os.makedirs(output_labels_folder, exist_ok=True)

    if oprmethod not in ('copy', 'move'):
        raise ValueError("oprmethod must be 'copy' or 'move'")

    op_func = shutil.copy2 if oprmethod == 'copy' else shutil.move

    count = 0

    for label_name in os.listdir(input_labels_folder):

        if not label_name.endswith('.txt'):
            continue

        label_path = os.path.join(input_labels_folder, label_name)

        if not contains_class(label_path, class_index):
            continue

        img_path = find_image(label_name, input_images_folder)
        if img_path is None:
            print(f"[WARN] Image not found for {label_name}")
            continue

        dst_img = os.path.join(output_images_folder, os.path.basename(img_path))
        dst_label = os.path.join(output_labels_folder, label_name)

        op_func(img_path, dst_img)
        op_func(label_path, dst_label)

        count += 1

    print(f"[INFO] Done. Total processed: {count}")



if __name__ == "__main__":

    # ===== 参数配置 =====
    root_path = r''
    input_images_floder = f"{root_path}/images"
    input_labels_floder = f"{root_path}/labels"
    class_index = 4                # 需要筛选的类别 id
    output_images_floder = f"{root_path}/Clause/images"
    output_labels_floder = f"{root_path}/Clause/labels"
    oprmethod = "move"              # "copy" or "move"
    # ===================

    filter_yolo_dataset(
        input_images_folder=input_images_floder,
        input_labels_folder=input_labels_floder,
        class_index=class_index,
        output_images_folder=output_images_floder,
        output_labels_folder=output_labels_floder,
        oprmethod=oprmethod
    )
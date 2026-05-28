import os
import shutil

# 定义文件夹路径
images_folder = r""
labels_folder = r""
missing_labels_folder = r""
os.makedirs(missing_labels_folder, exist_ok=True)
# 获取所有图片文件
image_files = [f for f in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, f))]

# 遍历每个图片文件，检查是否存在对应的标签文件
for image_file in image_files:
    image_path = os.path.join(images_folder, image_file)
    label_file = os.path.join(labels_folder, os.path.splitext(image_file)[0] + ".txt")

    # 如果标签文件不存在，则将图片移动到另一个文件夹
    if not os.path.exists(label_file):
        missing_image_path = os.path.join(missing_labels_folder, image_file)
        shutil.move(image_path, missing_image_path)
        print(f"Moved {image_file} to {missing_labels_folder}")

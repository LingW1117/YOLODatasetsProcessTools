import os

def rename_images_in_folder(input_folder, output_folder, class_name, extensions):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取文件夹中的所有文件
    files = os.listdir(input_folder)

    # 过滤出文件
    files = [f for f in files if any(f.lower().endswith(ext) for ext in extensions)]

    # 按文件名排序（可选）
    files.sort()

    # 重命名并移动图片
    index = 1
    for image_file in files:
        old_path = os.path.join(input_folder, image_file)
        new_name = f"{class_name}_{index}.jpg"
        new_path = os.path.join(output_folder, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed {old_path} to {new_path}")
        index += 1

# 示例调用
input_folder = r''
extensions = ['.jpg', '.png', '.jpeg', '.tif']
output_folder = input_folder
class_name = 'temp'
rename_images_in_folder(input_folder, output_folder, class_name, extensions, extensions)

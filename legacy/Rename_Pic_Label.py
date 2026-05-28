import os

# 设置图片和标签文件夹的路径
images_folder = r''
labels_folder = r''
cls = 'ClassName'  # 替换为你的类别名称 作为文件名前缀

# 获取图片文件夹中的所有文件名
image_files = os.listdir(images_folder)

# 获取标签文件夹中的所有文件名
label_files = os.listdir(labels_folder)

# 遍历图片文件
for i, image_file in enumerate(image_files):
    image_extension = os.path.splitext(image_file)[1]

    # 获取图片文件名（去除扩展名）
    image_name_without_ext = os.path.splitext(image_file)[0]

    # 在标签文件夹中寻找与图片文件名匹配的标签文件
    corresponding_label_file = f"{image_name_without_ext}.txt"

    if corresponding_label_file not in label_files:
        print(f"警告：未找到对应标签文件：{corresponding_label_file} (跳过图片: {image_file})")
        continue

    # 如果找到了标签文件，进行重命名
    try:
        label_extension = os.path.splitext(corresponding_label_file)[1]

        # 使用新的命名格式，确保文件从1开始，且使用四位数字
        new_image_name = f"{cls}_{i + 1:04d}{image_extension}"
        new_label_name = f"{cls}_{i + 1:04d}{label_extension}"

        # 重命名图片和标签
        os.rename(os.path.join(images_folder, image_file), os.path.join(images_folder, new_image_name))
        os.rename(os.path.join(labels_folder, corresponding_label_file), os.path.join(labels_folder, new_label_name))

        # 记录成功重命名的文件
        print(f"重命名成功: {image_file} -> {new_image_name}, {corresponding_label_file} -> {new_label_name}")

    except Exception as e:
        print(f"错误：处理文件 {image_file} 时出现问题，错误信息：{str(e)}")

print("数据集重命名完成")
import os


def find_files_with_label(folder_path, label):
    """
    查找指定文件夹下包含指定类标签的 .txt 文件名

    :param folder_path: 要搜索的文件夹路径
    :param label: 要查找的类标签
    :return: 包含类标签的文件名列表
    """
    matching_files = []

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                # 读取文件内容
                for line in file:
                    # 检查行是否以指定的类标签开头
                    if line.startswith(str(label)):
                        matching_files.append(filename)
                        break  # 找到后跳出循环，避免重复读取

    return matching_files


# 指定文件夹路径和类标签
obj_folder = r''
label = 3

# 调用函数并打印结果
matching_files = find_files_with_label(obj_folder, label)
for file in matching_files:
    print(file)

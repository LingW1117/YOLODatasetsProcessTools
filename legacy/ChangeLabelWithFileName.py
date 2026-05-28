import os


def modify_files_with_prefix(folder_path, filefront, obj_cls):
    """
    修改指定文件夹下以指定前缀开头的 .txt 文件的第一列

    :param folder_path: 要搜索的文件夹路径
    :param filefront: 文件名前缀
    :param obj_cls: 新的第一列值
    """
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.startswith(filefront) and filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            # 读取文件内容
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # 修改第一列
            modified_lines = []
            for line in lines:
                columns = line.split()
                if columns:
                    columns[0] = str(obj_cls)
                    modified_lines.append(' '.join(columns) + '\n')

            # 写回文件
            with open(file_path, 'w') as file:
                file.writelines(modified_lines)
            print(f"已修改 {filename}为{obj_cls}")


# 指定文件夹路径、文件名前缀和新的类标签
obj_folder = r''
filefront = ''  # 请替换为实际的文件名前缀
obj_cls = 85  # 请替换为实际的类标签

# 调用函数
modify_files_with_prefix(obj_folder, filefront, obj_cls)

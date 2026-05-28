import os
import shutil

# 处理信贷资料库中的图片，将图片移动到对应的文件夹中

""" 处理前文件格式
    |--Folder1
        -Pic1
    |--Folder2
        -Pic2
    .....
    
    处理后文件格式
    |--Folder
        -Pic1
        -Pic2
        -Pic3
        -Pic_n....
"""

def move_files(source_path, obj_path):
    """
    遍历source_path目录下的所有文件夹，并将这些文件夹中的所有文件移动到obj_path目录。

    :param source_path: 源目录路径
    :param obj_path: 目标目录路径
    """
    # 确保目标目录存在
    if not os.path.exists(obj_path):
        os.makedirs(obj_path)

    # 遍历源目录
    for root, dirs, files in os.walk(source_path):
        for file in files:
            # 构建源文件路径
            source_file_path = os.path.join(root, file)
            # 构建目标文件路径
            dest_file_path = os.path.join(obj_path, file)

            # 移动文件
            shutil.move(source_file_path, dest_file_path)
            print(f"Moved: {source_file_path} to {dest_file_path}")

    # 删除空文件夹
    for root, dirs, files in os.walk(source_path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):  # 检查文件夹是否为空
                os.rmdir(dir_path)
                print(f"Deleted empty folder: {dir_path}")



if __name__ == "__main__":

    process_folder = r""
    for cls_folder in os.listdir(process_folder):
        source_path = f'{process_folder}/{cls_folder}'
        obj_path = f'{source_path}/images'
        move_files(source_path, obj_path)

    # source_path = r''
    # obj_path = f'{source_path}\images'
    # move_files(source_path, obj_path)
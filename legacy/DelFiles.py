import os
import glob

def delete_files_with_extensions(directory, extensions):
    """
    删除指定目录及其子目录下具有指定后缀名的文件。

    :param directory: 指定目录路径
    :param extensions: 后缀名列表，例如 ['.jpg', '.png']
    """
    # 确保目录存在
    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在。")
        return

    # 计数
    count = 0

    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            for ext in extensions:
                if file.endswith(ext):
                    try:
                        os.remove(file_path)
                        print(f"已删除: {file_path}")
                        count += 1
                    except OSError as e:
                        print(f"删除文件 {file_path} 时发生错误: {e}")

    print(f"总共删除了 {count} 个文件。")

if __name__ == "__main__":

    source_path = r''
    for cls_folder in os.listdir(source_path):
        directory = f'{source_path}/{cls_folder}/images'
        extensions = ['.pdf', '.doc', '.txt', '.html', '.xls', '.docx', '.rtf', '.wps', '.et', '.PDF', '.mp4']
        delete_files_with_extensions(directory, extensions)


    #
    # directory = r''  # 目录路径
    # extensions = ['.pdf', '.doc', '.txt', '.html', '.xls', '.docx', '.rtf', '.wps', '.et', '.PDF', '.mp4']  # 需要删除的后缀名列表
    # delete_files_with_extensions(directory, extensions)

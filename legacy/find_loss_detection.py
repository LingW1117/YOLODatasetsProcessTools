import os
import shutil

def copy_missing_files(source_path, det_path, loss_det_path):
    """
    对比source_path和det_path目录下的所有文件，将source_path目录下存在但det_path目录下不存在的文件复制到loss_det_path目录。

    :param source_path: 源目录路径
    :param det_path: 对比目录路径
    :param loss_det_path: 目标目录路径
    """
    # 确保目标目录存在
    if not os.path.exists(loss_det_path):
        os.makedirs(loss_det_path)

    # 计数
    count = 0

    # 获取source_path目录下的所有文件名（不包括后缀）
    source_files = set()
    for root, dirs, files in os.walk(source_path):
        for file in files:
            file_name = os.path.splitext(os.path.relpath(os.path.join(root, file), source_path))[0]
            source_files.add(file_name)

    # 获取det_path目录下的所有文件名（不包括后缀）
    det_files = set()
    for root, dirs, files in os.walk(det_path):
        for file in files:
            file_name = os.path.splitext(os.path.relpath(os.path.join(root, file), det_path))[0]
            det_files.add(file_name)

    # 找出source_path中存在但det_path中不存在的文件
    missing_files = source_files - det_files

    # 复制缺失的文件到loss_det_path
    for file_name in missing_files:
        # 重新构建文件路径，包括后缀
        for root, dirs, files in os.walk(source_path):
            for file in files:
                if os.path.splitext(file)[0] == file_name:
                    source_file_path = os.path.join(root, file)
                    dest_file_path = os.path.join(loss_det_path, os.path.relpath(source_file_path, source_path))
                    # 确保目标文件路径的目录存在
                    os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
                    # 复制文件
                    shutil.copy2(source_file_path, dest_file_path)
                    print(f"Copied: {source_file_path} to {dest_file_path}")
                    count = count + 1
                    break
    print(f"Total files copied: {count}")


if __name__ == "__main__":


    source_path = r''
    for cls_folder in os.listdir(source_path):
        cls_path = f'{source_path}/{cls_folder}'
        img_path = f'{cls_path}/images'
        det_path = f'{cls_path}/det'
        loss_det_path = f'{cls_path}/loss_det'
        copy_missing_files(img_path, det_path, loss_det_path)


    # source_path = r''
    # det_path = r''
    # loss_det_path = r''
    # copy_missing_files(source_path, det_path, loss_det_path)

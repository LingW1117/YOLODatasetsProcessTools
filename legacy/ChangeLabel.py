import os

def modify_labels(input_folder, output_folder, origin_label, modify_label):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的每个txt文件
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # 打开输入文件并读取内容
            with open(input_path, 'r') as input_file:
                lines = input_file.readlines()

            # 修改指定的标签
            modified_lines = [
                f"{modify_label}{line[len(str(origin_label)):]}" if line.startswith(str(origin_label)) else line
                for line in lines
            ]

            # 将修改后的内容写入输出文件
            with open(output_path, 'w') as output_file:
                output_file.writelines(modified_lines)
            print(f"已修改 {filename}标签{origin_label}为{modify_label}")

if __name__ == "__main__":
    input_folder = r""
    output_folder = input_folder
    origin_label = 0
    modify_label = 4

    modify_labels(input_folder, output_folder, origin_label, modify_label)

import os

def filter_labels(input_folder, output_folder, filter_class):
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

            # 过滤指定类别的标签
            filtered_lines = [line for line in lines if line.split()[0] != str(filter_class)]

            # 将过滤后的内容写入输出文件
            with open(output_path, 'w') as output_file:
                output_file.writelines(filtered_lines)
            print(f"已过滤 {filename}中标签{filter_class}")

if __name__ == "__main__":
    input_folder = r""
    output_folder = r""
    filter_class = 6
    filter_labels(input_folder, output_folder, filter_class)

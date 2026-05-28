import os
import xml.etree.ElementTree as ET

def xml_folder_to_yolo_txt_folder_auto_map(xml_folder, image_folder, txt_folder):
    """
    将VOC XML批量转换为YOLO txt，并根据XML中的标签自动生成 class_mapping（从0开始，新标签+1）。
    返回：class_mapping (dict: {class_name: class_id})
    """
    os.makedirs(txt_folder, exist_ok=True)

    class_mapping = {}   # 自动生成
    next_class_id = 0

    # 固定遍历顺序，保证映射稳定
    for filename in sorted(os.listdir(xml_folder)):
        if not filename.lower().endswith(".xml"):
            continue

        xml_path = os.path.join(xml_folder, filename)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 输出 txt 路径（用 xml 同名）
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(txt_folder, txt_filename)

        # 读取图像宽高（从XML里取）
        width_node = root.find(".//size/width")
        height_node = root.find(".//size/height")
        if width_node is None or height_node is None:
            # 没有尺寸信息，无法归一化，跳过该xml
            continue

        image_width = float(width_node.text)
        image_height = float(height_node.text)
        if image_width <= 0 or image_height <= 0:
            continue

        with open(txt_path, "w", encoding="utf-8") as txt_file:
            for obj in root.findall(".//object"):
                name_node = obj.find("name")
                bndbox = obj.find("bndbox")
                if name_node is None or bndbox is None:
                    continue

                name = name_node.text.strip()

                # 自动分配类别ID
                if name not in class_mapping:
                    class_mapping[name] = next_class_id
                    next_class_id += 1
                class_index = class_mapping[name]

                # 读取bbox
                try:
                    xmin = float(bndbox.find("xmin").text)
                    ymin = float(bndbox.find("ymin").text)
                    xmax = float(bndbox.find("xmax").text)
                    ymax = float(bndbox.find("ymax").text)
                except Exception:
                    continue

                # 可选：简单过滤非法框（避免负值/反向）
                if xmax <= xmin or ymax <= ymin:
                    continue

                # 转YOLO格式（归一化）
                x_center = ((xmin + xmax) / 2.0) / image_width
                y_center = ((ymin + ymax) / 2.0) / image_height
                w = (xmax - xmin) / image_width
                h = (ymax - ymin) / image_height

                txt_file.write(f"{class_index} {x_center} {y_center} {w} {h}\n")

    return class_mapping


# 用法示例
xml_folder_path = r""
image_folder_path = r""  # 这里目前不强依赖，可保留参数
txt_folder_path = r""

class_mapping = xml_folder_to_yolo_txt_folder_auto_map(
    xml_folder=xml_folder_path,
    image_folder=image_folder_path,
    txt_folder=txt_folder_path
)

print("最终class_mapping：", class_mapping)
# -*- coding: utf-8 -*-
import os
import cv2
import requests
import base64
import numpy as np
from pathlib import Path
import time

# 类别名称列表
names = [
    "Official_Seal",
    "Personal_Seal",
    "Sign_FingerPrint",
    "CrossPage_Seal"
]

def convert_to_yoloclass(name):
    """将类别名称转换为YOLO格式的类别ID"""
    name_to_class_id = {name: idx for idx, name in enumerate(names)}
    return name_to_class_id.get(name, -1)

def convert_to_yolo(x_min, y_min, box_width, box_height, img_width, img_height, class_id):
    """将常规坐标转换为YOLOv8格式"""
    x_center = (x_min + box_width / 2) / img_width
    y_center = (y_min + box_height / 2) / img_height
    norm_width = box_width / img_width
    norm_height = box_height / img_height
    return f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}"

def process_images(input_folder, det_result_savepath, label_savepath, visualize=False, save_det_result=False, save_labels=False):

    if save_det_result:
        os.makedirs(det_result_savepath, exist_ok=True)
    if save_labels:
        os.makedirs(label_savepath, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif')):
            result_filename = Path(filename).stem
            image_path = os.path.join(input_folder, filename)

            # 读取图片
            with open(image_path, 'rb') as f:
                image_data = f.read()
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_UNCHANGED)

            if image is None:
                print(f"[ERROR] Failed to read image: {image_path}")
                continue

            # 如果是4通道转为3通道
            if image.ndim == 3 and image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

            # 将图片编码为Base64
            _, image_encoded = cv2.imencode('.png', image)
            image_base64 = base64.b64encode(image_encoded.tobytes()).decode('utf-8')

            # 调用检测接口
            url = 'http://localhost:1133/detect'
            data = {'image': image_base64}
            response = requests.post(url, json=data)

            if response.status_code != 200:
                print(f"[ERROR] Request failed for {filename}: {response.status_code} {response.text}")
                continue

            detections = response.json()
            if not detections:
                print(f"[INFO] No detections for {filename}")
                continue

            yolo_lines = []
            for detection in detections:
                label = detection['label']
                x1, y1, x2, y2 = detection['coordinates']
                conf = detection['confidence']
                cls = convert_to_yoloclass(label)
                label_conf = f"{label}: {conf:.2f}"
                if cls == -1:
                    print(f"[WARN] Unknown class: {label}")
                    continue

                # 绘制检测框
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, label_conf, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # 转YOLO格式
                width = x2 - x1
                height = y2 - y1
                img_width, img_height = image.shape[1], image.shape[0]
                yolo_format = convert_to_yolo(x1, y1, width, height, img_width, img_height, cls)
                yolo_lines.append(yolo_format)

            # 保存标签文件
            if save_labels:
                label_filename = os.path.join(label_savepath, f"{result_filename}.txt")
                with open(label_filename, 'w', encoding="utf-8") as f:
                    for line in yolo_lines:
                        f.write(line + '\n')

            # 可视化
            if visualize:
                cv2.namedWindow("test", 0)
                cv2.imshow("test", image)
                cv2.waitKey()

            # 保存结果图
            if save_det_result:
                result_filename = Path(filename).stem  # 去掉扩展名，避免奇怪字符
                output_path = os.path.join(det_result_savepath, f"{result_filename}.jpg")

                # 确保是 uint8 格式
                image = np.ascontiguousarray(image, dtype=np.uint8)

                try:
                    # 用 imencode 支持中文路径
                    ext = os.path.splitext(output_path)[1]
                    success, buf = cv2.imencode(ext, image)
                    if success:
                        buf.tofile(output_path)
                        print(f"[OK] Processed and saved: {output_path}")
                    else:
                        print(f"[ERROR] cv2.imencode failed: {output_path}")
                except Exception as e:
                    print(f"[ERROR] Exception saving {output_path}: {e}")
        cur_time_use = time.time() - time_start
        print(f"Current time use:{cur_time_use}s")

    print("[DONE] Processing complete.")

# 示例调用
if __name__ == "__main__":

    time_start = time.time()

    # 处理文件夹
    # process_folder = r""
    # for cls_folder in os.listdir(process_folder):
    #     input_folder = f"{process_folder}/{cls_folder}/images/"
    #     det_result_savepath = f"{process_folder}/{cls_folder}/det/"
    #     label_savepath = f"{process_folder}/{cls_folder}/labels/"
    #     visualize = False
    #     save_det_result = True
    #     savelabels = True
    #     print(f"Processing folder: {input_folder}")
    #
    #     process_images(input_folder, det_result_savepath, label_savepath, visualize, save_det_result, savelabels)



    # 处理单个目录
    process_folder = r""
    input_folder = f"{process_folder}/images/"
    det_result_savepath = f"{process_folder}/det/"
    label_savepath = f"{process_folder}/labels/"
    visualize = False
    save_det_result = True
    savelabels = True
    print(f"Processing folder: {input_folder}")

    process_images(input_folder, det_result_savepath, label_savepath, visualize, save_det_result, savelabels)

    time_end = time.time()
    time_use = time_end - time_start
    print(f"[INFO] Processing time: {time_use}")
import os
import base64
from typing import Dict, Any
import requests
from pathlib import Path
import shutil



# ============ Qwen3.5-9B ============ #
def VLM_Qwen35(url_path, text):
    url = "http://localhost:8000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    with open(url_path, "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        new_base64 = preprocess_image(image_base64)
        payload = {
            "model": "Qwen3.5-9B",  # 或 "qwen-vl-max" 根据需求选择模型版本
            "temperature": 0,
            "max_tokens": 400,
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [
                {"role": "system", "content": "你是一个图片识别专家。没有识别到的内容，不要乱答。"},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpg;base64,{new_base64}"}
                        },
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ]
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return ""



def preprocess_image(image_base64):
    """简单的 base64 处理，如果需要压缩/调整可以在这加"""
    # 如果图片太大，可以在这里做压缩处理
    # 目前直接返回原图
    return image_base64


def filter_images_by_keyword(input_folder, output_folder, prompt, keywords):
    """
    遍历 input_folder 中的图片，用 VLM 识别标题，匹配关键词则移动
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.tif'}

    image_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if Path(file).suffix.lower() in image_exts:
                image_files.append(os.path.join(root, file))

    total = len(image_files)
    matched_count = 0
    error_count = 0

    print(f"共找到 {total} 张图片，开始处理...\n")

    for idx, img_path in enumerate(image_files):
        print(f"[{idx + 1}/{total}] 处理：{os.path.basename(img_path)}")

        try:
            # 调用 VLM 识别标题
            result = VLM_Qwen35(img_path, prompt)

            # 处理返回值：如果是字典，提取 content 字段
            if isinstance(result, dict):
                try:
                    result = result["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError):
                    result = ""

            if not result:
                print(f"  └─ 识别结果为空，跳过")
                error_count += 1
                continue

            # 确保 result 是字符串
            result = str(result)
            print(f"  └─ 识别结果：{result[:100]}{'...' if len(result) > 100 else ''}")

            # 检查是否包含关键词
            matched = False
            matched_keyword = None
            for kw in keywords:
                if kw in result:
                    matched = True
                    matched_keyword = kw
                    break

            if matched:
                filename = os.path.basename(img_path)
                dst_path = os.path.join(output_folder, filename)

                if os.path.exists(dst_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dst_path):
                        dst_path = os.path.join(output_folder, f"{base}_{counter}{ext}")
                        counter += 1

                shutil.move(img_path, dst_path)
                matched_count += 1
                print(f"  └─ ✓ 匹配关键词 '{matched_keyword}'，已移动")
            else:
                print(f"  └─ 无匹配关键词，跳过")

        except Exception as e:
            error_count += 1
            print(f"  └─ 错误：{str(e)}")

    print(f"\n============ 处理完成 ============")
    print(f"总计：{total} 张")
    print(f"匹配并移动：{matched_count} 张")
    print(f"识别失败/错误：{error_count} 张")
    print(f"输出目录：{output_folder}")


if __name__ == "__main__":
    # ============ 配置区域 ============ #
    input_folder = r""  # 输入目录
    output_folder = r""  # 输出目录
    prompt = "图中有几个身份证号？ 回答 一个/两个/三个/四个"
    keywords = ["一个"]  # 关键词列表

    # ============ 开始处理 ============ #
    filter_images_by_keyword(input_folder, output_folder, prompt, keywords)

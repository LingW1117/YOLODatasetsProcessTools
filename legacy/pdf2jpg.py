import os
import fitz  # PyMuPDF
from PIL import Image


def convert_pdf_to_jpg(pdf_folder_path, pic_folder_path):
    # 确保目标文件夹存在
    if not os.path.exists(pic_folder_path):
        os.makedirs(pic_folder_path)

    # 遍历PDF文件夹
    for root, dirs, files in os.walk(pdf_folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                # 构建完整的PDF文件路径
                pdf_path = os.path.join(root, file)
                # 构建目标图片文件路径
                base_name = os.path.splitext(file)[0]
                pic_path = os.path.join(pic_folder_path, f"{base_name}.jpg")

                try:
                    # 打开PDF文件
                    doc = fitz.open(pdf_path)
                    # 获取第一页
                    page = doc.load_page(0)
                    # 将页面转换为图片
                    pix = page.get_pixmap()
                    # 保存图片
                    pix.save(pic_path)
                    print(f"转换并保存图片: {pic_path}")
                except Exception as e:
                    print(f"无法转换PDF文件: {pdf_path}, 错误: {e}")


# 指定PDF文件夹路径和图片文件夹路径
pdf_folder_path = r''
pic_folder_path = r''
convert_pdf_to_jpg(pdf_folder_path, pic_folder_path)

from PIL import Image
import os


def convert_images_to_pdf(folder_path, output_pdf):
    images = [img for img in os.listdir(folder_path) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
    images.sort()  # 按文件名排序

    if not images:
        print("未找到图片文件！")
        return

    # 转换第一张图片创建PDF
    first_image = Image.open(os.path.join(folder_path, images[0])).convert('RGB')
    other_images = [Image.open(os.path.join(folder_path, img)).convert('RGB') for img in images[1:]]

    first_image.save(output_pdf, save_all=True, append_images=other_images)
    print(f"PDF 已生成：{output_pdf}")


# 使用示例
convert_images_to_pdf('ZFWTS/images', 'YTYBG/ZFWTS.pdf')

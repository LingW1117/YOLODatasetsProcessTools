import os
import cv2
from PIL import Image

def check_and_fix_images(input_dir, output_dir=None, exts={".jpg", ".jpeg"}):
    """
    检测并修复异常 JPEG 文件
    :param input_dir: 原始图片目录
    :param output_dir: 修复后保存目录（为 None 时原地覆盖）
    :param exts: 需要检查的扩展名
    """
    if output_dir is None:
        output_dir = input_dir
    os.makedirs(output_dir, exist_ok=True)

    bad_images = []
    fixed_count = 0
    all_images = []

    for root, _, files in os.walk(input_dir):
        for fname in files:
            ext = os.path.splitext(fname)[-1].lower()
            if ext in exts:
                fpath = os.path.join(root, fname)
                all_images.append(fpath)

                rel_path = os.path.relpath(fpath, input_dir)
                out_path = os.path.join(output_dir, rel_path)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                is_bad = False

                # 1️⃣ 用 OpenCV 检测
                try:
                    img = cv2.imread(fpath)
                    if img is None:
                        is_bad = True
                except Exception:
                    is_bad = True

                # 2️⃣ 用 PIL 检测
                if not is_bad:
                    try:
                        with Image.open(fpath) as im:
                            im.verify()
                    except Exception:
                        is_bad = True

                if is_bad:
                    try:
                        # 尝试用 PIL 打开再保存修复
                        with Image.open(fpath) as im:
                            im = im.convert("RGB")  # 转换为标准 RGB
                            im.save(out_path, "JPEG", quality=95)
                        fixed_count += 1
                        print(f"[修复成功] {fpath} → {out_path}")
                    except Exception as e:
                        bad_images.append((fpath, str(e)))
                        print(f"[修复失败] {fpath}: {e}")
                else:
                    # 正常文件直接复制（或原地覆盖）
                    if input_dir != output_dir:
                        with Image.open(fpath) as im:
                            im.save(out_path, "JPEG", quality=95)

    print("\n=== 检测完成 ===")
    print(f"总共检测 {len(all_images)} 张图片")
    print(f"修复 {fixed_count} 张异常 JPEG")
    print(f"仍有 {len(bad_images)} 张无法修复")

    if bad_images:
        print("\n无法修复的文件：")
        for fpath, err in bad_images:
            print(f"{fpath} —— {err}")

    return bad_images


if __name__ == "__main__":
    dataset_path = r""       # 👉 这里换成你的数据集目录
    fixed_path = r""   # 👉 修复后保存的目录（设为 None 表示原地覆盖）
    check_and_fix_images(dataset_path, fixed_path)
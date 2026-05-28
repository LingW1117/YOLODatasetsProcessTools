from pathlib import Path
from PIL import Image

def find_single_channel_images(images_floder: str,
                               img_exts=(".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")):
    """
    寻找 images_floder 下的单通道图片（灰度/单通道），返回路径列表。
    判定规则：PIL 打开后 mode in {"L", "1", "I;16", "I"} 视为单通道。
    """
    images_dir = Path(images_floder)
    if not images_dir.exists():
        raise FileNotFoundError(f"images_floder not found: {images_dir}")
    if not images_dir.is_dir():
        raise NotADirectoryError(f"images_floder is not a folder: {images_dir}")

    img_exts = tuple(e.lower() for e in img_exts)

    single_channel = []
    for p in images_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in img_exts:
            continue

        try:
            with Image.open(p) as im:
                # 单通道常见 mode：L(8-bit灰度), 1(1-bit), I/I;16(整型灰度)
                if im.mode in ("L", "1", "I", "I;16"):
                    single_channel.append(str(p))
        except Exception:
            # 读不了的图片直接跳过
            continue

    return single_channel


# 示例：
gray_imgs = find_single_channel_images(r"")
print(len(gray_imgs))
print("\n".join(gray_imgs[:20]))
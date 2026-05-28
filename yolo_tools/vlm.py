from __future__ import annotations

import base64
import os
import shutil
from pathlib import Path

from openai import OpenAI


def vlm_classify_image(
    image_path: str,
    prompt: str,
    api_url: str,
    model: str,
    api_key: str,
) -> str | None:
    """Send an image to a VLM API and return the model's text response.

    Args:
        image_path: Path to the image file.
        prompt: Text prompt for the VLM.
        api_url: OpenAI-compatible API base URL.
        model: Model name to use.
        api_key: API key for authentication.

    Returns:
        The model's text response, or None on failure.
    """
    client = OpenAI(base_url=api_url, api_key=api_key)

    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            max_tokens=400,
            messages=[
                {
                    "role": "system",
                    "content": "你是图片识别助手，根据要求完成图片识别任务",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpg;base64,{image_base64}"
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                },
            ],
        )
        return response.choices[0].message.content
    except Exception:
        return None


def filter_images_by_keyword(
    input_folder: str,
    output_folder: str,
    prompt: str,
    keywords: list[str],
    api_url: str,
    model: str,
    api_key: str,
) -> dict:
    """Filter images by VLM response: move images whose response matches any keyword.

    Args:
        input_folder: Directory of images to scan.
        output_folder: Where to move matching images.
        prompt: Text prompt for the VLM.
        keywords: List of keywords to match in the VLM response.
        api_url: OpenAI-compatible API base URL.
        model: Model name to use.
        api_key: API key for authentication.

    Returns:
        Summary dict with keys: total, matched, errors, output_folder.
    """
    os.makedirs(output_folder, exist_ok=True)

    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp", ".tif"}

    image_files: list[str] = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if Path(file).suffix.lower() in image_exts:
                image_files.append(os.path.join(root, file))

    total = len(image_files)
    matched_count = 0
    error_count = 0

    print(f"Found {total} images, starting...\n")

    for idx, img_path in enumerate(image_files):
        print(f"[{idx + 1}/{total}] Processing: {os.path.basename(img_path)}")

        try:
            result = vlm_classify_image(img_path, prompt, api_url, model, api_key)

            if not result:
                print("  └─ Empty result, skipped.")
                error_count += 1
                continue

            result = str(result)
            print(
                f"  └─ Result: {result[:100]}"
                f"{'...' if len(result) > 100 else ''}"
            )

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
                        dst_path = os.path.join(
                            output_folder, f"{base}_{counter}{ext}"
                        )
                        counter += 1

                shutil.move(img_path, dst_path)
                matched_count += 1
                print(f"  └─ Matched keyword '{matched_keyword}', moved.")
            else:
                print("  └─ No keyword match, skipped.")

        except Exception as e:
            error_count += 1
            print(f"  └─ Error: {e}")

    print(f"\n============ Done ============")
    print(f"Total: {total}")
    print(f"Matched & moved: {matched_count}")
    print(f"Errors: {error_count}")
    print(f"Output: {output_folder}")

    return {
        "total": total,
        "matched": matched_count,
        "errors": error_count,
        "output_folder": output_folder,
    }

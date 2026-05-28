from __future__ import annotations

import base64
import os
import time
from pathlib import Path

import cv2
import numpy as np
import requests

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def _is_image(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMG_EXTS


def _iter_images(input_root: Path):
    for p in input_root.rglob("*"):
        if _is_image(p):
            yield p


def classify_and_save(
    input_path: str,
    cls: str,
    output_path: str,
    operation: str,
    api_url: str | None = None,
    timeout_s: float = 60.0,
    retries: int = 2,
    retry_sleep_s: float = 0.5,
    keep_rel_structure: bool = True,
    verbose: bool = True,
) -> dict:
    """Recursively scan images, call a detection API, and save hits.

    If the API returns any label containing `cls`, the image is saved
    (copied or moved) to output_path.

    Args:
        input_path: Directory of images to scan.
        cls: Class name substring to match in detection results.
        output_path: Where to save matching images.
        operation: 'copy' or 'move'.
        api_url: Detection API endpoint URL.
        timeout_s: Request timeout in seconds.
        retries: Number of retry attempts on failure.
        retry_sleep_s: Seconds to sleep between retries.
        keep_rel_structure: If True, preserve relative directory structure.
        verbose: If True, print progress.

    Returns:
        Summary dict with keys: processed, hit, fail, elapsed_s.
    """
    input_root = Path(input_path).resolve()
    output_root = Path(output_path).resolve()

    if not input_root.exists() or not input_root.is_dir():
        raise NotADirectoryError(f"input_path not a directory: {input_root}")

    output_root.mkdir(parents=True, exist_ok=True)

    processed = matched = failed = 0
    t0 = time.time()

    with requests.Session() as session:
        for img_path in _iter_images(input_root):
            processed += 1
            if verbose:
                print(f"[PROCESSING] {processed} | {img_path}")

            img_b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")
            payload = {"image": img_b64}

            ok = False
            labels: list[str] = []
            raw = None

            for attempt in range(retries + 1):
                try:
                    resp = session.post(
                        api_url, json=payload, timeout=timeout_s,
                    )
                    try:
                        data = resp.json()
                    except Exception:
                        data = resp.text

                    if resp.status_code != 200:
                        raw = f"HTTP {resp.status_code}: {data}"
                    else:
                        if isinstance(data, list):
                            for det in data:
                                if isinstance(det, dict) and "label" in det:
                                    labels.append(str(det["label"]))
                            ok = True
                            break
                        raw = f"Unexpected response: {data}"
                except Exception as e:
                    raw = str(e)

                if attempt < retries:
                    time.sleep(retry_sleep_s)

            if not ok:
                failed += 1
                if verbose:
                    print(f"[FAIL] {img_path} | {raw}")
                continue

            hit = any(str(cls) in lb for lb in labels)

            if hit:
                matched += 1
                if keep_rel_structure:
                    rel = img_path.relative_to(input_root)
                    dst = output_root / rel
                else:
                    dst = output_root / img_path.name

                from yolo_tools.utils import safe_copy_or_move
                final_dst = safe_copy_or_move(img_path, dst, operation)
                if verbose:
                    print(f"[HIT]  {img_path} -> {final_dst} | labels={labels}")
            else:
                if verbose:
                    print(f"[MISS] {img_path} | labels={labels}")

            elapsed = time.time() - t0
            if verbose and processed % 100 == 0:
                print(
                    f"[PROGRESS] processed={processed}, hit={matched}, "
                    f"fail={failed}, elapsed={elapsed:.1f}s"
                )

    elapsed = time.time() - t0
    if verbose:
        print(
            f"\n[DONE] processed={processed}, hit={matched}, "
            f"fail={failed}, elapsed={elapsed:.1f}s"
        )

    return {
        "processed": processed,
        "hit": matched,
        "fail": failed,
        "elapsed_s": elapsed,
    }


def process_images_with_detection(
    input_folder: str,
    det_result_savepath: str,
    label_savepath: str,
    visualize: bool = False,
    save_det_result: bool = True,
    save_labels: bool = True,
    api_url: str = "http://localhost:1133/detect",
    class_names: list[str] | None = None,
) -> None:
    """Run a detection API on images and save visualized results and YOLO labels.

    Args:
        input_folder: Directory containing images to process.
        det_result_savepath: Where to save visualized detection images.
        label_savepath: Where to save YOLO-format label files.
        visualize: If True, display results interactively with OpenCV.
        save_det_result: If True, save annotated images.
        save_labels: If True, save YOLO label files.
        api_url: Detection API endpoint URL.
        class_names: Optional list of class name strings for label mapping.
    """
    from yolo_tools.labels import convert_to_yoloclass
    from yolo_tools.utils import convert_to_yolo_format

    if save_det_result:
        os.makedirs(det_result_savepath, exist_ok=True)
    if save_labels:
        os.makedirs(label_savepath, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".tif")):
            continue

        result_filename = Path(filename).stem
        image_path = os.path.join(input_folder, filename)

        with open(image_path, "rb") as f:
            image_data = f.read()
        image = cv2.imdecode(
            np.frombuffer(image_data, np.uint8), cv2.IMREAD_UNCHANGED
        )

        if image is None:
            print(f"[ERROR] Failed to read image: {image_path}")
            continue

        if image.ndim == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        _, image_encoded = cv2.imencode(".png", image)
        image_base64 = base64.b64encode(
            image_encoded.tobytes()
        ).decode("utf-8")

        url = api_url
        data = {"image": image_base64}
        response = requests.post(url, json=data)

        if response.status_code != 200:
            print(
                f"[ERROR] Request failed for {filename}: "
                f"{response.status_code} {response.text}"
            )
            continue

        detections = response.json()
        if not detections:
            print(f"[INFO] No detections for {filename}")
            continue

        yolo_lines: list[str] = []
        for detection in detections:
            label = detection["label"]
            x1, y1, x2, y2 = detection["coordinates"]
            conf = detection["confidence"]
            cls = convert_to_yoloclass(label, class_names)
            label_conf = f"{label}: {conf:.2f}"
            if cls == -1:
                print(f"[WARN] Unknown class: {label}")
                continue

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image, label_conf, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2,
            )

            width = x2 - x1
            height = y2 - y1
            img_width, img_height = image.shape[1], image.shape[0]
            yolo_lines.append(
                convert_to_yolo_format(
                    x1, y1, width, height, img_width, img_height, cls,
                )
            )

        if save_labels:
            label_filename = os.path.join(
                label_savepath, f"{result_filename}.txt"
            )
            with open(label_filename, "w", encoding="utf-8") as f:
                for line in yolo_lines:
                    f.write(line + "\n")

        if visualize:
            cv2.namedWindow("test", 0)
            cv2.imshow("test", image)
            cv2.waitKey()

        if save_det_result:
            output_path = os.path.join(
                det_result_savepath, f"{result_filename}.jpg"
            )
            image = np.ascontiguousarray(image, dtype=np.uint8)
            try:
                ext = os.path.splitext(output_path)[1]
                success, buf = cv2.imencode(ext, image)
                if success:
                    buf.tofile(output_path)
                    print(f"[OK] Saved: {output_path}")
                else:
                    print(f"[ERROR] cv2.imencode failed: {output_path}")
            except Exception as e:
                print(f"[ERROR] Exception saving {output_path}: {e}")

    print("[DONE] Processing complete.")

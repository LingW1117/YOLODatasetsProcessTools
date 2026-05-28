# -*- coding: utf-8 -*-
import time
import base64
import shutil
from pathlib import Path

import requests

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def _is_image(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMG_EXTS


def _iter_images(input_root: Path):
    # 递归遍历，天然是顺序的
    for p in input_root.rglob("*"):
        if _is_image(p):
            yield p


def _safe_copy_or_move(src: Path, dst: Path, method: str) -> Path:
    """
    Move/Copy src -> dst.
    If dst exists, auto-append suffix: _1, _2, ...
    """
    dst.parent.mkdir(parents=True, exist_ok=True)

    final_dst = dst
    if final_dst.exists():
        stem, suf = dst.stem, dst.suffix
        i = 1
        while True:
            candidate = dst.with_name(f"{stem}_{i}{suf}")
            if not candidate.exists():
                final_dst = candidate
                break
            i += 1

    if method == "copy":
        shutil.copy2(src, final_dst)
    elif method == "move":
        shutil.move(str(src), str(final_dst))
    else:
        raise ValueError("OprMethod must be 'move' or 'copy'")

    return final_dst


def _call_detect_api(session: requests.Session, url: str, img_path: Path,
                     timeout_s: float = 60.0, retries: int = 2, retry_sleep_s: float = 0.5):
    """
    Returns: (ok: bool, labels: list[str], err_or_raw)
    """
    img_b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")
    payload = {"image": img_b64}

    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = session.post(url, json=payload, timeout=timeout_s)

            try:
                data = resp.json()
            except Exception:
                data = resp.text

            if resp.status_code != 200:
                last_err = f"HTTP {resp.status_code}: {data}"
            else:
                # 正常返回 list[ {label, coordinates, confidence}, ... ]
                if isinstance(data, list):
                    labels = []
                    for det in data:
                        if isinstance(det, dict) and "label" in det:
                            labels.append(str(det["label"]))
                    return True, labels, data
                last_err = f"Unexpected response: {data}"

        except Exception as e:
            last_err = str(e)

        if attempt < retries:
            time.sleep(retry_sleep_s)

    return False, [], last_err


def classify_and_save(input_path: str,
                      cls: str,
                      output_path: str,
                      OprMethod: str,
                      api_url: str = None,
                      timeout_s: float = 60.0,
                      retries: int = 2,
                      retry_sleep_s: float = 0.5,
                      keep_rel_structure: bool = True,
                      verbose: bool = True):
    """
    递归扫描 input_path 下所有图片，逐张调用检测接口。
    若返回任意 label “包含” cls，则按 OprMethod(move/copy) 保存到 output_path。

    keep_rel_structure=True: 保留相对目录结构（推荐，避免同名覆盖）
    keep_rel_structure=False: 平铺输出到 output_path 根目录
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
            time_used = elapsed = time.time() - t0
            print(f"[PROCESSING] {processed} time {time_used}")

            ok, labels, raw = _call_detect_api(
                session, api_url, img_path,
                timeout_s=timeout_s, retries=retries, retry_sleep_s=retry_sleep_s
            )

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

                final_dst = _safe_copy_or_move(img_path, dst, OprMethod)
                if verbose:
                    print(f"[HIT]  {img_path} -> {final_dst} | labels={labels}")
            else:
                if verbose:
                    print(f"[MISS] {img_path} | labels={labels}")

            if verbose and processed % 100 == 0:
                elapsed = time.time() - t0
                print(f"[PROGRESS] processed={processed}, hit={matched}, fail={failed}, elapsed={elapsed:.1f}s")

    elapsed = time.time() - t0
    if verbose:
        print(f"\n[DONE] processed={processed}, hit={matched}, fail={failed}, elapsed={elapsed:.1f}s")

    return {"processed": processed, "hit": matched, "fail": failed, "elapsed_s": elapsed}


# ===== 示例调用（你自己改路径即可）=====
if __name__ == "__main__":
    classify_and_save(
        input_path=r"",
        cls="ClassName",
        output_path=r"",
        OprMethod="copy",
        api_url="http://170.xxx.xxx.xxx:xxxx/detect",
        keep_rel_structure=False,
        verbose=True
    )
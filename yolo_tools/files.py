from __future__ import annotations

import os
import shutil


def delete_files_with_extensions(
    directory: str,
    extensions: list[str],
) -> int:
    """Recursively delete all files with specified extensions from a directory.

    Returns the number of deleted files.
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return 0

    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            for ext in extensions:
                if file.endswith(ext):
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                        count += 1
                    except OSError as e:
                        print(f"Error deleting {file_path}: {e}")

    print(f"Total deleted: {count} files.")
    return count


def move_files(source_path: str, obj_path: str) -> None:
    """Flatten nested subdirectories: move all files into a single target directory.

    Empty source subdirectories are removed after moving.
    """
    os.makedirs(obj_path, exist_ok=True)

    for root, _, files in os.walk(source_path):
        for file in files:
            source_file_path = os.path.join(root, file)
            dest_file_path = os.path.join(obj_path, file)
            shutil.move(source_file_path, dest_file_path)
            print(f"Moved: {source_file_path} -> {dest_file_path}")

    for root, dirs, _ in os.walk(source_path, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"Deleted empty folder: {dir_path}")


def copy_missing_files(
    source_path: str,
    det_path: str,
    loss_det_path: str,
) -> int:
    """Copy files from source_path that are missing in det_path to loss_det_path.

    Comparison is done by filename stem (without extension).
    Returns the number of copied files.
    """
    os.makedirs(loss_det_path, exist_ok=True)

    def _get_stems(path: str) -> set[str]:
        stems: set[str] = set()
        for root, _, files in os.walk(path):
            for file in files:
                stem = os.path.splitext(
                    os.path.relpath(os.path.join(root, file), path)
                )[0]
                stems.add(stem)
        return stems

    source_stems = _get_stems(source_path)
    det_stems = _get_stems(det_path)
    missing = source_stems - det_stems

    count = 0
    for stem in missing:
        for root, _, files in os.walk(source_path):
            for file in files:
                if os.path.splitext(file)[0] == stem:
                    src = os.path.join(root, file)
                    dst = os.path.join(
                        loss_det_path, os.path.relpath(src, source_path)
                    )
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    print(f"Copied: {src} -> {dst}")
                    count += 1
                    break

    print(f"Total files copied: {count}")
    return count

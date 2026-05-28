from __future__ import annotations

import click

from yolo_tools import (
    augment_dataset,
    augment_dataset_auto,
    check_and_fix_images,
    check_images,
    classify_and_save,
    convert_images_to_pdf,
    convert_pdf_to_jpg,
    convert_single_to_three_channel,
    convert_to_yoloclass,
    copy_missing_files,
    copy_single_channel_images,
    delete_empty_label_files,
    delete_files_with_extensions,
    delete_images_without_labels,
    draw_labels,
    ensure_empty_labels,
    filter_images_by_keyword,
    filter_labels,
    filter_yolo_dataset,
    find_files_with_label,
    find_single_channel_images,
    modify_labels,
    modify_labels_by_filename_prefix,
    move_empty_labels,
    move_files,
    move_images_without_labels,
    move_orphan_labels,
    move_samples_by_label_id,
    move_samples_more_than_n,
    process_images_with_detection,
    rename_images_in_folder,
    rename_pic_label,
    split_dataset,
    vlm_classify_image,
    xml_folder_to_yolo_txt_folder_auto_map,
)


@click.group()
@click.version_option(version="1.0.0")
def main():
    """YOLO Tools - Dataset processing utilities for YOLO-format datasets."""


# ============================================================
# labels
# ============================================================
@main.group()
def labels():
    """Label file processing commands."""


@labels.command("modify")
@click.option("--input-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", required=True, type=click.Path())
@click.option("--origin", "-f", required=True, type=int, help="Original class ID")
@click.option("--target", "-t", required=True, type=int, help="New class ID")
def labels_modify(input_dir, output_dir, origin, target):
    """Replace all instances of a class ID with a new one."""
    modify_labels(input_dir, output_dir, origin, target)


@labels.command("modify-by-prefix")
@click.option("--dir", "-d", required=True, type=click.Path(exists=True))
@click.option("--prefix", "-p", required=True, help="Filename prefix to match")
@click.option("--target", "-t", required=True, type=int, help="New class ID")
def labels_modify_by_prefix(dir, prefix, target):
    """Replace class ID in label files whose names start with a prefix."""
    modify_labels_by_filename_prefix(dir, prefix, target)


@labels.command("filter")
@click.option("--input-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", required=True, type=click.Path())
@click.option("--class-id", "-c", required=True, type=int, help="Class ID to remove")
def labels_filter(input_dir, output_dir, class_id):
    """Remove all lines of a given class ID from label files."""
    filter_labels(input_dir, output_dir, class_id)


@labels.command("delete-empty")
@click.option("--dir", "-d", required=True, type=click.Path(exists=True))
def labels_delete_empty(dir):
    """Delete label files that contain no valid bounding boxes."""
    checked, deleted = delete_empty_label_files(dir)
    click.echo(f"Checked: {checked}, Deleted: {deleted}")


@labels.command("move-empty")
@click.option("--label-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", required=True, type=click.Path())
def labels_move_empty(label_dir, output_dir):
    """Move empty label files to a separate directory."""
    move_empty_labels(label_dir, output_dir)


@labels.command("ensure")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path())
def labels_ensure(images_dir, labels_dir):
    """Create empty label files for images that lack them."""
    created, skipped = ensure_empty_labels(images_dir, labels_dir)
    click.echo(f"Created: {created}, Skipped (already exist): {skipped}")


@labels.command("find")
@click.option("--dir", "-d", required=True, type=click.Path(exists=True))
@click.option("--class-id", "-c", required=True, type=int)
def labels_find(dir, class_id):
    """List label files that contain a specific class ID."""
    result = find_files_with_label(dir, class_id)
    for f in result:
        click.echo(f)


@labels.command("draw")
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--save-dir", "-s", required=True, type=click.Path())
@click.option("--names", "-n", default=None, help="Comma-separated class names, e.g. 'cat,dog,bird'")
def labels_draw(labels_dir, images_dir, save_dir, names):
    """Draw YOLO labels on images and save annotated results."""
    class_names = [n.strip() for n in names.split(",")] if names else None
    count = draw_labels(labels_dir, images_dir, save_dir, class_names)
    click.echo(f"Processed: {count} images")


# ============================================================
# dataset
# ============================================================
@main.group()
def dataset():
    """Dataset organization commands."""


@dataset.command("split")
@click.option("--src", required=True, type=click.Path(exists=True))
@click.option("--dst", required=True, type=click.Path())
@click.option("--train", default=0.7, type=float, help="Train ratio")
@click.option("--val", default=0.2, type=float, help="Validation ratio")
@click.option("--test", default=0.1, type=float, help="Test ratio")
@click.option("--move/--copy", default=False, help="Move files instead of copying")
@click.option("--seed", type=int, default=None, help="Random seed for reproducibility")
def dataset_split(src, dst, train, val, test, move, seed):
    """Split a YOLO dataset into train/val/test splits."""
    split_dataset(src, dst, train, val, test, move=move, seed=seed)


@dataset.command("delete-no-label")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
def dataset_delete_no_label(images_dir, labels_dir):
    """Delete images that have no corresponding label file."""
    checked, deleted = delete_images_without_labels(images_dir, labels_dir)
    click.echo(f"Checked: {checked}, Deleted: {deleted}")


@dataset.command("filter-by-class")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--class-id", "-c", required=True, type=int)
@click.option("--output-images", "-oi", required=True, type=click.Path())
@click.option("--output-labels", "-ol", required=True, type=click.Path())
@click.option("--mode", type=click.Choice(["copy", "move"]), default="copy")
def dataset_filter_by_class(images_dir, labels_dir, class_id, output_images, output_labels, mode):
    """Filter dataset: keep only samples containing a specific class."""
    count = filter_yolo_dataset(images_dir, labels_dir, class_id, output_images, output_labels, mode)
    click.echo(f"Processed: {count}")


@dataset.command("filter-by-count")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--max-boxes", "-m", required=True, type=int, help="Move samples with MORE boxes than this")
@click.option("--output-images", "-oi", required=True, type=click.Path())
@click.option("--output-labels", "-ol", required=True, type=click.Path())
def dataset_filter_by_count(images_dir, labels_dir, max_boxes, output_images, output_labels):
    """Move samples where the label has more than N bounding boxes."""
    result = move_samples_more_than_n(images_dir, labels_dir, max_boxes, output_images, output_labels)
    click.echo(f"Moved: {result['moved_pairs']}")


@dataset.command("orphan-labels")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", required=True, type=click.Path())
def dataset_orphan_labels(images_dir, labels_dir, output_dir):
    """Move label files that have no matching image."""
    moved = move_orphan_labels(images_dir, labels_dir, output_dir)
    click.echo(f"Moved: {moved}")


@dataset.command("orphan-images")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", required=True, type=click.Path())
def dataset_orphan_images(images_dir, labels_dir, output_dir):
    """Move images that have no matching label."""
    moved = move_images_without_labels(images_dir, labels_dir, output_dir)
    click.echo(f"Moved: {moved}")


@dataset.command("filter-by-label-id")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--label-id", required=True, type=int, help="Class ID to filter by")
@click.option("--output-images", "-oi", required=True, type=click.Path())
@click.option("--output-labels", "-ol", required=True, type=click.Path())
def dataset_filter_by_label_id(images_dir, labels_dir, label_id, output_images, output_labels):
    """Move samples containing a specific class ID."""
    result = move_samples_by_label_id(images_dir, labels_dir, output_images, output_labels, label_id)
    click.echo(f"Moved: {result['moved_pairs']}")


# ============================================================
# detect
# ============================================================
@main.group()
def detect():
    """Detection API integration commands."""


@detect.command("classify")
@click.option("--input-path", "-i", required=True, type=click.Path(exists=True))
@click.option("--class-name", "-c", required=True)
@click.option("--output-path", "-o", required=True, type=click.Path())
@click.option("--api-url", required=True)
@click.option("--mode", type=click.Choice(["copy", "move"]), default="copy")
@click.option("--timeout", type=float, default=60.0)
@click.option("--flat/--keep-structure", default=False)
def detect_classify(input_path, class_name, output_path, api_url, mode, timeout, flat):
    """Scan images via detection API, save hits matching a class name."""
    classify_and_save(
        input_path, class_name, output_path, mode,
        api_url=api_url, timeout_s=timeout,
        keep_rel_structure=not flat,
    )


@detect.command("predict")
@click.option("--input-folder", "-i", required=True, type=click.Path(exists=True))
@click.option("--det-output", "-d", required=True, type=click.Path())
@click.option("--label-output", "-l", required=True, type=click.Path())
@click.option("--api-url", default="http://localhost:1133/detect")
@click.option("--visualize/--no-visualize", default=False)
def detect_predict(input_folder, det_output, label_output, api_url, visualize):
    """Run detection API on images, save results and YOLO labels."""
    process_images_with_detection(
        input_folder, det_output, label_output,
        visualize=visualize, api_url=api_url,
    )


# ============================================================
# image-quality
# ============================================================
@main.group("image-quality")
def image_quality():
    """Image quality check and repair commands."""


@image_quality.command("check")
@click.option("--dir", "-d", required=True, type=click.Path(exists=True))
def iq_check(dir):
    """Scan for corrupted/unreadable images."""
    bad = check_images(dir)
    click.echo(f"Bad images: {len(bad)}")
    for fpath, err in bad:
        click.echo(f"{fpath} -- {err}")


@image_quality.command("fix")
@click.option("--input-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", type=click.Path())
def iq_fix(input_dir, output_dir):
    """Attempt to repair corrupted JPEG images."""
    bad = check_and_fix_images(input_dir, output_dir)
    click.echo(f"Unrecoverable: {len(bad)}")


@image_quality.command("find-gray")
@click.option("--dir", "-d", required=True, type=click.Path(exists=True))
def iq_find_gray(dir):
    """List single-channel (grayscale) images."""
    result = find_single_channel_images(dir)
    for p in result:
        click.echo(p)


# ============================================================
# image-convert
# ============================================================
@main.group("image-convert")
def image_convert():
    """Image format conversion commands."""


@image_convert.command("gray-to-rgb")
@click.option("--src", "-s", required=True, type=click.Path(exists=True))
@click.option("--dst", "-d", required=True, type=click.Path())
def ic_gray_to_rgb(src, dst):
    """Convert single-channel images to 3-channel RGB."""
    count = convert_single_to_three_channel(src, dst)
    click.echo(f"Converted: {count}")


@image_convert.command("images-to-pdf")
@click.option("--folder", "-f", required=True, type=click.Path(exists=True))
@click.option("--output", "-o", required=True, type=click.Path())
def ic_images_to_pdf(folder, output):
    """Merge all images in a folder into a single PDF."""
    convert_images_to_pdf(folder, output)


@image_convert.command("pdf-to-jpg")
@click.option("--pdf-dir", "-p", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", required=True, type=click.Path())
def ic_pdf_to_jpg(pdf_dir, output_dir):
    """Convert the first page of each PDF to JPG."""
    convert_pdf_to_jpg(pdf_dir, output_dir)


@image_convert.command("xml-to-yolo")
@click.option("--xml-dir", "-x", required=True, type=click.Path(exists=True))
@click.option("--txt-dir", "-t", required=True, type=click.Path())
def ic_xml_to_yolo(xml_dir, txt_dir):
    """Convert VOC XML annotations to YOLO TXT format."""
    class_map = xml_folder_to_yolo_txt_folder_auto_map(xml_dir, txt_dir)
    click.echo(f"Class mapping: {class_map}")


@image_convert.command("rename")
@click.option("--input-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", required=True, type=click.Path())
@click.option("--class-name", "-c", required=True)
def ic_rename(input_dir, output_dir, class_name):
    """Batch rename images as class_name_1.jpg, class_name_2.jpg, ..."""
    rename_images_in_folder(input_dir, output_dir, class_name)


@image_convert.command("rename-pair")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--class-name", "-c", required=True)
def ic_rename_pair(images_dir, labels_dir, class_name):
    """Synchronized rename of images and labels (cls_0001 format)."""
    rename_pic_label(images_dir, labels_dir, class_name)


# ============================================================
# augment
# ============================================================
@main.group()
def augment():
    """Data augmentation commands."""


@augment.command("rotate")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--output-images", "-oi", required=True, type=click.Path())
@click.option("--output-labels", "-ol", required=True, type=click.Path())
@click.option("--angle", "-a", default=90.0, type=float)
@click.option("--direction", type=click.Choice(["left", "right"]), default="left")
def augment_rotate(images_dir, labels_dir, output_images, output_labels, angle, direction):
    """Rotate images and labels by a single angle."""
    augment_dataset(images_dir, labels_dir, output_images, output_labels, direction, angle)


@augment.command("rotate-auto")
@click.option("--images-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--labels-dir", "-l", required=True, type=click.Path(exists=True))
@click.option("--output-images", "-oi", required=True, type=click.Path())
@click.option("--output-labels", "-ol", required=True, type=click.Path())
@click.option("--direction", type=click.Choice(["left", "right"]), default="left")
@click.option("--start", type=float, default=0, help="Starting angle in degrees")
@click.option("--end", type=float, default=180, help="Ending angle in degrees")
@click.option("--step", type=float, default=2, help="Angle step in degrees")
def augment_rotate_auto(images_dir, labels_dir, output_images, output_labels, direction, start, end, step):
    """Rotate images through a range of angles (e.g. 0-180 with 2-degree steps)."""
    augment_dataset_auto(images_dir, labels_dir, output_images, output_labels, direction, start, end, step)


# ============================================================
# files
# ============================================================
@main.group()
def files():
    """File system operation commands."""


@files.command("delete-by-ext")
@click.option("--dir", "-d", required=True, type=click.Path(exists=True))
@click.option("--extensions", "-e", required=True, help="Comma-separated, e.g. .pdf,.doc")
def files_delete_by_ext(dir, extensions):
    """Recursively delete files with specified extensions."""
    ext_list = [e.strip() for e in extensions.split(",")]
    count = delete_files_with_extensions(dir, ext_list)
    click.echo(f"Deleted: {count}")


@files.command("flatten")
@click.option("--src", "-s", required=True, type=click.Path(exists=True))
@click.option("--dst", "-d", required=True, type=click.Path())
def files_flatten(src, dst):
    """Move files from nested subdirectories into a flat target directory."""
    move_files(src, dst)


@files.command("diff")
@click.option("--source-dir", "-s", required=True, type=click.Path(exists=True))
@click.option("--compare-dir", "-c", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", required=True, type=click.Path())
def files_diff(source_dir, compare_dir, output_dir):
    """Copy files present in source-dir but missing from compare-dir."""
    count = copy_missing_files(source_dir, compare_dir, output_dir)
    click.echo(f"Copied: {count}")


# ============================================================
# vlm
# ============================================================
@main.group()
def vlm():
    """Vision Language Model integration commands."""


@vlm.command("classify")
@click.option("--image", "-i", required=True, type=click.Path(exists=True))
@click.option("--prompt", "-p", required=True)
@click.option("--api-url", default="http://localhost:8000/v1")
@click.option("--api-key", default="not-needed", help="API key for authentication")
@click.option("--model", default="Qwen3.5-9B")
def vlm_classify(image, prompt, api_url, api_key, model):
    """Send a single image to a VLM and print the response."""
    result = vlm_classify_image(image, prompt, api_url, model, api_key)
    click.echo(result)


@vlm.command("filter")
@click.option("--input-dir", "-i", required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", required=True, type=click.Path())
@click.option("--prompt", "-p", required=True)
@click.option("--keywords", "-k", required=True, help="Comma-separated keywords")
@click.option("--api-url", default="http://localhost:8000/v1")
@click.option("--api-key", default="not-needed", help="API key for authentication")
@click.option("--model", default="Qwen3.5-9B")
def vlm_filter(input_dir, output_dir, prompt, keywords, api_url, api_key, model):
    """Filter images by VLM response: move those matching any keyword."""
    kw_list = [k.strip() for k in keywords.split(",")]
    result = filter_images_by_keyword(input_dir, output_dir, prompt, kw_list, api_url, model, api_key)
    click.echo(f"Matched: {result['matched']}, Errors: {result['errors']}")


def cli():
    """Entry point for console_scripts."""
    main()

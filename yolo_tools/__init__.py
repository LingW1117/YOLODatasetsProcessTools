"""YOLO Tools - Dataset processing utilities for YOLO-format datasets.

Usage:
    import yolo_tools as yt
    yt.split_dataset(src="./raw", dst="./split", train_ratio=0.7, val_ratio=0.3, test_ratio=0.0)
"""

from yolo_tools.utils import (
    IMAGE_EXTENSIONS,
    convert_to_yolo_format,
    cv_imread,
    cv_imwrite,
    find_image_path,
    load_labels,
    save_labels,
    safe_copy_or_move,
)

from yolo_tools.labels import (
    contains_class,
    convert_to_yoloclass,
    delete_empty_label_files,
    draw_labels,
    ensure_empty_labels,
    filter_labels,
    find_files_with_label,
    get_category_by_index,
    modify_labels,
    modify_labels_by_filename_prefix,
    move_empty_labels,
)

from yolo_tools.dataset import (
    delete_images_without_labels,
    filter_yolo_dataset,
    move_images_without_labels,
    move_orphan_labels,
    move_samples_by_label_id,
    move_samples_more_than_n,
    split_dataset,
)

from yolo_tools.detect import classify_and_save, process_images_with_detection

from yolo_tools.image_quality import (
    check_and_fix_images,
    check_images,
    copy_single_channel_images,
    find_single_channel_images,
)

from yolo_tools.image_convert import (
    convert_images_to_pdf,
    convert_pdf_to_jpg,
    convert_single_to_three_channel,
    rename_images_in_folder,
    rename_pic_label,
    xml_folder_to_yolo_txt_folder_auto_map,
)

from yolo_tools.augment import (
    augment_dataset,
    augment_dataset_auto,
    rotate_image_and_labels,
)

from yolo_tools.files import (
    copy_missing_files,
    delete_files_with_extensions,
    move_files,
)

from yolo_tools.vlm import filter_images_by_keyword, vlm_classify_image

__all__ = [
    # utils
    "IMAGE_EXTENSIONS",
    "convert_to_yolo_format",
    "cv_imread",
    "cv_imwrite",
    "find_image_path",
    "load_labels",
    "save_labels",
    "safe_copy_or_move",
    # labels
    "contains_class",
    "convert_to_yoloclass",
    "delete_empty_label_files",
    "draw_labels",
    "ensure_empty_labels",
    "filter_labels",
    "find_files_with_label",
    "get_category_by_index",
    "modify_labels",
    "modify_labels_by_filename_prefix",
    "move_empty_labels",
    # dataset
    "delete_images_without_labels",
    "filter_yolo_dataset",
    "move_images_without_labels",
    "move_orphan_labels",
    "move_samples_by_label_id",
    "move_samples_more_than_n",
    "split_dataset",
    # detect
    "classify_and_save",
    "process_images_with_detection",
    # image_quality
    "check_and_fix_images",
    "check_images",
    "copy_single_channel_images",
    "find_single_channel_images",
    # image_convert
    "convert_images_to_pdf",
    "convert_pdf_to_jpg",
    "convert_single_to_three_channel",
    "rename_images_in_folder",
    "rename_pic_label",
    "xml_folder_to_yolo_txt_folder_auto_map",
    # augment
    "augment_dataset",
    "augment_dataset_auto",
    "rotate_image_and_labels",
    # files
    "copy_missing_files",
    "delete_files_with_extensions",
    "move_files",
    # vlm
    "filter_images_by_keyword",
    "vlm_classify_image",
]

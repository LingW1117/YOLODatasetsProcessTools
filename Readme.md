# YOLO Tools

YOLO-format dataset processing utilities. Supports both Python import API and CLI command-line usage.

## Installation

```bash
pip install -e .
```

Or install dependencies manually:

```bash
pip install -r requirements.txt
```

## Quick Start

### Python API

```python
import yolo_tools as yt

# Split a dataset
yt.split_dataset(
    original_dataset_path="./raw_dataset",
    new_dataset_path="./split_dataset",
    train_ratio=0.7, val_ratio=0.2, test_ratio=0.1,
    move=True, seed=42,
)
```

### CLI

```bash
yolo-tools dataset split --src ./raw_dataset --dst ./split_dataset \
    --train 0.7 --val 0.2 --test 0.1 --move --seed 42
```

---

## Feature Overview

### labels -- Label Processing

| Function | Description |
|---|---|
| [`modify_labels`](#modify_labels) | Replace class ID in all label files |
| [`modify_labels_by_filename_prefix`](#modify_labels_by_filename_prefix) | Replace class ID in files matching a name prefix |
| [`filter_labels`](#filter_labels) | Remove all lines of a given class ID |
| [`delete_empty_label_files`](#delete_empty_label_files) | Delete label files with no valid bounding boxes |
| [`move_empty_labels`](#move_empty_labels) | Move empty label files to a separate directory |
| [`ensure_empty_labels`](#ensure_empty_labels) | Create empty label files for unlabeled images |
| [`find_files_with_label`](#find_files_with_label) | List label files containing a specific class ID |
| [`draw_labels`](#draw_labels) | Draw YOLO labels on images and save annotated results |
| [`convert_to_yoloclass`](#convert_to_yoloclass) | Convert class name to class ID |
| `get_category_by_index` | Convert class ID to class name |

### dataset -- Dataset Organization

| Function | Description |
|---|---|
| [`split_dataset`](#split_dataset) | Split dataset into train/val/test |
| [`delete_images_without_labels`](#delete_images_without_labels) | Delete images without corresponding labels |
| [`filter_yolo_dataset`](#filter_yolo_dataset) | Keep only samples containing a specific class |
| [`move_samples_more_than_n`](#move_samples_more_than_n) | Move samples with more than N bounding boxes |
| [`move_samples_by_label_id`](#move_samples_by_label_id) | Move samples containing a specific class ID |
| [`move_orphan_labels`](#move_orphan_labels) | Move labels without matching images |
| [`move_images_without_labels`](#move_images_without_labels) | Move images without matching labels |

### detect -- Detection API Integration

| Function | Description |
|---|---|
| [`classify_and_save`](#classify_and_save) | Scan images via detection API, save hits |
| [`process_images_with_detection`](#process_images_with_detection) | Run detection API, save annotated results and labels |

### image-quality -- Image Quality Check/Repair

| Function | Description |
|---|---|
| [`check_images`](#check_images) | Scan for corrupted/unreadable images |
| [`check_and_fix_images`](#check_and_fix_images) | Attempt to repair corrupted JPEGs |
| [`find_single_channel_images`](#find_single_channel_images) | Find grayscale images (PIL) |
| [`copy_single_channel_images`](#copy_single_channel_images) | Find and copy grayscale images (OpenCV) |

### image-convert -- Image Format Conversion

| Function | Description |
|---|---|
| [`convert_single_to_three_channel`](#convert_single_to_three_channel) | Convert grayscale to 3-channel RGB |
| [`convert_images_to_pdf`](#convert_images_to_pdf) | Merge images into a single PDF |
| [`convert_pdf_to_jpg`](#convert_pdf_to_jpg) | Convert first page of PDFs to JPG |
| [`xml_folder_to_yolo_txt_folder_auto_map`](#xml_folder_to_yolo_txt_folder_auto_map) | Convert VOC XML to YOLO TXT |
| [`rename_images_in_folder`](#rename_images_in_folder) | Batch rename images as class_N.jpg |
| [`rename_pic_label`](#rename_pic_label) | Synchronized rename of image + label pairs |

### augment -- Data Augmentation

| Function | Description |
|---|---|
| [`rotate_image_and_labels`](#rotate_image_and_labels) | Core rotation (image + labels) |
| [`augment_dataset`](#augment_dataset) | Rotate by a single angle |
| [`augment_dataset_auto`](#augment_dataset_auto) | Rotate through a range of angles |

### files -- File Operations

| Function | Description |
|---|---|
| [`delete_files_with_extensions`](#delete_files_with_extensions) | Recursively delete files by extension |
| [`move_files`](#move_files) | Flatten nested subdirectories |
| [`copy_missing_files`](#copy_missing_files) | Copy files missing from comparison directory |

### vlm -- Vision Language Model

| Function | Description |
|---|---|
| [`vlm_classify_image`](#vlm_classify_image) | Send an image to a VLM, get text response |
| [`filter_images_by_keyword`](#filter_images_by_keyword) | Filter images by VLM keyword matching |

---

## Usage Reference

### labels -- Label Processing

<a id="modify_labels"></a>

#### `modify_labels` -- Replace class IDs in labels

Replace all occurrences of a given class ID with a new class ID in all label files.

```python
import yolo_tools as yt

yt.modify_labels(
    input_folder="./labels",      # Path to label directory
    output_folder="./labels_out", # Output directory (can be same as input)
    origin_label=3,               # Class ID to replace
    modify_label=0,               # New class ID
)
```

```bash
yolo-tools labels modify -i ./labels -o ./labels_out -f 3 -t 0
```

| Option | Description |
|---|---|
| `-i, --input-dir` | Input label directory |
| `-o, --output-dir` | Output label directory |
| `-f, --origin` | Original class ID to replace |
| `-t, --target` | New class ID |

---

<a id="modify_labels_by_filename_prefix"></a>

#### `modify_labels_by_filename_prefix` -- Replace class ID by filename prefix

Replace the first column (class ID) in label files whose names start with a given prefix.

```python
yt.modify_labels_by_filename_prefix(
    folder_path="./labels",  # Directory containing label files
    filefront="prefix_",     # Filename prefix to match
    obj_cls=85,              # New class ID for the first column
)
```

```bash
yolo-tools labels modify-by-prefix -d ./labels -p prefix_ -t 85
```

| Option | Description |
|---|---|
| `-d, --dir` | Target directory |
| `-p, --prefix` | Filename prefix to match |
| `-t, --target` | New class ID |

---

<a id="filter_labels"></a>

#### `filter_labels` -- Remove lines of a given class

Remove all annotation lines belonging to a specific class ID from label files.

```python
yt.filter_labels(
    input_folder="./labels",   # Input label directory
    output_folder="./filtered", # Output directory
    filter_class=6,            # Class ID to remove
)
```

```bash
yolo-tools labels filter -i ./labels -o ./filtered -c 6
```

| Option | Description |
|---|---|
| `-i, --input-dir` | Input label directory |
| `-o, --output-dir` | Output label directory |
| `-c, --class-id` | Class ID to remove |

---

<a id="delete_empty_label_files"></a>

#### `delete_empty_label_files` -- Delete empty label files

Delete `.txt` label files that contain no valid bounding boxes (ignoring whitespace and `#` comment lines).

```python
checked, deleted = yt.delete_empty_label_files("./labels")
print(f"Checked: {checked}, Deleted: {deleted}")
```

```bash
yolo-tools labels delete-empty -d ./labels
```

| Option | Description |
|---|---|
| `-d, --dir` | Label directory to scan |

---

<a id="move_empty_labels"></a>

#### `move_empty_labels` -- Move empty label files

Move label files that have no valid content to a separate directory. Handles name collisions by appending `_1`, `_2`, etc.

```python
yt.move_empty_labels(
    label_path="./labels",          # Source label directory
    empty_labels_path="./empty",    # Destination for empty labels
)
```

```bash
yolo-tools labels move-empty -l ./labels -o ./empty
```

| Option | Description |
|---|---|
| `-l, --label-dir` | Source label directory |
| `-o, --output-dir` | Destination for empty labels |

---

<a id="ensure_empty_labels"></a>

#### `ensure_empty_labels` -- Generate empty labels for unlabeled images

Create empty `.txt` label files for images that don't have one yet. Existing labels are never overwritten.

```python
created, skipped = yt.ensure_empty_labels(
    images_folder="./images",  # Image directory
    labels_folder="./labels",  # Label directory
)
print(f"Created: {created}, Skipped: {skipped}")
```

```bash
yolo-tools labels ensure -i ./images -l ./labels
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Image directory |
| `-l, --labels-dir` | Label directory |

---

<a id="find_files_with_label"></a>

#### `find_files_with_label` -- Find labels containing a class

List the names of label files that contain a specific class ID.

```python
files = yt.find_files_with_label(
    folder_path="./labels",  # Label directory
    label=3,                 # Class ID to search for
)
for f in files:
    print(f)
```

```bash
yolo-tools labels find -d ./labels -c 3
```

| Option | Description |
|---|---|
| `-d, --dir` | Label directory |
| `-c, --class-id` | Class ID to search for |

---

<a id="draw_labels"></a>

#### `draw_labels` -- Draw labels on images

Draw YOLO-format bounding boxes and class names on images, saving the annotated results.

```python
import yolo_tools as yt

count = yt.draw_labels(
    labels_path="./labels",                          # Directory with YOLO .txt label files
    images_path="./images",                          # Directory with corresponding images
    save_path="./output",                            # Directory to save annotated images
    class_names=["cat", "dog", "bird"],              # Optional: class names for display
)
print(f"Processed: {count} images")
```

```bash
yolo-tools labels draw -l ./labels -i ./images -s ./output -n cat,dog,bird
```

| Option | Description |
|---|---|
| `-l, --labels-dir` | Directory with YOLO .txt label files |
| `-i, --images-dir` | Directory with corresponding images |
| `-s, --save-dir` | Directory to save annotated images |
| `-n, --names` | Optional: comma-separated class names (e.g. `cat,dog,bird`) |

---

<a id="convert_to_yoloclass"></a>

#### `convert_to_yoloclass` / `get_category_by_index` -- Class name/index mapping

Convert between class names and class IDs. No CLI for these -- they are utility functions for use in scripts.

```python
names = ["Seal", "Signature", "Stamp", "Text"]

# Name -> ID
cls_id = yt.convert_to_yoloclass("Stamp", names)  # Returns 2

# ID -> Name
name = yt.get_category_by_index(1, names)  # Returns "Signature"
```

---

### dataset -- Dataset Organization

<a id="split_dataset"></a>

#### `split_dataset` -- Split into train/val/test

Split a YOLO-format dataset (with `images/` and `labels/` subdirectories) into train/validation/test splits.

```python
yt.split_dataset(
    original_dataset_path="./raw",   # Source dataset (contains images/ and labels/)
    new_dataset_path="./split",      # Output path for split dataset
    train_ratio=0.7,                 # Train proportion (default 0.7)
    val_ratio=0.2,                   # Validation proportion (default 0.2)
    test_ratio=0.1,                  # Test proportion (default 0.1)
    move=False,                      # True = move, False = copy
    seed=42,                         # Random seed for reproducibility
)
```

```bash
yolo-tools dataset split --src ./raw --dst ./split \
    --train 0.7 --val 0.2 --test 0.1 --seed 42
# Add --move to move files instead of copying
```

| Option | Description |
|---|---|
| `--src` | Source dataset path (contains images/ and labels/) |
| `--dst` | Output path for split dataset |
| `--train` | Train ratio (default 0.7) |
| `--val` | Validation ratio (default 0.2) |
| `--test` | Test ratio (default 0.1) |
| `--move / --copy` | Move or copy files (default copy) |
| `--seed` | Random seed for reproducible splits |

---

<a id="delete_images_without_labels"></a>

#### `delete_images_without_labels` -- Delete unlabeled images

Delete images that have no corresponding label file (or whose label file is empty).

```python
checked, deleted = yt.delete_images_without_labels(
    images_folder="./images",  # Image directory
    labels_folder="./labels",  # Label directory
)
```

```bash
yolo-tools dataset delete-no-label -i ./images -l ./labels
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Image directory |
| `-l, --labels-dir` | Label directory |

---

<a id="filter_yolo_dataset"></a>

#### `filter_yolo_dataset` -- Filter samples by class ID

Extract samples (image + label) that contain a specific class ID. Supports copy or move.

```python
count = yt.filter_yolo_dataset(
    input_images_folder="./images",    # Source image directory
    input_labels_folder="./labels",    # Source label directory
    class_index=2,                     # Class ID to filter by
    output_images_folder="./out/img",  # Output image directory
    output_labels_folder="./out/lbl",  # Output label directory
    operation="copy",                  # "copy" or "move"
)
```

```bash
yolo-tools dataset filter-by-class \
    -i ./images -l ./labels -c 2 \
    -oi ./out/img -ol ./out/lbl --mode copy
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Source image directory |
| `-l, --labels-dir` | Source label directory |
| `-c, --class-id` | Class ID to filter by |
| `-oi, --output-images` | Output image directory |
| `-ol, --output-labels` | Output label directory |
| `--mode` | `copy` or `move` (default copy) |

---

<a id="move_samples_more_than_n"></a>

#### `move_samples_more_than_n` -- Filter by box count

Move samples whose label files contain more than N bounding boxes. Preserves relative directory structure.

```python
result = yt.move_samples_more_than_n(
    input_images_path="./images",    # Source image directory
    input_labels_path="./labels",    # Source label directory
    max_box_num=2,                   # Threshold: move samples with MORE than this
    output_images_path="./out/img",  # Output image directory
    output_labels_path="./out/lbl",  # Output label directory
)
print(f"Moved: {result['moved_pairs']}")
```

```bash
yolo-tools dataset filter-by-count \
    -i ./images -l ./labels -m 2 \
    -oi ./out/img -ol ./out/lbl
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Source image directory |
| `-l, --labels-dir` | Source label directory |
| `-m, --max-boxes` | Move samples with MORE boxes than this |
| `-oi, --output-images` | Output image directory |
| `-ol, --output-labels` | Output label directory |

---

<a id="move_samples_by_label_id"></a>

#### `move_samples_by_label_id` -- Filter by label ID

Move samples (image + label pairs) that contain a specific class ID. Preserves relative directory structure.

```python
result = yt.move_samples_by_label_id(
    images_path="./images",          # Source image directory
    labels_path="./labels",          # Source label directory
    output_images_path="./out/img",  # Output image directory
    output_labels_path="./out/lbl",  # Output label directory
    label_id=3,                      # Class ID to filter by
)
print(f"Moved: {result['moved_pairs']}")
```

```bash
yolo-tools dataset filter-by-label-id \
    -i ./images -l ./labels --label-id 3 \
    -oi ./out/img -ol ./out/lbl
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Source image directory |
| `-l, --labels-dir` | Source label directory |
| `--label-id` | Class ID to filter by |
| `-oi, --output-images` | Output image directory |
| `-ol, --output-labels` | Output label directory |

---

<a id="move_orphan_labels"></a>

#### `move_orphan_labels` -- Move labels without matching images

Find label files that have no corresponding image and move them to a separate directory.

```python
moved = yt.move_orphan_labels(
    images_folder="./images",   # Image directory
    labels_folder="./labels",   # Label directory
    output_path="./orphans",    # Destination for orphan labels
)
```

```bash
yolo-tools dataset orphan-labels -i ./images -l ./labels -o ./orphans
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Image directory |
| `-l, --labels-dir` | Label directory |
| `-o, --output-dir` | Destination for orphan labels |

---

<a id="move_images_without_labels"></a>

#### `move_images_without_labels` -- Move images without matching labels

Move images that have no corresponding label file to a separate directory.

```python
moved = yt.move_images_without_labels(
    images_folder="./images",           # Image directory
    labels_folder="./labels",           # Label directory
    missing_labels_folder="./nolabel",  # Destination for unlabeled images
)
```

```bash
yolo-tools dataset orphan-images -i ./images -l ./labels -o ./nolabel
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Image directory |
| `-l, --labels-dir` | Label directory |
| `-o, --output-dir` | Destination for unlabeled images |

---

### detect -- Detection API Integration

<a id="classify_and_save"></a>

#### `classify_and_save` -- Classify images via detection API

Recursively scan images, send them to a detection API, and save any image whose returned labels contain a target class name.

```python
result = yt.classify_and_save(
    input_path="./images",                  # Directory of images to scan
    cls="Seal",                             # Class name to match (substring)
    output_path="./hits",                   # Where to save matching images
    operation="copy",                       # "copy" or "move"
    api_url="http://host:port/detect",      # Detection API endpoint
    timeout_s=60.0,                         # Request timeout in seconds
    retries=2,                              # Retry attempts on failure
    keep_rel_structure=True,                # Preserve subdirectory structure
    verbose=True,                           # Print progress
)
print(f"Processed: {result['processed']}, Hit: {result['hit']}")
```

```bash
yolo-tools detect classify \
    -i ./images -c Seal -o ./hits \
    --api-url http://host:port/detect --mode copy
# Add --flat to flatten output (no subdirectory structure)
```

| Option | Description |
|---|---|
| `-i, --input-path` | Directory of images to scan |
| `-c, --class-name` | Class name to match in detection results |
| `-o, --output-path` | Where to save matching images |
| `--api-url` | Detection API endpoint URL |
| `--mode` | `copy` or `move` (default copy) |
| `--timeout` | Request timeout in seconds (default 60) |
| `--flat / --keep-structure` | Flatten or preserve directory structure |

---

<a id="process_images_with_detection"></a>

#### `process_images_with_detection` -- Run detection and save results

Run a detection API on all images in a folder, then save visualized detection images and YOLO-format label files.

```python
yt.process_images_with_detection(
    input_folder="./images",                      # Image directory
    det_result_savepath="./results",              # Where to save visualized images
    label_savepath="./labels",                    # Where to save YOLO labels
    visualize=False,                              # Show results interactively
    save_det_result=True,                         # Save annotated images
    save_labels=True,                             # Save YOLO label files
    api_url="http://host:port/detect",            # API endpoint
    class_names=["Seal", "Signature", "Stamp"],   # Optional: class name list for ID mapping
)
```

```bash
yolo-tools detect predict \
    -i ./images -d ./results -l ./labels \
    --api-url http://host:port/detect
# Add --visualize for interactive display
```

| Option | Description |
|---|---|
| `-i, --input-folder` | Image directory |
| `-d, --det-output` | Where to save visualized detection images |
| `-l, --label-output` | Where to save YOLO label files |
| `--api-url` | Detection API endpoint URL |
| `--visualize / --no-visualize` | Show results interactively (default off) |

---

### image-quality -- Image Quality Check/Repair

<a id="check_images"></a>

#### `check_images` -- Scan for corrupted images

Scan a directory for corrupted or unreadable images using both OpenCV and PIL validation.

```python
bad = yt.check_images(
    input_dir="./images",                     # Directory to scan
    exts={".jpg", ".jpeg", ".png"},           # Extensions to check
)
for fpath, err in bad:
    print(f"{fpath} -- {err}")
```

```bash
yolo-tools image-quality check -d ./images
```

| Option | Description |
|---|---|
| `-d, --dir` | Directory to scan |

---

<a id="check_and_fix_images"></a>

#### `check_and_fix_images` -- Repair corrupted JPEGs

Detect and attempt to repair corrupted JPEG images by re-encoding with PIL. If `output_dir` is `None`, files are overwritten in place.

```python
unrecoverable = yt.check_and_fix_images(
    input_dir="./images",       # Source directory
    output_dir="./fixed",       # Output directory (None = overwrite in place)
)
```

```bash
yolo-tools image-quality fix -i ./images -o ./fixed
# Omit -o to overwrite in place
```

| Option | Description |
|---|---|
| `-i, --input-dir` | Source directory |
| `-o, --output-dir` | Output directory (optional, omit to fix in place) |

---

<a id="find_single_channel_images"></a>

#### `find_single_channel_images` -- Find grayscale images (PIL)

Find all single-channel (grayscale) images using PIL mode detection. No CLI -- use this from scripts.

```python
gray_images = yt.find_single_channel_images("./images")
print(f"Found {len(gray_images)} grayscale images")
```

---

<a id="copy_single_channel_images"></a>

#### `copy_single_channel_images` -- Find and copy grayscale images (OpenCV)

Find single-channel images using OpenCV shape detection and copy them to a destination directory.

```python
count = yt.copy_single_channel_images(
    src_dir="./images",    # Source directory
    dst_dir="./gray",      # Destination for grayscale images
)
```

```bash
yolo-tools image-quality find-gray -d ./images
```

| Option | Description |
|---|---|
| `-d, --dir` | Directory to scan |

---

### image-convert -- Image Format Conversion

<a id="convert_single_to_three_channel"></a>

#### `convert_single_to_three_channel` -- Grayscale to RGB

Convert single-channel (grayscale) images to 3-channel RGB and save to a destination directory.

```python
count = yt.convert_single_to_three_channel(
    src_dir="./gray",    # Source directory
    dst_dir="./rgb",     # Destination directory
)
```

```bash
yolo-tools image-convert gray-to-rgb -s ./gray -d ./rgb
```

| Option | Description |
|---|---|
| `-s, --src` | Source directory |
| `-d, --dst` | Destination directory |

---

<a id="convert_images_to_pdf"></a>

#### `convert_images_to_pdf` -- Images to PDF

Merge all images in a folder into a single PDF file, sorted by filename.

```python
yt.convert_images_to_pdf(
    folder_path="./images",      # Folder containing images
    output_pdf="./output.pdf",   # Output PDF path
)
```

```bash
yolo-tools image-convert images-to-pdf -f ./images -o ./output.pdf
```

| Option | Description |
|---|---|
| `-f, --folder` | Folder containing images |
| `-o, --output` | Output PDF path |

---

<a id="convert_pdf_to_jpg"></a>

#### `convert_pdf_to_jpg` -- PDF first page to JPG

Convert the first page of each PDF in a folder to a JPG image.

```python
yt.convert_pdf_to_jpg(
    pdf_folder_path="./pdfs",    # Folder containing PDF files
    pic_folder_path="./jpgs",    # Output folder for JPG images
)
```

```bash
yolo-tools image-convert pdf-to-jpg -p ./pdfs -o ./jpgs
```

| Option | Description |
|---|---|
| `-p, --pdf-dir` | Folder containing PDF files |
| `-o, --output-dir` | Output folder for JPG images |

---

<a id="xml_folder_to_yolo_txt_folder_auto_map"></a>

#### `xml_folder_to_yolo_txt_folder_auto_map` -- VOC XML to YOLO

Batch-convert Pascal VOC XML annotations to YOLO TXT format. Class IDs are auto-assigned (starting from 0) as new class names are encountered.

```python
class_map = yt.xml_folder_to_yolo_txt_folder_auto_map(
    xml_folder="./voc_xml",     # Folder containing VOC XML files
    txt_folder="./yolo_txt",    # Output folder for YOLO TXT files
)
print(f"Class mapping: {class_map}")  # e.g. {"person": 0, "car": 1}
```

```bash
yolo-tools image-convert xml-to-yolo -x ./voc_xml -t ./yolo_txt
```

| Option | Description |
|---|---|
| `-x, --xml-dir` | Folder containing VOC XML files |
| `-t, --txt-dir` | Output folder for YOLO TXT files |

---

<a id="rename_images_in_folder"></a>

#### `rename_images_in_folder` -- Batch rename images

Rename images in a folder to `class_name_1.jpg`, `class_name_2.jpg`, etc. Files are sorted alphabetically before renaming.

```python
yt.rename_images_in_folder(
    input_folder="./images",    # Input folder
    output_folder="./renamed",  # Output folder (can be same as input)
    class_name="product",       # Class name to use as prefix
)
```

```bash
yolo-tools image-convert rename -i ./images -o ./renamed -c product
```

| Option | Description |
|---|---|
| `-i, --input-dir` | Input folder |
| `-o, --output-dir` | Output folder |
| `-c, --class-name` | Class name prefix |

---

<a id="rename_pic_label"></a>

#### `rename_pic_label` -- Synchronized rename of image + label pairs

Rename images and their corresponding label files together in `cls_0001` format (e.g. `Seal_0001.jpg`, `Seal_0001.txt`).

```python
yt.rename_pic_label(
    images_folder="./images",  # Image directory
    labels_folder="./labels",  # Label directory
    cls="Seal",                # Class name for the prefix
)
```

```bash
yolo-tools image-convert rename-pair -i ./images -l ./labels -c Seal
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Image directory |
| `-l, --labels-dir` | Label directory |
| `-c, --class-name` | Class name prefix |

---

### augment -- Data Augmentation

<a id="rotate_image_and_labels"></a>

#### `rotate_image_and_labels` -- Core rotation function

Rotate an image and its YOLO labels by a given angle. Returns the rotated image array and updated labels. This is a low-level function used by the two augmentation functions below.

```python
rotated_img, rotated_labels = yt.rotate_image_and_labels(
    img=image_array,        # BGR image as numpy array
    labels=label_list,      # YOLO labels [[cls, x, y, w, h], ...]
    angle=45,               # Rotation angle in degrees
    direction="left",       # "left" (CCW) or "right" (CW)
)
```

---

<a id="augment_dataset"></a>

#### `augment_dataset` -- Single-angle rotation augmentation

Rotate all images and labels in a dataset by a single specified angle. Output files are named `{original}_{direction}{angle}.ext`.

```python
yt.augment_dataset(
    img_dir="./images",        # Input image directory
    label_dir="./labels",      # Input label directory
    out_img_dir="./aug/img",   # Output image directory
    out_label_dir="./aug/lbl", # Output label directory
    direction="right",         # "left" or "right"
    angle=15,                  # Rotation angle in degrees
)
```

```bash
yolo-tools augment rotate \
    -i ./images -l ./labels \
    -oi ./aug/img -ol ./aug/lbl \
    --angle 15 --direction right
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Input image directory |
| `-l, --labels-dir` | Input label directory |
| `-oi, --output-images` | Output image directory |
| `-ol, --output-labels` | Output label directory |
| `-a, --angle` | Rotation angle in degrees (default 90) |
| `--direction` | `left` or `right` (default left) |

---

<a id="augment_dataset_auto"></a>

#### `augment_dataset_auto` -- Range-based rotation augmentation

Rotate all images and labels through a range of angles. Generates a variant at every step within [start, end].

```python
yt.augment_dataset_auto(
    img_dir="./images",        # Input image directory
    label_dir="./labels",      # Input label directory
    out_img_dir="./aug/img",   # Output image directory
    out_label_dir="./aug/lbl", # Output label directory
    direction="left",          # "left" or "right"
    angle_start=0,             # Starting angle (default 0)
    angle_end=180,             # Ending angle (default 180)
    angle_step=2,              # Angle step (default 2)
)
```

```bash
yolo-tools augment rotate-auto \
    -i ./images -l ./labels \
    -oi ./aug/img -ol ./aug/lbl \
    --direction left --start 0 --end 180 --step 2
```

| Option | Description |
|---|---|
| `-i, --images-dir` | Input image directory |
| `-l, --labels-dir` | Input label directory |
| `-oi, --output-images` | Output image directory |
| `-ol, --output-labels` | Output label directory |
| `--direction` | `left` or `right` (default left) |
| `--start` | Starting angle in degrees (default 0) |
| `--end` | Ending angle in degrees (default 180) |
| `--step` | Angle step in degrees (default 2) |

---

### files -- File System Operations

<a id="delete_files_with_extensions"></a>

#### `delete_files_with_extensions` -- Delete by extension

Recursively delete all files with specified extensions from a directory.

```python
count = yt.delete_files_with_extensions(
    directory="./dataset",                        # Root directory
    extensions=[".pdf", ".doc", ".html", ".xls"], # Extensions to delete
)
print(f"Deleted: {count}")
```

```bash
yolo-tools files delete-by-ext -d ./dataset -e ".pdf,.doc,.html,.xls"
```

| Option | Description |
|---|---|
| `-d, --dir` | Root directory to scan |
| `-e, --extensions` | Comma-separated extensions (e.g. `.pdf,.doc`) |

---

<a id="move_files"></a>

#### `move_files` -- Flatten nested directories

Move all files from nested subdirectories into a single flat target directory. Empty source subdirectories are removed afterward.

```python
yt.move_files(
    source_path="./nested",   # Source directory with subdirectories
    obj_path="./flat",        # Target flat directory
)
```

```bash
yolo-tools files flatten -s ./nested -d ./flat
```

| Option | Description |
|---|---|
| `-s, --src` | Source directory with subdirectories |
| `-d, --dst` | Target flat directory |

---

<a id="copy_missing_files"></a>

#### `copy_missing_files` -- Diff and copy

Compare two directories by filename stem. Copy files that exist in `source_path` but are missing from `det_path` into `loss_det_path`.

```python
count = yt.copy_missing_files(
    source_path="./images",      # Source directory
    det_path="./detections",     # Comparison directory
    loss_det_path="./missing",   # Output for missing files
)
print(f"Copied: {count}")
```

```bash
yolo-tools files diff -s ./images -c ./detections -o ./missing
```

| Option | Description |
|---|---|
| `-s, --source-dir` | Source directory |
| `-c, --compare-dir` | Comparison directory |
| `-o, --output-dir` | Output for missing files |

---

### vlm -- Vision Language Model Integration

<a id="vlm_classify_image"></a>

#### `vlm_classify_image` -- Single image VLM classification

Send an image to a VLM API (OpenAI-compatible chat completions endpoint) and return the model's text response.

```python
response = yt.vlm_classify_image(
    image_path="./image.jpg",                               # Path to image
    prompt="How many people are in this image?",            # Text prompt
    api_url="http://host:8000/v1/chat/completions",         # API endpoint
    model="Qwen3.5-9B",                                    # Model name
)
print(response)
```

```bash
yolo-tools vlm classify -i ./image.jpg -p "图中有几个人？" \
    --api-url http://host:8000/v1/chat/completions --model Qwen3.5-9B
```

| Option | Description |
|---|---|
| `-i, --image` | Path to image file |
| `-p, --prompt` | Text prompt for the VLM |
| `--api-url` | API endpoint URL |
| `--model` | Model name (default Qwen3.5-9B) |

---

<a id="filter_images_by_keyword"></a>

#### `filter_images_by_keyword` -- Filter images by VLM keywords

Scan images in a directory, send each to a VLM with a prompt, and move images whose response contains any of the specified keywords.

```python
result = yt.filter_images_by_keyword(
    input_folder="./images",                                # Input image directory
    output_folder="./matched",                              # Output for matched images
    prompt="Describe the main object in one word.",         # Text prompt
    keywords=["person", "people", "human"],                 # Keywords to match
    api_url="http://host:8000/v1/chat/completions",         # API endpoint
    model="Qwen3.5-9B",                                    # Model name
)
print(f"Matched: {result['matched']}, Errors: {result['errors']}")
```

```bash
yolo-tools vlm filter \
    -i ./images -o ./matched \
    -p "用一个词描述图中的主要内容" \
    -k "人物,人,行人" \
    --api-url http://host:8000/v1/chat/completions
```

| Option | Description |
|---|---|
| `-i, --input-dir` | Input image directory |
| `-o, --output-dir` | Output for matched images |
| `-p, --prompt` | Text prompt for the VLM |
| `-k, --keywords` | Comma-separated keywords to match |
| `--api-url` | API endpoint URL |
| `--model` | Model name (default Qwen3.5-9B) |

---

## Dependencies

- opencv-python >= 4.5
- numpy >= 1.21
- Pillow >= 9.0
- requests >= 2.25
- PyMuPDF >= 1.19
- click >= 8.0

## YOLO Dataset Format

- Typical structure:
  - `images/` contains image files
  - `labels/` contains label files (same stem, `.txt` extension)
  - Optionally split into `train/val/test`:
    - `images/train`, `images/val`, `images/test`
    - `labels/train`, `labels/val`, `labels/test`
- Label file format (one object per line):
  - `class_id x_center y_center width height`
  - All coordinates normalized to [0, 1]

## License

MIT

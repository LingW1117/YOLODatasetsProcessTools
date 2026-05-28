# YOLO Tools

YOLO 格式数据集处理工具集，支持 Python API 导入调用和 CLI 命令行调用两种方式。

## 安装

```bash
pip install -e .
```

或手动安装依赖：

```bash
pip install -r requirements.txt
```

## 快速开始

### Python API

```python
import yolo_tools as yt

# 划分数据集
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

## 功能概览

### labels - 标签处理

| 函数 | 说明 |
|---|---|
| [`modify_labels`](#modify_labels) | 批量替换标签文件中的类别 ID |
| [`modify_labels_by_filename_prefix`](#modify_labels_by_filename_prefix) | 按文件名前缀替换标签类别 ID |
| [`filter_labels`](#filter_labels) | 删除指定类别的所有标注行 |
| [`delete_empty_label_files`](#delete_empty_label_files) | 删除无有效标注框的空标签文件 |
| [`move_empty_labels`](#move_empty_labels) | 将空标签文件移动到指定目录 |
| [`ensure_empty_labels`](#ensure_empty_labels) | 为无标签的图片生成空标签文件 |
| [`find_files_with_label`](#find_files_with_label) | 查找包含指定类别 ID 的标签文件 |
| [`draw_labels`](#draw_labels) | 在图片上绘制 YOLO 标签框并保存标注结果 |
| [`convert_to_yoloclass`](#convert_to_yoloclass) | 类别名称转类别 ID |
| [`get_category_by_index`](#convert_to_yoloclass) | 类别 ID 转类别名称 |

### dataset - 数据集整理

| 函数 | 说明 |
|---|---|
| [`split_dataset`](#split_dataset) | 按比例拆分数据集为 train/val/test |
| [`delete_images_without_labels`](#delete_images_without_labels) | 删除无对应标签的图片 |
| [`filter_yolo_dataset`](#filter_yolo_dataset) | 按类别 ID 筛选数据集样本 |
| [`move_samples_more_than_n`](#move_samples_more_than_n) | 移动标注框数量超过 N 的样本 |
| [`move_samples_by_label_id`](#move_samples_by_label_id) | 移动包含指定类别 ID 的样本 |
| [`move_orphan_labels`](#move_orphan_labels) | 移动无对应图片的孤立标签 |
| [`move_images_without_labels`](#move_images_without_labels) | 移动无对应标签的孤立图片 |

### detect - 检测 API 集成

| 函数 | 说明 |
|---|---|
| [`classify_and_save`](#classify_and_save) | 通过检测 API 扫描图片，保存命中目标类别的图片 |
| [`process_images_with_detection`](#process_images_with_detection) | 调用检测 API，保存标注结果图和 YOLO 标签 |

### image-quality - 图片质量检测与修复

| 函数 | 说明 |
|---|---|
| [`check_images`](#check_images) | 扫描损坏或无法读取的图片 |
| [`check_and_fix_images`](#check_and_fix_images) | 尝试修复损坏的 JPEG 图片 |
| [`find_single_channel_images`](#find_single_channel_images) | 查找单通道灰度图片（PIL） |
| [`copy_single_channel_images`](#copy_single_channel_images) | 查找并复制单通道灰度图片（OpenCV） |

### image-convert - 图片格式转换

| 函数 | 说明 |
|---|---|
| [`convert_single_to_three_channel`](#convert_single_to_three_channel) | 灰度图转 3 通道 RGB |
| [`convert_images_to_pdf`](#convert_images_to_pdf) | 多张图片合并为单个 PDF |
| [`convert_pdf_to_jpg`](#convert_pdf_to_jpg) | PDF 首页转 JPG |
| [`xml_folder_to_yolo_txt_folder_auto_map`](#xml_folder_to_yolo_txt_folder_auto_map) | VOC XML 批量转 YOLO TXT |
| [`rename_images_in_folder`](#rename_images_in_folder) | 批量重命名为 class_N.jpg |
| [`rename_pic_label`](#rename_pic_label) | 图片与标签同步重命名 |

### augment - 数据增强

| 函数 | 说明 |
|---|---|
| [`rotate_image_and_labels`](#rotate_image_and_labels) | 核心旋转函数（图片+标签） |
| [`augment_dataset`](#augment_dataset) | 单角度旋转增强 |
| [`augment_dataset_auto`](#augment_dataset_auto) | 多角度范围旋转增强 |

### files - 文件操作

| 函数 | 说明 |
|---|---|
| [`delete_files_with_extensions`](#delete_files_with_extensions) | 按后缀递归删除文件 |
| [`move_files`](#move_files) | 多子目录文件扁平化汇总 |
| [`copy_missing_files`](#copy_missing_files) | 复制对比目录中缺失的文件 |

### vlm - 视觉大模型集成

| 函数 | 说明 |
|---|---|
| [`vlm_classify_image`](#vlm_classify_image) | 发送图片到 VLM，获取文字回复 |
| [`filter_images_by_keyword`](#filter_images_by_keyword) | 通过 VLM 关键词匹配筛选图片 |

---

## 用法参考

### labels - 标签处理

<a id="modify_labels"></a>

#### `modify_labels` - 批量替换标签类别 ID

将标签文件中所有指定类别 ID 替换为新 ID。

```python
import yolo_tools as yt

yt.modify_labels(
    input_folder="./labels",      # 标签目录
    output_folder="./labels_out", # 输出目录（可与输入相同）
    origin_label=3,               # 要替换的原始类别 ID
    modify_label=0,               # 新的类别 ID
)
```

```bash
yolo-tools labels modify -i ./labels -o ./labels_out -f 3 -t 0
```

| 参数 | 说明 |
|---|---|
| `-i, --input-dir` | 输入标签目录 |
| `-o, --output-dir` | 输出标签目录 |
| `-f, --origin` | 要替换的原始类别 ID |
| `-t, --target` | 新的类别 ID |

---

<a id="modify_labels_by_filename_prefix"></a>

#### `modify_labels_by_filename_prefix` - 按文件名前缀替换类别 ID

仅对文件名以指定前缀开头的标签文件，替换每行第一列的类别 ID。

```python
yt.modify_labels_by_filename_prefix(
    folder_path="./labels",  # 标签目录
    filefront="prefix_",     # 文件名前缀
    obj_cls=85,              # 新的类别 ID
)
```

```bash
yolo-tools labels modify-by-prefix -d ./labels -p prefix_ -t 85
```

| 参数 | 说明 |
|---|---|
| `-d, --dir` | 目标目录 |
| `-p, --prefix` | 文件名前缀 |
| `-t, --target` | 新的类别 ID |

---

<a id="filter_labels"></a>

#### `filter_labels` - 删除指定类别的标注行

从标签文件中删除指定类别 ID 的所有标注行。

```python
yt.filter_labels(
    input_folder="./labels",    # 输入标签目录
    output_folder="./filtered", # 输出目录
    filter_class=6,             # 要删除的类别 ID
)
```

```bash
yolo-tools labels filter -i ./labels -o ./filtered -c 6
```

| 参数 | 说明 |
|---|---|
| `-i, --input-dir` | 输入标签目录 |
| `-o, --output-dir` | 输出标签目录 |
| `-c, --class-id` | 要删除的类别 ID |

---

<a id="delete_empty_label_files"></a>

#### `delete_empty_label_files` - 删除空标签文件

删除无有效标注框的标签文件（忽略空行和 `#` 注释行）。

```python
checked, deleted = yt.delete_empty_label_files("./labels")
print(f"检查: {checked}, 删除: {deleted}")
```

```bash
yolo-tools labels delete-empty -d ./labels
```

| 参数 | 说明 |
|---|---|
| `-d, --dir` | 要扫描的标签目录 |

---

<a id="move_empty_labels"></a>

#### `move_empty_labels` - 移动空标签文件

将空标签文件移动到指定目录，通过追加 `_1`、`_2` 等后缀避免重名覆盖。

```python
yt.move_empty_labels(
    label_path="./labels",        # 源标签目录
    empty_labels_path="./empty",  # 空标签目标目录
)
```

```bash
yolo-tools labels move-empty -l ./labels -o ./empty
```

| 参数 | 说明 |
|---|---|
| `-l, --label-dir` | 源标签目录 |
| `-o, --output-dir` | 空标签目标目录 |

---

<a id="ensure_empty_labels"></a>

#### `ensure_empty_labels` - 为无标签图片生成空标签

为没有对应标签文件的图片创建空 `.txt` 标签文件，已存在的标签不会被覆盖。

```python
created, skipped = yt.ensure_empty_labels(
    images_folder="./images",  # 图片目录
    labels_folder="./labels",  # 标签目录
)
print(f"新建: {created}, 跳过: {skipped}")
```

```bash
yolo-tools labels ensure -i ./images -l ./labels
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 图片目录 |
| `-l, --labels-dir` | 标签目录 |

---

<a id="find_files_with_label"></a>

#### `find_files_with_label` - 查找包含指定类别的标签

列出包含指定类别 ID 的标签文件名。

```python
files = yt.find_files_with_label(
    folder_path="./labels",  # 标签目录
    label=3,                 # 要查找的类别 ID
)
for f in files:
    print(f)
```

```bash
yolo-tools labels find -d ./labels -c 3
```

| 参数 | 说明 |
|---|---|
| `-d, --dir` | 标签目录 |
| `-c, --class-id` | 要查找的类别 ID |

---

<a id="draw_labels"></a>

#### `draw_labels` - 在图片上绘制标签框

读取 YOLO 格式标签，在对应图片上绘制标注框和类别名称，保存到输出目录。

```python
import yolo_tools as yt

count = yt.draw_labels(
    labels_path="./labels",                          # YOLO .txt 标签文件目录
    images_path="./images",                          # 对应图片目录
    save_path="./output",                            # 标注结果保存目录
    class_names=["猫", "狗", "鸟"],                  # 可选：类别名称列表，用于框上显示
)
print(f"处理: {count} 张图片")
```

```bash
yolo-tools labels draw -l ./labels -i ./images -s ./output -n 猫,狗,鸟
```

| 参数 | 说明 |
|---|---|
| `-l, --labels-dir` | YOLO .txt 标签文件目录 |
| `-i, --images-dir` | 对应图片目录 |
| `-s, --save-dir` | 标注结果保存目录 |
| `-n, --names` | 可选：逗号分隔的类别名称（如 `猫,狗,鸟`） |

---

<a id="convert_to_yoloclass"></a>

#### `convert_to_yoloclass` / `get_category_by_index` - 类别名称与索引互查

在类别名称和类别 ID 之间互相转换。这两个是工具函数，无 CLI，仅在脚本中使用。

```python
names = ["印章", "签名", "指印", "文字"]

# 名称 -> ID
cls_id = yt.convert_to_yoloclass("签名", names)  # 返回 1

# ID -> 名称
name = yt.get_category_by_index(2, names)  # 返回 "指印"
```

---

### dataset - 数据集整理

<a id="split_dataset"></a>

#### `split_dataset` - 划分数据集

将包含 `images/` 和 `labels/` 子目录的 YOLO 数据集按比例拆分为 train/val/test。

```python
yt.split_dataset(
    original_dataset_path="./raw",   # 源数据集路径（含 images/ 和 labels/）
    new_dataset_path="./split",      # 划分后数据集输出路径
    train_ratio=0.7,                 # 训练集比例（默认 0.7）
    val_ratio=0.2,                   # 验证集比例（默认 0.2）
    test_ratio=0.1,                  # 测试集比例（默认 0.1）
    move=False,                      # True=移动, False=复制
    seed=42,                         # 随机种子，保证结果可复现
)
```

```bash
yolo-tools dataset split --src ./raw --dst ./split \
    --train 0.7 --val 0.2 --test 0.1 --seed 42
# 添加 --move 改为移动文件
```

| 参数 | 说明 |
|---|---|
| `--src` | 源数据集路径（含 images/ 和 labels/） |
| `--dst` | 划分后数据集输出路径 |
| `--train` | 训练集比例（默认 0.7） |
| `--val` | 验证集比例（默认 0.2） |
| `--test` | 测试集比例（默认 0.1） |
| `--move / --copy` | 移动或复制文件（默认复制） |
| `--seed` | 随机种子，保证划分可复现 |

---

<a id="delete_images_without_labels"></a>

#### `delete_images_without_labels` - 删除无标签的图片

删除没有对应标签文件（或标签为空）的图片。

```python
checked, deleted = yt.delete_images_without_labels(
    images_folder="./images",  # 图片目录
    labels_folder="./labels",  # 标签目录
)
```

```bash
yolo-tools dataset delete-no-label -i ./images -l ./labels
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 图片目录 |
| `-l, --labels-dir` | 标签目录 |

---

<a id="filter_yolo_dataset"></a>

#### `filter_yolo_dataset` - 按类别筛选数据集

提取包含指定类别 ID 的样本（图片+标签），支持复制或移动。

```python
count = yt.filter_yolo_dataset(
    input_images_folder="./images",    # 源图片目录
    input_labels_folder="./labels",    # 源标签目录
    class_index=2,                     # 要筛选的类别 ID
    output_images_folder="./out/img",  # 输出图片目录
    output_labels_folder="./out/lbl",  # 输出标签目录
    operation="copy",                  # "copy" 或 "move"
)
```

```bash
yolo-tools dataset filter-by-class \
    -i ./images -l ./labels -c 2 \
    -oi ./out/img -ol ./out/lbl --mode copy
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 源图片目录 |
| `-l, --labels-dir` | 源标签目录 |
| `-c, --class-id` | 要筛选的类别 ID |
| `-oi, --output-images` | 输出图片目录 |
| `-ol, --output-labels` | 输出标签目录 |
| `--mode` | `copy` 或 `move`（默认 copy） |

---

<a id="move_samples_more_than_n"></a>

#### `move_samples_more_than_n` - 按标注框数量筛选

将标注框数量超过 N 的样本（图片+标签）移动到输出目录，保留相对目录结构。

```python
result = yt.move_samples_more_than_n(
    input_images_path="./images",    # 源图片目录
    input_labels_path="./labels",    # 源标签目录
    max_box_num=2,                   # 阈值：超过此数量的样本将被移动
    output_images_path="./out/img",  # 输出图片目录
    output_labels_path="./out/lbl",  # 输出标签目录
)
print(f"移动: {result['moved_pairs']}")
```

```bash
yolo-tools dataset filter-by-count \
    -i ./images -l ./labels -m 2 \
    -oi ./out/img -ol ./out/lbl
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 源图片目录 |
| `-l, --labels-dir` | 源标签目录 |
| `-m, --max-boxes` | 阈值：超过此数量的样本将被移动 |
| `-oi, --output-images` | 输出图片目录 |
| `-ol, --output-labels` | 输出标签目录 |

---

<a id="move_samples_by_label_id"></a>

#### `move_samples_by_label_id` - 按类别 ID 移动样本

将包含指定类别 ID 的样本（图片+标签）移动到新目录，保留相对目录结构。

```python
result = yt.move_samples_by_label_id(
    images_path="./images",          # 源图片目录
    labels_path="./labels",          # 源标签目录
    output_images_path="./out/img",  # 输出图片目录
    output_labels_path="./out/lbl",  # 输出标签目录
    label_id=3,                      # 要筛选的类别 ID
)
print(f"移动: {result['moved_pairs']}")
```

```bash
yolo-tools dataset filter-by-label-id \
    -i ./images -l ./labels --label-id 3 \
    -oi ./out/img -ol ./out/lbl
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 源图片目录 |
| `-l, --labels-dir` | 源标签目录 |
| `--label-id` | 要筛选的类别 ID |
| `-oi, --output-images` | 输出图片目录 |
| `-ol, --output-labels` | 输出标签目录 |

---

<a id="move_orphan_labels"></a>

#### `move_orphan_labels` - 移动无对应图片的标签

找到"有标签但无图片"的标签文件，将其移动到指定目录。

```python
moved = yt.move_orphan_labels(
    images_folder="./images",   # 图片目录
    labels_folder="./labels",   # 标签目录
    output_path="./orphans",    # 孤立标签目标目录
)
```

```bash
yolo-tools dataset orphan-labels -i ./images -l ./labels -o ./orphans
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 图片目录 |
| `-l, --labels-dir` | 标签目录 |
| `-o, --output-dir` | 孤立标签目标目录 |

---

<a id="move_images_without_labels"></a>

#### `move_images_without_labels` - 移动无对应标签的图片

将"有图片但无标签"的图片移动到指定目录。

```python
moved = yt.move_images_without_labels(
    images_folder="./images",           # 图片目录
    labels_folder="./labels",           # 标签目录
    missing_labels_folder="./nolabel",  # 无标签图片目标目录
)
```

```bash
yolo-tools dataset orphan-images -i ./images -l ./labels -o ./nolabel
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 图片目录 |
| `-l, --labels-dir` | 标签目录 |
| `-o, --output-dir` | 无标签图片目标目录 |

---

### detect - 检测 API 集成

<a id="classify_and_save"></a>

#### `classify_and_save` - 通过检测 API 分类保存

递归扫描图片，发送到检测 API，将返回标签中包含目标类别名称的图片复制或移动到输出目录。

```python
result = yt.classify_and_save(
    input_path="./images",                  # 要扫描的图片目录
    cls="印章",                             # 要匹配的类别名称（支持子串匹配）
    output_path="./hits",                   # 命中图片的输出目录
    operation="copy",                       # "copy" 或 "move"
    api_url="http://host:port/detect",      # 检测 API 地址
    timeout_s=60.0,                         # 请求超时（秒）
    retries=2,                              # 失败重试次数
    keep_rel_structure=True,                # 保留相对目录结构
    verbose=True,                           # 打印进度
)
print(f"处理: {result['processed']}, 命中: {result['hit']}")
```

```bash
yolo-tools detect classify \
    -i ./images -c 印章 -o ./hits \
    --api-url http://host:port/detect --mode copy
# 添加 --flat 平铺输出（不保留子目录结构）
```

| 参数 | 说明 |
|---|---|
| `-i, --input-path` | 要扫描的图片目录 |
| `-c, --class-name` | 要匹配的类别名称 |
| `-o, --output-path` | 命中图片的输出目录 |
| `--api-url` | 检测 API 地址 |
| `--mode` | `copy` 或 `move`（默认 copy） |
| `--timeout` | 请求超时秒数（默认 60） |
| `--flat / --keep-structure` | 平铺或保留目录结构 |

---

<a id="process_images_with_detection"></a>

#### `process_images_with_detection` - 检测并保存结果

对目录内所有图片调用检测 API，保存可视化检测结果图和 YOLO 格式标签文件。

```python
yt.process_images_with_detection(
    input_folder="./images",                      # 图片目录
    det_result_savepath="./results",              # 可视化结果保存目录
    label_savepath="./labels",                    # YOLO 标签保存目录
    visualize=False,                              # 是否交互式显示结果
    save_det_result=True,                         # 是否保存标注图
    save_labels=True,                             # 是否保存标签文件
    api_url="http://host:port/detect",            # API 地址
    class_names=["印章", "签名", "指印"],          # 可选：类别名称列表，用于 ID 映射
)
```

```bash
yolo-tools detect predict \
    -i ./images -d ./results -l ./labels \
    --api-url http://host:port/detect
# 添加 --visualize 可交互式显示
```

| 参数 | 说明 |
|---|---|
| `-i, --input-folder` | 图片目录 |
| `-d, --det-output` | 可视化结果保存目录 |
| `-l, --label-output` | YOLO 标签保存目录 |
| `--api-url` | 检测 API 地址 |
| `--visualize / --no-visualize` | 是否交互式显示（默认关闭） |

---

### image-quality - 图片质量检测与修复

<a id="check_images"></a>

#### `check_images` - 扫描损坏图片

使用 OpenCV 和 PIL 双重校验，扫描目录中损坏或无法正常读取的图片。

```python
bad = yt.check_images(
    input_dir="./images",                     # 要扫描的目录
    exts={".jpg", ".jpeg", ".png"},           # 要检查的扩展名
)
for fpath, err in bad:
    print(f"{fpath} -- {err}")
```

```bash
yolo-tools image-quality check -d ./images
```

| 参数 | 说明 |
|---|---|
| `-d, --dir` | 要扫描的目录 |

---

<a id="check_and_fix_images"></a>

#### `check_and_fix_images` - 修复损坏的 JPEG

检测并尝试修复损坏的 JPEG 图片（通过 PIL 重新编码）。如果 `output_dir` 为 `None`，则原地覆盖。

```python
unrecoverable = yt.check_and_fix_images(
    input_dir="./images",       # 源目录
    output_dir="./fixed",       # 修复后输出目录（None 则原地覆盖）
)
```

```bash
yolo-tools image-quality fix -i ./images -o ./fixed
# 省略 -o 则原地覆盖修复
```

| 参数 | 说明 |
|---|---|
| `-i, --input-dir` | 源目录 |
| `-o, --output-dir` | 输出目录（可选，省略则原地修复） |

---

<a id="find_single_channel_images"></a>

#### `find_single_channel_images` - 查找单通道图片（PIL）

使用 PIL 模式检测查找所有单通道（灰度）图片。无 CLI，仅通过脚本调用。

```python
gray_images = yt.find_single_channel_images("./images")
print(f"找到 {len(gray_images)} 张灰度图片")
```

---

<a id="copy_single_channel_images"></a>

#### `copy_single_channel_images` - 查找并复制灰度图片（OpenCV）

使用 OpenCV 形状检测查找单通道图片，并复制到目标目录。

```python
count = yt.copy_single_channel_images(
    src_dir="./images",    # 源目录
    dst_dir="./gray",      # 灰度图片目标目录
)
```

```bash
yolo-tools image-quality find-gray -d ./images
```

| 参数 | 说明 |
|---|---|
| `-d, --dir` | 要扫描的目录 |

---

### image-convert - 图片格式转换

<a id="convert_single_to_three_channel"></a>

#### `convert_single_to_three_channel` - 灰度转 RGB

将单通道图片转为 3 通道 RGB 并保存到目标目录。

```python
count = yt.convert_single_to_three_channel(
    src_dir="./gray",    # 源目录
    dst_dir="./rgb",     # 目标目录
)
```

```bash
yolo-tools image-convert gray-to-rgb -s ./gray -d ./rgb
```

| 参数 | 说明 |
|---|---|
| `-s, --src` | 源目录 |
| `-d, --dst` | 目标目录 |

---

<a id="convert_images_to_pdf"></a>

#### `convert_images_to_pdf` - 图片合并为 PDF

将目录内所有图片按文件名排序后合并为一个 PDF 文件。

```python
yt.convert_images_to_pdf(
    folder_path="./images",      # 图片目录
    output_pdf="./output.pdf",   # 输出 PDF 路径
)
```

```bash
yolo-tools image-convert images-to-pdf -f ./images -o ./output.pdf
```

| 参数 | 说明 |
|---|---|
| `-f, --folder` | 图片目录 |
| `-o, --output` | 输出 PDF 路径 |

---

<a id="convert_pdf_to_jpg"></a>

#### `convert_pdf_to_jpg` - PDF 首页转 JPG

将目录内每个 PDF 文件的第一页转换为 JPG 图片。

```python
yt.convert_pdf_to_jpg(
    pdf_folder_path="./pdfs",    # PDF 目录
    pic_folder_path="./jpgs",    # JPG 输出目录
)
```

```bash
yolo-tools image-convert pdf-to-jpg -p ./pdfs -o ./jpgs
```

| 参数 | 说明 |
|---|---|
| `-p, --pdf-dir` | PDF 文件目录 |
| `-o, --output-dir` | JPG 输出目录 |

---

<a id="xml_folder_to_yolo_txt_folder_auto_map"></a>

#### `xml_folder_to_yolo_txt_folder_auto_map` - VOC XML 转 YOLO

批量将 Pascal VOC XML 标注转换为 YOLO TXT 格式。类别 ID 自动分配（从 0 开始，遇到新类名自动递增）。

```python
class_map = yt.xml_folder_to_yolo_txt_folder_auto_map(
    xml_folder="./voc_xml",     # VOC XML 文件目录
    txt_folder="./yolo_txt",    # YOLO TXT 输出目录
)
print(f"类别映射: {class_map}")  # 例如 {"person": 0, "car": 1}
```

```bash
yolo-tools image-convert xml-to-yolo -x ./voc_xml -t ./yolo_txt
```

| 参数 | 说明 |
|---|---|
| `-x, --xml-dir` | VOC XML 文件目录 |
| `-t, --txt-dir` | YOLO TXT 输出目录 |

---

<a id="rename_images_in_folder"></a>

#### `rename_images_in_folder` - 批量重命名图片

将目录内图片重命名为 `class_name_1.jpg`、`class_name_2.jpg` 等格式。文件按字母排序后再编号。

```python
yt.rename_images_in_folder(
    input_folder="./images",    # 输入目录
    output_folder="./renamed",  # 输出目录（可与输入相同）
    class_name="product",       # 类别名称前缀
)
```

```bash
yolo-tools image-convert rename -i ./images -o ./renamed -c product
```

| 参数 | 说明 |
|---|---|
| `-i, --input-dir` | 输入目录 |
| `-o, --output-dir` | 输出目录 |
| `-c, --class-name` | 类别名称前缀 |

---

<a id="rename_pic_label"></a>

#### `rename_pic_label` - 同步重命名图片与标签

将图片及其对应的标签文件同步重命名为 `cls_0001` 格式（如 `印章_0001.jpg`、`印章_0001.txt`）。

```python
yt.rename_pic_label(
    images_folder="./images",  # 图片目录
    labels_folder="./labels",  # 标签目录
    cls="印章",               # 类别名称前缀
)
```

```bash
yolo-tools image-convert rename-pair -i ./images -l ./labels -c 印章
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 图片目录 |
| `-l, --labels-dir` | 标签目录 |
| `-c, --class-name` | 类别名称前缀 |

---

### augment - 数据增强

<a id="rotate_image_and_labels"></a>

#### `rotate_image_and_labels` - 核心旋转函数

将图片及其 YOLO 标签按指定角度旋转。返回旋转后的图片数组和更新后的标签列表。这是底层函数，供下面两个增强函数使用。

```python
rotated_img, rotated_labels = yt.rotate_image_and_labels(
    img=image_array,        # BGR 图片 (numpy array)
    labels=label_list,      # YOLO 标签 [[cls, x, y, w, h], ...]
    angle=45,               # 旋转角度
    direction="left",       # "left" (逆时针) 或 "right" (顺时针)
)
```

---

<a id="augment_dataset"></a>

#### `augment_dataset` - 单角度旋转增强

将数据集中所有图片和标签按指定角度旋转一次。输出文件命名为 `{原名}_{direction}{angle}.ext`。

```python
yt.augment_dataset(
    img_dir="./images",        # 输入图片目录
    label_dir="./labels",      # 输入标签目录
    out_img_dir="./aug/img",   # 输出图片目录
    out_label_dir="./aug/lbl", # 输出标签目录
    direction="right",         # "left" 或 "right"
    angle=15,                  # 旋转角度
)
```

```bash
yolo-tools augment rotate \
    -i ./images -l ./labels \
    -oi ./aug/img -ol ./aug/lbl \
    --angle 15 --direction right
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 输入图片目录 |
| `-l, --labels-dir` | 输入标签目录 |
| `-oi, --output-images` | 输出图片目录 |
| `-ol, --output-labels` | 输出标签目录 |
| `-a, --angle` | 旋转角度（默认 90） |
| `--direction` | `left` 或 `right`（默认 left） |

---

<a id="augment_dataset_auto"></a>

#### `augment_dataset_auto` - 多角度范围旋转增强

将数据集中所有图片和标签在指定角度范围内按步长生成多个旋转版本。

```python
yt.augment_dataset_auto(
    img_dir="./images",        # 输入图片目录
    label_dir="./labels",      # 输入标签目录
    out_img_dir="./aug/img",   # 输出图片目录
    out_label_dir="./aug/lbl", # 输出标签目录
    direction="left",          # "left" 或 "right"
    angle_start=0,             # 起始角度（默认 0）
    angle_end=180,             # 结束角度（默认 180）
    angle_step=2,              # 角度步长（默认 2）
)
```

```bash
yolo-tools augment rotate-auto \
    -i ./images -l ./labels \
    -oi ./aug/img -ol ./aug/lbl \
    --direction left --start 0 --end 180 --step 2
```

| 参数 | 说明 |
|---|---|
| `-i, --images-dir` | 输入图片目录 |
| `-l, --labels-dir` | 输入标签目录 |
| `-oi, --output-images` | 输出图片目录 |
| `-ol, --output-labels` | 输出标签目录 |
| `--direction` | `left` 或 `right`（默认 left） |
| `--start` | 起始角度（默认 0） |
| `--end` | 结束角度（默认 180） |
| `--step` | 角度步长（默认 2） |

---

### files - 文件操作

<a id="delete_files_with_extensions"></a>

#### `delete_files_with_extensions` - 按后缀删除文件

递归删除目录下所有指定后缀名的文件。

```python
count = yt.delete_files_with_extensions(
    directory="./dataset",                        # 根目录
    extensions=[".pdf", ".doc", ".html", ".xls"], # 要删除的后缀列表
)
print(f"删除: {count}")
```

```bash
yolo-tools files delete-by-ext -d ./dataset -e ".pdf,.doc,.html,.xls"
```

| 参数 | 说明 |
|---|---|
| `-d, --dir` | 要扫描的根目录 |
| `-e, --extensions` | 逗号分隔的后缀列表（如 `.pdf,.doc`） |

---

<a id="move_files"></a>

#### `move_files` - 扁平化多子目录

将多子目录中的文件汇总移动到一个扁平目标目录，完成后删除空的源子目录。

```python
yt.move_files(
    source_path="./nested",   # 含子目录的源目录
    obj_path="./flat",        # 扁平化目标目录
)
```

```bash
yolo-tools files flatten -s ./nested -d ./flat
```

| 参数 | 说明 |
|---|---|
| `-s, --src` | 含子目录的源目录 |
| `-d, --dst` | 扁平化目标目录 |

---

<a id="copy_missing_files"></a>

#### `copy_missing_files` - 差异对比复制

按文件名主干（不含扩展名）比较两个目录，将源目录中有但对比目录中没有的文件复制到输出目录。

```python
count = yt.copy_missing_files(
    source_path="./images",      # 源目录
    det_path="./detections",     # 对比目录
    loss_det_path="./missing",   # 缺失文件输出目录
)
print(f"复制: {count}")
```

```bash
yolo-tools files diff -s ./images -c ./detections -o ./missing
```

| 参数 | 说明 |
|---|---|
| `-s, --source-dir` | 源目录 |
| `-c, --compare-dir` | 对比目录 |
| `-o, --output-dir` | 缺失文件输出目录 |

---

### vlm - 视觉大模型集成

<a id="vlm_classify_image"></a>

#### `vlm_classify_image` - 单张图片 VLM 识别

将图片发送到 VLM API（OpenAI 兼容的 chat completions 端点），返回模型的文本回复。

```python
response = yt.vlm_classify_image(
    image_path="./image.jpg",                               # 图片路径
    prompt="图中有几个人？",                                 # 文本提示
    api_url="http://host:8000/v1/chat/completions",         # API 地址
    model="Qwen3.5-9B",                                    # 模型名称
)
print(response)
```

```bash
yolo-tools vlm classify -i ./image.jpg -p "图中有几个人？" \
    --api-url http://host:8000/v1/chat/completions --model Qwen3.5-9B
```

| 参数 | 说明 |
|---|---|
| `-i, --image` | 图片文件路径 |
| `-p, --prompt` | 文本提示 |
| `--api-url` | API 地址 |
| `--model` | 模型名称（默认 Qwen3.5-9B） |

---

<a id="filter_images_by_keyword"></a>

#### `filter_images_by_keyword` - VLM 关键词筛选

遍历目录中的图片，发送到 VLM 识别，将回复中包含任意关键词的图片移动到输出目录。

```python
result = yt.filter_images_by_keyword(
    input_folder="./images",                                # 输入图片目录
    output_folder="./matched",                              # 匹配图片输出目录
    prompt="图中文件标题是什么",                       # 文本提示
    keywords=["财务表","统计表"],                         # 关键词列表
    api_url="http://host:8000/v1/chat/completions",         # API 地址
    model="Qwen3.5", 
    api_key="xxxx"
)
print(f"匹配: {result['matched']}, 错误: {result['errors']}")
```

```bash
yolo-tools vlm filter \
    -i ./images -o ./matched \
    -p "图中文件标题是什么" \
    -k "财务表,统计表" \
    --api-url http://host:8000/v1/chat/completions
```

| 参数 | 说明 |
|---|---|
| `-i, --input-dir` | 输入图片目录 |
| `-o, --output-dir` | 匹配图片输出目录 |
| `-p, --prompt` | 文本提示 |
| `-k, --keywords` | 逗号分隔的关键词列表 |
| `--api-url` | API 地址 |
| `--model` | 模型名称（默认 Qwen3.5-9B） |

---

## 依赖

- opencv-python >= 4.5
- numpy >= 1.21
- Pillow >= 9.0
- requests >= 2.25
- PyMuPDF >= 1.19
- click >= 8.0

## YOLO 数据集结构与标注格式

- 典型结构：
  - `images/` 存放图片
  - `labels/` 存放标签（与图片同名的 `.txt` 文件）
  - 可选按 `train/val/test` 分层：
    - `images/train`、`images/val`、`images/test`
    - `labels/train`、`labels/val`、`labels/test`
- 图片与标签一一对应：`images/xxx.jpg` 对应 `labels/xxx.txt`
- 标签文件格式（每行一个目标）：
  - `class_id x_center y_center width height`
  - `class_id` 为类别索引（整数，从 0 开始）
  - 坐标为归一化值（相对图片宽高，范围 0~1）
  - 允许多行，空文件表示"无目标"

## License

MIT

# 类别名称列表
names = [
    "className1",
    "className2",
    "className3",
    "className4",
    "classNameN",
]

def convert_to_yoloclass(name):
    """将类别名称转换为YOLO格式的类别ID"""
    # 创建类别名称到索引的映射
    name_to_class_id = {name: idx for idx, name in enumerate(names)}
    return name_to_class_id.get(name, -1)

def get_category_by_index(index):
    """根据序号查询类别名称"""
    if 0 <= index < len(names):
        return names[index]
    else:
        return "Invalid index"

# # 测试
map = convert_to_yoloclass('PersonLoanContract_Cover')
print(map)


# 测试
# category = get_category_by_index(77)
# print(category)
# category = get_category_by_index(75)
# print(category)
# category = get_category_by_index(51)
# print(category)
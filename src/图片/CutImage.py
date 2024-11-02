# coding=utf-8
import os
from src import ver_onnx
from src import yolo_onnx
from src import utils
from PIL import Image


class JYClick(object):
    def __init__(self, per_path='pre_model_v6.onnx', yolo_path='best.onnx'):
        save_path = os.path.join(os.path.dirname(__file__), "../")
        path = lambda a, b: os.path.join(a, b)
        per_path = path(save_path, per_path)
        yolo_path = path(save_path, yolo_path)
        self.yolo = yolo_onnx.YOLOV5_ONNX(yolo_path, classes=['char', 'target'], providers=['CPUExecutionProvider'])
        self.pre = ver_onnx.PreONNX(per_path, providers=['CPUExecutionProvider'])

    def run(self, image_path):
        img = utils.open_image(image_path)
        data = self.yolo.decect(image_path)

        # 提取 targets 和 chars 的边界框坐标
        targets = [i.get("crop") for i in data if i.get("classes") == "target"]
        chars = [i.get("crop") for i in data if i.get("classes") == "char"]

        # 根据信息排序
        chars.sort(key=lambda x: x[0])  # 按照 x 坐标排序

        # 获取原始图片的宽高
        img_width, img_height = img.size

        # 将每个目标转换为 YOLO 格式
        yolo_labels = []

        # 处理 targets 类别
        for target in targets:
            class_id = 1  # 将 'target' 的类索引设置为 1
            # 确保 target 是坐标格式 [x1, y1, x2, y2]
            x_center = (target[0] + target[2]) / 2 / img_width
            y_center = (target[1] + target[3]) / 2 / img_height
            width = (target[2] - target[0]) / img_width
            height = (target[3] - target[1]) / img_height

            yolo_labels.append(f"{class_id} {x_center} {y_center} {width} {height}")

        # 处理 chars 类别
        for char in chars:
            class_id = 0  # 将 'char' 的类索引设置为 0
            # 确保 char 是坐标格式 [x1, y1, x2, y2]
            x_center = (char[0] + char[2]) / 2 / img_width
            y_center = (char[1] + char[3]) / 2 / img_height
            width = (char[2] - char[0]) / img_width
            height = (char[3] - char[1]) / img_height

            yolo_labels.append(f"{class_id} {x_center} {y_center} {width} {height}")

        return yolo_labels

    def crop_and_save_images(self, char_crop, target_crop, image_path, group_index):
        base_dir = os.path.dirname(image_path)  # 获取输入图片所在目录
        filename_without_extension = os.path.splitext(os.path.basename(image_path))[0]  # 获取输入图片的文件名（不包含扩展名）

        group_output_dir = os.path.join(base_dir, f"{filename_without_extension}_{group_index}")  # 创建组级输出文件夹路径，例如 "A1"
        os.makedirs(group_output_dir, exist_ok=True)  # 创建组级输出文件夹，如果已存在则不创建

        # 裁剪并保存 char 图片
        char_img = Image.open(image_path).crop(char_crop).resize((105, 105))
        char_output_path = os.path.join(group_output_dir, f"CHAR{group_index}.jpg")
        char_img.save(char_output_path)

        # 裁剪并保存 target 图片
        target_img = Image.open(image_path).crop(target_crop).resize((105, 105))
        target_output_path = os.path.join(group_output_dir, f"TARGET{group_index}.jpg")
        target_img.save(target_output_path)

        print(f"Cropped and saved images to {group_output_dir}")


def process_all_images_in_directory(directory):
    cap = JYClick()  # 实例化 JYClick 类

    # 获取目录中的所有 .jpg 文件
    jpg_files = [f for f in os.listdir(directory) if f.endswith('.jpg')]

    for jpg_file in jpg_files:
        image_path = os.path.join(directory, jpg_file)
        print(f"Processing {image_path}...")

        data = cap.run(image_path)

        targets = [data[i] for i in range(0, len(data), 2)]
        chars = [data[i] for i in range(1, len(data), 2)]

        # 根据信息排序
        chars.sort(key=lambda x: x[0])  # 按照 x 坐标排序

        for idx, (char_info, target_info) in enumerate(zip(chars, targets)):
            char_coords = utils.yolo_to_coords(char_info, image_path)
            target_coords = utils.yolo_to_coords(target_info, image_path)

            cap.crop_and_save_images(char_coords, target_coords, image_path, idx + 1)

    print("All images processed successfully")


if __name__ == '__main__':
    images_directory = os.path.join(os.path.dirname(__file__))  # 替换为您的图像目录路径
    process_all_images_in_directory(images_directory)

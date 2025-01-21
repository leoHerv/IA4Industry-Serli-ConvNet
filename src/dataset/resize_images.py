from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import os


def process_image(input_path, output_path, size=(256, 256)):
    try:

        with Image.open(input_path) as img:
            img_resized = img.resize(size, Image.LANCZOS)
            img_resized.save(output_path)
    except Exception as e:
        print(f"Error processing {input_path}: {e}")


def resize_images_in_directory(base_input_dir, base_output_dir, size=(256, 256), max_workers=8):
    tasks = []

    for root, dirs, files in os.walk(base_input_dir):
        relative_path = os.path.relpath(root, base_input_dir)
        output_dir = os.path.join(base_output_dir, relative_path)

        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                input_path = os.path.join(root, file)
                output_path = os.path.join(output_dir, file)
                tasks.append((input_path, output_path, size))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda task: process_image(*task), tasks)


if __name__ == "__main__":
  DATASET_PATH = "./part000"

  resize_images_in_directory(DATASET_PATH, DATASET_PATH, (224, 224))

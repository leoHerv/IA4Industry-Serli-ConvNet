import numpy as np
import onnxruntime as ort
from PIL import Image
import torch
from torch.utils.data import DataLoader
import torchvision.transforms as T

from src.dataset.dataset import MyDataset

def get_transform():
    transform = T.Compose([
        T.Resize((380, 380)),
        T.ToTensor()
    ])
    return transform


def evaluate(onnx_model_path, dataset):
    session = ort.InferenceSession(onnx_model_path, providers=['CUDAExecutionProvider'])
    
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    data_loader = DataLoader(dataset, batch_size=1, shuffle=False)

    distances = []

    for image, labels in data_loader:
        input_data = image.numpy()

        outputs = session.run([output_name], {input_name: input_data})
        prediction = outputs[0]

        
        pred_lat = prediction[0][0] / 1000.0 + 47.39
        pred_lon = prediction[0][1] / 1000.0 - 1.18
        
        true_lat = labels[0, 0].item() / 1000.0 + 47.39
        true_lon = labels[0, 1].item() / 1000.0 - 1.18

        dist = np.sqrt((pred_lat - true_lat)**2 + (pred_lon - true_lon)**2)
        distances.append(dist)

    avg_distance = float(np.mean(distances))
    return avg_distance


def main():

    transform = get_transform()
    dataset = MyDataset(csv_file='dataset.csv', root_dir='./resizeDataSet', transform=transform)


    avg_dist = evaluate("kart_resnet50.onnx", dataset)
    print(f"Average Euclidean Distance: {avg_dist:.6f}")


if __name__ == "__main__":
    main()

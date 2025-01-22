import argparse
import onnxruntime as ort
from PIL import Image
import torch
import torchvision.transforms as T

def get_transform():
    transform = T.Compose([
        T.Resize((380, 380)),
        T.ToTensor()
    ])
    return transform

def load_image(image_path, transform):
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image)
    # Add a batch dimension since ONNX model expects [batch_size, 3, 224, 224].
    return image_tensor.unsqueeze(0)

def run_inference(onnx_model_path, image_tensor):
    session = ort.InferenceSession(onnx_model_path, providers=['CPUExecutionProvider'])
    
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    input_data = image_tensor.numpy()

    outputs = session.run([output_name], {input_name: input_data})
    return outputs[0]

def main():
    parser = argparse.ArgumentParser(description='Infer coordinates using ONNX model.')
    parser.add_argument('--model', type=str, default='kart_resnet50.onnx',
                        help='Path to the ONNX model file.')
    parser.add_argument('--image', type=str, required=True,
                        help='Path to the input image.')
    args = parser.parse_args()

    transform = get_transform()
    image_tensor = load_image(args.image, transform)

    prediction = run_inference(args.model, image_tensor)


    lat = prediction[0][0] /1000.0 + 47.39
    lon = prediction[0][1] /1000.0 - 1.18

    print("Predicted coordinates:", lat, lon)  # [x, y] for example

if __name__ == '__main__':
    main()

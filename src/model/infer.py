import argparse
import torch
import onnxruntime as ort
from PIL import Image
import torchvision.transforms as T

from src.utils.chrono import Chrono
from src.utils.utils import validate_source

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
    # providers = [("CUDAExecutionProvider", {"device_id": torch.cuda.current_device(),
    #                                         "user_compute_stream": str(torch.cuda.current_stream().cuda_stream)})]
    # sess_options = ort.SessionOptions()
    # session = ort.InferenceSession(onnx_model_path, sess_options=sess_options, providers=providers)
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
    parser.add_argument('--folder', type=str, required=False,
                        help='Path to the folder of images.')
    args = parser.parse_args()

    if args.folder is None:
        transform = get_transform()
        image_tensor = load_image(args.image, transform)

        chrono = Chrono()
        chrono.start()

        prediction = run_inference(args.model, image_tensor)

        time_inference = chrono.stop()

        print(f"Time inference : {time_inference:.5f} seconds")

        lat = prediction[0][0] /1000.0 + 47.39
        lon = prediction[0][1] /1000.0 - 1.18

        print("Predicted coordinates:", lat, lon)  # [x, y] for example

    else:
        time_moy = 0
        files = validate_source(args.folder)
        # print(files)
        point = (0, 0)
        i = 0
        index_moy = 1
        for file in files:

            transform = get_transform()
            image_tensor = load_image(file, transform)

            chrono = Chrono()
            chrono.start()

            prediction = run_inference(args.model, image_tensor)

            time_inference = chrono.stop()

            time_moy += time_inference


            lat = prediction[0][0] / 1000.0 + 47.39
            lon = prediction[0][1] / 1000.0 - 1.18

            i += 1
            point = (point[0] + lat, point[1] + lon)
            if i % index_moy == 0:
                point = (point[0] / index_moy, point[1] / index_moy)
                print(f"({point[0]:.8f}, {point[1]:.8f}),")
                point = (0, 0)


        time_moy /= len(files)

        print(f"Average Time inference : {time_moy:.5f} seconds")


if __name__ == '__main__':
    main()

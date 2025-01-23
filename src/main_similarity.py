# https://github.com/totogot/ImageSimilarity
import os
import image_similarity as imgsim
from dotenv import load_dotenv
load_dotenv()


if __name__ == "__main__":

    ImgSim = imgsim.Img2Vec('resnet50', weights='DEFAULT')
    COMPACTED_DATASET_PATH = os.getenv('COMPACTED_DATASET_PATH')
    TARGET_PATH = os.getenv('TARGET_PATH')

    # Path to the data set
    #ImgSim.embed_dataset(COMPACTED_DATASET_PATH)
    ImgSim.dataset

    # Path to the image to search similarity
    ImgSim.similar_images(TARGET_PATH, COMPACTED_DATASET_PATH, n=5)

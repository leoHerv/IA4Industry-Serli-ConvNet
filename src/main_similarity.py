# https://github.com/totogot/ImageSimilarity

import image_similarity as imgsim

ImgSim = imgsim.Img2Vec('resnet50', weights='DEFAULT')

# Path to the data set
ImgSim.embed_dataset("path")
ImgSim.dataset

# Path to the image to search similarity
ImgSim.similar_images("path to image", n=5)

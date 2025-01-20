# https://github.com/totogot/ImageSimilarity

import image_similarity as imgsim

ImgSim = imgsim.Img2Vec('resnet50', weights='DEFAULT')

# Path to the data set
#ImgSim.embed_dataset("path")
ImgSim.embed_dataset("C:/Users/leooh/Documents/Ecole/Universite/M2/IA4Industry/dataset/test3/")
ImgSim.dataset

# Path to the image to search similarity
# ImgSim.similar_images("path to image", n=5)
ImgSim.similar_images("C:/Users/leooh/Documents/Ecole/Universite/M2/IA4Industry/dataset/part009/frame_9036.png", n=5)
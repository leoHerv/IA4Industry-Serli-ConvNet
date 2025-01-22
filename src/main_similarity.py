# https://github.com/totogot/ImageSimilarity

import image_similarity as imgsim

ImgSim = imgsim.Img2Vec('resnet50', weights='DEFAULT')

# Path to the data set
#ImgSim.embed_dataset("path")
ImgSim.embed_dataset("C:/M2S1/workshop/ai4industry/dataset/Compressed/")
ImgSim.dataset

# Path to the image to search similarity
# ImgSim.similar_images("path to image", n=5)
ImgSim.similar_images("C:/M2S1/workshop/ai4industry/dataset/part000/frame_900.png", n=5)
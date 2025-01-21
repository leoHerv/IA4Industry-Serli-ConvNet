# IA4Industry-Serli-ConvNet

Group : Mazen AL NATOUR, Tom CAILLAUD, Mohamed FADLI, Léo HERVOUET and Edgar PAVIOT.

## Install 

Run the command `pip install -r requirements.txt` to install all the packages needed for this project. 

Run the command `pip freeze > requirements.txt` to get this file. 

## Use 

Create a `.env` with the `.envExemple`

```
DATASET_PATH= the path to the data set to compress  
COMPACTED_DATASET_PATH= the path to the data set to see similarities  
TARGET_PATH= the path of the image to search similarities   
```

Run the `main_similarity.py`

## What we have done

- Creation of a lighter dataset for model training
- Beginning of the creation of a visualization to display GPS points on the map (study of the existing)
- Definition of our model's architecture
- Research on the loss function that can be used for training our model (triplet loss, metric loss)


For now, we have a prototype that works but uses a lot of RAM, which prevents us from loading many images, and as a result, 
the output is not very accurate.  

Files:
- datasetcreate.py: creates a small dataset of images for testing
- image_similarity.py: allows the use of a convolutional model to find the similarity between an image and a set of images
- main_similarity.py: the main file to launch the search for images similar to a given image
- compression.py and CompressRes.py: for image compression
- /dataset: for dataset creation
- kartModel.py: Mazen experimentation



# Credits

We used the code of totogot.
Repo here : https://github.com/totogot/ImageSimilarity

For the triplet loss : 
https://github.com/KevinMusgrave/pytorch-metric-learning/blob/master/examples/README.md


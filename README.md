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

Run `kart_model.py` to create the model
Run `infer.py` to use the model 

## What we have done

L'approche que nous avons est d'utiliser un modèle qui permet de transformer nos images en vecteurs descripteurs.
Avec ces vecteurs descripteurs, nous pouvons calculer la distance entre les images, ce qui nous permet de trouver l'image 
la plus proche et donc de déterminer notre point GPS en fonction de cette image dont nous connaissons la position.

La première approche était de calculer tous les vecteurs descripteurs de toutes nos images, puis de les comparer à une 
nouvelle image pour trouver la plus proche et donc la position la plus proche. Mais le problème avec cette méthode était 
que les vecteurs descripteurs étaient trop grands et prenaient trop de mémoire (130 vecteurs max avec 16 Go de RAM).

Nous avons donc décidé d'utiliser un modèle capable de prédire une position sur la piste en fonction d'un vecteur descripteur.
L'idée derrière cela est de faire apprendre au modèle la similarité entre les vecteurs et leurs positions sur la piste.
Cette approche nous permet de compresser les données tout en calculant la position en fonction de nos données et non en 
fonction de la seule position d'une image que nous connaissons.

Pour créer ces vecteurs, nous utilisons un modèle pré-entraîné CNN qui est EfficientNet B4 (de Google, voir les performances :
https://github.com/lukemelas/EfficientNet-PyTorch).


En plus de création du modèle, nous avons fait un programme capable de prendre un fichier .json avec les positions et 
d'afficher ces positions sur la map du circuit. Ce programme se trouve sur la branche `print-track`.


Files:
- /dataset: for dataset creation
- /model: for the creation and use of the model
- rest of the files old tests

### How to prepare the dataset
ensure the .env file is correctly filled with the paths to the dataset and the compacted dataset


then run the command `python resize_images.py` to resize the images to 224x224, but before ensure you update the DATASET_PATH

then run the command `python create_labels.py` to create the labels for the dataset, but before ensure you update the dir_path


## What we have todo 

Maintenant que nous avons le modèle, le but est de le rendre encore meilleur pour améliorer la précision de la position.
Nous devons aussi relier le programme qui calcule les positions et le programme qui les affiche.

## Credits

We used the code of totogot.
Repo here : https://github.com/totogot/ImageSimilarity

For the triplet loss : 
https://github.com/KevinMusgrave/pytorch-metric-learning/blob/master/examples/README.md

To extract images from a .mp4 : https://github.com/Serli/gokart
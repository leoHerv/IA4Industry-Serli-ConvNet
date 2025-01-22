import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


class ImageCompressor:
    def __init__(self, base_directory, quality=85, target_size=(224, 224)):
        """
        Initialise le compresseur d'images.

        :param base_directory: Répertoire de base contenant les sous-dossiers à traiter.
        :param quality: Qualité de compression (entre 1 et 100).
        :param target_size: Taille maximale pour le redimensionnement des images (largeur, hauteur).
        """
        self.base_directory = base_directory
        self.quality = quality
        self.target_size = target_size

    def resize_image(self, img):
        """
        Redimensionne une image selon la taille cible.

        :param img: Instance PIL.Image.
        :return: Image redimensionnée.
        """
        img.thumbnail(self.target_size)
        return img

    def compress_image(self, img, output_path):
        """
        Compresse une image et la sauvegarde dans le chemin spécifié.

        :param img: Instance PIL.Image.
        :param output_path: Chemin de l'image de sortie.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, optimize=True, quality=self.quality)

    def process_image(self, input_path, output_path):
        """
        Redimensionne et compresse une image PNG.

        :param input_path: Chemin de l'image source.
        :param output_path: Chemin de l'image de sortie.
        """
        try:
            with Image.open(input_path) as img:
                img = self.resize_image(img)  # Redimensionner
                self.compress_image(img, output_path)  # Compresser
                print(f"Image traitée : {output_path}")
        except Exception as e:
            print(f"Erreur pour {input_path} : {e}")

    def process_folder(self, input_folder, output_folder):
        """
        Traite un dossier en compressant et redimensionnant toutes les images PNG.

        :param input_folder: Chemin du dossier source.
        :param output_folder: Chemin du dossier de sortie.
        """
        for root, _, files in os.walk(input_folder):
            for file in files:
                if file.endswith(".png"):
                    input_path = os.path.join(root, file)
                    output_path = os.path.join(output_folder, os.path.relpath(input_path, input_folder))
                    self.process_image(input_path, output_path)

    def process_all_folders(self):
        """
        Traite tous les sous-dossiers "PartXXX" du répertoire de base.
        """
        folders = [
            (os.path.join(self.base_directory, f"Part{i:03d}"),
             os.path.join(self.base_directory, f"Compressed_Part{i:03d}"))
            for i in range(15)
            if os.path.exists(os.path.join(self.base_directory, f"Part{i:03d}"))
        ]

        if not folders:
            print("Aucun dossier valide trouvé. Vérifiez le chemin.")
            return

        print(f"{len(folders)} dossiers trouvés. Compression en cours...")
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.process_folder, input_folder, output_folder)
                for input_folder, output_folder in folders
            ]

        print("Traitement terminé !")


# Exemple d'utilisation
def main():
    base_directory = input("Entrez le chemin du dossier contenant les sous-dossiers Part000 à Part014 : ").strip()
    quality = int(input("Entrez le niveau de qualité de compression (50-100, recommandé : 85) : ").strip())
    target_size = (224, 224)  # Taille cible par défaut

    # Initialiser et exécuter le compresseur
    compressor = ImageCompressor(base_directory, quality, target_size)
    compressor.process_all_folders()



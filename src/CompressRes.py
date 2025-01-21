import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# Fonction pour redimensionner et compresser une image
def process_image(input_path, output_path, size):
    try:
        with Image.open(input_path) as img:
            img.thumbnail(size)  # Redimensionner
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, optimize=True, quality=85)  # Compresser
            print(f"Image traitée : {output_path}")
    except Exception as e:
        print(f"Erreur pour {input_path} : {e}")

# Fonction pour traiter un dossier
def process_folder(input_folder, output_folder, size):
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".png"):
                input_path = os.path.join(root, file)
                output_path = os.path.join(output_folder, os.path.relpath(input_path, input_folder))
                process_image(input_path, output_path, size)

# Fonction principale
def main():
    # Chemin vers le répertoire contenant les sous-dossiers
    base_directory = input("Entrez le chemin du dossier contenant les sous-dossiers Part000 à Part014 : ").strip()
    target_size = (224, 224)  # Largeur et hauteur maximum

    # Préparer les dossiers à traiter
    folders = [(os.path.join(base_directory, f"Part{i:03d}"),
                os.path.join(base_directory, f"Compressed_Part{i:03d}"))
               for i in range(15)
               if os.path.exists(os.path.join(base_directory, f"Part{i:03d}"))]

    if not folders:
        print("Aucun dossier valide trouvé. Vérifiez le chemin.")
        return

    # Utiliser ThreadPoolExecutor pour exécuter en parallèle
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_folder, input_folder, output_folder, target_size)
            for input_folder, output_folder in folders
        ]

    print("Traitement terminé !")

# Exécution
if __name__ == "__main__":
    main()

import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


# Fonction pour optimiser et compresser un PNG
def compress_png(input_path, output_folder, quality=85):
    try:
        # Préparer le chemin de sortie
        output_path = os.path.join(output_folder, os.path.basename(input_path))
        os.makedirs(output_folder, exist_ok=True)

        # Ouvrir l'image
        with Image.open(input_path) as img:
            # Convertir en mode "P" (palette de couleurs) pour réduire la taille
            img = img.convert("P", palette=Image.ADAPTIVE)

            # Sauvegarder avec compression et optimisation
            img.save(output_path, optimize=True, quality=quality)
            print(f"Image compressée : {output_path}")
    except Exception as e:
        print(f"Erreur pour {input_path} : {e}")


# Fonction pour traiter tous les dossiers en parallèle
def process_all_folders(base_directory, output_folder, quality=85):
    image_paths = []

    # Collecter les chemins des fichiers PNG dans les sous-dossiers
    for i in range(15):  # Dossiers Part000 à Part014
        input_folder = os.path.join(base_directory, f"Part{i:03d}")
        if os.path.exists(input_folder):
            for root, _, files in os.walk(input_folder):
                for file in files:
                    if file.endswith(".png"):
                        image_paths.append(os.path.join(root, file))
        else:
            print(f"Dossier introuvable : {input_folder}")

    # Traiter les images en parallèle
    print(f"{len(image_paths)} images trouvées. Compression en cours...")
    with ThreadPoolExecutor() as executor:
        executor.map(lambda path: compress_png(path, output_folder, quality), image_paths)


# Fonction principale
def main():
    # Chemin vers le répertoire parent contenant les dossiers Part000 à Part014
    base_directory = input("Entrez le chemin du dossier contenant les sous-dossiers Part000 à Part014 : ").strip()

    # Chemin du dossier de sortie unique
    output_folder = input("Entrez le chemin du dossier où sauvegarder les images compressées : ").strip()

    # Qualité de compression
    quality = int(input("Entrez le niveau de qualité de compression (50-100, recommandé : 85) : ").strip())

    # Traiter les dossiers
    process_all_folders(base_directory, output_folder, quality)

    print("Compression terminée. Les fichiers optimisés sont dans le dossier unique.")


# Exécution
if __name__ == "__main__":
    main()

import os
import shutil
import re
from dotenv import load_dotenv
load_dotenv()
DATASET_PATH = os.getenv('DATASET_PATH')

def copy_images_by_interval(source_dirs, dest_dir, start, end, step):
    """
    Copie les images des dossiers sources dans un dossier de destination en respectant un intervalle.

    :param source_dirs: Liste des chemins des dossiers sources.
    :param dest_dir: Chemin du dossier de destination.
    :param start: Numéro de début de l'intervalle (inclus).
    :param end: Numéro de fin de l'intervalle (inclus).
    :param step: Pas de l'intervalle.
    """
    # Créer le dossier de destination s'il n'existe pas
    os.makedirs(dest_dir, exist_ok=True)

    # Construire le pattern regex pour les fichiers d'images
    pattern = re.compile(r"frame_(\d+)\.png")

    for source_dir in source_dirs:
        if not os.path.isdir(source_dir):
            print(f"Le dossier source {source_dir} n'existe pas. Ignoré.")
            continue

        for filename in os.listdir(source_dir):
            match = pattern.match(filename)
            if match:
                frame_number = int(match.group(1))
                # Vérifier si le numéro de l'image est dans l'intervalle souhaité
                if start <= frame_number <= end and (frame_number - start) % step == 0:
                    src_path = os.path.join(source_dir, filename)
                    dest_path = os.path.join(dest_dir, filename)
                    shutil.copy(src_path, dest_path)
                    print(f"Copié: {src_path} -> {dest_path}")

if __name__ == "__main__":
    source_dirs = [f"{DATASET_PATH}\\part000",
                   f"{DATASET_PATH}\\part001",
                   f"{DATASET_PATH}\\part002",
                   f"{DATASET_PATH}\\part003",
                   f"{DATASET_PATH}\\part004",
                   f"{DATASET_PATH}\\part006",
                   f"{DATASET_PATH}\\part007",
                   f"{DATASET_PATH}\\part008",
                   f"{DATASET_PATH}\\part009",
                   f"{DATASET_PATH}\\part010",
                   f"{DATASET_PATH}\\part011",
                   f"{DATASET_PATH}\\part012",
                   f"{DATASET_PATH}\\part013",
                   f"{DATASET_PATH}\\part014"]

    dest_dir = f"{DATASET_PATH}\\compactedDataSet"  # Dossier de destination

    # Intervalle d'images à copier
    start = 1  # Premier numéro inclus
    end = 10000000  # Dernier numéro inclus
    step = 100  # Intervalle

    copy_images_by_interval(source_dirs, dest_dir, start, end, step)

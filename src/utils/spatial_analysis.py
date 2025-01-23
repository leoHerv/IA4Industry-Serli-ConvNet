import math
from dataclasses import dataclass
from typing import Optional
from src.model.evaluate import evaluate


@dataclass
class GPSCoordinate:
    latitude: float
    longitude: float


def calculate_haversine_distance(coord1: GPSCoordinate, coord2: GPSCoordinate) -> float:
    """
    Calcule la distance entre deux coordonnées GPS en utilisant la formule de Haversine.
    """
    # Conversion des degrés en radians
    lat1_rad = math.radians(coord1.latitude)
    lon1_rad = math.radians(coord1.longitude)
    lat2_rad = math.radians(coord2.latitude)
    lon2_rad = math.radians(coord2.longitude)

    EARTH_RADIUS_M = 6378100  # Rayon terrestre moyen en mètres

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    haversine_term = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )

    return round(2 * EARTH_RADIUS_M * math.asin(math.sqrt(haversine_term)), 3)


def calculate_image_ground_resolution(
        model_path: str,
        dataset: str,
        reference_coord: GPSCoordinate
) -> None:
    """
    Calcule et affiche la résolution spatiale au sol d'une image.
    """
    try:
        characteristic_distance = evaluate(model_path, dataset)
        offset_point = GPSCoordinate(
            latitude=reference_coord.latitude,
            longitude=reference_coord.longitude + characteristic_distance
        )

        ground_distance = calculate_haversine_distance(offset_point, reference_coord)
        print(f"\nRésolution spatiale calculée: {ground_distance} mètres")

    except Exception as e:
        print(f"\nErreur lors du calcul: {str(e)}")


def get_user_input(prompt: str, required: bool = True) -> str:
    """Collecte une entrée utilisateur avec validation basique."""
    while True:
        value = input(prompt).strip()
        if required and not value:
            print("Cette valeur est obligatoire.")
            continue
        return value


def get_gps_coordinates_from_user() -> GPSCoordinate:
    """
    Demande à l'utilisateur de saisir les coordonnées GPS de référence.
    """
    print("\nSaisie des coordonnées GPS de référence :")
    while True:
        try:
            latitude = float(get_user_input("Latitude (en degrés décimaux, ex: 48.858370): "))
            longitude = float(get_user_input("Longitude (en degrés décimaux, ex: 2.294481): "))

            # Validation des valeurs GPS
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                print("Erreur : Latitude doit être entre -90 et 90, et longitude entre -180 et 180.")
                continue

            return GPSCoordinate(latitude=latitude, longitude=longitude)

        except ValueError:
            print("Erreur : Veuillez entrer des nombres valides.")

if __name__ == "__main__":
    print("\n=== Configuration de l'analyse ===")

    # Collecte des entrées utilisateur
    the_model_path = get_user_input("Chemin vers le modèle ONNX: ")
    dataset_path = get_user_input("Chemin vers le dataset d'évaluation: ")

    # Récupération des coordonnées GPS de référence
    reference_point = get_gps_coordinates_from_user()

    # Lancement du calcul
    calculate_image_ground_resolution(
        model_path=the_model_path,
        dataset=dataset_path,
        reference_coord=reference_point
    )
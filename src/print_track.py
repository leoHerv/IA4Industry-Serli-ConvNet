import json
import cv2
import matplotlib.pyplot as plt


def pos_to_xy(bounds, lat, lon, limits, tile_size=512):
    """
    Convert latitude and longitude into x, y pixel coordinates on a map.
    """
    xratio = (lon - limits['p1']['longitude']) / (limits['p2']['longitude'] - limits['p1']['longitude'])
    yratio = 1.0 - ((lat - limits['p1']['latitude']) / (limits['p2']['latitude'] - limits['p1']['latitude']))

    x = int((bounds[2] - bounds[0] - tile_size) * xratio + 0.5) + (tile_size // 2) + 64
    y = int((bounds[3] - bounds[1] - tile_size) * yratio + 0.5) + (tile_size // 2) + 64

    return x, y


# Charger le fichier JSON contenant les limites et les données des circuits
with open('../data/theworld.json', 'r') as file:
    circuit_data = json.load(file)

# Sélectionner le circuit "Ancenis"
circuit_name = "Ancenis"
selected_circuit = next(track for track in circuit_data["tracks"] if track["name"] == circuit_name)

# Récupérer les limites géographiques
limits = {
    "p1": {"latitude": selected_circuit["limits"]["p1"]["lat"], "longitude": selected_circuit["limits"]["p1"]["lon"]},
    "p2": {"latitude": selected_circuit["limits"]["p2"]["lat"], "longitude": selected_circuit["limits"]["p2"]["lon"]}
}

# Dimensions de l'image satellite
image_width, image_height = 2393, 2801
bounds = (0, 0, image_width, image_height)

# Exemple de données des frames (en JSON ou fichier)
frame_data = [
    {"lat": 47.3966379, "lon": -1.1855914, "alt": 67.966, "spd": 0.022, "accuracy": 185},
    {"lat": 47.3962329, "lon": -1.1846790, "alt": 67.950, "spd": 0.025, "accuracy": 180},
    {"lat": 47.3958000, "lon": -1.1850000, "alt": 67.930, "spd": 0.030, "accuracy": 150}
]

# Convertir les positions GPS en coordonnées pixels
pixel_positions = [
    pos_to_xy(bounds, frame["lat"], frame["lon"], limits) for frame in frame_data if frame["accuracy"] <= 200
]

# Charger l'image satellite
satellite_img = cv2.imread('../data/Ancenis.png')
satellite_img = cv2.cvtColor(satellite_img, cv2.COLOR_BGR2RGB)

# Traçage de la trajectoire
plt.figure(figsize=(12, 12))
plt.imshow(satellite_img)

# Dessiner les points et la trajectoire
for point in pixel_positions:
    plt.plot(point[0], point[1], 'ro')  # Points rouges
#plt.plot(*zip(*pixel_positions), 'b-', linewidth=2, label="Trajectoire")  # Ligne bleue

# Ajouter le point de départ
start_point = pos_to_xy(
    bounds,
    selected_circuit["start"]["p1"]["lat"],
    selected_circuit["start"]["p1"]["lon"],
    limits
)
plt.plot(start_point[0], start_point[1], 'go', markersize=10, label="Départ")  # Point vert

# Configurer l'affichage
plt.title(f"Trajectoire du kart sur le circuit '{circuit_name}'")
plt.axis('off')
plt.legend()
plt.show()

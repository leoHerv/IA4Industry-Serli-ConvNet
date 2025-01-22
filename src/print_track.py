import json
import cv2
import matplotlib.pyplot as plt
from PIL import Image


def pos_to_xy(bounds, lat, lon, limits, tile_size=512):
    """
    Convert latitude and longitude into x, y pixel coordinates on a map.
    """
    xratio = (lon - limits['p1']['longitude']) / (limits['p2']['longitude'] - limits['p1']['longitude'])
    yratio = 1.0 - ((lat - limits['p1']['latitude']) / (limits['p2']['latitude'] - limits['p1']['latitude']))

    x = int((bounds[2] - bounds[0] - tile_size) * xratio + 0.5) + (tile_size // 2) + 64
    y = int((bounds[3] - bounds[1] - tile_size) * yratio + 0.5) + (tile_size // 2) + 64

    return x, y

def draw_position(circuit_name, lat, lon):
    # Load limits and circuit datas json file
    with open('../data/theworld.json', 'r') as file:
        circuit_data = json.load(file)

    selected_circuit = next(track for track in circuit_data["tracks"] if track["name"] == circuit_name)

    # Get real gps coordinates that represents circuit limits
    limits = {
        "p1": {"latitude": selected_circuit["limits"]["p1"]["lat"], "longitude": selected_circuit["limits"]["p1"]["lon"]},
        "p2": {"latitude": selected_circuit["limits"]["p2"]["lat"], "longitude": selected_circuit["limits"]["p2"]["lon"]}
    }

    image_path = "../data/" + circuit_name + ".png"
    image = Image.open(image_path)

    image_width, image_height = image.size
    bounds = (0, 0, image_width, image_height)

    pos_x, pos_y = pos_to_xy(bounds, lat, lon, limits)

    # Load satellite image
    satellite_img = cv2.imread(image_path)
    satellite_img = cv2.cvtColor(satellite_img, cv2.COLOR_BGR2RGB)

    # Plot current position
    plt.figure(figsize=(12, 12))
    plt.imshow(satellite_img)
    plt.plot(pos_x, pos_y, 'ro')

    # Plot start position
    # start_point = pos_to_xy(
    #     bounds,
    #     selected_circuit["start"]["p1"]["lat"],
    #     selected_circuit["start"]["p1"]["lon"],
    #     limits
    # )
    # plt.plot(start_point[0], start_point[1], 'go', markersize=10, label="Départ")

    # Configurer l'affichage
    plt.title(f"Position du kart sur le circuit '{circuit_name}'")
    plt.axis('off')
    plt.legend()
    plt.show()

draw_position("Ancenis", 47.3962329, -1.1846790)
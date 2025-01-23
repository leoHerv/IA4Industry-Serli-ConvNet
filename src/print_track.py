import pygame
import json
import os
import math

import json
import os


def load_coordinates(dataset_path, output_file):
    """
    Load coordinates from JSON files in the dataset folder and save them to a JSON file.

    :param dataset_path: Path to the dataset folder containing partXXX folders.
    :param output_file: Path to the output JSON file where coordinates will be saved.
    :return: List of tuples (lat, lon).
    """
    coordinates = []
    part_folders = sorted(os.listdir(dataset_path))
    total_parts = len(part_folders)

    for part_idx, part_folder in enumerate(part_folders):
        part_path = os.path.join(dataset_path, part_folder)
        if os.path.isdir(part_path):
            frame_files = sorted(os.listdir(part_path))
            total_frames = len(frame_files)

            for frame_idx, frame_file in enumerate(frame_files):
                frame_path = os.path.join(part_path, frame_file)
                if frame_path.endswith('.json'):
                    with open(frame_path, 'r') as file:
                        frame_data = json.load(file)
                        coordinates.append({"lat": frame_data["lat"], "lon": frame_data["lon"]})

                # Print progress
                print(
                    f"Loading {part_folder}: Frame {frame_idx + 1}/{total_frames} "
                    f"({part_idx + 1}/{total_parts} parts complete)"
                )

    # Save coordinates to a JSON file
    with open(output_file, 'w') as outfile:
        json.dump(coordinates, outfile, indent=4)
        print(f"Coordinates saved to {output_file}")

    return coordinates


# Example usage
# dataset_path = "C:/M2S1/workshop/ai4industry/dataset/"  # Path to the dataset folder
# output_file = "coordinates.json"  # Path to the output file
# coordinates = load_coordinates(dataset_path, output_file)

def load_coordinates_from_json(file_path):
    """
    Load coordinates from a JSON file.

    :param file_path: Path to the JSON file containing the coordinates.
    :return: List of tuples (lat, lon).
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
        coordinates = [(entry["lat"], entry["lon"]) for entry in data]
    print(f"Loaded {len(coordinates)} coordinates from {file_path}")
    return coordinates

def load_coordinates(dataset_path):
    """
    Load coordinates from JSON files in the dataset folder.

    :param dataset_path: Path to the dataset folder containing partXXX folders
    :return: List of tuples (lat, lon)
    """
    coordinates = []
    part_folders = sorted(os.listdir(dataset_path))
    total_parts = len(part_folders)

    for part_idx, part_folder in enumerate(part_folders):
        part_path = os.path.join(dataset_path, part_folder)
        if os.path.isdir(part_path):
            frame_files = sorted(os.listdir(part_path))
            total_frames = len(frame_files)

            for frame_idx, frame_file in enumerate(frame_files):
                frame_path = os.path.join(part_path, frame_file)
                if frame_path.endswith('.json'):
                    with open(frame_path, 'r') as file:
                        frame_data = json.load(file)
                        coordinates.append((frame_data["lat"], frame_data["lon"]))

                # Print progress
                print(
                    f"Loading {part_folder}: Frame {frame_idx + 1}/{total_frames} "
                    f"({part_idx + 1}/{total_parts} parts complete)"
                )
    return coordinates

def distance(p1, p2):
    """Distance euclidienne simple en 2D."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def pos_to_xy(bounds, lat, lon, limits, tile_size=512):
    """
    Convert latitude and longitude into x, y pixel coordinates on a map.
    """
    xratio = (lon - limits['p1']['longitude']) / (limits['p2']['longitude'] - limits['p1']['longitude'])
    yratio = 1.0 - ((lat - limits['p1']['latitude']) / (limits['p2']['latitude'] - limits['p1']['latitude']))

    x = int((bounds[2] - bounds[0] - tile_size) * xratio + 0.5) + (tile_size // 2) + 64
    y = int((bounds[3] - bounds[1] - tile_size) * yratio + 0.5) + (tile_size // 2) + 64

    return x, y




def draw_positions_progressive(circuit_name, coordinates):
    """
    Dessine progressivement les positions (latitude, longitude) sur un circuit,
    avec :
      - Zoom / drag (panning) de l'image
      - Lignes entre les points
      - Couleur qui change à chaque tour (lap)
      - Boutons (Reset, Start, FPS Up/Down, Filter)
    """

    pygame.init()
    clock = pygame.time.Clock()
    try:
        # --- 1) Chargement des données du circuit ---
        with open('../data/theworld.json', 'r') as file:
            circuit_data = json.load(file)

        selected_circuit = next(track for track in circuit_data["tracks"]
                                if track["name"] == circuit_name)

        # Limites géographiques
        limits = {
            "p1": {
                "latitude": selected_circuit["limits"]["p1"]["lat"],
                "longitude": selected_circuit["limits"]["p1"]["lon"]
            },
            "p2": {
                "latitude": selected_circuit["limits"]["p2"]["lat"],
                "longitude": selected_circuit["limits"]["p2"]["lon"]
            }
        }

        # --- 2) Chargement de l'image satellite originale ---
        image_path = "../data/" + circuit_name + ".png"
        satellite_image_original = pygame.image.load(image_path)
        image_width, image_height = satellite_image_original.get_width(), satellite_image_original.get_height()

        # Définition de la bounding box de l'image
        bounds = (0, 0, image_width, image_height)

        # --- 3) Conversion des coordonnées GPS -> pixels (image d'origine) ---
        positions = [pos_to_xy(bounds, lat, lon, limits) for lat, lon in coordinates]
        start_position = pos_to_xy(
            bounds,
            selected_circuit["start"]["p1"]["lat"],
            selected_circuit["start"]["p1"]["lon"],
            limits
        )

        # --- 4) Configuration de la fenêtre Pygame ---
        menu_width = 200
        screen_width, screen_height = 1280, 720
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f"Circuit '{circuit_name}'")

        font = pygame.font.Font(None, 36)

        # --- 5) Création des boutons (zone menu à droite) ---
        button_reset = pygame.Rect(screen_width - menu_width + 20, 50, 150, 40)
        button_start = pygame.Rect(screen_width - menu_width + 20, 100, 150, 40)
        button_fps_up = pygame.Rect(screen_width - menu_width + 20, 160, 70, 40)
        button_fps_down = pygame.Rect(screen_width - menu_width + 100, 160, 70, 40)
        button_filter = pygame.Rect(screen_width - menu_width + 20, 220, 150, 40)

        # --- 6) Couleurs de tour (laps) ---
        lap_colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 128, 128), (128, 0, 0)
        ]

        # --- 7) Variables d'état ---
        # Calcul d'un zoom initial pour que l'image tienne dans l'écran (en laissant la place au menu)
        initial_zoom = min((screen_width - menu_width) / image_width, screen_height / image_height, 1.0)
        zoom_factor = initial_zoom

        offset_x, offset_y = 0, 0  # décalage de l'image
        is_dragging = False
        drag_start = (0, 0)

        running = True
        started = False

        # `speed` = nombre de points qu'on ajoute à la liste par frame
        speed = 1
        current_index = 0

        lap_count = 0
        current_color = lap_colors[lap_count % len(lap_colors)]

        # Liste de tous les points déjà "défilés" + leur couleur.
        # Format : [(x, y, color), (x2, y2, color2), ...]
        drawn_positions = []

        # Gestion du FPS. On fixe 25 par défaut. min=25, max=144
        current_fps = 5

        # Filtre (exemple) : s'il est actif, on peut imaginer filtrer certains points
        filter_active = False

        # --- 8) Boucle principale ---
        while running:
            clock.tick(current_fps)  # limite l’affichage à current_fps images par seconde

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # clic gauche
                        if button_reset.collidepoint(event.pos):
                            # --- Reset ---
                            started = False
                            current_index = 0
                            lap_count = 0
                            current_color = lap_colors[0]
                            drawn_positions.clear()

                        elif button_start.collidepoint(event.pos):
                            # --- Start ---
                            started = True

                        elif button_fps_up.collidepoint(event.pos):
                            # --- Augmenter FPS ---
                            current_fps = min(current_fps + 5, 144)

                        elif button_fps_down.collidepoint(event.pos):
                            # --- Diminuer FPS ---
                            current_fps = max(current_fps - 5, 25)

                        elif button_filter.collidepoint(event.pos):
                            # --- Toggle Filter ---
                            filter_active = not filter_active

                        else:
                            # Démarrage du "drag" pour déplacer la vue
                            is_dragging = True
                            drag_start = event.pos

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        is_dragging = False

                elif event.type == pygame.MOUSEMOTION and is_dragging:
                    dx, dy = event.pos[0] - drag_start[0], event.pos[1] - drag_start[1]
                    offset_x += dx
                    offset_y += dy
                    drag_start = event.pos

                elif event.type == pygame.MOUSEWHEEL and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    # Zoom/dézoom autour de la souris avec CTRL + molette
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    old_zoom = zoom_factor
                    # event.y > 0 => molette vers l'avant => zoom in
                    zoom_factor += 0.1 if event.y > 0 else -0.1
                    zoom_factor = max(0.2, min(5.0, zoom_factor))  # limite de zoom

                    # On recalcule l'offset pour que le point sous la souris reste au même endroit
                    scale = zoom_factor / old_zoom
                    offset_x = mouse_x - scale * (mouse_x - offset_x)
                    offset_y = mouse_y - scale * (mouse_y - offset_y)

            # --- 9) Gestion de l'affichage ---

            # 9.1) Fond
            screen.fill((0, 0, 0))

            # 9.2) Image (zoomée + décalée)
            scaled_w = int(image_width * zoom_factor)
            scaled_h = int(image_height * zoom_factor)
            scaled_image = pygame.transform.scale(satellite_image_original, (scaled_w, scaled_h))
            screen.blit(scaled_image, (offset_x, offset_y))

            # 9.3) Menu à droite
            pygame.draw.rect(screen, (50, 50, 50), (screen_width - menu_width, 0, menu_width, screen_height))

            # Boutons
            pygame.draw.rect(screen, (255, 0, 0), button_reset)
            pygame.draw.rect(screen, (0, 255, 0), button_start)
            pygame.draw.rect(screen, (128, 128, 128), button_fps_up)
            pygame.draw.rect(screen, (128, 128, 128), button_fps_down)
            pygame.draw.rect(screen, (0, 128, 255), button_filter)

            # Texte des boutons
            reset_text = font.render("Reset", True, (255, 255, 255))
            start_text = font.render("Start", True, (255, 255, 255))
            up_text = font.render("+FPS", True, (0, 0, 0))
            down_text = font.render("-FPS", True, (0, 0, 0))
            filter_text = font.render("Filter", True, (255, 255, 255))

            screen.blit(reset_text, (button_reset.x + 20, button_reset.y + 5))
            screen.blit(start_text, (button_start.x + 20, button_start.y + 5))
            screen.blit(up_text, (button_fps_up.x + 10, button_fps_up.y + 5))
            screen.blit(down_text, (button_fps_down.x + 5, button_fps_down.y + 5))
            screen.blit(filter_text, (button_filter.x + 20, button_filter.y + 5))

            # Affichage du FPS actuel
            fps_info = font.render(f"FPS: {current_fps}", True, (255, 255, 255))
            screen.blit(fps_info, (screen_width - menu_width + 20, 280))

            # Indication si le filtre est actif ou non
            if filter_active:
                filter_status = font.render("Filter ON", True, (255, 255, 0))
            else:
                filter_status = font.render("Filter OFF", True, (200, 200, 200))
            screen.blit(filter_status, (screen_width - menu_width + 20, 320))

            # 9.4) Mise à jour de la liste drawn_positions si on est en mode "Start"
            if started and current_index < len(positions):
                # On ajoute "speed" points par frame
                for i in range(current_index, min(current_index + speed, len(positions))):
                    (pos_x, pos_y) = positions[i]

                    # Vérification du tour (lap) dans l'espace "original" (sans zoom)
                    # On considère qu'on incrémente si on repasse sur la zone de départ
                    if distance((pos_x, pos_y), start_position) < 30 and i > 0:
                        lap_count += 1
                        current_color = lap_colors[lap_count % len(lap_colors)]

                    # Exemple de "filtre" : si filter_active, on pourrait ignorer certains points
                    # Ici, simple exemple : on ignore un point sur deux si filter_active est True
                    if filter_active:
                        if i % 2 == 0:
                            continue

                    # On ajoute le point avec la couleur actuelle
                    drawn_positions.append((pos_x, pos_y, current_color))

                current_index += speed

            # 9.5) Dessin de tous les points (et des lignes) déjà « défilés »
            for i, (px, py, c) in enumerate(drawn_positions):
                # Application du zoom et de l'offset
                adjx = int(px * zoom_factor + offset_x)
                adjy = int(py * zoom_factor + offset_y)

                # On dessine un petit cercle
                pygame.draw.circle(screen, c, (adjx, adjy), 4)

                # On relie au point précédent par une ligne
                if i > 0:
                    px_prev, py_prev, c_prev = drawn_positions[i - 1]
                    adjx_prev = int(px_prev * zoom_factor + offset_x)
                    adjy_prev = int(py_prev * zoom_factor + offset_y)
                    # Ici on choisit la couleur du 2e point ou la moyenne, etc.
                    pygame.draw.line(screen, c, (adjx_prev, adjy_prev), (adjx, adjy), 2)

            # 9.6) Mise à jour de l'affichage
            pygame.display.flip()

        # Fin de la boucle
    finally:
        pygame.quit()


# Load coordinates from the dataset
# dataset_path = "C:/M2S1/workshop/ai4industry/dataset/"  # Path to the dataset folder
# coordinates = load_coordinates(dataset_path)

# Load coordinates from the saved JSON file
coordinates_file = "../data/coordinates.json"  # Path to the saved JSON file
coordinates = load_coordinates_from_json(coordinates_file)



# Call the function to draw positions
draw_positions_progressive("Ancenis", coor)

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
    Affiche progressivement les coordonnées GPS sur un circuit avec Pygame.
    Inclus :
      - Découpage en tours (laps)
      - Couleurs distinctes pour chaque tour
      - Zoom & Pan
      - Boutons :
        * Start / Reset
        * Lines ON/OFF
        * FPS +/- (25 à 144)
        * Tours complets ON/OFF (n'affiche pas le dernier tour en cours)
    """
    pygame.init()
    clock = pygame.time.Clock()

    try:
        # --- 1) Lecture des données du circuit ---
        with open('../data/theworld.json', 'r') as f:
            circuit_data = json.load(f)

        selected_circuit = next(track for track in circuit_data["tracks"] if track["name"] == circuit_name)

        limits = {
            "p1": {
                "latitude":  selected_circuit["limits"]["p1"]["lat"],
                "longitude": selected_circuit["limits"]["p1"]["lon"]
            },
            "p2": {
                "latitude":  selected_circuit["limits"]["p2"]["lat"],
                "longitude": selected_circuit["limits"]["p2"]["lon"]
            }
        }

        # --- 2) Chargement de l'image ---
        image_path = "../data/" + circuit_name + ".png"
        satellite_image_original = pygame.image.load(image_path)
        image_width, image_height = satellite_image_original.get_width(), satellite_image_original.get_height()

        bounds = (0, 0, image_width, image_height)

        # --- 3) Conversion GPS -> pixels ---
        positions = []
        for (lat, lon) in coordinates:
            px, py = pos_to_xy(bounds, lat, lon, limits, tile_size=512)
            positions.append((px, py))

        # Détection du point de départ
        start_position = pos_to_xy(bounds,
                                   selected_circuit["start"]["p1"]["lat"],
                                   selected_circuit["start"]["p1"]["lon"],
                                   limits,
                                   tile_size=512)

        # --- 4) Fenêtre Pygame ---
        menu_width = 200
        screen_width, screen_height = 1280, 720
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f"Circuit '{circuit_name}'")

        font = pygame.font.Font(None, 32)

        # --- 5) Boutons ---
        button_reset         = pygame.Rect(screen_width - menu_width + 20,  50, 150, 40)
        button_start         = pygame.Rect(screen_width - menu_width + 20, 100, 150, 40)
        button_toggle_lines  = pygame.Rect(screen_width - menu_width + 20, 160, 150, 40)
        button_fps_up        = pygame.Rect(screen_width - menu_width + 20, 220, 70, 40)
        button_fps_down      = pygame.Rect(screen_width - menu_width + 110, 220, 60, 40)
        button_toggle_laps   = pygame.Rect(screen_width - menu_width + 20, 280, 150, 40)

        # --- 6) Gestion des tours ---
        # laps_positions[i] = liste des points du tour i
        laps_positions = [[]]
        current_lap_index = 0

        lap_colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255),
            (128, 128, 128),
            (128, 0, 0)
        ]
        current_color = lap_colors[current_lap_index % len(lap_colors)]

        # **Hystérésis** pour éviter de repasser plusieurs fois la ligne de départ
        in_start_zone = False  # True si on est dans la zone de départ

        # --- 7) Variables d'état ---
        running = True
        started = False
        current_index = 0
        speed = 1  # points ajoutés par frame

        # Lignes ON/OFF
        draw_lines = True

        # FPS (borné entre 25 et 144)
        current_fps = 30

        # Affichage tours complets uniquement ?
        show_completed_laps_only = False

        # Zoom initial
        initial_zoom = min((screen_width - menu_width) / image_width,
                           screen_height / image_height,
                           1.0)
        zoom_factor = initial_zoom
        offset_x, offset_y = 0, 0
        is_dragging = False
        drag_start = (0, 0)

        # --- 8) Boucle principale ---
        while running:
            clock.tick(current_fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if button_reset.collidepoint(event.pos):
                            # Reset
                            started = False
                            current_index = 0
                            laps_positions = [[]]
                            current_lap_index = 0
                            current_color = lap_colors[0]
                            in_start_zone = False

                        elif button_start.collidepoint(event.pos):
                            # Start
                            started = True

                        elif button_toggle_lines.collidepoint(event.pos):
                            # ON/OFF des lignes
                            draw_lines = not draw_lines

                        elif button_fps_up.collidepoint(event.pos):
                            # FPS +
                            current_fps = min(current_fps + 5, 144)

                        elif button_fps_down.collidepoint(event.pos):
                            # FPS -
                            current_fps = max(current_fps - 5, 25)

                        elif button_toggle_laps.collidepoint(event.pos):
                            # Affichage seulement des tours complets
                            show_completed_laps_only = not show_completed_laps_only

                        else:
                            # Drag start
                            is_dragging = True
                            drag_start = event.pos

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        is_dragging = False

                elif event.type == pygame.MOUSEMOTION and is_dragging:
                    dx = event.pos[0] - drag_start[0]
                    dy = event.pos[1] - drag_start[1]
                    offset_x += dx
                    offset_y += dy
                    drag_start = event.pos

                elif event.type == pygame.MOUSEWHEEL and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    # Zoom autour de la souris
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    old_zoom = zoom_factor
                    zoom_factor += 0.1 if event.y > 0 else -0.1
                    zoom_factor = max(0.2, min(5.0, zoom_factor))
                    scale = zoom_factor / old_zoom
                    offset_x = mouse_x - scale * (mouse_x - offset_x)
                    offset_y = mouse_y - scale * (mouse_y - offset_y)

            # --- 9) Ajout progressif des points ---
            if started and current_index < len(positions):
                for i in range(current_index, min(current_index + speed, len(positions))):
                    (px, py) = positions[i]

                    # Calcul de la distance au point de départ
                    dist_to_start = distance((px, py), start_position)

                    # Système d'hystérésis :
                    # Si on n'était pas dans la zone, on teste si dist < 30 => Nouveau tour
                    if not in_start_zone:
                        if dist_to_start < 30 and i > 1:
                            current_lap_index += 1
                            laps_positions.append([])
                            current_color = lap_colors[current_lap_index % len(lap_colors)]
                            in_start_zone = True
                    else:
                        # On est dans la zone, on attend d'en sortir
                        # => dist > 50 => in_start_zone = False
                        if dist_to_start > 50:
                            in_start_zone = False

                    # On ajoute le point au tour courant
                    laps_positions[current_lap_index].append((px, py))

                current_index += speed

            # --- 10) Dessin ---
            screen.fill((0, 0, 0))

            # 10.1) Image
            scaled_w = int(image_width * zoom_factor)
            scaled_h = int(image_height * zoom_factor)
            scaled_image = pygame.transform.scale(satellite_image_original, (scaled_w, scaled_h))
            screen.blit(scaled_image, (offset_x, offset_y))

            # 10.2) Menu à droite
            pygame.draw.rect(screen, (50, 50, 50), (screen_width - menu_width, 0, menu_width, screen_height))

            # Boutons
            pygame.draw.rect(screen, (200, 0, 0), button_reset)
            pygame.draw.rect(screen, (0, 200, 0), button_start)
            pygame.draw.rect(screen, (128, 128, 128), button_toggle_lines)
            pygame.draw.rect(screen, (128, 128, 128), button_fps_up)
            pygame.draw.rect(screen, (128, 128, 128), button_fps_down)
            pygame.draw.rect(screen, (0, 128, 255), button_toggle_laps)

            txt_reset   = font.render("Reset", True, (255, 255, 255))
            txt_start   = font.render("Start", True, (255, 255, 255))
            txt_lines   = font.render("Lines: ON" if draw_lines else "Lines: OFF", True, (255, 255, 255))
            txt_fps_up  = font.render("+FPS", True, (0, 0, 0))
            txt_fps_down= font.render("-FPS", True, (0, 0, 0))
            txt_laps    = font.render("Complet ON" if show_completed_laps_only else "Complet OFF", True, (255, 255, 255))

            screen.blit(txt_reset,   (button_reset.x + 20, button_reset.y + 5))
            screen.blit(txt_start,   (button_start.x + 20, button_start.y + 5))
            screen.blit(txt_lines,   (button_toggle_lines.x + 10, button_toggle_lines.y + 5))
            screen.blit(txt_fps_up,  (button_fps_up.x + 10, button_fps_up.y + 5))
            screen.blit(txt_fps_down,(button_fps_down.x + 5, button_fps_down.y + 5))
            screen.blit(txt_laps,    (button_toggle_laps.x + 10, button_toggle_laps.y + 5))

            # Infos sur FPS
            fps_info = font.render(f"FPS: {current_fps}", True, (255, 255, 255))
            screen.blit(fps_info, (screen_width - menu_width + 20, 340))

            # 10.3) Dessin des tours
            # Si show_completed_laps_only = True, on n'affiche pas le dernier tour (qui est en cours)
            last_lap_index = len(laps_positions) - 1

            for lap_index, lap_points in enumerate(laps_positions):
                # Si on doit afficher uniquement les tours terminés, on saute si c'est le dernier ET qu'il n'y a pas eu de nouveau tour créé après
                if show_completed_laps_only and lap_index == last_lap_index:
                    # On n'affiche pas ce tour s'il est toujours en cours
                    continue

                color = lap_colors[lap_index % len(lap_colors)]

                # Dessin des points
                for i in range(len(lap_points)):
                    px, py = lap_points[i]
                    adjx = int(px * zoom_factor + offset_x)
                    adjy = int(py * zoom_factor + offset_y)

                    # Point
                    pygame.draw.circle(screen, color, (adjx, adjy), 4)

                    # Ligne
                    if draw_lines and i > 0:
                        px_prev, py_prev = lap_points[i - 1]
                        adjx_prev = int(px_prev * zoom_factor + offset_x)
                        adjy_prev = int(py_prev * zoom_factor + offset_y)
                        pygame.draw.line(screen, color, (adjx_prev, adjy_prev), (adjx, adjy), 2)

            pygame.display.flip()

        # Fin boucle
    finally:
        pygame.quit()


# Load coordinates from the dataset
# dataset_path = "C:/M2S1/workshop/ai4industry/dataset/"  # Path to the dataset folder
# coordinates = load_coordinates(dataset_path)

# Load coordinates from the saved JSON file
coordinates_file = "../data/coordinates.json"  # Path to the saved JSON file
coordinates = load_coordinates_from_json(coordinates_file)



# Call the function to draw positions
draw_positions_progressive("Ancenis", coordinates)

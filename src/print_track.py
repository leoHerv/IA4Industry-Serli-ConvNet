import pygame
import json
import os
import math


def pos_to_xy(bounds, lat, lon, limits, tile_size=512):
    """
    Convert latitude and longitude into x, y pixel coordinates on a map.
    """
    xratio = (lon - limits['p1']['longitude']) / (limits['p2']['longitude'] - limits['p1']['longitude'])
    yratio = 1.0 - ((lat - limits['p1']['latitude']) / (limits['p2']['latitude'] - limits['p1']['latitude']))

    x = int((bounds[2] - bounds[0] - tile_size) * xratio + 0.5) + (tile_size // 2) + 64
    y = int((bounds[3] - bounds[1] - tile_size) * yratio + 0.5) + (tile_size // 2) + 64

    return x, y


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


def distance(point1, point2):
    """Calculate the distance between two points."""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def draw_positions_progressive(circuit_name, coordinates):
    """
    Draw positions progressively on the circuit using Pygame.

    :param circuit_name: Name of the circuit (must match the image name, without extension)
    :param coordinates: List of tuples (latitude, longitude)
    """
    pygame.init()
    try:
        # Load limits and circuit data from JSON file
        with open('../data/theworld.json', 'r') as file:
            circuit_data = json.load(file)

        selected_circuit = next(track for track in circuit_data["tracks"] if track["name"] == circuit_name)

        # Get real GPS coordinates representing the circuit limits
        limits = {
            "p1": {"latitude": selected_circuit["limits"]["p1"]["lat"],
                   "longitude": selected_circuit["limits"]["p1"]["lon"]},
            "p2": {"latitude": selected_circuit["limits"]["p2"]["lat"],
                   "longitude": selected_circuit["limits"]["p2"]["lon"]}
        }

        # Load the circuit image
        image_path = "../data/" + circuit_name + ".png"
        satellite_image = pygame.image.load(image_path)

        image_width, image_height = satellite_image.get_width(), satellite_image.get_height()
        bounds = (0, 0, image_width, image_height)

        # Adjust the size to fit within a slightly smaller window
        max_width = 1400
        max_height = 900
        scale_factor = min(max_width / image_width, max_height / image_height, 1)
        adjusted_width = int(image_width * scale_factor)
        adjusted_height = int(image_height * scale_factor)

        # Convert GPS coordinates to pixel positions
        positions = [pos_to_xy(bounds, lat, lon, limits) for lat, lon in coordinates]
        start_position = pos_to_xy(
            bounds,
            selected_circuit["start"]["p1"]["lat"],
            selected_circuit["start"]["p1"]["lon"],
            limits
        )

        # Initialize Pygame variables
        menu_width = 200  # Width of the menu
        screen_width, screen_height = adjusted_width + menu_width, max(600, adjusted_height)
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f"Positions sur le circuit '{circuit_name}'")

        font = pygame.font.Font(None, 36)
        button_reset = pygame.Rect(adjusted_width + 20, 50, 150, 50)
        button_start = pygame.Rect(adjusted_width + 20, 120, 150, 50)
        button_increase_speed = pygame.Rect(adjusted_width + 20, 200, 150, 50)
        button_decrease_speed = pygame.Rect(adjusted_width + 20, 270, 150, 50)

        # Set up zoom and drag variables
        zoom_factor = scale_factor
        min_zoom = 0.1
        max_zoom = 5.0
        offset_x = 0
        offset_y = 0
        is_dragging = False
        drag_start = (0, 0)

        running = True
        started = False
        current_position_index = 0
        speed = 1
        last_position_color = (255, 0, 0)
        trail_colors = []
        lap_count = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle mouse wheel for zoom
                elif event.type == pygame.MOUSEWHEEL:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:  # Check if Ctrl is pressed
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        old_zoom = zoom_factor
                        if event.y > 0:  # Scroll up
                            zoom_factor = min(max_zoom, zoom_factor + 0.1)
                        elif event.y < 0:  # Scroll down
                            zoom_factor = max(min_zoom, zoom_factor - 0.1)
                        scale_factor = zoom_factor / old_zoom
                        offset_x = mouse_x - scale_factor * (mouse_x - offset_x)
                        offset_y = mouse_y - scale_factor * (mouse_y - offset_y)

                # Handle mouse button down for dragging or button clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if button_reset.collidepoint(event.pos):
                            started = False
                            current_position_index = 0
                            trail_colors = []
                            lap_count = 0
                        elif button_start.collidepoint(event.pos):
                            started = True
                        elif button_increase_speed.collidepoint(event.pos):
                            speed = min(10, speed + 1)  # Increase speed
                        elif button_decrease_speed.collidepoint(event.pos):
                            speed = max(1, speed - 1)  # Decrease speed
                        else:
                            is_dragging = True
                            drag_start = event.pos

                # Handle mouse button up to stop dragging
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        is_dragging = False

                # Handle mouse motion for dragging
                elif event.type == pygame.MOUSEMOTION:
                    if is_dragging:
                        dx = event.pos[0] - drag_start[0]
                        dy = event.pos[1] - drag_start[1]
                        offset_x += dx
                        offset_y += dy
                        drag_start = event.pos

            # Scale the satellite image
            scaled_width = max(1, int(image_width * zoom_factor))
            scaled_height = max(1, int(image_height * zoom_factor))
            scaled_image = pygame.transform.scale(satellite_image, (scaled_width, scaled_height))

            # Clear the screen
            screen.fill((0, 0, 0))

            # Draw the scaled image
            screen.blit(scaled_image, (offset_x, offset_y))

            # Draw the menu
            pygame.draw.rect(screen, (50, 50, 50), (adjusted_width, 0, menu_width, screen_height))

            # Draw buttons
            pygame.draw.rect(screen, (255, 0, 0), button_reset)
            pygame.draw.rect(screen, (0, 255, 0), button_start)
            pygame.draw.rect(screen, (0, 0, 255), button_increase_speed)
            pygame.draw.rect(screen, (255, 255, 0), button_decrease_speed)
            reset_text = font.render("Reset", True, (255, 255, 255))
            start_text = font.render("Start", True, (255, 255, 255))
            increase_speed_text = font.render("Plus Vitesse", True, (255, 255, 255))
            decrease_speed_text = font.render("Moins Vitesse", True, (255, 255, 255))
            screen.blit(reset_text, (button_reset.x + 20, button_reset.y + 10))
            screen.blit(start_text, (button_start.x + 20, button_start.y + 10))
            screen.blit(increase_speed_text, (button_increase_speed.x + 10, button_increase_speed.y + 10))
            screen.blit(decrease_speed_text, (button_decrease_speed.x + 10, button_decrease_speed.y + 10))

            # Draw positions progressively
            if started:
                for i in range(current_position_index + 1):
                    if i < len(positions):
                        pos_x, pos_y = positions[i]
                        adjusted_pos_x = int((pos_x * zoom_factor) + offset_x)
                        adjusted_pos_y = int((pos_y * zoom_factor) + offset_y)

                        # Check if it's a new lap
                        if distance((pos_x, pos_y), start_position) < 50 and i not in trail_colors:
                            lap_count += 1
                            last_position_color = (0, 255, 0) if lap_count % 2 == 0 else (0, 0, 255)
                            trail_colors.append(i)

                        # Set the color for the current point
                        point_color = last_position_color if i in trail_colors else (255, 0, 0)
                        pygame.draw.circle(screen, point_color, (adjusted_pos_x, adjusted_pos_y), 5)

                # Move to the next position
                current_position_index += speed
                if current_position_index >= len(positions):
                    current_position_index = len(positions) - 1  # Stop at the end

            # Update the display
            pygame.display.flip()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pygame.quit()


# Load coordinates from the dataset
dataset_path = "C:/M2S1/workshop/ai4industry/dataset/"  # Path to the dataset folder
coordinates = load_coordinates(dataset_path)

# Call the function to draw positions
draw_positions_progressive("Ancenis", coordinates)

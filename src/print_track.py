import pygame
import json
import os


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


def draw_positions_progressive(circuit_name, coordinates):
    """
    Draw positions progressively on the circuit using Pygame.

    :param circuit_name: Name of the circuit (must match the image name, without extension)
    :param coordinates: List of tuples (latitude, longitude)
    """
    # Load limits and circuit data from JSON file
    with open('../data/theworld.json', 'r') as file:
        circuit_data = json.load(file)

    selected_circuit = next(track for track in circuit_data["tracks"] if track["name"] == circuit_name)

    # Get real GPS coordinates representing the circuit limits
    limits = {
        "p1": {"latitude": selected_circuit["limits"]["p1"]["lat"], "longitude": selected_circuit["limits"]["p1"]["lon"]},
        "p2": {"latitude": selected_circuit["limits"]["p2"]["lat"], "longitude": selected_circuit["limits"]["p2"]["lon"]}
    }

    # Load the circuit image
    image_path = "../data/" + circuit_name + ".png"
    satellite_image = pygame.image.load(image_path)

    image_width, image_height = satellite_image.get_width(), satellite_image.get_height()
    bounds = (0, 0, image_width, image_height)

    # Convert GPS coordinates to pixel positions
    positions = [pos_to_xy(bounds, lat, lon, limits) for lat, lon in coordinates]

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption(f"Positions sur le circuit '{circuit_name}'")

    font = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(350, 500, 100, 50)

    # Set up zoom and drag variables
    zoom_factor = 1.0
    min_zoom = 0.1
    max_zoom = 5.0
    offset_x = 0
    offset_y = 0
    is_dragging = False
    drag_start = (0, 0)

    running = True
    started = False
    current_position_index = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle mouse wheel for zoom
            elif event.type == pygame.MOUSEWHEEL:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:  # Check if Ctrl is pressed
                    if event.y > 0:  # Scroll up
                        zoom_factor = min(max_zoom, zoom_factor + 0.1)
                    elif event.y < 0:  # Scroll down
                        zoom_factor = max(min_zoom, zoom_factor - 0.1)

            # Handle mouse button down for dragging
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    is_dragging = True
                    drag_start = event.pos
                # Handle button click to start
                if button_rect.collidepoint(event.pos):
                    started = True

            # Handle mouse button up to stop dragging
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    is_dragging = False

            # Handle mouse motion for dragging
            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    dx, dy = event.pos[0] - drag_start[0], event.pos[1] - drag_start[1]
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

        # Draw button
        pygame.draw.rect(screen, (0, 255, 0), button_rect)
        text = font.render("Start", True, (0, 0, 0))
        screen.blit(text, (button_rect.x + 10, button_rect.y + 10))

        # Draw positions progressively
        if started:
            for i in range(current_position_index + 1):
                if i < len(positions):
                    pos_x, pos_y = positions[i]
                    adjusted_pos_x = int((pos_x * zoom_factor) + offset_x)
                    adjusted_pos_y = int((pos_y * zoom_factor) + offset_y)
                    pygame.draw.circle(screen, (255, 0, 0), (adjusted_pos_x, adjusted_pos_y), 5)

            # Move to the next position
            current_position_index += 1
            if current_position_index >= len(positions):
                current_position_index = len(positions) - 1  # Stop at the end

        # Update the display
        pygame.display.flip()

    pygame.quit()


# Load coordinates from the dataset
dataset_path = "C:/M2S1/workshop/ai4industry/dataset/"  # Path to the dataset folder
coordinates = load_coordinates(dataset_path)

# Call the function to draw positions
draw_positions_progressive("Ancenis", coordinates)

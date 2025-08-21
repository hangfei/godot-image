import pygame
import json
import os
import sys
import math
import random
from typing import Dict, List, Tuple, Optional
from game_state_generator import generate_starlight_courier_state

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 960
GRID_WIDTH = 16
GRID_HEIGHT = 12
CELL_SIZE = 64
GRID_OFFSET_X = (WINDOW_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
GRID_OFFSET_Y = 80

# Colors (Deep space theme)
SPACE_DARK = (8, 12, 25)
SPACE_BLUE = (20, 35, 80)
STARLIGHT = (220, 240, 255)
BEACON_GOLD = (255, 215, 100)
PARCEL_CYAN = (100, 255, 255)
DRONE_RED = (255, 80, 80)
COVER_GRAY = (60, 65, 75)
GRID_LINE = (40, 50, 80)
PLAYER_BLUE = (100, 150, 255)
TELEPAD_PURPLE = (180, 100, 255)
VISION_CONE = (255, 100, 100, 60)
UI_TEXT = (200, 220, 255)

class StarlightCourier:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Starlight Courier")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 18)
        
        # Game state
        self.game_state = None
        self.step_counter = 0
        self.running = True
        self.stars = self.generate_stars()
        
        # Load or generate initial game state
        self.load_or_generate_game_state()
        
    def generate_stars(self) -> List[Tuple[int, int, int]]:
        """Generate parallax stars for background"""
        stars = []
        for _ in range(200):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            brightness = random.randint(50, 255)
            stars.append((x, y, brightness))
        return stars
    
    def load_or_generate_game_state(self):
        """Load existing game state or generate new one"""
        # Find the highest numbered game state file
        max_step = 0
        latest_file = None
        
        for filename in os.listdir('.'):
            if filename.startswith('game_state_step_') and filename.endswith('.json'):
                try:
                    step_num = int(filename.replace('game_state_step_', '').replace('.json', ''))
                    if step_num > max_step:
                        max_step = step_num
                        latest_file = filename
                except ValueError:
                    continue
        
        if latest_file:
            try:
                with open(latest_file, 'r') as f:
                    self.game_state = json.load(f)
                self.step_counter = max_step
                print(f"Loaded game state from {latest_file}")
            except Exception as e:
                print(f"Error loading {latest_file}: {e}")
                self.generate_new_game_state()
        else:
            self.generate_new_game_state()
    
    def generate_new_game_state(self):
        """Generate a new random game state"""
        state_json = generate_starlight_courier_state()
        self.game_state = json.loads(state_json)
        self.step_counter = 0
        self.save_game_state()
        print("Generated new game state")
    
    def save_game_state(self):
        """Save current game state to JSON file"""
        self.step_counter += 1
        filename = f"game_state_step_{self.step_counter}.json"
        self.game_state['step'] = self.step_counter
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.game_state, f, indent=2)
            print(f"Saved game state to {filename}")
        except Exception as e:
            print(f"Error saving game state: {e}")
    
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates"""
        screen_x = GRID_OFFSET_X + grid_x * CELL_SIZE
        screen_y = GRID_OFFSET_Y + grid_y * CELL_SIZE
        return screen_x, screen_y
    
    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to grid coordinates"""
        grid_x = (screen_x - GRID_OFFSET_X) // CELL_SIZE
        grid_y = (screen_y - GRID_OFFSET_Y) // CELL_SIZE
        return grid_x, grid_y
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is valid and not blocked"""
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        
        # Check for cover spots (walls, obstacles)
        for cover in self.game_state['cover_spots']:
            if cover['x'] == x and cover['y'] == y:
                return False
        
        return True
    
    def calculate_vision_cones(self):
        """Calculate vision cones for all drones"""
        vision_cones = []
        
        for drone in self.game_state['drones']:
            cone_cells = []
            drone_x, drone_y = drone['x'], drone['y']
            facing = drone['facing']
            detection_range = drone['detection_range']
            
            # Calculate vision cone based on facing direction
            if facing == 'north':
                for dist in range(1, detection_range + 1):
                    for offset in range(-dist, dist + 1):
                        if abs(offset) <= dist:  # Cone shape
                            x, y = drone_x + offset, drone_y - dist
                            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                                cone_cells.append((x, y))
            elif facing == 'south':
                for dist in range(1, detection_range + 1):
                    for offset in range(-dist, dist + 1):
                        if abs(offset) <= dist:
                            x, y = drone_x + offset, drone_y + dist
                            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                                cone_cells.append((x, y))
            elif facing == 'east':
                for dist in range(1, detection_range + 1):
                    for offset in range(-dist, dist + 1):
                        if abs(offset) <= dist:
                            x, y = drone_x + dist, drone_y + offset
                            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                                cone_cells.append((x, y))
            elif facing == 'west':
                for dist in range(1, detection_range + 1):
                    for offset in range(-dist, dist + 1):
                        if abs(offset) <= dist:
                            x, y = drone_x - dist, drone_y + offset
                            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                                cone_cells.append((x, y))
            
            vision_cones.append({
                'drone_id': drone['id'],
                'cells': cone_cells
            })
        
        self.game_state['vision_cones'] = vision_cones
    
    def check_player_detection(self) -> bool:
        """Check if player is detected by any drone"""
        player_x = self.game_state['player']['x']
        player_y = self.game_state['player']['y']
        player_stealth = self.game_state['player']['stealth_mode']
        
        detected = False
        
        for vision_cone in self.game_state['vision_cones']:
            if (player_x, player_y) in vision_cone['cells']:
                # Check if player is in stealth behind cover
                if player_stealth:
                    # Check if there's cover at player position
                    has_cover = any(cover['x'] == player_x and cover['y'] == player_y 
                                  for cover in self.game_state['cover_spots'])
                    if not has_cover:
                        detected = True
                        break
                else:
                    detected = True
                    break
        
        if detected:
            self.game_state['score']['detection_count'] += 1
            self.game_state['score']['perfect_stealth'] = False
        
        return detected
    
    def move_drones(self):
        """Move drones based on player's last move (mirroring mechanic)"""
        player_last_move = self.game_state['player']['last_move']
        
        for drone in self.game_state['drones']:
            # Store the move the drone will make next turn
            if player_last_move and drone['last_player_move']:
                # Execute the queued move (player's previous move)
                move = drone['last_player_move']
                new_x, new_y = drone['x'], drone['y']
                
                if move == 'up':
                    new_y -= 1
                    drone['facing'] = 'north'
                elif move == 'down':
                    new_y += 1
                    drone['facing'] = 'south'
                elif move == 'left':
                    new_x -= 1
                    drone['facing'] = 'west'
                elif move == 'right':
                    new_x += 1
                    drone['facing'] = 'east'
                
                # Only move if valid position
                if self.is_valid_position(new_x, new_y):
                    # Check for collisions with other drones
                    collision = False
                    for other_drone in self.game_state['drones']:
                        if other_drone['id'] != drone['id']:
                            if other_drone['x'] == new_x and other_drone['y'] == new_y:
                                collision = True
                                break
                    
                    if not collision:
                        drone['x'] = new_x
                        drone['y'] = new_y
            
            # Queue the current player move for next turn
            drone['last_player_move'] = player_last_move
    
    def handle_interaction(self):
        """Handle SPACE key interactions"""
        player = self.game_state['player']
        player_x, player_y = player['x'], player['y']
        
        # Check for parcel pickup/drop
        if player['carrying_parcel'] is None:
            # Try to pick up parcel
            for parcel in self.game_state['parcels']:
                if parcel['x'] == player_x and parcel['y'] == player_y and parcel['carried_by'] is None:
                    parcel['carried_by'] = 'player'
                    player['carrying_parcel'] = parcel['id']
                    self.game_state['last_action'] = f"picked_up_{parcel['id']}"
                    return
            
            # Try to use telepad
            for telepad in self.game_state['telepads']:
                if (telepad['x'] == player_x and telepad['y'] == player_y and 
                    telepad['active'] and telepad['charges'] > 0):
                    if telepad['destination_x'] is not None:
                        # Teleport to destination
                        player['x'] = telepad['destination_x']
                        player['y'] = telepad['destination_y']
                        telepad['charges'] -= 1
                        if telepad['charges'] <= 0:
                            telepad['active'] = False
                        self.game_state['last_action'] = f"used_{telepad['id']}"
                        return
            
            # Toggle stealth mode at cover spots
            for cover in self.game_state['cover_spots']:
                if cover['x'] == player_x and cover['y'] == player_y:
                    player['stealth_mode'] = not player['stealth_mode']
                    self.game_state['last_action'] = f"stealth_{'on' if player['stealth_mode'] else 'off'}"
                    return
        
        else:
            # Try to deliver parcel to beacon
            for beacon in self.game_state['beacons']:
                if (beacon['x'] == player_x and beacon['y'] == player_y and 
                    beacon['needs_parcel'] and beacon['active']):
                    
                    # Find the carried parcel
                    carried_parcel = None
                    for parcel in self.game_state['parcels']:
                        if parcel['id'] == player['carrying_parcel']:
                            carried_parcel = parcel
                            break
                    
                    if carried_parcel:
                        # Check if parcel type matches beacon requirement
                        if carried_parcel['type'] == beacon['parcel_type'] or beacon['parcel_type'] == 'normal':
                            # Successful delivery
                            beacon['needs_parcel'] = False
                            beacon['active'] = False
                            player['carrying_parcel'] = None
                            carried_parcel['carried_by'] = None
                            
                            # Calculate score
                            base_points = carried_parcel['value']
                            type_multiplier = self.game_state['rewards']['multipliers'].get(carried_parcel['type'], 1.0)
                            stealth_bonus = 50 if self.game_state['score']['detection_count'] == 0 else 0
                            
                            total_points = int(base_points * type_multiplier) + stealth_bonus
                            
                            self.game_state['score']['points'] += total_points
                            self.game_state['score']['deliveries'] += 1
                            self.game_state['score']['stealth_bonus'] += stealth_bonus
                            
                            # Unlock rewards
                            if carried_parcel['type'] not in self.game_state['rewards']['unlocked_parcel_types']:
                                self.game_state['rewards']['unlocked_parcel_types'].append(carried_parcel['type'])
                            
                            self.game_state['last_action'] = f"delivered_{carried_parcel['id']}_to_{beacon}"
                            
                            # Check win condition
                            if all(not beacon['needs_parcel'] for beacon in self.game_state['beacons']):
                                self.game_state['game_status'] = 'won'
                            
                            return
            
            # Drop parcel at current location
            for parcel in self.game_state['parcels']:
                if parcel['id'] == player['carrying_parcel']:
                    parcel['x'] = player_x
                    parcel['y'] = player_y
                    parcel['carried_by'] = None
                    player['carrying_parcel'] = None
                    self.game_state['last_action'] = f"dropped_{parcel['id']}"
                    return
    
    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type != pygame.KEYDOWN:
            return
        
        player = self.game_state['player']
        new_x, new_y = player['x'], player['y']
        moved = False
        
        if event.key == pygame.K_w:
            new_y -= 1
            player['last_move'] = 'up'
            moved = True
        elif event.key == pygame.K_s:
            new_y += 1
            player['last_move'] = 'down'
            moved = True
        elif event.key == pygame.K_a:
            new_x -= 1
            player['last_move'] = 'left'
            moved = True
        elif event.key == pygame.K_d:
            new_x += 1
            player['last_move'] = 'right'
            moved = True
        elif event.key == pygame.K_SPACE:
            self.handle_interaction()
            self.process_turn()
            return
        elif event.key == pygame.K_r:
            # Reset game
            self.generate_new_game_state()
            return
        elif event.key == pygame.K_ESCAPE:
            self.running = False
            return
        
        if moved and self.is_valid_position(new_x, new_y):
            player['x'] = new_x
            player['y'] = new_y
            self.process_turn()
    
    def process_turn(self):
        """Process a complete game turn"""
        # Move drones based on player's last move
        self.move_drones()
        
        # Calculate vision cones
        self.calculate_vision_cones()
        
        # Check for detection
        detected = self.check_player_detection()
        
        # Increment turn counter
        self.game_state['turn_number'] += 1
        
        # Save game state
        self.save_game_state()
        
        # Check game over conditions
        if detected and self.game_state['score']['detection_count'] >= 3:
            self.game_state['game_status'] = 'game_over'
    
    def draw_stars(self):
        """Draw parallax star background"""
        for x, y, brightness in self.stars:
            color = (brightness, brightness, brightness)
            size = 1 if brightness < 150 else 2
            pygame.draw.circle(self.screen, color, (x, y), size)
    
    def draw_grid(self):
        """Draw the game grid with rim lighting effect"""
        # Draw grid background
        grid_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, 
                               GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(self.screen, SPACE_BLUE, grid_rect)
        
        # Draw grid lines with glow effect
        for x in range(GRID_WIDTH + 1):
            start_x = GRID_OFFSET_X + x * CELL_SIZE
            start_y = GRID_OFFSET_Y
            end_y = GRID_OFFSET_Y + GRID_HEIGHT * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE, (start_x, start_y), (start_x, end_y), 2)
        
        for y in range(GRID_HEIGHT + 1):
            start_x = GRID_OFFSET_X
            start_y = GRID_OFFSET_Y + y * CELL_SIZE
            end_x = GRID_OFFSET_X + GRID_WIDTH * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE, (start_x, start_y), (end_x, start_y), 2)
        
        # Draw coordinate labels
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                screen_x, screen_y = self.grid_to_screen(x, y)
                coord_text = self.small_font.render(f"{x},{y}", True, (80, 90, 120))
                text_rect = coord_text.get_rect()
                text_rect.topleft = (screen_x + 2, screen_y + 2)
                self.screen.blit(coord_text, text_rect)
    
    def draw_vision_cones(self):
        """Draw drone vision cones with transparency"""
        for vision_cone in self.game_state['vision_cones']:
            for cell_x, cell_y in vision_cone['cells']:
                screen_x, screen_y = self.grid_to_screen(cell_x, cell_y)
                
                # Create a surface with per-pixel alpha
                cone_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                cone_surface.fill(VISION_CONE)
                self.screen.blit(cone_surface, (screen_x, screen_y))
    
    def draw_entities(self):
        """Draw all game entities"""
        # Draw cover spots
        for cover in self.game_state['cover_spots']:
            screen_x, screen_y = self.grid_to_screen(cover['x'], cover['y'])
            
            if cover['type'] == 'wall':
                pygame.draw.rect(self.screen, COVER_GRAY, 
                               (screen_x + 8, screen_y + 8, CELL_SIZE - 16, CELL_SIZE - 16))
            elif cover['type'] == 'asteroid':
                pygame.draw.circle(self.screen, COVER_GRAY, 
                                 (screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE // 2), 
                                 CELL_SIZE // 3)
            else:  # debris
                for i in range(3):
                    offset_x = random.randint(10, CELL_SIZE - 10)
                    offset_y = random.randint(10, CELL_SIZE - 10)
                    pygame.draw.circle(self.screen, COVER_GRAY, 
                                     (screen_x + offset_x, screen_y + offset_y), 4)
        
        # Draw telepads
        for telepad in self.game_state['telepads']:
            if telepad['active']:
                screen_x, screen_y = self.grid_to_screen(telepad['x'], telepad['y'])
                
                # Pulsing effect
                pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
                color = (*TELEPAD_PURPLE[:3], pulse)
                
                # Create surface for telepad
                telepad_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(telepad_surface, color, 
                                 (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 3)
                self.screen.blit(telepad_surface, (screen_x, screen_y))
                
                # Draw charge indicator
                charges_text = self.small_font.render(str(telepad['charges']), True, STARLIGHT)
                self.screen.blit(charges_text, (screen_x + 5, screen_y + 5))
        
        # Draw beacons
        for beacon in self.game_state['beacons']:
            if beacon['active']:
                screen_x, screen_y = self.grid_to_screen(beacon['x'], beacon['y'])
                
                # Glowing beacon effect
                glow_intensity = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.005))
                beacon_color = (*BEACON_GOLD[:3], glow_intensity)
                
                # Draw beacon
                beacon_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(beacon_surface, beacon_color, 
                                 (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 4)
                self.screen.blit(beacon_surface, (screen_x, screen_y))
                
                # Draw parcel type requirement
                type_text = self.small_font.render(beacon['parcel_type'][:1].upper(), True, SPACE_DARK)
                text_rect = type_text.get_rect(center=(screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE // 2))
                self.screen.blit(type_text, text_rect)
        
        # Draw parcels
        for parcel in self.game_state['parcels']:
            if parcel['carried_by'] is None:
                screen_x, screen_y = self.grid_to_screen(parcel['x'], parcel['y'])
                
                # Different shapes for different types
                if parcel['type'] == 'heavy':
                    pygame.draw.rect(self.screen, PARCEL_CYAN, 
                                   (screen_x + 16, screen_y + 16, CELL_SIZE - 32, CELL_SIZE - 32))
                elif parcel['type'] == 'fragile':
                    points = [
                        (screen_x + CELL_SIZE // 2, screen_y + 12),
                        (screen_x + CELL_SIZE - 12, screen_y + CELL_SIZE - 12),
                        (screen_x + 12, screen_y + CELL_SIZE - 12)
                    ]
                    pygame.draw.polygon(self.screen, PARCEL_CYAN, points)
                else:  # normal
                    pygame.draw.circle(self.screen, PARCEL_CYAN, 
                                     (screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE // 2), 
                                     CELL_SIZE // 4)
                
                # Draw parcel ID
                id_text = self.small_font.render(parcel['id'][-1], True, SPACE_DARK)
                text_rect = id_text.get_rect(center=(screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE // 2))
                self.screen.blit(id_text, text_rect)
        
        # Draw drones
        for drone in self.game_state['drones']:
            screen_x, screen_y = self.grid_to_screen(drone['x'], drone['y'])
            
            # Main drone body
            pygame.draw.circle(self.screen, DRONE_RED, 
                             (screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE // 2), 
                             CELL_SIZE // 3)
            
            # Direction indicator
            center_x = screen_x + CELL_SIZE // 2
            center_y = screen_y + CELL_SIZE // 2
            
            if drone['facing'] == 'north':
                end_x, end_y = center_x, center_y - CELL_SIZE // 4
            elif drone['facing'] == 'south':
                end_x, end_y = center_x, center_y + CELL_SIZE // 4
            elif drone['facing'] == 'east':
                end_x, end_y = center_x + CELL_SIZE // 4, center_y
            else:  # west
                end_x, end_y = center_x - CELL_SIZE // 4, center_y
            
            pygame.draw.line(self.screen, STARLIGHT, (center_x, center_y), (end_x, end_y), 3)
        
        # Draw player
        player = self.game_state['player']
        screen_x, screen_y = self.grid_to_screen(player['x'], player['y'])
        
        # Player glow effect
        if player['stealth_mode']:
            player_color = (100, 100, 150)
        else:
            player_color = PLAYER_BLUE
        
        # Player body
        pygame.draw.circle(self.screen, player_color, 
                         (screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE // 2), 
                         CELL_SIZE // 3)
        
        # Carried parcel indicator
        if player['carrying_parcel']:
            pygame.draw.circle(self.screen, PARCEL_CYAN, 
                             (screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE // 4), 8)
        
        # Stealth mode indicator
        if player['stealth_mode']:
            pygame.draw.circle(self.screen, (0, 255, 0), 
                             (screen_x + CELL_SIZE - 8, screen_y + 8), 4)
    
    def draw_ui(self):
        """Draw user interface"""
        # Title
        title_text = self.title_font.render("STARLIGHT COURIER", True, STARLIGHT)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title_text, title_rect)
        
        # Score
        score = self.game_state['score']
        score_text = self.font.render(f"Score: {score['points']}", True, UI_TEXT)
        self.screen.blit(score_text, (20, 80))
        
        deliveries_text = self.font.render(f"Deliveries: {score['deliveries']}", True, UI_TEXT)
        self.screen.blit(deliveries_text, (20, 105))
        
        stealth_text = self.font.render(f"Stealth Bonus: {score['stealth_bonus']}", True, UI_TEXT)
        self.screen.blit(stealth_text, (20, 130))
        
        detections_text = self.font.render(f"Detections: {score['detection_count']}", True, UI_TEXT)
        self.screen.blit(detections_text, (20, 155))
        
        # Turn info
        turn_text = self.font.render(f"Turn: {self.game_state['turn_number']}", True, UI_TEXT)
        self.screen.blit(turn_text, (WINDOW_WIDTH - 150, 80))
        
        step_text = self.font.render(f"Step: {self.step_counter}", True, UI_TEXT)
        self.screen.blit(step_text, (WINDOW_WIDTH - 150, 105))
        
        # Controls
        controls_y = WINDOW_HEIGHT - 120
        controls = [
            "WASD: Move",
            "SPACE: Interact",
            "R: Reset Game",
            "ESC: Quit"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, UI_TEXT)
            self.screen.blit(control_text, (20, controls_y + i * 20))
        
        # Game status
        status = self.game_state['game_status']
        if status == 'won':
            status_text = self.title_font.render("MISSION COMPLETE!", True, BEACON_GOLD)
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(status_text, status_rect)
        elif status == 'game_over':
            status_text = self.title_font.render("DETECTED! GAME OVER", True, DRONE_RED)
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(status_text, status_rect)
        
        # Carried parcel info
        player = self.game_state['player']
        if player['carrying_parcel']:
            carried_parcel = None
            for parcel in self.game_state['parcels']:
                if parcel['id'] == player['carrying_parcel']:
                    carried_parcel = parcel
                    break
            
            if carried_parcel:
                parcel_info = f"Carrying: {carried_parcel['type']} ({carried_parcel['value']} pts)"
                parcel_text = self.font.render(parcel_info, True, PARCEL_CYAN)
                self.screen.blit(parcel_text, (WINDOW_WIDTH - 300, 130))
    
    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_input(event)
            
            # Clear screen
            self.screen.fill(SPACE_DARK)
            
            # Draw everything
            self.draw_stars()
            self.draw_grid()
            self.draw_vision_cones()
            self.draw_entities()
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = StarlightCourier()
    game.run()

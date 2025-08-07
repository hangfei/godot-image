import pygame
import json
import random
import math
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32
GRID_WIDTH = 64  # Larger world for camera scrolling
GRID_HEIGHT = 48  # Larger world for camera scrolling

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

class TileType(Enum):
    GRASS = "grass"
    WALL = "wall"
    WATER = "water"
    TREASURE = "treasure"
    ENEMY = "enemy"
    NPC = "npc"
    DOOR = "door"
    KEY = "key"

@dataclass
class Position:
    x: int
    y: int
    
    def to_dict(self):
        return {"x": self.x, "y": self.y}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["x"], data["y"])

@dataclass
class Player:
    position: Position
    health: int = 100
    score: int = 0
    keys: int = 0
    level: int = 1
    experience: int = 0
    
    def to_dict(self):
        return {
            "position": self.position.to_dict(),
            "health": self.health,
            "score": self.score,
            "keys": self.keys,
            "level": self.level,
            "experience": self.experience
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            Position.from_dict(data["position"]),
            data["health"],
            data["score"],
            data["keys"],
            data["level"],
            data["experience"]
        )

@dataclass
class Enemy:
    position: Position
    health: int
    reward: int
    enemy_type: str = "goblin"
    
    def to_dict(self):
        return {
            "position": self.position.to_dict(),
            "health": self.health,
            "reward": self.reward,
            "enemy_type": self.enemy_type
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            Position.from_dict(data["position"]),
            data["health"],
            data["reward"],
            data["enemy_type"]
        )

@dataclass
class Treasure:
    position: Position
    value: int
    treasure_type: str = "gold"
    
    def to_dict(self):
        return {
            "position": self.position.to_dict(),
            "value": self.value,
            "treasure_type": self.treasure_type
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            Position.from_dict(data["position"]),
            data["value"],
            data["treasure_type"]
        )

@dataclass
class NPC:
    position: Position
    name: str
    dialogue: str
    quest_reward: int = 0
    
    def to_dict(self):
        return {
            "position": self.position.to_dict(),
            "name": self.name,
            "dialogue": self.dialogue,
            "quest_reward": self.quest_reward
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            Position.from_dict(data["position"]),
            data["name"],
            data["dialogue"],
            data["quest_reward"]
        )

class GameState:
    def __init__(self):
        self.player = Player(Position(GRID_WIDTH // 2, GRID_HEIGHT // 2))
        self.enemies: List[Enemy] = []
        self.treasures: List[Treasure] = []
        self.npcs: List[NPC] = []
        self.world_map: List[List[TileType]] = []
        self.doors: List[Position] = []
        self.keys_positions: List[Position] = []
        self.turn_count = 0
        self.game_over = False
        self.victory = False
        self.message = ""
        self.message_timer = 0
        
        self.generate_world()
    
    def generate_world(self):
        # Create a procedurally generated world
        self.world_map = [[TileType.GRASS for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Add walls around the border
        for x in range(GRID_WIDTH):
            self.world_map[0][x] = TileType.WALL
            self.world_map[GRID_HEIGHT-1][x] = TileType.WALL
        for y in range(GRID_HEIGHT):
            self.world_map[y][0] = TileType.WALL
            self.world_map[y][GRID_WIDTH-1] = TileType.WALL
        
        # Add some internal walls and structures
        for _ in range(25):  # More structures for larger world
            x = random.randint(2, GRID_WIDTH-3)
            y = random.randint(2, GRID_HEIGHT-3)
            # Create small wall structures
            for dx in range(random.randint(1, 4)):
                for dy in range(random.randint(1, 3)):
                    if x+dx < GRID_WIDTH-1 and y+dy < GRID_HEIGHT-1:
                        self.world_map[y+dy][x+dx] = TileType.WALL
        
        # Add water features
        for _ in range(15):  # More water features
            x = random.randint(3, GRID_WIDTH-4)
            y = random.randint(3, GRID_HEIGHT-4)
            for dx in range(random.randint(2, 4)):
                for dy in range(random.randint(2, 4)):
                    if x+dx < GRID_WIDTH-2 and y+dy < GRID_HEIGHT-2:
                        self.world_map[y+dy][x+dx] = TileType.WATER
        
        # Generate enemies
        for _ in range(20):  # More enemies for larger world
            pos = self.get_random_empty_position()
            if pos:
                enemy_types = ["goblin", "orc", "skeleton", "spider"]
                enemy_type = random.choice(enemy_types)
                health = random.randint(20, 50)
                reward = random.randint(10, 30)
                self.enemies.append(Enemy(pos, health, reward, enemy_type))
        
        # Generate treasures
        for _ in range(25):  # More treasures
            pos = self.get_random_empty_position()
            if pos:
                treasure_types = ["gold", "gem", "artifact", "potion"]
                treasure_type = random.choice(treasure_types)
                value = random.randint(50, 200)
                self.treasures.append(Treasure(pos, value, treasure_type))
        
        # Generate NPCs
        npc_data = [
            ("Merchant", "Welcome, traveler! I have wares for sale.", 0),
            ("Wizard", "I sense great potential in you. Complete my quest for a reward!", 100),
            ("Guard", "Stay safe out there. Danger lurks in these lands.", 50),
            ("Healer", "Let me restore your health, brave adventurer.", 0)
        ]
        
        for name, dialogue, reward in npc_data:
            pos = self.get_random_empty_position()
            if pos:
                self.npcs.append(NPC(pos, name, dialogue, reward))
        
        # Add doors and keys
        for _ in range(8):  # More doors and keys for larger world
            door_pos = self.get_random_empty_position()
            key_pos = self.get_random_empty_position()
            if door_pos and key_pos:
                self.doors.append(door_pos)
                self.keys_positions.append(key_pos)
    
    def get_random_empty_position(self) -> Optional[Position]:
        for _ in range(100):  # Try 100 times to find an empty position
            x = random.randint(2, GRID_WIDTH-3)
            y = random.randint(2, GRID_HEIGHT-3)
            pos = Position(x, y)
            
            if (self.world_map[y][x] == TileType.GRASS and 
                not self.is_position_occupied(pos) and
                pos.x != self.player.position.x and pos.y != self.player.position.y):
                return pos
        return None
    
    def is_position_occupied(self, pos: Position) -> bool:
        for enemy in self.enemies:
            if enemy.position.x == pos.x and enemy.position.y == pos.y:
                return True
        for treasure in self.treasures:
            if treasure.position.x == pos.x and treasure.position.y == pos.y:
                return True
        for npc in self.npcs:
            if npc.position.x == pos.x and npc.position.y == pos.y:
                return True
        for door in self.doors:
            if door.x == pos.x and door.y == pos.y:
                return True
        for key in self.keys_positions:
            if key.x == pos.x and key.y == pos.y:
                return True
        return False
    
    def to_dict(self):
        return {
            "player": self.player.to_dict(),
            "enemies": [enemy.to_dict() for enemy in self.enemies],
            "treasures": [treasure.to_dict() for treasure in self.treasures],
            "npcs": [npc.to_dict() for npc in self.npcs],
            "doors": [{"x": door.x, "y": door.y} for door in self.doors],
            "keys_positions": [{"x": key.x, "y": key.y} for key in self.keys_positions],
            "turn_count": self.turn_count,
            "game_over": self.game_over,
            "victory": self.victory,
            "world_seed": random.getstate()[1][0]  # Store random seed for world generation
        }
    
    @classmethod
    def from_dict(cls, data):
        state = cls()
        state.player = Player.from_dict(data["player"])
        state.enemies = [Enemy.from_dict(e) for e in data["enemies"]]
        state.treasures = [Treasure.from_dict(t) for t in data["treasures"]]
        state.npcs = [NPC.from_dict(n) for n in data["npcs"]]
        state.doors = [Position(d["x"], d["y"]) for d in data["doors"]]
        state.keys_positions = [Position(k["x"], k["y"]) for k in data["keys_positions"]]
        state.turn_count = data["turn_count"]
        state.game_over = data["game_over"]
        state.victory = data["victory"]
        
        # Regenerate world with same seed
        if "world_seed" in data:
            random.seed(data["world_seed"])
            state.generate_world()
        
        return state

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Epic 2D Adventure Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Try to load existing game state
        self.game_state = self.load_game_state()
        
        # Create fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Animation variables
        self.animation_time = 0
        
        # Camera system
        self.camera_x = 0
        self.camera_y = 0
        self.camera_smooth = 0.1  # Camera smoothing factor
        
    def load_game_state(self) -> GameState:
        """Load game state from JSON files in directory, or create new if none exist"""
        json_files = [f for f in os.listdir('.') if f.endswith('.json') and f.startswith('save_')]
        
        if json_files:
            # Load the most recent save file
            latest_file = max(json_files, key=lambda f: os.path.getmtime(f))
            try:
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                print(f"Loaded game from {latest_file}")
                return GameState.from_dict(data)
            except Exception as e:
                print(f"Error loading save file: {e}")
        
        print("Creating new game")
        return GameState()
    
    def save_game_state(self):
        """Save current game state to JSON file"""
        filename = f"save_game_{self.game_state.turn_count:04d}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.game_state.to_dict(), f, indent=2)
            self.show_message(f"Game saved to {filename}")
        except Exception as e:
            self.show_message(f"Error saving game: {e}")
    
    def show_message(self, message: str, duration: int = 180):
        """Show a temporary message on screen"""
        self.game_state.message = message
        self.game_state.message_timer = duration
    
    def update_camera(self):
        """Update camera position to follow the player"""
        # Target camera position (center player on screen)
        target_x = self.game_state.player.position.x * TILE_SIZE - SCREEN_WIDTH // 2
        target_y = self.game_state.player.position.y * TILE_SIZE - (SCREEN_HEIGHT - 120) // 2  # Account for UI height
        
        # Clamp camera to world boundaries
        max_camera_x = GRID_WIDTH * TILE_SIZE - SCREEN_WIDTH
        max_camera_y = GRID_HEIGHT * TILE_SIZE - (SCREEN_HEIGHT - 120)
        
        target_x = max(0, min(target_x, max_camera_x))
        target_y = max(0, min(target_y, max_camera_y))
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * self.camera_smooth
        self.camera_y += (target_y - self.camera_y) * self.camera_smooth
    
    def world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x * TILE_SIZE - self.camera_x
        screen_y = world_y * TILE_SIZE - self.camera_y
        return int(screen_x), int(screen_y)
    
    def is_visible(self, world_x: int, world_y: int) -> bool:
        """Check if a world coordinate is visible on screen"""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        return (-TILE_SIZE <= screen_x <= SCREEN_WIDTH and 
                -TILE_SIZE <= screen_y <= SCREEN_HEIGHT - 120)
    
    def handle_input(self):
        """Handle keyboard input for turn-based gameplay"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_state.game_over:
                    if event.key == pygame.K_r:
                        self.game_state = GameState()
                        self.show_message("New game started!")
                    return
                
                # Movement with WASD
                new_pos = Position(self.game_state.player.position.x, self.game_state.player.position.y)
                
                if event.key == pygame.K_w:  # Up
                    new_pos.y -= 1
                elif event.key == pygame.K_s:  # Down
                    new_pos.y += 1
                elif event.key == pygame.K_a:  # Left
                    new_pos.x -= 1
                elif event.key == pygame.K_d:  # Right
                    new_pos.x += 1
                elif event.key == pygame.K_SPACE:  # Interact
                    self.handle_interaction()
                    return
                elif event.key == pygame.K_F5:  # Save game
                    self.save_game_state()
                    return
                else:
                    return  # No valid input, don't advance turn
                
                # Validate movement
                if self.is_valid_move(new_pos):
                    self.game_state.player.position = new_pos
                    self.game_state.turn_count += 1
                    self.check_for_interactions()
                    self.update_enemies()
    
    def is_valid_move(self, pos: Position) -> bool:
        """Check if the move is valid (not into walls, water, or enemies)"""
        if (pos.x < 0 or pos.x >= GRID_WIDTH or 
            pos.y < 0 or pos.y >= GRID_HEIGHT):
            return False
        
        tile = self.game_state.world_map[pos.y][pos.x]
        if tile in [TileType.WALL, TileType.WATER]:
            return False
        
        # Check for enemies
        for enemy in self.game_state.enemies:
            if enemy.position.x == pos.x and enemy.position.y == pos.y:
                return False
        
        # Check for locked doors
        for door in self.game_state.doors:
            if door.x == pos.x and door.y == pos.y and self.game_state.player.keys == 0:
                self.show_message("You need a key to open this door!")
                return False
        
        return True
    
    def handle_interaction(self):
        """Handle space key interactions"""
        player_pos = self.game_state.player.position
        
        # Check adjacent tiles for interactions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]:
            check_x = player_pos.x + dx
            check_y = player_pos.y + dy
            
            # Check for enemies to attack
            for i, enemy in enumerate(self.game_state.enemies):
                if enemy.position.x == check_x and enemy.position.y == check_y:
                    damage = random.randint(15, 25) + self.game_state.player.level * 5
                    enemy.health -= damage
                    self.show_message(f"You attack {enemy.enemy_type} for {damage} damage!")
                    
                    if enemy.health <= 0:
                        self.game_state.player.score += enemy.reward
                        self.game_state.player.experience += enemy.reward // 2
                        self.show_message(f"Defeated {enemy.enemy_type}! +{enemy.reward} score")
                        self.game_state.enemies.pop(i)
                        
                        # Level up check
                        if self.game_state.player.experience >= self.game_state.player.level * 100:
                            self.game_state.player.level += 1
                            self.game_state.player.health = min(100, self.game_state.player.health + 20)
                            self.show_message(f"Level up! Now level {self.game_state.player.level}")
                    
                    self.game_state.turn_count += 1
                    return
            
            # Check for NPCs to talk to
            for npc in self.game_state.npcs:
                if npc.position.x == check_x and npc.position.y == check_y:
                    self.show_message(f"{npc.name}: {npc.dialogue}")
                    if npc.quest_reward > 0:
                        self.game_state.player.score += npc.quest_reward
                        self.show_message(f"Quest completed! +{npc.quest_reward} score")
                        npc.quest_reward = 0  # One-time reward
                    self.game_state.turn_count += 1
                    return
        
        # Check current position for items
        # Check for treasures
        for i, treasure in enumerate(self.game_state.treasures):
            if (treasure.position.x == player_pos.x and 
                treasure.position.y == player_pos.y):
                self.game_state.player.score += treasure.value
                self.show_message(f"Found {treasure.treasure_type}! +{treasure.value} score")
                self.game_state.treasures.pop(i)
                self.game_state.turn_count += 1
                return
        
        # Check for keys
        for i, key_pos in enumerate(self.game_state.keys_positions):
            if (key_pos.x == player_pos.x and key_pos.y == player_pos.y):
                self.game_state.player.keys += 1
                self.show_message(f"Found a key! Total keys: {self.game_state.player.keys}")
                self.game_state.keys_positions.pop(i)
                self.game_state.turn_count += 1
                return
        
        # Check for doors to unlock
        for i, door in enumerate(self.game_state.doors):
            if (door.x == player_pos.x and door.y == player_pos.y and 
                self.game_state.player.keys > 0):
                self.game_state.player.keys -= 1
                self.game_state.player.score += 100
                self.show_message("Door unlocked! +100 score")
                self.game_state.doors.pop(i)
                self.game_state.turn_count += 1
                return
    
    def check_for_interactions(self):
        """Check for automatic interactions when stepping on items"""
        player_pos = self.game_state.player.position
        
        # Auto-collect treasures
        for i, treasure in enumerate(self.game_state.treasures):
            if (treasure.position.x == player_pos.x and 
                treasure.position.y == player_pos.y):
                self.game_state.player.score += treasure.value
                self.show_message(f"Found {treasure.treasure_type}! +{treasure.value} score")
                self.game_state.treasures.pop(i)
                break
        
        # Auto-collect keys
        for i, key_pos in enumerate(self.game_state.keys_positions):
            if (key_pos.x == player_pos.x and key_pos.y == player_pos.y):
                self.game_state.player.keys += 1
                self.show_message(f"Found a key! Total keys: {self.game_state.player.keys}")
                self.game_state.keys_positions.pop(i)
                break
    
    def update_enemies(self):
        """Update enemy AI - simple movement towards player"""
        for enemy in self.game_state.enemies:
            if random.random() < 0.3:  # 30% chance to move each turn
                # Simple AI: move towards player
                dx = self.game_state.player.position.x - enemy.position.x
                dy = self.game_state.player.position.y - enemy.position.y
                
                new_pos = Position(enemy.position.x, enemy.position.y)
                
                if abs(dx) > abs(dy):
                    new_pos.x += 1 if dx > 0 else -1
                else:
                    new_pos.y += 1 if dy > 0 else -1
                
                # Check if move is valid for enemy
                if (0 <= new_pos.x < GRID_WIDTH and 0 <= new_pos.y < GRID_HEIGHT and
                    self.game_state.world_map[new_pos.y][new_pos.x] not in [TileType.WALL, TileType.WATER] and
                    not (new_pos.x == self.game_state.player.position.x and new_pos.y == self.game_state.player.position.y)):
                    enemy.position = new_pos
    
    def draw_tile(self, x: int, y: int, tile_type: TileType):
        """Draw a single tile with enhanced visuals"""
        screen_x, screen_y = self.world_to_screen(x, y)
        rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
        
        if tile_type == TileType.GRASS:
            # Animated grass
            wave = math.sin(self.animation_time * 0.05 + x + y) * 3
            color = (0, 150 + int(wave), 0)
            pygame.draw.rect(self.screen, color, rect)
            # Add grass details
            for i in range(3):
                grass_x = screen_x + random.randint(2, TILE_SIZE-2)
                grass_y = screen_y + random.randint(2, TILE_SIZE-2)
                pygame.draw.circle(self.screen, DARK_GREEN, (grass_x, grass_y), 1)
        
        elif tile_type == TileType.WALL:
            # Stone wall with texture
            pygame.draw.rect(self.screen, GRAY, rect)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 2)
            # Add stone texture
            for i in range(4):
                stone_x = screen_x + random.randint(2, TILE_SIZE-4)
                stone_y = screen_y + random.randint(2, TILE_SIZE-4)
                pygame.draw.rect(self.screen, WHITE, (stone_x, stone_y, 2, 2))
        
        elif tile_type == TileType.WATER:
            # Animated water
            wave = math.sin(self.animation_time * 0.1 + x * 0.5 + y * 0.5) * 10
            color = (0, 100 + int(wave), 200 + int(wave))
            pygame.draw.rect(self.screen, color, rect)
            # Water ripples
            ripple_color = (150, 150, 255, 100)
            pygame.draw.circle(self.screen, ripple_color, rect.center, 8 + int(wave))
    
    def draw_entity(self, pos: Position, entity_type: str, color: Tuple[int, int, int], secondary_color: Optional[Tuple[int, int, int]] = None):
        """Draw an entity with enhanced visuals"""
        screen_x, screen_y = self.world_to_screen(pos.x, pos.y)
        x = screen_x + TILE_SIZE // 2
        y = screen_y + TILE_SIZE // 2
        
        # Pulsing animation
        pulse = math.sin(self.animation_time * 0.1) * 2
        radius = TILE_SIZE // 3 + int(pulse)
        
        # Draw shadow
        pygame.draw.circle(self.screen, (50, 50, 50), (x + 2, y + 2), radius)
        
        # Draw main entity
        pygame.draw.circle(self.screen, color, (x, y), radius)
        
        # Draw details based on entity type
        if entity_type == "player":
            # Make player larger and more distinctive
            player_radius = TILE_SIZE // 2 + int(pulse * 1.5)  # Larger than other entities
            
            # Draw glowing aura effect
            for i in range(3):
                aura_radius = player_radius + 8 - i * 3
                aura_alpha = 50 - i * 15
                aura_color = (255, 255, 0, aura_alpha)  # Yellow glow
                pygame.draw.circle(self.screen, (255, 255, 0), (x, y), aura_radius, 2)
            
            # Redraw player with new size
            pygame.draw.circle(self.screen, (50, 50, 50), (x + 3, y + 3), player_radius)  # Shadow
            pygame.draw.circle(self.screen, (0, 150, 255), (x, y), player_radius)  # Bright blue body
            
            # Hero emblem/chest piece
            pygame.draw.circle(self.screen, GOLD, (x, y - 2), 6)
            pygame.draw.circle(self.screen, WHITE, (x, y - 2), 4)
            
            # Enhanced face features
            eye_offset = 6
            # Eyes with more detail
            pygame.draw.circle(self.screen, WHITE, (x - eye_offset, y - 6), 4)
            pygame.draw.circle(self.screen, WHITE, (x + eye_offset, y - 6), 4)
            pygame.draw.circle(self.screen, BLUE, (x - eye_offset, y - 6), 2)
            pygame.draw.circle(self.screen, BLUE, (x + eye_offset, y - 6), 2)
            pygame.draw.circle(self.screen, BLACK, (x - eye_offset, y - 6), 1)
            pygame.draw.circle(self.screen, BLACK, (x + eye_offset, y - 6), 1)
            
            # Hero smile
            pygame.draw.arc(self.screen, BLACK, (x - 8, y + 2, 16, 10), 0, math.pi, 3)
            
            # Cape effect
            cape_points = [
                (x - player_radius + 2, y - player_radius // 2),
                (x - player_radius - 5, y + player_radius + 5),
                (x + player_radius - 2, y - player_radius // 2),
                (x + player_radius + 5, y + player_radius + 5)
            ]
            pygame.draw.polygon(self.screen, RED, cape_points)
            
            # Crown/helmet detail
            crown_points = [
                (x - 8, y - player_radius),
                (x, y - player_radius - 5),
                (x + 8, y - player_radius)
            ]
            pygame.draw.polygon(self.screen, GOLD, crown_points)
            
            return  # Skip the normal radius border drawing for player
        
        elif entity_type in ["goblin", "orc", "skeleton", "spider"]:
            # Enemy eyes (red)
            eye_offset = 3
            pygame.draw.circle(self.screen, RED, (x - eye_offset, y - 3), 2)
            pygame.draw.circle(self.screen, RED, (x + eye_offset, y - 3), 2)
            # Angry mouth
            pygame.draw.arc(self.screen, BLACK, (x - 4, y + 2, 8, 4), math.pi, 2 * math.pi, 2)
        
        elif entity_type == "npc":
            # Friendly NPC
            eye_offset = 3
            pygame.draw.circle(self.screen, BLACK, (x - eye_offset, y - 3), 2)
            pygame.draw.circle(self.screen, BLACK, (x + eye_offset, y - 3), 2)
            # Neutral mouth
            pygame.draw.line(self.screen, BLACK, (x - 4, y + 3), (x + 4, y + 3), 2)
        
        # Add border
        if secondary_color is not None:
            pygame.draw.circle(self.screen, secondary_color, (x, y), radius, 2)
    
    def draw_item(self, pos: Position, item_type: str, color: Tuple[int, int, int]):
        """Draw an item with sparkling effect"""
        screen_x, screen_y = self.world_to_screen(pos.x, pos.y)
        x = screen_x + TILE_SIZE // 2
        y = screen_y + TILE_SIZE // 2
        
        # Sparkling animation
        sparkle = math.sin(self.animation_time * 0.15) * 0.5 + 0.5
        
        if item_type in ["gold", "gem", "artifact"]:
            # Treasure sparkle effect
            for i in range(5):
                angle = (self.animation_time * 0.1 + i * math.pi * 2 / 5) % (2 * math.pi)
                sparkle_x = x + math.cos(angle) * 15 * sparkle
                sparkle_y = y + math.sin(angle) * 15 * sparkle
                pygame.draw.circle(self.screen, YELLOW, (int(sparkle_x), int(sparkle_y)), 2)
            
            # Main treasure
            pygame.draw.rect(self.screen, color, (x - 8, y - 8, 16, 16))
            pygame.draw.rect(self.screen, YELLOW, (x - 8, y - 8, 16, 16), 2)
        
        elif item_type == "key":
            # Key shape
            pygame.draw.rect(self.screen, color, (x - 3, y - 8, 6, 12))
            pygame.draw.rect(self.screen, color, (x + 3, y - 5, 4, 3))
            pygame.draw.rect(self.screen, color, (x + 3, y, 4, 3))
            # Glow effect
            pygame.draw.circle(self.screen, YELLOW, (x, y), 12, 1)
        
        elif item_type == "door":
            # Door
            pygame.draw.rect(self.screen, BROWN, (x - 10, y - 12, 20, 24))
            pygame.draw.rect(self.screen, DARK_GRAY, (x - 10, y - 12, 20, 24), 2)
            # Door handle
            pygame.draw.circle(self.screen, GOLD, (x + 6, y), 3)
    
    def draw_ui(self):
        """Draw the user interface"""
        # Background for UI
        ui_rect = pygame.Rect(0, SCREEN_HEIGHT - 120, SCREEN_WIDTH, 120)
        pygame.draw.rect(self.screen, (30, 30, 30), ui_rect)
        pygame.draw.rect(self.screen, WHITE, ui_rect, 2)
        
        # Player stats
        stats_text = [
            f"Health: {self.game_state.player.health}/100",
            f"Score: {self.game_state.player.score}",
            f"Level: {self.game_state.player.level}",
            f"XP: {self.game_state.player.experience}/{self.game_state.player.level * 100}",
            f"Keys: {self.game_state.player.keys}",
            f"Turn: {self.game_state.turn_count}"
        ]
        
        for i, text in enumerate(stats_text):
            surface = self.font_medium.render(text, True, WHITE)
            self.screen.blit(surface, (10 + (i % 3) * 200, SCREEN_HEIGHT - 110 + (i // 3) * 25))
        
        # Health bar
        health_bar_rect = pygame.Rect(10, SCREEN_HEIGHT - 50, 200, 20)
        pygame.draw.rect(self.screen, RED, health_bar_rect)
        health_width = int(200 * self.game_state.player.health / 100)
        health_rect = pygame.Rect(10, SCREEN_HEIGHT - 50, health_width, 20)
        pygame.draw.rect(self.screen, GREEN, health_rect)
        pygame.draw.rect(self.screen, WHITE, health_bar_rect, 2)
        
        # Experience bar
        xp_bar_rect = pygame.Rect(220, SCREEN_HEIGHT - 50, 200, 20)
        pygame.draw.rect(self.screen, DARK_GRAY, xp_bar_rect)
        xp_progress = self.game_state.player.experience / (self.game_state.player.level * 100)
        xp_width = int(200 * xp_progress)
        xp_rect = pygame.Rect(220, SCREEN_HEIGHT - 50, xp_width, 20)
        pygame.draw.rect(self.screen, CYAN, xp_rect)
        pygame.draw.rect(self.screen, WHITE, xp_bar_rect, 2)
        
        # Controls
        controls_text = "WASD: Move | SPACE: Interact/Attack | F5: Save Game"
        surface = self.font_small.render(controls_text, True, WHITE)
        self.screen.blit(surface, (430, SCREEN_HEIGHT - 50))
        
        # Message display
        if self.game_state.message and self.game_state.message_timer > 0:
            message_surface = self.font_medium.render(self.game_state.message, True, YELLOW)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
            
            # Message background
            bg_rect = message_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(self.screen, YELLOW, bg_rect, 2)
            
            self.screen.blit(message_surface, message_rect)
            self.game_state.message_timer -= 1
        
        # Game over screen
        if self.game_state.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = "GAME OVER" if not self.game_state.victory else "VICTORY!"
            text_color = RED if not self.game_state.victory else GOLD
            
            title_surface = self.font_large.render(game_over_text, True, text_color)
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(title_surface, title_rect)
            
            score_surface = self.font_medium.render(f"Final Score: {self.game_state.player.score}", True, WHITE)
            score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(score_surface, score_rect)
            
            restart_surface = self.font_medium.render("Press R to restart", True, WHITE)
            restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_surface, restart_rect)
    
    def update(self):
        """Update game state"""
        self.animation_time += 1
        
        # Update camera to follow player
        self.update_camera()
        
        # Check win condition
        if (len(self.game_state.enemies) == 0 and len(self.game_state.treasures) <= 2 and
            self.game_state.player.score >= 1000):
            self.game_state.victory = True
            self.game_state.game_over = True
        
        # Check lose condition
        if self.game_state.player.health <= 0:
            self.game_state.game_over = True
        
        # Random events
        if random.random() < 0.001:  # Very rare events
            events = [
                ("You found a healing spring! +20 health", 20, "health"),
                ("A mysterious merchant appears! +50 score", 50, "score"),
                ("You feel more experienced! +25 XP", 25, "experience")
            ]
            event_text, value, stat = random.choice(events)
            
            if stat == "health":
                self.game_state.player.health = min(100, self.game_state.player.health + value)
            elif stat == "score":
                self.game_state.player.score += value
            elif stat == "experience":
                self.game_state.player.experience += value
            
            self.show_message(event_text)
    
    def draw(self):
        """Draw the entire game"""
        self.screen.fill(BLACK)
        
        # Draw world tiles (only visible ones for performance)
        start_x = max(0, int(self.camera_x // TILE_SIZE) - 1)
        end_x = min(GRID_WIDTH, int((self.camera_x + SCREEN_WIDTH) // TILE_SIZE) + 2)
        start_y = max(0, int(self.camera_y // TILE_SIZE) - 1)
        end_y = min(GRID_HEIGHT, int((self.camera_y + SCREEN_HEIGHT - 120) // TILE_SIZE) + 2)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    self.draw_tile(x, y, self.game_state.world_map[y][x])
        
        # Draw doors (only visible ones)
        for door in self.game_state.doors:
            if self.is_visible(door.x, door.y):
                self.draw_item(door, "door", BROWN)
        
        # Draw keys (only visible ones)
        for key_pos in self.game_state.keys_positions:
            if self.is_visible(key_pos.x, key_pos.y):
                self.draw_item(key_pos, "key", GOLD)
        
        # Draw treasures (only visible ones)
        for treasure in self.game_state.treasures:
            if self.is_visible(treasure.position.x, treasure.position.y):
                color = GOLD if treasure.treasure_type == "gold" else PURPLE if treasure.treasure_type == "gem" else ORANGE
                self.draw_item(treasure.position, treasure.treasure_type, color)
        
        # Draw enemies (only visible ones)
        for enemy in self.game_state.enemies:
            if self.is_visible(enemy.position.x, enemy.position.y):
                color = RED if enemy.enemy_type == "goblin" else DARK_GRAY if enemy.enemy_type == "orc" else WHITE
                self.draw_entity(enemy.position, enemy.enemy_type, color, RED)
        
        # Draw NPCs (only visible ones)
        for npc in self.game_state.npcs:
            if self.is_visible(npc.position.x, npc.position.y):
                self.draw_entity(npc.position, "npc", BLUE, WHITE)
        
        # Draw player (color and secondary_color are ignored since player draws itself completely)
        self.draw_entity(self.game_state.player.position, "player", (0, 150, 255), None)
        
        # Draw interaction indicator if player can interact with something
        player_pos = self.game_state.player.position
        can_interact = False
        
        # Check for nearby interactables
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]:
            check_x = player_pos.x + dx
            check_y = player_pos.y + dy
            
            # Check for enemies, NPCs, or items at interaction range
            for enemy in self.game_state.enemies:
                if enemy.position.x == check_x and enemy.position.y == check_y:
                    can_interact = True
                    break
            
            for npc in self.game_state.npcs:
                if npc.position.x == check_x and npc.position.y == check_y:
                    can_interact = True
                    break
            
            for treasure in self.game_state.treasures:
                if treasure.position.x == check_x and treasure.position.y == check_y:
                    can_interact = True
                    break
            
            for key_pos in self.game_state.keys_positions:
                if key_pos.x == check_x and key_pos.y == check_y:
                    can_interact = True
                    break
            
            for door in self.game_state.doors:
                if door.x == check_x and door.y == check_y:
                    can_interact = True
                    break
            
            if can_interact:
                break
        
        # Draw interaction prompt
        if can_interact:
            screen_x, screen_y = self.world_to_screen(player_pos.x, player_pos.y)
            prompt_x = screen_x + TILE_SIZE // 2
            prompt_y = screen_y - 15
            
            # Pulsing "SPACE" indicator
            pulse_alpha = int(128 + 127 * math.sin(self.animation_time * 0.2))
            prompt_surface = self.font_small.render("SPACE", True, (255, 255, 255))
            prompt_rect = prompt_surface.get_rect(center=(prompt_x, prompt_y))
            
            # Background for prompt
            bg_rect = prompt_rect.inflate(8, 4)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(self.screen, (255, 255, 0), bg_rect, 1)
            
            self.screen.blit(prompt_surface, prompt_rect)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS for smooth animations
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

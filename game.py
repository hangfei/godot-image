import pygame
import json
import os
import random
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
GRID_SIZE = 32
GRID_WIDTH = 25
GRID_HEIGHT = 20

# Colors (Neon Synthwave theme)
BLACK = (0, 0, 0)
DARK_PURPLE = (25, 5, 35)
NEON_PINK = (255, 16, 240)
NEON_CYAN = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_ORANGE = (255, 165, 0)
NEON_BLUE = (0, 191, 255)
PURPLE_GLOW = (138, 43, 226)
GRID_COLOR = (50, 0, 100)

class TileType(Enum):
    EMPTY = "empty"
    WALL = "wall"
    CRYSTAL = "crystal"
    TELEPORTER = "teleporter"
    HAZARD = "hazard"

class EnemyType(Enum):
    TRACKER = "tracker"
    GUARDIAN = "guardian"
    HUNTER = "hunter"

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
    x: int
    y: int
    hp: int
    max_hp: int
    score: int
    combo_multiplier: int
    mods: List[str]
    
    def to_dict(self):
        return {
            "x": self.x, "y": self.y, "hp": self.hp, "max_hp": self.max_hp,
            "score": self.score, "combo_multiplier": self.combo_multiplier, "mods": self.mods
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class Enemy:
    type: str
    x: int
    y: int
    hp: int
    max_hp: int
    
    def to_dict(self):
        return {"type": self.type, "x": self.x, "y": self.y, "hp": self.hp, "max_hp": self.max_hp}
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class Pickup:
    type: str
    x: int
    y: int
    value: int
    
    def to_dict(self):
        return {"type": self.type, "x": self.x, "y": self.y, "value": self.value}
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class Effect:
    type: str
    x: int
    y: int
    duration: int
    color: Tuple[int, int, int]
    
    def to_dict(self):
        return {"type": self.type, "x": self.x, "y": self.y, "duration": self.duration, "color": self.color}
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class GameState:
    def __init__(self):
        self.seed = random.randint(1, 1000000)
        self.step = 0
        self.player = Player(x=5, y=5, hp=100, max_hp=100, score=0, combo_multiplier=1, mods=[])
        self.enemies: List[Enemy] = []
        self.tiles = self.generate_level()
        self.pickups: List[Pickup] = []
        self.effects_queue: List[Effect] = []
        self.flawless_turns = 0
        self.artifacts = []
        
    def generate_level(self):
        """Generate a basic level layout"""
        tiles = {}
        random.seed(self.seed + self.step)
        
        # Fill with empty tiles
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                tiles[f"{x},{y}"] = TileType.EMPTY.value
        
        # Add some walls
        for _ in range(20):
            x, y = random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2)
            tiles[f"{x},{y}"] = TileType.WALL.value
        
        # Add crystals
        for _ in range(8):
            x, y = random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2)
            if tiles[f"{x},{y}"] == TileType.EMPTY.value:
                tiles[f"{x},{y}"] = TileType.CRYSTAL.value
        
        # Add teleporters
        for _ in range(2):
            x, y = random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2)
            if tiles[f"{x},{y}"] == TileType.EMPTY.value:
                tiles[f"{x},{y}"] = TileType.TELEPORTER.value
                
        return tiles
    
    def spawn_enemies(self):
        """Spawn initial enemies"""
        random.seed(self.seed + self.step)
        for _ in range(3):
            x, y = random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2)
            if self.is_position_free(x, y):
                enemy_type = random.choice(list(EnemyType)).value
                hp = 50 if enemy_type == "tracker" else 75
                self.enemies.append(Enemy(type=enemy_type, x=x, y=y, hp=hp, max_hp=hp))
    
    def is_position_free(self, x: int, y: int) -> bool:
        """Check if position is free for movement"""
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        
        tile_key = f"{x},{y}"
        if tile_key in self.tiles and self.tiles[tile_key] == TileType.WALL.value:
            return False
        
        # Check for player
        if self.player.x == x and self.player.y == y:
            return False
        
        # Check for enemies
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return False
                
        return True
    
    def to_dict(self):
        return {
            "seed": self.seed,
            "step": self.step,
            "player": self.player.to_dict(),
            "enemies": [enemy.to_dict() for enemy in self.enemies],
            "tiles": self.tiles,
            "pickups": [pickup.to_dict() for pickup in self.pickups],
            "effects_queue": [effect.to_dict() for effect in self.effects_queue],
            "flawless_turns": self.flawless_turns,
            "artifacts": self.artifacts
        }
    
    @classmethod
    def from_dict(cls, data):
        state = cls()
        state.seed = data["seed"]
        state.step = data["step"]
        state.player = Player.from_dict(data["player"])
        state.enemies = [Enemy.from_dict(e) for e in data["enemies"]]
        state.tiles = data["tiles"]
        state.pickups = [Pickup.from_dict(p) for p in data["pickups"]]
        state.effects_queue = [Effect.from_dict(e) for e in data["effects_queue"]]
        state.flawless_turns = data.get("flawless_turns", 0)
        state.artifacts = data.get("artifacts", [])
        return state

class NeonGridcrawler:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Neon Gridcrawler")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load or create game state
        self.game_state = self.load_latest_state()
        if not self.game_state.enemies:
            self.game_state.spawn_enemies()
        
        self.running = True
        self.glow_surfaces = {}
        
    def load_latest_state(self) -> GameState:
        """Load the latest game state from JSON files or create new"""
        json_files = [f for f in os.listdir('.') if f.startswith('game_state_step_') and f.endswith('.json')]
        
        if json_files:
            # Sort by step number and load the latest
            json_files.sort(key=lambda x: int(x.split('_')[3].split('.')[0]))
            latest_file = json_files[-1]
            try:
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    print(f"Loaded game state from {latest_file}")
                    return GameState.from_dict(data)
            except Exception as e:
                print(f"Error loading {latest_file}: {e}")
        
        print("Creating new game state")
        return GameState()
    
    def save_state(self):
        """Save current game state to JSON"""
        filename = f"game_state_step_{self.game_state.step}.json"
        with open(filename, 'w') as f:
            json.dump(self.game_state.to_dict(), f, indent=2)
        print(f"Saved game state to {filename}")
    
    def create_glow_surface(self, color: Tuple[int, int, int], size: int = 64) -> pygame.Surface:
        """Create a glowing effect surface"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        for radius in range(center, 0, -2):
            alpha = max(0, 255 - (center - radius) * 8)
            glow_color = (*color, alpha)
            pygame.draw.circle(surface, glow_color, (center, center), radius)
            
        return surface
    
    def handle_input(self) -> bool:
        """Handle input events and return True if a game tick should occur"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Movement with WASD
                moved = False
                new_x, new_y = self.game_state.player.x, self.game_state.player.y
                
                if event.key == pygame.K_w:
                    new_y -= 1
                elif event.key == pygame.K_s:
                    new_y += 1
                elif event.key == pygame.K_a:
                    new_x -= 1
                elif event.key == pygame.K_d:
                    new_x += 1
                elif event.key == pygame.K_SPACE:
                    self.handle_interact()
                    return True
                elif event.key == pygame.K_r:
                    # Restart game
                    self.game_state = GameState()
                    self.game_state.spawn_enemies()
                    return True
                
                # Try to move player
                if new_x != self.game_state.player.x or new_y != self.game_state.player.y:
                    if self.game_state.is_position_free(new_x, new_y):
                        self.game_state.player.x = new_x
                        self.game_state.player.y = new_y
                        self.handle_tile_interaction()
                        moved = True
                
                if moved:
                    return True
                    
        return False
    
    def handle_interact(self):
        """Handle space key interaction"""
        # Check for pickups at player position
        player_pos = (self.game_state.player.x, self.game_state.player.y)
        for pickup in self.game_state.pickups[:]:
            if pickup.x == player_pos[0] and pickup.y == player_pos[1]:
                self.game_state.player.score += pickup.value * self.game_state.player.combo_multiplier
                self.game_state.pickups.remove(pickup)
                self.add_effect("collect", pickup.x, pickup.y, NEON_GREEN)
    
    def handle_tile_interaction(self):
        """Handle interaction with tiles the player steps on"""
        tile_key = f"{self.game_state.player.x},{self.game_state.player.y}"
        tile_type = self.game_state.tiles.get(tile_key, TileType.EMPTY.value)
        
        if tile_type == TileType.CRYSTAL.value:
            # Collect crystal
            self.game_state.player.score += 100 * self.game_state.player.combo_multiplier
            self.game_state.tiles[tile_key] = TileType.EMPTY.value
            self.add_effect("crystal", self.game_state.player.x, self.game_state.player.y, NEON_CYAN)
            
        elif tile_type == TileType.TELEPORTER.value:
            # Random teleport
            for _ in range(100):  # Try to find a safe spot
                x, y = random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2)
                if self.game_state.is_position_free(x, y):
                    self.game_state.player.x = x
                    self.game_state.player.y = y
                    self.add_effect("teleport", x, y, NEON_PINK)
                    break
                    
        elif tile_type == TileType.HAZARD.value:
            # Take damage
            self.game_state.player.hp -= 20
            self.add_effect("damage", self.game_state.player.x, self.game_state.player.y, NEON_ORANGE)
    
    def add_effect(self, effect_type: str, x: int, y: int, color: Tuple[int, int, int]):
        """Add visual effect to queue"""
        self.game_state.effects_queue.append(Effect(effect_type, x, y, 30, color))
    
    def update_enemies(self):
        """Update enemy AI after player action"""
        for enemy in self.game_state.enemies:
            # Simple AI: move towards player
            dx = self.game_state.player.x - enemy.x
            dy = self.game_state.player.y - enemy.y
            
            move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
            move_y = 0 if dy == 0 else (1 if dy > 0 else -1)
            
            # Try to move towards player
            new_x = enemy.x + move_x
            new_y = enemy.y + move_y
            
            if self.game_state.is_position_free(new_x, new_y):
                enemy.x = new_x
                enemy.y = new_y
            elif self.game_state.is_position_free(enemy.x + move_x, enemy.y):
                enemy.x += move_x
            elif self.game_state.is_position_free(enemy.x, enemy.y + move_y):
                enemy.y += move_y
    
    def update_effects(self):
        """Update visual effects"""
        for effect in self.game_state.effects_queue[:]:
            effect.duration -= 1
            if effect.duration <= 0:
                self.game_state.effects_queue.remove(effect)
    
    def game_tick(self):
        """Execute one game tick"""
        self.game_state.step += 1
        self.update_enemies()
        self.update_effects()
        self.save_state()
    
    def render(self):
        """Render the game"""
        self.screen.fill(DARK_PURPLE)
        
        # Draw grid
        for x in range(GRID_WIDTH + 1):
            start_pos = (x * GRID_SIZE, 0)
            end_pos = (x * GRID_SIZE, GRID_HEIGHT * GRID_SIZE)
            pygame.draw.line(self.screen, GRID_COLOR, start_pos, end_pos, 1)
            
        for y in range(GRID_HEIGHT + 1):
            start_pos = (0, y * GRID_SIZE)
            end_pos = (GRID_WIDTH * GRID_SIZE, y * GRID_SIZE)
            pygame.draw.line(self.screen, GRID_COLOR, start_pos, end_pos, 1)
        
        # Draw tiles
        for tile_key, tile_type in self.game_state.tiles.items():
            x, y = map(int, tile_key.split(','))
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            if tile_type == TileType.WALL.value:
                pygame.draw.rect(self.screen, NEON_BLUE, rect)
            elif tile_type == TileType.CRYSTAL.value:
                pygame.draw.rect(self.screen, NEON_CYAN, rect)
            elif tile_type == TileType.TELEPORTER.value:
                pygame.draw.rect(self.screen, NEON_PINK, rect)
            elif tile_type == TileType.HAZARD.value:
                pygame.draw.rect(self.screen, NEON_ORANGE, rect)
        
        # Draw enemies
        for enemy in self.game_state.enemies:
            rect = pygame.Rect(enemy.x * GRID_SIZE + 4, enemy.y * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)
            color = NEON_ORANGE if enemy.type == "tracker" else NEON_PINK
            pygame.draw.rect(self.screen, color, rect)
        
        # Draw player
        player_rect = pygame.Rect(
            self.game_state.player.x * GRID_SIZE + 2, 
            self.game_state.player.y * GRID_SIZE + 2, 
            GRID_SIZE - 4, GRID_SIZE - 4
        )
        pygame.draw.rect(self.screen, NEON_GREEN, player_rect)
        
        # Draw effects
        for effect in self.game_state.effects_queue:
            alpha = min(255, effect.duration * 8)
            effect_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            color_with_alpha = (*effect.color, alpha)
            pygame.draw.circle(effect_surface, color_with_alpha, (GRID_SIZE//2, GRID_SIZE//2), GRID_SIZE//2)
            self.screen.blit(effect_surface, (effect.x * GRID_SIZE, effect.y * GRID_SIZE))
        
        # Draw UI
        self.render_ui()
        
        pygame.display.flip()
    
    def render_ui(self):
        """Render the user interface"""
        ui_x = GRID_WIDTH * GRID_SIZE + 20
        
        # Score
        score_text = self.font.render(f"Score: {self.game_state.player.score}", True, NEON_CYAN)
        self.screen.blit(score_text, (ui_x, 20))
        
        # HP
        hp_text = self.font.render(f"HP: {self.game_state.player.hp}/{self.game_state.player.max_hp}", True, NEON_GREEN)
        self.screen.blit(hp_text, (ui_x, 60))
        
        # Combo
        combo_text = self.font.render(f"Combo: x{self.game_state.player.combo_multiplier}", True, NEON_PINK)
        self.screen.blit(combo_text, (ui_x, 100))
        
        # Step
        step_text = self.small_font.render(f"Step: {self.game_state.step}", True, NEON_BLUE)
        self.screen.blit(step_text, (ui_x, 140))
        
        # Controls
        controls = [
            "WASD: Move",
            "Space: Interact", 
            "R: Restart"
        ]
        
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, PURPLE_GLOW)
            self.screen.blit(text, (ui_x, 200 + i * 25))
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle input and check if a game tick should occur
            if self.handle_input():
                self.game_tick()
            
            # Check for game over
            if self.game_state.player.hp <= 0:
                print("Game Over! Restarting...")
                self.game_state = GameState()
                self.game_state.spawn_enemies()
            
            # Render
            self.render()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = NeonGridcrawler()
    game.run()

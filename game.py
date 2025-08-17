import pygame
import json
import math
import random
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TILE_SIZE = 64
GRID_WIDTH = 15
GRID_HEIGHT = 12

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)

# Noir color scheme
FLOOR_COLOR = (32, 32, 48)
WALL_COLOR = (24, 24, 32)
GUARD_COLOR = (160, 80, 80)
PLAYER_COLOR = (80, 160, 80)
LOOT_COLOR = (255, 215, 0)
LIGHT_COLOR = (255, 255, 180)
SHADOW_COLOR = (16, 16, 24)

class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

@dataclass
class Player:
    x: int
    y: int
    inventory: List[str]
    stealth_streak: int = 0
    
    def move(self, dx: int, dy: int, grid_width: int, grid_height: int) -> bool:
        new_x = max(0, min(grid_width - 1, self.x + dx))
        new_y = max(0, min(grid_height - 1, self.y + dy))
        
        if new_x != self.x or new_y != self.y:
            self.x = new_x
            self.y = new_y
            return True
        return False

@dataclass
class Guard:
    x: int
    y: int
    route: List[Tuple[int, int]]
    route_index: int
    alert: bool
    direction: Direction
    vision_range: int = 4
    
    def patrol(self):
        if self.route and len(self.route) > 0:
            self.route_index = (self.route_index + 1) % len(self.route)
            target_x, target_y = self.route[self.route_index]
            
            # Calculate direction to target
            dx = target_x - self.x
            dy = target_y - self.y
            
            if dx > 0:
                self.direction = Direction.EAST
            elif dx < 0:
                self.direction = Direction.WEST
            elif dy > 0:
                self.direction = Direction.SOUTH
            elif dy < 0:
                self.direction = Direction.NORTH
            
            self.x = target_x
            self.y = target_y
    
    def can_see_position(self, target_x: int, target_y: int, walls: List[List[bool]]) -> bool:
        # Calculate distance
        distance = math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2)
        if distance > self.vision_range:
            return False
        
        # Check if target is in front of guard
        dx = target_x - self.x
        dy = target_y - self.y
        
        if self.direction == Direction.NORTH and dy >= 0:
            return False
        elif self.direction == Direction.SOUTH and dy <= 0:
            return False
        elif self.direction == Direction.EAST and dx <= 0:
            return False
        elif self.direction == Direction.WEST and dx >= 0:
            return False
        
        # Line of sight check
        steps = int(distance * 2)
        for i in range(steps):
            t = i / steps if steps > 0 else 0
            check_x = int(self.x + dx * t)
            check_y = int(self.y + dy * t)
            
            if 0 <= check_x < len(walls) and 0 <= check_y < len(walls[0]):
                if walls[check_x][check_y]:
                    return False
        
        return True

@dataclass
class Loot:
    id: str
    x: int
    y: int
    value: int
    taken: bool
    name: str

class GameState:
    def __init__(self):
        self.seed = random.randint(0, 999999)
        self.step = 0
        self.player = Player(1, 1, [])
        self.guards = []
        self.loot = []
        self.walls = []
        self.score = 0
        self.stealth_bonus_multiplier = 1.0
        self.game_over = False
        self.win = False
        self.visibility_mask = []
        
        self.initialize_level()
    
    def initialize_level(self):
        # Create walls (simple border + some internal walls)
        self.walls = [[False for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        
        # Border walls
        for x in range(GRID_WIDTH):
            self.walls[x][0] = True
            self.walls[x][GRID_HEIGHT-1] = True
        for y in range(GRID_HEIGHT):
            self.walls[0][y] = True
            self.walls[GRID_WIDTH-1][y] = True
        
        # Some internal walls for museum layout
        for x in range(3, 6):
            self.walls[x][3] = True
        for x in range(8, 11):
            self.walls[x][7] = True
        for y in range(2, 5):
            self.walls[5][y] = True
        for y in range(6, 9):
            self.walls[9][y] = True
        
        # Initialize guards with patrol routes
        self.guards = [
            Guard(4, 6, [(4, 6), (7, 6), (7, 9), (4, 9)], 0, False, Direction.EAST),
            Guard(10, 3, [(10, 3), (12, 3), (12, 5), (10, 5)], 0, False, Direction.EAST),
            Guard(3, 10, [(3, 10), (6, 10), (6, 8), (3, 8)], 0, False, Direction.EAST)
        ]
        
        # Initialize loot
        self.loot = [
            Loot("mona_lisa", 6, 4, 1000, False, "Mona Lisa"),
            Loot("starry_night", 11, 6, 800, False, "Starry Night"),
            Loot("scream", 8, 3, 600, False, "The Scream"),
            Loot("venus", 4, 8, 700, False, "Venus de Milo"),
            Loot("thinking_man", 13, 4, 500, False, "The Thinker")
        ]
        
        # Initialize visibility mask
        self.visibility_mask = [[False for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self.update_visibility()
    
    def update_visibility(self):
        # Reset visibility
        self.visibility_mask = [[False for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        
        # Mark areas visible to guards
        for guard in self.guards:
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if guard.can_see_position(x, y, self.walls):
                        self.visibility_mask[x][y] = True
    
    def move_player(self, dx: int, dy: int) -> bool:
        old_x, old_y = self.player.x, self.player.y
        
        # Check if new position is valid (not a wall)
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and 
            not self.walls[new_x][new_y]):
            
            if self.player.move(dx, dy, GRID_WIDTH, GRID_HEIGHT):
                self.step += 1
                
                # Check if player is in light
                if self.visibility_mask[self.player.x][self.player.y]:
                    self.player.stealth_streak = 0
                    self.stealth_bonus_multiplier = 1.0
                    # Check if any guard can see the player
                    for guard in self.guards:
                        if guard.can_see_position(self.player.x, self.player.y, self.walls):
                            guard.alert = True
                            self.game_over = True
                else:
                    self.player.stealth_streak += 1
                    self.stealth_bonus_multiplier = 1.0 + (self.player.stealth_streak * 0.1)
                
                # Move guards after player moves
                for guard in self.guards:
                    guard.patrol()
                
                # Update visibility after guards move
                self.update_visibility()
                
                # Save game state
                self.save_state()
                return True
        
        return False
    
    def try_steal_loot(self):
        for loot_item in self.loot:
            if (not loot_item.taken and 
                abs(loot_item.x - self.player.x) <= 1 and 
                abs(loot_item.y - self.player.y) <= 1):
                
                loot_item.taken = True
                self.player.inventory.append(loot_item.id)
                self.score += int(loot_item.value * self.stealth_bonus_multiplier)
                
                # Check win condition
                if all(loot.taken for loot in self.loot):
                    self.win = True
                
                self.step += 1
                self.save_state()
                return True
        return False
    
    def save_state(self):
        state_dict = {
            "seed": self.seed,
            "step": self.step,
            "player": {
                "x": self.player.x,
                "y": self.player.y,
                "inventory": self.player.inventory,
                "stealth_streak": self.player.stealth_streak
            },
            "guards": [
                {
                    "x": guard.x,
                    "y": guard.y,
                    "route": guard.route,
                    "route_index": guard.route_index,
                    "alert": guard.alert,
                    "direction": guard.direction.name,
                    "vision_range": guard.vision_range
                } for guard in self.guards
            ],
            "loot": [
                {
                    "id": loot.id,
                    "x": loot.x,
                    "y": loot.y,
                    "value": loot.value,
                    "taken": loot.taken,
                    "name": loot.name
                } for loot in self.loot
            ],
            "score": self.score,
            "stealth_bonus_multiplier": self.stealth_bonus_multiplier,
            "game_over": self.game_over,
            "win": self.win,
            "visibility_mask": self.visibility_mask
        }
        
        filename = f"game_state_step_{self.step}.json"
        with open(filename, 'w') as f:
            json.dump(state_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        game_state = cls()
        game_state.seed = data["seed"]
        game_state.step = data["step"]
        
        # Load player
        player_data = data["player"]
        game_state.player = Player(
            player_data["x"],
            player_data["y"],
            player_data["inventory"],
            player_data.get("stealth_streak", 0)
        )
        
        # Load guards
        game_state.guards = []
        for guard_data in data["guards"]:
            direction = Direction[guard_data["direction"]]
            guard = Guard(
                guard_data["x"],
                guard_data["y"],
                guard_data["route"],
                guard_data["route_index"],
                guard_data["alert"],
                direction,
                guard_data.get("vision_range", 4)
            )
            game_state.guards.append(guard)
        
        # Load loot
        game_state.loot = []
        for loot_data in data["loot"]:
            loot = Loot(
                loot_data["id"],
                loot_data["x"],
                loot_data["y"],
                loot_data["value"],
                loot_data["taken"],
                loot_data["name"]
            )
            game_state.loot.append(loot)
        
        game_state.score = data.get("score", 0)
        game_state.stealth_bonus_multiplier = data.get("stealth_bonus_multiplier", 1.0)
        game_state.game_over = data.get("game_over", False)
        game_state.win = data.get("win", False)
        game_state.visibility_mask = data.get("visibility_mask", [])
        
        # Initialize walls (assuming same layout)
        game_state.initialize_level()
        
        return game_state

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def iso_to_screen(self, x: int, y: int) -> Tuple[int, int]:
        # Convert grid coordinates to isometric screen coordinates
        iso_x = (x - y) * TILE_SIZE // 2 + SCREEN_WIDTH // 2
        iso_y = (x + y) * TILE_SIZE // 4 + 100
        return iso_x, iso_y
    
    def draw_tile(self, x: int, y: int, color: Tuple[int, int, int], border_color: Optional[Tuple[int, int, int]] = None):
        iso_x, iso_y = self.iso_to_screen(x, y)
        
        # Diamond shape for isometric tile
        points = [
            (iso_x, iso_y),
            (iso_x + TILE_SIZE // 2, iso_y + TILE_SIZE // 4),
            (iso_x, iso_y + TILE_SIZE // 2),
            (iso_x - TILE_SIZE // 2, iso_y + TILE_SIZE // 4)
        ]
        
        pygame.draw.polygon(self.screen, color, points)
        if border_color is not None:
            pygame.draw.polygon(self.screen, border_color, points, 2)
    
    def draw_character(self, x: int, y: int, color: Tuple[int, int, int], char: Optional[str] = None):
        iso_x, iso_y = self.iso_to_screen(x, y)
        
        # Draw character as circle
        pygame.draw.circle(self.screen, color, (iso_x, iso_y - 10), 15)
        pygame.draw.circle(self.screen, BLACK, (iso_x, iso_y - 10), 15, 2)
        
        if char is not None:
            text = self.small_font.render(char, True, WHITE)
            text_rect = text.get_rect(center=(iso_x, iso_y - 10))
            self.screen.blit(text, text_rect)
    
    def draw_loot(self, x: int, y: int, taken: bool, name: str):
        if taken:
            return
            
        iso_x, iso_y = self.iso_to_screen(x, y)
        
        # Draw loot as golden rectangle
        rect = pygame.Rect(iso_x - 8, iso_y - 8, 16, 16)
        pygame.draw.rect(self.screen, LOOT_COLOR, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        
        # Draw loot name
        text = self.small_font.render(name[:8], True, WHITE)
        text_rect = text.get_rect(center=(iso_x, iso_y + 20))
        self.screen.blit(text, text_rect)
    
    def draw_vision_cone(self, guard: Guard):
        iso_x, iso_y = self.iso_to_screen(guard.x, guard.y)
        
        # Draw vision cone based on direction
        cone_length = guard.vision_range * TILE_SIZE // 2
        cone_width = guard.vision_range * TILE_SIZE // 4
        
        dx, dy = guard.direction.value
        
        # Calculate cone points
        end_x = iso_x + dx * cone_length
        end_y = iso_y + dy * cone_length // 2
        
        if guard.direction in [Direction.NORTH, Direction.SOUTH]:
            left_x = end_x - cone_width
            right_x = end_x + cone_width
            left_y = right_y = end_y
        else:  # EAST, WEST
            left_y = end_y - cone_width
            right_y = end_y + cone_width
            left_x = right_x = end_x
        
        points = [
            (iso_x, iso_y),
            (left_x, left_y),
            (right_x, right_y)
        ]
        
        # Draw semi-transparent vision cone
        cone_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        cone_surface.set_alpha(50)
        pygame.draw.polygon(cone_surface, LIGHT_COLOR, points)
        self.screen.blit(cone_surface, (0, 0))
    
    def render(self, game_state: GameState):
        self.screen.fill(SHADOW_COLOR)
        
        # Draw floor tiles
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if game_state.walls[x][y]:
                    self.draw_tile(x, y, WALL_COLOR, DARK_GRAY)
                else:
                    floor_color = FLOOR_COLOR
                    if game_state.visibility_mask[x][y]:
                        # Lighter floor in guard vision
                        floor_color = (min(255, FLOOR_COLOR[0] + 40),
                                     min(255, FLOOR_COLOR[1] + 40),
                                     min(255, FLOOR_COLOR[2] + 40))
                    self.draw_tile(x, y, floor_color)
        
        # Draw vision cones
        for guard in game_state.guards:
            self.draw_vision_cone(guard)
        
        # Draw loot
        for loot in game_state.loot:
            self.draw_loot(loot.x, loot.y, loot.taken, loot.name)
        
        # Draw guards
        for guard in game_state.guards:
            color = RED if guard.alert else GUARD_COLOR
            self.draw_character(guard.x, guard.y, color, "G")
        
        # Draw player
        self.draw_character(game_state.player.x, game_state.player.y, PLAYER_COLOR, "P")
        
        # Draw UI
        self.draw_ui(game_state)
    
    def draw_ui(self, game_state: GameState):
        # Score
        score_text = self.font.render(f"Score: {game_state.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Stealth bonus
        bonus_text = self.font.render(f"Stealth Bonus: {game_state.stealth_bonus_multiplier:.1f}x", True, WHITE)
        self.screen.blit(bonus_text, (10, 40))
        
        # Streak
        streak_text = self.font.render(f"Stealth Streak: {game_state.player.stealth_streak}", True, WHITE)
        self.screen.blit(streak_text, (10, 70))
        
        # Inventory
        inv_text = self.font.render(f"Stolen: {len(game_state.player.inventory)}/{len(game_state.loot)}", True, WHITE)
        self.screen.blit(inv_text, (10, 100))
        
        # Controls
        controls = [
            "Controls:",
            "WASD - Move",
            "SPACE - Steal/Hide",
            "ESC - Quit"
        ]
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, LIGHT_GRAY)
            self.screen.blit(control_text, (SCREEN_WIDTH - 150, 10 + i * 20))
        
        # Game status
        if game_state.game_over:
            game_over_text = self.font.render("CAUGHT! Game Over", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
        elif game_state.win:
            win_text = self.font.render("HEIST COMPLETE! You Win!", True, GREEN)
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(win_text, text_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Museum Heist")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        
        # Try to load existing game state or create new one
        self.game_state = self.load_latest_state()
        
        self.running = True
    
    def load_latest_state(self) -> GameState:
        # Look for existing game state files
        state_files = [f for f in os.listdir('.') if f.startswith('game_state_step_') and f.endswith('.json')]
        
        if state_files:
            # Load the latest state
            state_files.sort(key=lambda x: int(x.split('_')[3].split('.')[0]))
            latest_file = state_files[-1]
            print(f"Loading game state from {latest_file}")
            return GameState.load_from_file(latest_file)
        else:
            print("No existing game state found, creating new game")
            return GameState()
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif not self.game_state.game_over and not self.game_state.win:
                    if event.key == pygame.K_w:
                        self.game_state.move_player(0, -1)
                    elif event.key == pygame.K_s:
                        self.game_state.move_player(0, 1)
                    elif event.key == pygame.K_a:
                        self.game_state.move_player(-1, 0)
                    elif event.key == pygame.K_d:
                        self.game_state.move_player(1, 0)
                    elif event.key == pygame.K_SPACE:
                        self.game_state.try_steal_loot()
    
    def run(self):
        while self.running:
            self.handle_input()
            self.renderer.render(self.game_state)
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

"""
CLOCKWORK CRYPTS
A puzzle-crawler where every 6th move the whole board "ticks" gears one notch.
Plan routes so moving platforms and doors align.
"""

import pygame
import sys
import json
import os
import random
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
GRID_SIZE = 12
TILE_SIZE = 48
GRID_OFFSET_X = 100
GRID_OFFSET_Y = 100

# Colors - Brass, marble and shadow theme
BRASS_GOLD = (218, 165, 32)
BRASS_DARK = (184, 134, 11)
MARBLE_WHITE = (248, 248, 255)
MARBLE_GRAY = (220, 220, 220)
SHADOW_BLACK = (20, 20, 20)
SHADOW_GRAY = (60, 60, 60)
GEAR_BRONZE = (205, 127, 50)
EMERALD_GREEN = (80, 200, 120)
RUBY_RED = (200, 80, 80)

class TileType(Enum):
    EMPTY = "empty"
    WALL = "wall"
    PLAYER = "player"
    GEAR = "gear"
    DOOR = "door"
    LEVER = "lever"
    TREASURE = "treasure"
    MOVING_PLATFORM = "moving_platform"
    EXIT = "exit"

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

@dataclass
class GearNode:
    """Represents a gear in the clockwork system"""
    x: int
    y: int
    phase: int  # 0-3 rotation phase
    connections: List[int]  # indices of connected gears

@dataclass
class Door:
    """Door that opens/closes based on gear phases"""
    x: int
    y: int
    required_phase: int
    gear_id: int
    is_open: bool = False

@dataclass
class Lever:
    """Lever that can be operated to affect gears"""
    x: int
    y: int
    target_gear_id: int
    is_activated: bool = False

@dataclass
class MovingPlatform:
    """Platform that moves based on gear rotations"""
    x: int
    y: int
    target_x: int
    target_y: int
    gear_id: int
    move_on_phase: int

@dataclass
class Treasure:
    """Collectible treasure"""
    x: int
    y: int
    value: int
    collected: bool = False

@dataclass
class GameState:
    """Complete serializable game state"""
    player_x: int
    player_y: int
    tick_count: int
    action_count: int
    score: int
    key_fragments: int
    level: int
    
    # Grid data
    grid: List[List[str]]  # TileType.value strings
    
    # Gear system
    gear_nodes: List[Dict[str, Any]]  # GearNode as dict
    doors: List[Dict[str, Any]]  # Door as dict
    levers: List[Dict[str, Any]]  # Lever as dict
    moving_platforms: List[Dict[str, Any]]  # MovingPlatform as dict
    treasures: List[Dict[str, Any]]  # Treasure as dict
    
    # Game metadata
    level_start_time: float
    move_streak: int
    max_moves_for_bonus: int

class ClockworkCrypts:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Clockwork Crypts")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize or load game state
        self.game_state = self.load_or_create_game_state()
        self.step_counter = 0
        
        # Visual effects
        self.vignette_alpha = 0
        self.tick_animation_timer = 0
        
        # Create background surface for cogs
        self.background = self.create_background()
        
    def load_or_create_game_state(self) -> GameState:
        """Load game state from JSON or create new one"""
        json_files = [f for f in os.listdir('.') if f.startswith('game_state_') and f.endswith('.json')]
        
        if json_files:
            # Load the most recent state file
            latest_file = max(json_files, key=lambda f: os.path.getmtime(f))
            try:
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    return self.dict_to_game_state(data)
            except Exception as e:
                print(f"Error loading {latest_file}: {e}")
        
        # Create new random game state
        return self.create_random_game_state()
    
    def dict_to_game_state(self, data: Dict[str, Any]) -> GameState:
        """Convert dictionary to GameState object"""
        return GameState(**data)
    
    def create_random_game_state(self) -> GameState:
        """Create a new random game state"""
        # Initialize empty grid
        grid = [[TileType.EMPTY.value for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Place walls around perimeter
        for i in range(GRID_SIZE):
            grid[0][i] = TileType.WALL.value
            grid[GRID_SIZE-1][i] = TileType.WALL.value
            grid[i][0] = TileType.WALL.value
            grid[i][GRID_SIZE-1] = TileType.WALL.value
        
        # Place some random walls
        for _ in range(10):
            x, y = random.randint(2, GRID_SIZE-3), random.randint(2, GRID_SIZE-3)
            grid[y][x] = TileType.WALL.value
        
        # Create gear system
        gear_nodes = []
        doors = []
        levers = []
        moving_platforms = []
        treasures = []
        
        # Place 3-5 gears
        gear_count = random.randint(3, 5)
        for i in range(gear_count):
            while True:
                x, y = random.randint(2, GRID_SIZE-3), random.randint(2, GRID_SIZE-3)
                if grid[y][x] == TileType.EMPTY.value:
                    grid[y][x] = TileType.GEAR.value
                    gear_nodes.append(asdict(GearNode(
                        x=x, y=y, phase=random.randint(0, 3),
                        connections=[]  # Will be filled later
                    )))
                    break
        
        # Connect gears randomly
        for i, gear in enumerate(gear_nodes):
            for j, other_gear in enumerate(gear_nodes):
                if i != j and random.random() < 0.3:  # 30% chance to connect
                    gear['connections'].append(j)
        
        # Place doors linked to gears
        for i in range(min(3, len(gear_nodes))):
            while True:
                x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
                if grid[y][x] == TileType.EMPTY.value:
                    grid[y][x] = TileType.DOOR.value
                    doors.append(asdict(Door(
                        x=x, y=y, 
                        required_phase=random.randint(0, 3),
                        gear_id=i,
                        is_open=False
                    )))
                    break
        
        # Place levers
        for i in range(min(2, len(gear_nodes))):
            while True:
                x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
                if grid[y][x] == TileType.EMPTY.value:
                    grid[y][x] = TileType.LEVER.value
                    levers.append(asdict(Lever(
                        x=x, y=y,
                        target_gear_id=i,
                        is_activated=False
                    )))
                    break
        
        # Place treasures
        for _ in range(5):
            while True:
                x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
                if grid[y][x] == TileType.EMPTY.value:
                    grid[y][x] = TileType.TREASURE.value
                    treasures.append(asdict(Treasure(
                        x=x, y=y,
                        value=random.randint(10, 50),
                        collected=False
                    )))
                    break
        
        # Place exit
        while True:
            x, y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
            if grid[y][x] == TileType.EMPTY.value:
                grid[y][x] = TileType.EXIT.value
                break
        
        # Place player
        player_x, player_y = 1, 1
        while grid[player_y][player_x] != TileType.EMPTY.value:
            player_x, player_y = random.randint(1, GRID_SIZE-2), random.randint(1, GRID_SIZE-2)
        
        return GameState(
            player_x=player_x,
            player_y=player_y,
            tick_count=0,
            action_count=0,
            score=0,
            key_fragments=0,
            level=1,
            grid=grid,
            gear_nodes=gear_nodes,
            doors=doors,
            levers=levers,
            moving_platforms=moving_platforms,
            treasures=treasures,
            level_start_time=pygame.time.get_ticks(),
            move_streak=0,
            max_moves_for_bonus=30
        )
    
    def save_game_state(self):
        """Save current game state to JSON"""
        self.step_counter += 1
        filename = f"game_state_step_{self.step_counter}.json"
        
        # Convert GameState to dict for JSON serialization
        state_dict = asdict(self.game_state)
        
        with open(filename, 'w') as f:
            json.dump(state_dict, f, indent=2)
        
        print(f"Game state saved to {filename}")
    
    def create_background(self):
        """Create parallax background with cogs"""
        bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        bg.fill(SHADOW_BLACK)
        
        # Draw large background cogs
        for i in range(5):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            radius = random.randint(50, 120)
            self.draw_gear(bg, x, y, radius, random.randint(0, 3), alpha=30)
        
        return bg
    
    def draw_gear(self, surface, x, y, radius, phase, alpha=255):
        """Draw a decorative gear"""
        gear_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        
        # Main gear body
        color = (*GEAR_BRONZE, alpha)
        pygame.draw.circle(gear_surface, color, (radius, radius), radius)
        pygame.draw.circle(gear_surface, (*BRASS_DARK, alpha), (radius, radius), radius, 3)
        
        # Gear teeth
        teeth = 8
        for i in range(teeth):
            angle = (i * 360 / teeth + phase * 45) * math.pi / 180
            tooth_x = radius + int((radius + 10) * math.cos(angle))
            tooth_y = radius + int((radius + 10) * math.sin(angle))
            pygame.draw.circle(gear_surface, color, (tooth_x, tooth_y), 8)
        
        # Center hole
        pygame.draw.circle(gear_surface, (*SHADOW_BLACK, alpha), (radius, radius), radius//3)
        
        surface.blit(gear_surface, (x-radius, y-radius))
    
    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            moved = False
            
            if event.key == pygame.K_w:
                moved = self.try_move(Direction.UP)
            elif event.key == pygame.K_s:
                moved = self.try_move(Direction.DOWN)
            elif event.key == pygame.K_a:
                moved = self.try_move(Direction.LEFT)
            elif event.key == pygame.K_d:
                moved = self.try_move(Direction.RIGHT)
            elif event.key == pygame.K_SPACE:
                moved = self.operate_adjacent_or_wait()
            
            if moved:
                self.game_state.action_count += 1
                self.game_state.move_streak += 1
                
                # Check for gear tick every 6 actions
                if self.game_state.action_count % 6 == 0:
                    self.tick_gears()
                
                self.save_game_state()
    
    def try_move(self, direction: Direction) -> bool:
        """Try to move player in given direction"""
        dx, dy = direction.value
        new_x = self.game_state.player_x + dx
        new_y = self.game_state.player_y + dy
        
        # Check bounds
        if new_x < 0 or new_x >= GRID_SIZE or new_y < 0 or new_y >= GRID_SIZE:
            return False
        
        # Check what's at the target position
        target_tile = self.game_state.grid[new_y][new_x]
        
        if target_tile == TileType.WALL.value:
            return False
        elif target_tile == TileType.DOOR.value:
            # Check if door is open
            door = self.get_door_at(new_x, new_y)
            if not door or not door['is_open']:
                return False
        
        # Move player
        self.game_state.player_x = new_x
        self.game_state.player_y = new_y
        
        # Check for treasure collection
        if target_tile == TileType.TREASURE.value:
            treasure = self.get_treasure_at(new_x, new_y)
            if treasure and not treasure['collected']:
                treasure['collected'] = True
                self.game_state.score += treasure['value']
                self.game_state.key_fragments += 1
                self.game_state.grid[new_y][new_x] = TileType.EMPTY.value
        
        # Check for exit
        if target_tile == TileType.EXIT.value:
            self.complete_level()
        
        return True
    
    def operate_adjacent_or_wait(self) -> bool:
        """Operate adjacent lever or just wait"""
        # Check adjacent tiles for levers
        for direction in Direction:
            dx, dy = direction.value
            check_x = self.game_state.player_x + dx
            check_y = self.game_state.player_y + dy
            
            if (0 <= check_x < GRID_SIZE and 0 <= check_y < GRID_SIZE and 
                self.game_state.grid[check_y][check_x] == TileType.LEVER.value):
                
                lever = self.get_lever_at(check_x, check_y)
                if lever:
                    lever['is_activated'] = not lever['is_activated']
                    # Advance target gear by one phase
                    if lever['target_gear_id'] < len(self.game_state.gear_nodes):
                        gear = self.game_state.gear_nodes[lever['target_gear_id']]
                        gear['phase'] = (gear['phase'] + 1) % 4
                    return True
        
        # No lever found, just wait (still counts as an action)
        return True
    
    def tick_gears(self):
        """Advance all gears by one tick"""
        self.game_state.tick_count += 1
        self.vignette_alpha = 255
        self.tick_animation_timer = 30
        
        # Rotate all gears
        for gear in self.game_state.gear_nodes:
            gear['phase'] = (gear['phase'] + 1) % 4
        
        # Update doors based on gear phases
        for door in self.game_state.doors:
            if door['gear_id'] < len(self.game_state.gear_nodes):
                gear = self.game_state.gear_nodes[door['gear_id']]
                door['is_open'] = (gear['phase'] == door['required_phase'])
        
        # Update moving platforms
        for platform in self.game_state.moving_platforms:
            if platform['gear_id'] < len(self.game_state.gear_nodes):
                gear = self.game_state.gear_nodes[platform['gear_id']]
                if gear['phase'] == platform['move_on_phase']:
                    # Swap platform position
                    old_x, old_y = platform['x'], platform['y']
                    platform['x'], platform['y'] = platform['target_x'], platform['target_y']
                    platform['target_x'], platform['target_y'] = old_x, old_y
    
    def complete_level(self):
        """Handle level completion"""
        # Bonus for completing within move limit
        if self.game_state.move_streak <= self.game_state.max_moves_for_bonus:
            bonus = 100 * (self.game_state.max_moves_for_bonus - self.game_state.move_streak)
            self.game_state.score += bonus
            self.game_state.key_fragments += 2
        
        self.game_state.level += 1
        self.game_state.move_streak = 0
        # Generate new level (simplified for now)
        self.game_state = self.create_random_game_state()
        self.game_state.level = self.game_state.level
    
    def get_door_at(self, x, y):
        """Get door at position"""
        for door in self.game_state.doors:
            if door['x'] == x and door['y'] == y:
                return door
        return None
    
    def get_lever_at(self, x, y):
        """Get lever at position"""
        for lever in self.game_state.levers:
            if lever['x'] == x and lever['y'] == y:
                return lever
        return None
    
    def get_treasure_at(self, x, y):
        """Get treasure at position"""
        for treasure in self.game_state.treasures:
            if treasure['x'] == x and treasure['y'] == y:
                return treasure
        return None
    
    def draw(self):
        """Main drawing function"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw vignette effect during tick
        if self.vignette_alpha > 0:
            vignette = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(vignette, (0, 0, 0, self.vignette_alpha), 
                             (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), WINDOW_WIDTH//2)
            self.screen.blit(vignette, (0, 0))
            self.vignette_alpha = max(0, self.vignette_alpha - 8)
        
        # Draw grid
        self.draw_grid()
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_grid(self):
        """Draw the game grid with all elements"""
        # Draw grid background
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(
                    GRID_OFFSET_X + x * TILE_SIZE,
                    GRID_OFFSET_Y + y * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )
                
                # Grid lines
                pygame.draw.rect(self.screen, MARBLE_GRAY, rect, 1)
                
                tile_type = self.game_state.grid[y][x]
                
                # Draw tiles
                if tile_type == TileType.WALL.value:
                    pygame.draw.rect(self.screen, SHADOW_GRAY, rect)
                    pygame.draw.rect(self.screen, SHADOW_BLACK, rect, 2)
                
                elif tile_type == TileType.GEAR.value:
                    gear = self.get_gear_at(x, y)
                    if gear:
                        self.draw_gear(self.screen, rect.centerx, rect.centery, 
                                     TILE_SIZE//3, gear['phase'])
                
                elif tile_type == TileType.DOOR.value:
                    door = self.get_door_at(x, y)
                    if door:
                        color = EMERALD_GREEN if door['is_open'] else RUBY_RED
                        pygame.draw.rect(self.screen, color, rect)
                        pygame.draw.rect(self.screen, BRASS_DARK, rect, 3)
                
                elif tile_type == TileType.LEVER.value:
                    lever = self.get_lever_at(x, y)
                    if lever:
                        color = BRASS_GOLD if lever['is_activated'] else BRASS_DARK
                        pygame.draw.rect(self.screen, color, rect)
                        # Draw lever handle
                        handle_rect = pygame.Rect(rect.centerx-5, rect.centery-10, 10, 20)
                        pygame.draw.rect(self.screen, MARBLE_WHITE, handle_rect)
                
                elif tile_type == TileType.TREASURE.value:
                    treasure = self.get_treasure_at(x, y)
                    if treasure and not treasure['collected']:
                        pygame.draw.circle(self.screen, BRASS_GOLD, rect.center, TILE_SIZE//4)
                        pygame.draw.circle(self.screen, BRASS_DARK, rect.center, TILE_SIZE//4, 2)
                
                elif tile_type == TileType.EXIT.value:
                    pygame.draw.rect(self.screen, EMERALD_GREEN, rect)
                    pygame.draw.rect(self.screen, MARBLE_WHITE, rect, 4)
                    # Draw exit symbol
                    pygame.draw.circle(self.screen, MARBLE_WHITE, rect.center, 8)
        
        # Draw player
        player_rect = pygame.Rect(
            GRID_OFFSET_X + self.game_state.player_x * TILE_SIZE + 8,
            GRID_OFFSET_Y + self.game_state.player_y * TILE_SIZE + 8,
            TILE_SIZE - 16, TILE_SIZE - 16
        )
        pygame.draw.ellipse(self.screen, MARBLE_WHITE, player_rect)
        pygame.draw.ellipse(self.screen, BRASS_GOLD, player_rect, 3)
    
    def get_gear_at(self, x, y):
        """Get gear at position"""
        for gear in self.game_state.gear_nodes:
            if gear['x'] == x and gear['y'] == y:
                return gear
        return None
    
    def draw_ui(self):
        """Draw user interface"""
        # Game info panel
        ui_x = GRID_OFFSET_X + GRID_SIZE * TILE_SIZE + 20
        
        # Title
        title = self.font.render("CLOCKWORK CRYPTS", True, BRASS_GOLD)
        self.screen.blit(title, (ui_x, 50))
        
        # Stats
        stats = [
            f"Level: {self.game_state.level}",
            f"Score: {self.game_state.score}",
            f"Key Fragments: {self.game_state.key_fragments}",
            f"Tick Count: {self.game_state.tick_count}",
            f"Actions: {self.game_state.action_count}",
            f"Next Tick: {6 - (self.game_state.action_count % 6)}",
            f"Move Streak: {self.game_state.move_streak}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.small_font.render(stat, True, MARBLE_WHITE)
            self.screen.blit(text, (ui_x, 100 + i * 25))
        
        # Controls
        controls = [
            "Controls:",
            "WASD - Move",
            "SPACE - Use/Wait",
            "",
            "Goal:",
            "Collect treasures",
            "Reach the exit",
            "Plan for gear ticks!"
        ]
        
        for i, control in enumerate(controls):
            color = BRASS_GOLD if control.endswith(":") else MARBLE_WHITE
            text = self.small_font.render(control, True, color)
            self.screen.blit(text, (ui_x, 300 + i * 20))
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_input(event)
            
            # Update tick animation
            if self.tick_animation_timer > 0:
                self.tick_animation_timer -= 1
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ClockworkCrypts()
    game.run()

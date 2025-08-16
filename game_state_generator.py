import random
import json
from typing import Dict, List, Tuple, Optional

def generate_random_game_state(
    seed: Optional[int] = None,
    step: int = 0,
    difficulty: float = 1.0,
    player_mods: Optional[List[str]] = None
) -> Dict:
    """
    Generate a completely random game state for Neon Gridcrawler.
    
    Args:
        seed: Random seed for reproducible generation. If None, uses random seed.
        step: Starting step number
        difficulty: Difficulty multiplier (0.5 = easy, 1.0 = normal, 2.0 = hard)
        player_mods: Optional list of player modifications/artifacts
    
    Returns:
        Dictionary containing the complete game state
    """
    
    # Constants
    GRID_WIDTH = 25
    GRID_HEIGHT = 20
    
    if seed is None:
        seed = random.randint(1, 1000000)
    
    random.seed(seed)
    
    # Generate level tiles
    tiles = {}
    
    # Initialize all tiles as empty
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            tiles[f"{x},{y}"] = "empty"
    
    # Add border walls
    for x in range(GRID_WIDTH):
        tiles[f"{x},0"] = "wall"
        tiles[f"{x},{GRID_HEIGHT-1}"] = "wall"
    for y in range(GRID_HEIGHT):
        tiles[f"0,{y}"] = "wall"
        tiles[f"{GRID_WIDTH-1},{y}"] = "wall"
    
    # Add random interior walls
    wall_count = int(random.randint(15, 30) * difficulty)
    for _ in range(wall_count):
        x = random.randint(2, GRID_WIDTH-3)
        y = random.randint(2, GRID_HEIGHT-3)
        if tiles[f"{x},{y}"] == "empty":
            tiles[f"{x},{y}"] = "wall"
    
    # Add crystals
    crystal_count = random.randint(8, 15)
    for _ in range(crystal_count):
        x = random.randint(1, GRID_WIDTH-2)
        y = random.randint(1, GRID_HEIGHT-2)
        if tiles[f"{x},{y}"] == "empty":
            tiles[f"{x},{y}"] = "crystal"
    
    # Add teleporters
    teleporter_count = random.randint(2, 4)
    for _ in range(teleporter_count):
        x = random.randint(1, GRID_WIDTH-2)
        y = random.randint(1, GRID_HEIGHT-2)
        if tiles[f"{x},{y}"] == "empty":
            tiles[f"{x},{y}"] = "teleporter"
    
    # Add hazards
    hazard_count = int(random.randint(3, 8) * difficulty)
    for _ in range(hazard_count):
        x = random.randint(1, GRID_WIDTH-2)
        y = random.randint(1, GRID_HEIGHT-2)
        if tiles[f"{x},{y}"] == "empty":
            tiles[f"{x},{y}"] = "hazard"
    
    # Find a safe starting position for player
    safe_positions = []
    for x in range(2, GRID_WIDTH-2):
        for y in range(2, GRID_HEIGHT-2):
            if tiles[f"{x},{y}"] == "empty":
                # Check 3x3 area around position
                safe_area = True
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        check_x, check_y = x + dx, y + dy
                        if f"{check_x},{check_y}" in tiles:
                            tile_type = tiles[f"{check_x},{check_y}"]
                            if tile_type in ["wall", "hazard"]:
                                safe_area = False
                                break
                    if not safe_area:
                        break
                
                if safe_area:
                    safe_positions.append((x, y))
    
    # Player starting position
    if safe_positions:
        player_x, player_y = random.choice(safe_positions)
    else:
        player_x, player_y = 5, 5  # fallback
    
    # Generate player stats
    base_hp = random.randint(80, 120)
    current_hp = random.randint(int(base_hp * 0.3), base_hp)
    
    player = {
        "x": player_x,
        "y": player_y,
        "hp": current_hp,
        "max_hp": base_hp,
        "score": random.randint(0, int(1000 * difficulty)),
        "combo_multiplier": random.randint(1, max(1, int(3 * difficulty))),
        "mods": player_mods or []
    }
    
    # Generate enemies
    enemies = []
    enemy_count = int(random.randint(3, 8) * difficulty)
    enemy_types = ["tracker", "guardian", "hunter"]
    
    for _ in range(enemy_count):
        attempts = 0
        while attempts < 100:
            x = random.randint(1, GRID_WIDTH-2)
            y = random.randint(1, GRID_HEIGHT-2)
            
            # Check if position is valid and not too close to player
            if (tiles[f"{x},{y}"] == "empty" and 
                (x != player_x or y != player_y) and
                abs(x - player_x) + abs(y - player_y) >= 4 and
                not any(e["x"] == x and e["y"] == y for e in enemies)):
                
                enemy_type = random.choice(enemy_types)
                base_hp = {"tracker": 40, "guardian": 80, "hunter": 60}[enemy_type]
                hp = int(base_hp * (0.8 + difficulty * 0.4))
                
                enemies.append({
                    "type": enemy_type,
                    "x": x,
                    "y": y,
                    "hp": hp,
                    "max_hp": hp
                })
                break
            
            attempts += 1
    
    # Generate pickups
    pickups = []
    pickup_count = random.randint(5, 12)
    pickup_types = ["artifact", "health", "score_boost", "combo_boost"]
    
    for _ in range(pickup_count):
        attempts = 0
        while attempts < 100:
            x = random.randint(1, GRID_WIDTH-2)
            y = random.randint(1, GRID_HEIGHT-2)
            
            # Check if position is valid and not occupied
            if (tiles[f"{x},{y}"] == "empty" and
                (x != player_x or y != player_y) and
                not any(e["x"] == x and e["y"] == y for e in enemies) and
                not any(p["x"] == x and p["y"] == y for p in pickups)):
                
                pickup_type = random.choice(pickup_types)
                value_map = {
                    "artifact": random.randint(500, 1000),
                    "health": random.randint(20, 40),
                    "score_boost": random.randint(200, 500),
                    "combo_boost": random.randint(1, 3)
                }
                
                pickups.append({
                    "type": pickup_type,
                    "x": x,
                    "y": y,
                    "value": value_map[pickup_type]
                })
                break
            
            attempts += 1
    
    # Generate visual effects
    effects_queue = []
    neon_colors = [(0, 255, 255), (255, 16, 240), (0, 191, 255), (57, 255, 20)]
    
    for _ in range(random.randint(0, 3)):
        effects_queue.append({
            "type": random.choice(["ambient_glow", "spark", "energy"]),
            "x": random.randint(0, GRID_WIDTH-1),
            "y": random.randint(0, GRID_HEIGHT-1),
            "duration": random.randint(10, 60),
            "color": random.choice(neon_colors)
        })
    
    # Generate artifacts
    available_artifacts = [
        "dash_boost", "chain_lightning", "shield_regen", "score_magnet",
        "combo_keeper", "crystal_vision", "enemy_fear", "teleport_safety",
        "hazard_immunity", "double_score"
    ]
    
    artifact_count = int(random.randint(0, 3) * difficulty)
    artifacts = random.sample(available_artifacts, min(artifact_count, len(available_artifacts)))
    
    # Return complete game state
    return {
        "seed": seed,
        "step": step,
        "player": player,
        "enemies": enemies,
        "tiles": tiles,
        "pickups": pickups,
        "effects_queue": effects_queue,
        "flawless_turns": random.randint(0, 5),
        "artifacts": artifacts
    }

# Example usage
if __name__ == "__main__":
    # Generate a few sample states
    easy_state = generate_random_game_state(seed=12345, difficulty=0.5)
    normal_state = generate_random_game_state(seed=67890, difficulty=1.0)
    hard_state = generate_random_game_state(seed=54321, difficulty=2.0)
    random_state = generate_random_game_state()
    
    # Save them to files
    with open("easy_game_state.json", "w") as f:
        json.dump(easy_state, f, indent=2)
    
    with open("normal_game_state.json", "w") as f:
        json.dump(normal_state, f, indent=2)
    
    with open("hard_game_state.json", "w") as f:
        json.dump(hard_state, f, indent=2)
    
    with open("random_game_state.json", "w") as f:
        json.dump(random_state, f, indent=2)
    
    print("Generated game states:")
    print(f"Easy: {len(easy_state['enemies'])} enemies, Score: {easy_state['player']['score']}")
    print(f"Normal: {len(normal_state['enemies'])} enemies, Score: {normal_state['player']['score']}")
    print(f"Hard: {len(hard_state['enemies'])} enemies, Score: {hard_state['player']['score']}")
    print(f"Random: {len(random_state['enemies'])} enemies, Score: {random_state['player']['score']}")
    print("Files saved: easy_game_state.json, normal_game_state.json, hard_game_state.json, random_game_state.json")

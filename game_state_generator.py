def generate_random_game_state():
    """Generate a random initial game state for Museum Heist without imports."""
    
    # Use hash of object id for pseudo-randomness (no imports needed)
    seed_base = abs(hash(str(id(object())))) % 1000000
    
    # Grid dimensions
    GRID_WIDTH = 15
    GRID_HEIGHT = 12
    
    # Pseudo-random number generator using hash
    def pseudo_random(seed, max_val):
        return abs(hash(str(seed))) % max_val
    
    def pseudo_random_float(seed):
        return (abs(hash(str(seed))) % 10000) / 10000.0
    
    # Generate random player position (avoiding walls)
    player_x = pseudo_random(seed_base * 7, GRID_WIDTH - 2) + 1
    player_y = pseudo_random(seed_base * 11, GRID_HEIGHT - 2) + 1
    
    # Directions
    directions = ["NORTH", "SOUTH", "EAST", "WEST"]
    
    # Generate random guards
    guards = []
    num_guards = pseudo_random(seed_base * 13, 4) + 2  # 2-5 guards
    
    for i in range(num_guards):
        guard_seed = seed_base * (i + 17)
        
        # Random guard position
        guard_x = pseudo_random(guard_seed, GRID_WIDTH - 2) + 1
        guard_y = pseudo_random(guard_seed * 3, GRID_HEIGHT - 2) + 1
        
        # Generate patrol route (3-5 points)
        route_length = pseudo_random(guard_seed * 5, 3) + 3
        route = []
        
        base_x, base_y = guard_x, guard_y
        route.append([base_x, base_y])
        
        for j in range(route_length - 1):
            route_seed = guard_seed * (j + 7)
            # Generate points within patrol area
            patrol_range = 3
            new_x = max(1, min(GRID_WIDTH - 2, base_x + pseudo_random(route_seed, patrol_range * 2) - patrol_range))
            new_y = max(1, min(GRID_HEIGHT - 2, base_y + pseudo_random(route_seed * 3, patrol_range * 2) - patrol_range))
            route.append([new_x, new_y])
        
        guard = {
            "x": guard_x,
            "y": guard_y,
            "route": route,
            "route_index": 0,
            "alert": False,
            "direction": directions[pseudo_random(guard_seed * 7, 4)],
            "vision_range": pseudo_random(guard_seed * 9, 3) + 3  # 3-5 vision range
        }
        guards.append(guard)
    
    # Generate random loot
    loot_names = [
        "Mona Lisa", "Starry Night", "The Scream", "Venus de Milo", "The Thinker",
        "Girl with Pearl", "Birth of Venus", "The Kiss", "American Gothic", "Guernica"
    ]
    
    loot_ids = [
        "mona_lisa", "starry_night", "scream", "venus", "thinking_man",
        "pearl_girl", "birth_venus", "the_kiss", "american_gothic", "guernica"
    ]
    
    loot = []
    num_loot = pseudo_random(seed_base * 19, 4) + 3  # 3-6 loot items
    
    for i in range(min(num_loot, len(loot_names))):
        loot_seed = seed_base * (i + 23)
        
        # Random loot position
        loot_x = pseudo_random(loot_seed, GRID_WIDTH - 2) + 1
        loot_y = pseudo_random(loot_seed * 3, GRID_HEIGHT - 2) + 1
        
        # Random value
        base_value = pseudo_random(loot_seed * 5, 500) + 500  # 500-999
        
        loot_item = {
            "id": loot_ids[i],
            "x": loot_x,
            "y": loot_y,
            "value": base_value,
            "taken": False,
            "name": loot_names[i]
        }
        loot.append(loot_item)
    
    # Generate visibility mask (initially all False)
    visibility_mask = []
    for x in range(GRID_WIDTH):
        row = []
        for y in range(GRID_HEIGHT):
            row.append(False)
        visibility_mask.append(row)
    
    # Create the complete game state
    game_state = {
        "seed": seed_base,
        "step": 0,
        "player": {
            "x": player_x,
            "y": player_y,
            "inventory": [],
            "stealth_streak": 0
        },
        "guards": guards,
        "loot": loot,
        "score": 0,
        "stealth_bonus_multiplier": 1.0,
        "game_over": False,
        "win": False,
        "visibility_mask": visibility_mask
    }
    
    return game_state


# Example usage and JSON string conversion without json module
def dict_to_json_string(obj, indent=0):
    """Convert dictionary to JSON string without json module."""
    spaces = "  " * indent
    
    if obj is None:
        return "null"
    elif obj is True:
        return "true"
    elif obj is False:
        return "false"
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, str):
        # Simple string escaping
        escaped = obj.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'"{escaped}"'
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        items = []
        for item in obj:
            items.append(dict_to_json_string(item, indent + 1))
        if len(str(items)) < 50:  # Short arrays on one line
            return "[" + ", ".join(items) + "]"
        else:
            item_strings = []
            for item in items:
                item_strings.append(f"{spaces}  {dict_to_json_string(item, indent + 1)}")
            return "[\n" + ",\n".join(item_strings) + "\n" + spaces + "]"
    elif isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for key, value in obj.items():
            key_str = f'"{key}"'
            value_str = dict_to_json_string(value, indent + 1)
            items.append(f'{spaces}  {key_str}: {value_str}')
        return "{\n" + ",\n".join(items) + "\n" + spaces + "}"
    else:
        return f'"{str(obj)}"'


if __name__ == "__main__":
    # Generate and save a random game state
    state = generate_random_game_state()
    json_string = dict_to_json_string(state, 0)
    
    with open(f"game_state_step_0.json", 'w') as f:
        f.write(json_string)
    
    print("Generated random game state saved to game_state_step_0.json")
    print(f"Seed: {state['seed']}")
    print(f"Player at: ({state['player']['x']}, {state['player']['y']})")
    print(f"Guards: {len(state['guards'])}")
    print(f"Loot items: {len(state['loot'])}")

def generate_starlight_courier_state():
    """
    Generate a random initial game state for Starlight Courier.
    Returns a JSON string with all necessary game components.
    """
    import json
    import random
    
    # Grid dimensions
    GRID_WIDTH = 16
    GRID_HEIGHT = 12
    
    # Generate player starting position
    player_x = random.randint(1, GRID_WIDTH - 2)
    player_y = random.randint(1, GRID_HEIGHT - 2)
    
    # Generate beacons (delivery points) - 3-5 beacons
    beacons = []
    beacon_count = random.randint(3, 5)
    beacon_positions = set()
    
    for _ in range(beacon_count):
        while True:
            x = random.randint(1, GRID_WIDTH - 2)
            y = random.randint(1, GRID_HEIGHT - 2)
            if (x, y) not in beacon_positions and (x, y) != (player_x, player_y):
                beacon_positions.add((x, y))
                beacons.append({
                    "x": x,
                    "y": y,
                    "needs_parcel": True,
                    "parcel_type": random.choice(["normal", "heavy", "fragile"]),
                    "active": True
                })
                break
    
    # Generate parcels - 2-4 parcels scattered around
    parcels = []
    parcel_count = random.randint(2, 4)
    parcel_positions = set()
    
    for i in range(parcel_count):
        while True:
            x = random.randint(1, GRID_WIDTH - 2)
            y = random.randint(1, GRID_HEIGHT - 2)
            pos = (x, y)
            if (pos not in parcel_positions and 
                pos not in beacon_positions and 
                pos != (player_x, player_y)):
                parcel_positions.add(pos)
                parcels.append({
                    "id": f"parcel_{i+1}",
                    "x": x,
                    "y": y,
                    "type": random.choice(["normal", "heavy", "fragile"]),
                    "carried_by": None,
                    "fragility": random.randint(1, 3) if random.choice([True, False]) else 1,
                    "weight": random.randint(1, 3),
                    "value": random.randint(50, 200)
                })
                break
    
    # Generate sentry drones - 2-4 drones
    drones = []
    drone_count = random.randint(2, 4)
    drone_positions = set()
    
    for i in range(drone_count):
        while True:
            x = random.randint(2, GRID_WIDTH - 3)
            y = random.randint(2, GRID_HEIGHT - 3)
            pos = (x, y)
            if (pos not in drone_positions and 
                pos not in beacon_positions and 
                pos not in parcel_positions and
                pos != (player_x, player_y)):
                drone_positions.add(pos)
                drones.append({
                    "id": f"drone_{i+1}",
                    "x": x,
                    "y": y,
                    "facing": random.choice(["north", "south", "east", "west"]),
                    "patrol_pattern": random.choice(["stationary", "clockwise", "linear"]),
                    "detection_range": 3,
                    "queued_move": None,
                    "last_player_move": None,
                    "alert_level": 0
                })
                break
    
    # Generate cover spots - walls and obstacles
    cover_spots = []
    cover_count = random.randint(8, 15)
    cover_positions = set()
    
    for _ in range(cover_count):
        while True:
            x = random.randint(1, GRID_WIDTH - 2)
            y = random.randint(1, GRID_HEIGHT - 2)
            pos = (x, y)
            if (pos not in cover_positions and 
                pos not in beacon_positions and 
                pos not in parcel_positions and
                pos not in drone_positions and
                pos != (player_x, player_y)):
                cover_positions.add(pos)
                cover_spots.append({
                    "x": x,
                    "y": y,
                    "type": random.choice(["wall", "asteroid", "debris"]),
                    "provides_cover": True
                })
                break
    
    # Generate telepads - 1-2 telepads for advanced movement
    telepads = []
    if random.choice([True, False]):  # 50% chance of having telepads
        telepad_count = random.randint(1, 2)
        telepad_positions = set()
        
        for i in range(telepad_count):
            while True:
                x = random.randint(1, GRID_WIDTH - 2)
                y = random.randint(1, GRID_HEIGHT - 2)
                pos = (x, y)
                if (pos not in telepad_positions and 
                    pos not in beacon_positions and 
                    pos not in parcel_positions and
                    pos not in drone_positions and
                    pos not in cover_positions and
                    pos != (player_x, player_y)):
                    telepad_positions.add(pos)
                    telepads.append({
                        "id": f"telepad_{i+1}",
                        "x": x,
                        "y": y,
                        "destination_x": None,  # Will be set when paired
                        "destination_y": None,
                        "charges": random.randint(2, 5),
                        "active": True
                    })
                    break
        
        # Pair telepads if there are 2
        if len(telepads) == 2:
            telepads[0]["destination_x"] = telepads[1]["x"]
            telepads[0]["destination_y"] = telepads[1]["y"]
            telepads[1]["destination_x"] = telepads[0]["x"]
            telepads[1]["destination_y"] = telepads[0]["y"]
    
    # Create the complete game state
    game_state = {
        "step": 0,
        "grid": {
            "width": GRID_WIDTH,
            "height": GRID_HEIGHT
        },
        "player": {
            "x": player_x,
            "y": player_y,
            "carrying_parcel": None,
            "stealth_mode": False,
            "last_move": None,
            "health": 100,
            "energy": 100
        },
        "drones": drones,
        "beacons": beacons,
        "parcels": parcels,
        "cover_spots": cover_spots,
        "telepads": telepads,
        "vision_cones": [],  # Will be calculated each turn
        "score": {
            "points": 0,
            "deliveries": 0,
            "stealth_bonus": 0,
            "detection_count": 0,
            "perfect_stealth": True
        },
        "rewards": {
            "unlocked_parcel_types": ["normal"],
            "multipliers": {
                "heavy": 1.0,
                "fragile": 1.0,
                "speed": 1.0
            }
        },
        "game_status": "active",
        "turn_number": 1,
        "last_action": "game_start"
    }
    
    return json.dumps(game_state, indent=2)

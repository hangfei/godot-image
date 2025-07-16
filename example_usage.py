#!/usr/bin/env python3
"""
Example usage script for the pygame automation Docker container.
This demonstrates how to run automated sequences of actions on the game.
"""

import subprocess
import os

def run_automation(image_name, commands, screenshot_dir="./screenshots"):
    """Run the automation Docker container with specified commands"""
    
    # Ensure screenshot directory exists
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Build the docker run command
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(screenshot_dir)}:/app/screenshots",
        image_name
    ] + commands
    
    print(f"Running: {' '.join(docker_cmd)}")
    
    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running automation: {e}")
        return False

def main():
    image_name = "pygame-automation"
    
    print("=" * 60)
    print("Pygame Automation Examples")
    print("=" * 60)
    
    # Example 1: Simple game sequence
    print("\n1. Playing a simple tic-tac-toe sequence...")
    commands = [
        "click 100 100",    # Top-left square
        "click 300 100",    # Top-middle square  
        "click 100 300",    # Middle-left square
        "click 300 300",    # Middle-middle square
        "click 100 500",    # Bottom-left square
        "keyboard r"        # Restart game
    ]
    
    success = run_automation(image_name, commands, "./screenshots/example1")
    if success:
        print("✓ Example 1 completed successfully!")
    else:
        print("✗ Example 1 failed!")
    
    # Example 2: Test different inputs
    print("\n2. Testing various keyboard inputs...")
    commands = [
        "click 200 200",    # Click center
        "wait",             # Wait
        "keyboard w",       # Test w key
        "keyboard a",       # Test a key 
        "keyboard s",       # Test s key
        "keyboard d",       # Test d key
        "keyboard r",       # Restart
        "screenshot"        # Take final screenshot
    ]
    
    success = run_automation(image_name, commands, "./screenshots/example2")
    if success:
        print("✓ Example 2 completed successfully!")
    else:
        print("✗ Example 2 failed!")
    
    # Example 3: Strategic game play
    print("\n3. Strategic tic-tac-toe gameplay...")
    commands = [
        "click 300 300",    # Center square (good strategy)
        "click 100 100",    # Top-left corner
        "click 500 500",    # Bottom-right corner  
        "click 100 500",    # Bottom-left corner
        "click 300 100",    # Top-middle (block)
        "screenshot",       # Take screenshot
        "keyboard r"        # Restart
    ]
    
    success = run_automation(image_name, commands, "./screenshots/example3")
    if success:
        print("✓ Example 3 completed successfully!")
    else:
        print("✗ Example 3 failed!")
    
    print("\n" + "=" * 60)
    print("Examples completed! Check the screenshots/ directories for results.")
    print("=" * 60)

if __name__ == "__main__":
    main() 
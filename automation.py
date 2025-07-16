#!/usr/bin/env python3
import subprocess
import sys
import time
import os
import threading
import pygame
from pygame.locals import *

class GameAutomation:
    def __init__(self, game_process=None):
        self.game_process = game_process
        self.screenshot_dir = "/app/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.screenshot_count = 0
        
    def take_screenshot(self, action_name=""):
        """Take a screenshot using scrot"""
        self.screenshot_count += 1
        filename = f"screenshot_{self.screenshot_count:03d}_{action_name}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        # Use scrot to capture the virtual display
        try:
            subprocess.run(['scrot', filepath], check=True, env={'DISPLAY': ':99'})
            print(f"Screenshot saved: {filename}")
            return filepath
        except subprocess.CalledProcessError as e:
            print(f"Failed to take screenshot: {e}")
            return None
    
    def send_keyboard_event(self, key):
        """Send keyboard event using xdotool"""
        try:
            # Map common keys
            key_mapping = {
                'w': 'w',
                'a': 'a', 
                's': 's',
                'd': 'd',
                'r': 'r',
                'space': 'space',
                'enter': 'Return',
                'esc': 'Escape'
            }
            
            mapped_key = key_mapping.get(key.lower(), key) or key
            subprocess.run(['xdotool', 'key', mapped_key], 
                         check=True, env={'DISPLAY': ':99'})
            print(f"Sent keyboard event: {key}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to send keyboard event {key}: {e}")
            return False
    
    def send_click_event(self, x, y):
        """Send mouse click event using xdotool"""
        try:
            # Move mouse and click
            subprocess.run(['xdotool', 'mousemove', str(x), str(y)], 
                         check=True, env={'DISPLAY': ':99'})
            time.sleep(0.1)  # Small delay
            subprocess.run(['xdotool', 'click', '1'], 
                         check=True, env={'DISPLAY': ':99'})
            print(f"Clicked at ({x}, {y})")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to click at ({x}, {y}): {e}")
            return False
    
    def wait_for_gui(self, timeout=10):
        """Wait for the pygame window to be ready"""
        print("Waiting for GUI to be ready...")
        for i in range(timeout):
            try:
                # Check if there's a window
                result = subprocess.run(['xdotool', 'search', '--name', 'Tic Tac Toe'], 
                                      capture_output=True, text=True, env={'DISPLAY': ':99'})
                if result.returncode == 0 and result.stdout.strip():
                    print("GUI is ready!")
                    time.sleep(1)  # Give it a moment to fully load
                    return True
            except:
                pass
            time.sleep(1)
        print("Timeout waiting for GUI")
        return False
    
    def execute_command(self, command):
        """Execute a single automation command"""
        command = command.strip()
        print(f"Executing command: {command}")
        
        if command.startswith("keyboard "):
            key = command.split(" ", 1)[1]
            success = self.send_keyboard_event(key)
            if success:
                time.sleep(0.5)  # Wait for action to complete
                self.take_screenshot(f"keyboard_{key}")
        
        elif command.startswith("click "):
            parts = command.split()
            if len(parts) >= 3:
                try:
                    x, y = int(parts[1]), int(parts[2])
                    success = self.send_click_event(x, y)
                    if success:
                        time.sleep(0.5)  # Wait for action to complete
                        self.take_screenshot(f"click_{x}_{y}")
                except ValueError:
                    print(f"Invalid click coordinates: {command}")
            else:
                print(f"Invalid click command format: {command}")
        
        elif command == "screenshot":
            self.take_screenshot("manual")
        
        elif command == "wait":
            time.sleep(1)
            
        else:
            print(f"Unknown command: {command}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python automation.py <command1> [command2] [...]")
        print("Commands:")
        print("  keyboard <key>     - Send keyboard event (w, a, s, d, r, etc.)")
        print("  click <x> <y>      - Send mouse click at coordinates")
        print("  screenshot         - Take a screenshot")
        print("  wait               - Wait 1 second")
        print("\nExample:")
        print('  python automation.py "click 200 200" "keyboard r" "screenshot"')
        return
    
    automation = GameAutomation()
    
    # Wait for GUI to be ready
    if not automation.wait_for_gui():
        print("GUI not ready, continuing anyway...")
    
    # Take initial screenshot
    automation.take_screenshot("initial")
    
    # Execute commands
    for command in sys.argv[1:]:
        automation.execute_command(command)
        time.sleep(0.2)  # Small delay between commands
    
    print(f"Automation complete. Screenshots saved in {automation.screenshot_dir}")

if __name__ == "__main__":
    main() 
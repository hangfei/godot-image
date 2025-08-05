#!/usr/bin/env python3
import subprocess
import sys
import time
import os
import threading
import pygame
import argparse
from pygame.locals import *

class GameAutomation:
    def __init__(self, game_process=None, target_window=None):
        self.game_process = game_process
        self.screenshot_dir = "/app/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.screenshot_count = 0
        self.window_id = None
        self.target_window = target_window
        
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
            print(f"Sending keyboard event: {key} -> {mapped_key}")
            
            # Focus the window first if we have window ID
            if self.window_id:
                print(f"Focusing window {self.window_id}")
                subprocess.run(['xdotool', 'windowfocus', self.window_id], 
                             check=True, env={'DISPLAY': ':99'})
                time.sleep(0.2)  # Longer delay after focusing
                
                # Send key to specific window
                print(f"Sending key '{mapped_key}' to window {self.window_id}")
                subprocess.run(['xdotool', 'key', '--window', self.window_id, mapped_key], 
                             check=True, env={'DISPLAY': ':99'})
                
                # Also try sending keydown/keyup events for better compatibility
                subprocess.run(['xdotool', 'keydown', '--window', self.window_id, mapped_key], 
                             check=False, env={'DISPLAY': ':99'})
                time.sleep(0.1)
                subprocess.run(['xdotool', 'keyup', '--window', self.window_id, mapped_key], 
                             check=False, env={'DISPLAY': ':99'})
            else:
                print("No window ID found, sending global key event")
                # Fallback to global key event
                subprocess.run(['xdotool', 'key', mapped_key], 
                             check=True, env={'DISPLAY': ':99'})
            
            print(f"Successfully sent keyboard event: {key}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to send keyboard event {key}: {e}")
            return False
    
    def send_click_event(self, x, y):
        """Send mouse click event using xdotool"""
        try:
            # Focus the window first if we have window ID
            if self.window_id:
                subprocess.run(['xdotool', 'windowfocus', self.window_id], 
                             check=True, env={'DISPLAY': ':99'})
                time.sleep(0.1)  # Small delay after focusing
            
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
        
        # If a specific window ID or name is provided, try that first
        if self.target_window:
            print(f"Looking for specific window: {self.target_window}")
            try:
                # Check if it's a window ID (numeric)
                if self.target_window.isdigit():
                    self.window_id = self.target_window
                    print(f"Using provided window ID: {self.window_id}")
                    # Verify the window exists
                    result = subprocess.run(['xdotool', 'getwindowname', self.window_id],
                                          capture_output=True, text=True, env={'DISPLAY': ':99'})
                    if result.returncode == 0:
                        print(f"Window title: '{result.stdout.strip()}'")
                        return True
                else:
                    # Search by window name
                    result = subprocess.run(['xdotool', 'search', '--name', self.target_window], 
                                          capture_output=True, text=True, env={'DISPLAY': ':99'})
                    if result.returncode == 0 and result.stdout.strip():
                        self.window_id = result.stdout.strip().split('\n')[0]
                        print(f"Found target window: {self.target_window}, ID: {self.window_id}")
                        return True
            except Exception as e:
                print(f"Error finding target window: {e}")
        
        for i in range(timeout):
            try:
                # First, let's see what windows are available
                if i == 0:  # Only on first attempt to avoid spam
                    try:
                        all_windows = subprocess.run(['xdotool', 'search', '--name', '.*'], 
                                                   capture_output=True, text=True, env={'DISPLAY': ':99'})
                        if all_windows.returncode == 0:
                            window_list = all_windows.stdout.strip().split('\n')
                            print(f"Available windows: {window_list}")
                            
                            # Show window titles for each ID
                            for window_id in window_list[:5]:  # Limit to first 5 to avoid spam
                                if window_id.strip():
                                    try:
                                        title_result = subprocess.run(['xdotool', 'getwindowname', window_id.strip()],
                                                                    capture_output=True, text=True, env={'DISPLAY': ':99'})
                                        if title_result.returncode == 0:
                                            print(f"  Window {window_id.strip()}: '{title_result.stdout.strip()}'")
                                    except:
                                        pass
                    except:
                        pass
                
                # Check if there's a window - try different approaches
                window_patterns = [
                    ('GLB Asset Adventure', '--name'),
                    ('Tic Tac Toe', '--name'),
                    ('pygame', '--name'),
                    ('python', '--name'),
                ]
                
                for pattern, search_type in window_patterns:
                    result = subprocess.run(['xdotool', 'search', search_type, pattern], 
                                          capture_output=True, text=True, env={'DISPLAY': ':99'})
                    if result.returncode == 0 and result.stdout.strip():
                        window_ids = result.stdout.strip().split('\n')
                        for window_id in window_ids:
                            if window_id.strip():
                                self.window_id = window_id.strip()
                                print(f"GUI is ready! Found window with pattern '{pattern}', Window ID: {self.window_id}")
                                
                                # Get the actual window title for debugging
                                try:
                                    title_result = subprocess.run(['xdotool', 'getwindowname', self.window_id],
                                                                capture_output=True, text=True, env={'DISPLAY': ':99'})
                                    if title_result.returncode == 0:
                                        actual_title = title_result.stdout.strip()
                                        print(f"Actual window title: '{actual_title}'")
                                        
                                        # If we found the window via pygame/python pattern, assume it's our game
                                        # even if the title is empty (common issue in virtual displays)
                                        if pattern in ['pygame', 'python'] or actual_title:
                                            time.sleep(1)  # Give it a moment to fully load
                                            return True
                                except:
                                    pass
                                
                                # If we can't get the title but found the window, use it anyway
                                print(f"Using window {self.window_id} (title detection failed)")
                                time.sleep(1)
                                return True
                                
            except Exception as e:
                print(f"Error during window search: {e}")
            time.sleep(1)
        
        # Final fallback: if we have any windows available, use the first one
        try:
            print("🔄 Final fallback: using any available window...")
            all_windows = subprocess.run(['xdotool', 'search', '--name', '.*'], 
                                       capture_output=True, text=True, env={'DISPLAY': ':99'})
            if all_windows.returncode == 0 and all_windows.stdout.strip():
                window_list = all_windows.stdout.strip().split('\n')
                if window_list and window_list[0].strip():
                    self.window_id = window_list[0].strip()
                    print(f"Using fallback window ID: {self.window_id}")
                    try:
                        title_result = subprocess.run(['xdotool', 'getwindowname', self.window_id],
                                                    capture_output=True, text=True, env={'DISPLAY': ':99'})
                        if title_result.returncode == 0:
                            print(f"Fallback window title: '{title_result.stdout.strip()}'")
                    except:
                        print("Could not get fallback window title")
                    return True
        except Exception as e:
            print(f"Fallback failed: {e}")
        
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
    parser = argparse.ArgumentParser(description='Pygame Game Automation Tool')
    parser.add_argument('commands', nargs='*', help='Automation commands to execute')
    parser.add_argument('--window', '-w', help='Target window name or ID (e.g., "1293" or "GLB Asset")')
    parser.add_argument('--list-windows', '-l', action='store_true', help='List all available windows and exit')
    
    args = parser.parse_args()
    
    # List windows option
    if args.list_windows:
        try:
            result = subprocess.run(['xdotool', 'search', '--name', '.*'], 
                                  capture_output=True, text=True, env={'DISPLAY': ':99'})
            if result.returncode == 0:
                window_ids = result.stdout.strip().split('\n')
                print("Available windows:")
                for window_id in window_ids:
                    if window_id.strip():
                        try:
                            title_result = subprocess.run(['xdotool', 'getwindowname', window_id.strip()],
                                                        capture_output=True, text=True, env={'DISPLAY': ':99'})
                            if title_result.returncode == 0:
                                print(f"  ID {window_id.strip()}: '{title_result.stdout.strip()}'")
                        except:
                            print(f"  ID {window_id.strip()}: <unknown title>")
            else:
                print("No windows found")
        except Exception as e:
            print(f"Error listing windows: {e}")
        return
    
    if not args.commands:
        print("Usage: python automation.py [options] <command1> [command2] [...]")
        print("\nOptions:")
        print("  --window, -w <name/id>   Target specific window (name or ID)")
        print("  --list-windows, -l       List all available windows")
        print("\nCommands:")
        print("  keyboard <key>           Send keyboard event (w, a, s, d, r, etc.)")
        print("  click <x> <y>            Send mouse click at coordinates")
        print("  screenshot               Take a screenshot")
        print("  wait                     Wait 1 second")
        print("\nExamples:")
        print('  python automation.py "click 200 200" "keyboard r" "screenshot"')
        print('  python automation.py --window 1293 "keyboard w" "keyboard d"')
        print('  python automation.py --window "GLB Asset" "click 500 400"')
        print('  python automation.py --list-windows')
        print('')
        print('Note: If GAME_WINDOW_ID environment variable is set, it will be used automatically.')
        return
    
    # Use provided window, or check for environment variable
    target_window = args.window
    if not target_window and 'GAME_WINDOW_ID' in os.environ:
        target_window = os.environ['GAME_WINDOW_ID']
        print(f"Using GAME_WINDOW_ID from environment: {target_window}")
    
    automation = GameAutomation(target_window=target_window)
    
    # Wait for GUI to be ready
    if not automation.wait_for_gui():
        print("GUI not ready, continuing anyway...")
    
    # Take initial screenshot
    automation.take_screenshot("initial")
    
    # Execute commands
    for command in args.commands:
        automation.execute_command(command)
        time.sleep(0.2)  # Small delay between commands
    
    print(f"Automation complete. Screenshots saved in {automation.screenshot_dir}")

if __name__ == "__main__":
    main() 
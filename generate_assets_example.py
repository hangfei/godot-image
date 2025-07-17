#!/usr/bin/env python3
"""
Example usage of the GLB Asset Generator
Run this after installing dependencies: pip install -r requirements.txt
"""

try:
    from generate_assets import GLBAssetGenerator
except ImportError as e:
    print("❌ Missing dependencies! Please install them first:")
    print("pip install trimesh numpy networkx")
    print(f"Error: {e}")
    exit(1)

def main():
    print("🎮 GLB Asset Generator Example")
    print("=" * 40)
    
    # Create generator
    generator = GLBAssetGenerator("example_assets")
    
    print("\n🧊 Creating basic shapes...")
    generator.create_basic_cube(size=2.0, name="example_cube")
    generator.create_sphere(radius=1.5, name="example_sphere")
    
    print("\n🌍 Creating environment assets...")
    generator.create_terrain(width=20, height=20, name="example_terrain")
    generator.create_tree(name="example_tree")
    
    print("\n🏗️ Creating building assets...")
    generator.create_building_block(width=3, height=4, depth=2, name="example_building")
    
    print("\n✨ All done! Check the 'example_assets' folder.")
    print("💡 Import these .glb files into Godot, Unity, or Blender!")

if __name__ == "__main__":
    main() 
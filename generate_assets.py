#!/usr/bin/env python3
"""
GLB Asset Generator for Game Development
Generates 3D models in GLB format for use in game engines like Godot, Unity, etc.
"""

import os
import numpy as np
import trimesh
from PIL import Image, ImageDraw
import argparse
import json
from pathlib import Path

class GLBAssetGenerator:
    def __init__(self, output_dir="assets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}")
    
    def create_basic_cube(self, size=1.0, name="cube"):
        """Create a basic textured cube"""
        print(f"🧊 Generating cube: {name}")
        
        # Create cube mesh
        mesh = trimesh.creation.box(extents=[size, size, size])
        
        # Create a simple texture
        texture = self._create_checkerboard_texture(64, 64)
        
        # Create material
        material = trimesh.visual.material.PBRMaterial(
            baseColorTexture=texture,
            metallicFactor=0.1,
            roughnessFactor=0.8
        )
        
        # Apply material
        mesh.visual.material = material
        
        # Export to GLB
        output_path = self.output_dir / f"{name}.glb"
        mesh.export(str(output_path))
        print(f"✅ Saved: {output_path}")
        return output_path
    
    def create_sphere(self, radius=1.0, subdivisions=2, name="sphere"):
        """Create a UV sphere"""
        print(f"🌍 Generating sphere: {name}")
        
        mesh = trimesh.creation.uv_sphere(radius=radius, count=[subdivisions*8, subdivisions*8])
        
        # Create a gradient texture
        texture = self._create_gradient_texture(128, 128)
        
        material = trimesh.visual.material.PBRMaterial(
            baseColorTexture=texture,
            metallicFactor=0.2,
            roughnessFactor=0.6
        )
        
        mesh.visual.material = material
        
        output_path = self.output_dir / f"{name}.glb"
        mesh.export(str(output_path))
        print(f"✅ Saved: {output_path}")
        return output_path
    
    def create_cylinder(self, radius=1.0, height=2.0, sections=16, name="cylinder"):
        """Create a cylinder"""
        print(f"🪣 Generating cylinder: {name}")
        
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
        
        # Create a wood-like texture
        texture = self._create_wood_texture(128, 128)
        
        material = trimesh.visual.material.PBRMaterial(
            baseColorTexture=texture,
            metallicFactor=0.0,
            roughnessFactor=0.9
        )
        
        mesh.visual.material = material
        
        output_path = self.output_dir / f"{name}.glb"
        mesh.export(str(output_path))
        print(f"✅ Saved: {output_path}")
        return output_path
    
    def create_terrain(self, width=10, height=10, subdivisions=32, name="terrain"):
        """Create a simple terrain with height variation"""
        print(f"🏔️ Generating terrain: {name}")
        
        # Create height map
        x = np.linspace(-width/2, width/2, subdivisions)
        y = np.linspace(-height/2, height/2, subdivisions)
        X, Y = np.meshgrid(x, y)
        
        # Generate some hills using sine waves
        Z = (np.sin(X * 0.5) * np.cos(Y * 0.5) * 2 + 
             np.sin(X * 1.2) * np.cos(Y * 0.8) * 1 +
             np.sin(X * 0.3) * np.sin(Y * 0.4) * 0.8 +
             np.random.random(X.shape) * 0.3 - 0.15)  # Add some random noise
        
        # Create vertices
        vertices = []
        for i in range(subdivisions):
            for j in range(subdivisions):
                vertices.append([X[i,j], Z[i,j], Y[i,j]])
        
        # Create faces (triangles)
        faces = []
        for i in range(subdivisions-1):
            for j in range(subdivisions-1):
                # Two triangles per quad
                v1 = i * subdivisions + j
                v2 = v1 + 1
                v3 = (i + 1) * subdivisions + j
                v4 = v3 + 1
                
                faces.append([v1, v3, v2])
                faces.append([v2, v3, v4])
        
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        mesh.fix_normals()
        
        # Create grass-like texture
        texture = self._create_grass_texture(256, 256)
        
        material = trimesh.visual.material.PBRMaterial(
            baseColorTexture=texture,
            metallicFactor=0.0,
            roughnessFactor=1.0
        )
        
        mesh.visual.material = material
        
        output_path = self.output_dir / f"{name}.glb"
        mesh.export(str(output_path))
        print(f"✅ Saved: {output_path}")
        return output_path
    
    def create_tree(self, name="tree"):
        """Create a simple tree model"""
        print(f"🌳 Generating tree: {name}")
        
        # Create trunk (cylinder)
        trunk = trimesh.creation.cylinder(radius=0.2, height=3.0, sections=8)
        trunk.apply_translation([0, 1.5, 0])
        
        # Create foliage (sphere)
        foliage = trimesh.creation.uv_sphere(radius=1.5)
        foliage.apply_translation([0, 4, 0])
        
        # Combine trunk and foliage
        tree_mesh = trunk + foliage
        
        # Create bark texture for trunk and leaves texture for foliage
        bark_texture = self._create_bark_texture(128, 128)
        
        # Simple material (trimesh doesn't support multi-material easily, so we'll use one)
        material = trimesh.visual.material.PBRMaterial(
            baseColorTexture=bark_texture,
            metallicFactor=0.0,
            roughnessFactor=0.9
        )
        
        tree_mesh.visual.material = material
        
        output_path = self.output_dir / f"{name}.glb"
        tree_mesh.export(str(output_path))
        print(f"✅ Saved: {output_path}")
        return output_path
    
    def create_building_block(self, width=2, height=3, depth=2, name="building"):
        """Create a simple building block"""
        print(f"🏢 Generating building: {name}")
        
        mesh = trimesh.creation.box(extents=[width, height, depth])
        
        # Create brick texture
        texture = self._create_brick_texture(128, 128)
        
        material = trimesh.visual.material.PBRMaterial(
            baseColorTexture=texture,
            metallicFactor=0.1,
            roughnessFactor=0.8
        )
        
        mesh.visual.material = material
        
        output_path = self.output_dir / f"{name}.glb"
        mesh.export(str(output_path))
        print(f"✅ Saved: {output_path}")
        return output_path
    
    def _create_checkerboard_texture(self, width, height):
        """Create a checkerboard pattern texture"""
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        square_size = width // 8
        for i in range(0, width, square_size * 2):
            for j in range(0, height, square_size * 2):
                draw.rectangle([i, j, i + square_size, j + square_size], fill='black')
                draw.rectangle([i + square_size, j + square_size, 
                              i + square_size * 2, j + square_size * 2], fill='black')
        
        return image
    
    def _create_gradient_texture(self, width, height):
        """Create a gradient texture"""
        image = Image.new('RGB', (width, height))
        pixels = []
        
        for y in range(height):
            for x in range(width):
                # Create a radial gradient
                center_x, center_y = width // 2, height // 2
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                max_distance = (center_x ** 2 + center_y ** 2) ** 0.5
                intensity = int(255 * (1 - min(distance / max_distance, 1)))
                pixels.append((intensity, intensity // 2, 255 - intensity))
        
        image.putdata(pixels)
        return image
    
    def _create_wood_texture(self, width, height):
        """Create a wood-like texture"""
        image = Image.new('RGB', (width, height))
        pixels = []
        
        for y in range(height):
            for x in range(width):
                # Create wood grain effect
                grain = int(139 + 30 * np.sin(y * 0.3) + 20 * np.sin(x * 0.1))
                pixels.append((grain, grain - 20, grain - 40))
        
        image.putdata(pixels)
        return image
    
    def _create_grass_texture(self, width, height):
        """Create a grass-like texture"""
        image = Image.new('RGB', (width, height))
        pixels = []
        
        for y in range(height):
            for x in range(width):
                # Random grass colors
                base_green = 60 + int(40 * np.random.random())
                pixels.append((base_green // 3, base_green, base_green // 4))
        
        image.putdata(pixels)
        return image
    
    def _create_bark_texture(self, width, height):
        """Create a bark-like texture"""
        image = Image.new('RGB', (width, height))
        pixels = []
        
        for y in range(height):
            for x in range(width):
                # Brown bark colors with variation
                brown = int(101 + 30 * np.sin(y * 0.2) * np.cos(x * 0.3))
                pixels.append((brown, brown - 20, brown - 40))
        
        image.putdata(pixels)
        return image
    
    def _create_brick_texture(self, width, height):
        """Create a brick pattern texture"""
        image = Image.new('RGB', (width, height), (180, 100, 80))  # Base brick color
        draw = ImageDraw.Draw(image)
        
        brick_height = height // 8
        brick_width = width // 6
        
        for row in range(0, height, brick_height):
            offset = (brick_width // 2) if (row // brick_height) % 2 else 0
            for col in range(-offset, width, brick_width):
                # Draw mortar lines
                draw.rectangle([col + brick_width - 2, row, 
                              col + brick_width, row + brick_height], fill=(120, 120, 120))
                draw.rectangle([col, row + brick_height - 2, 
                              col + brick_width, row + brick_height], fill=(120, 120, 120))
        
        return image
    
    def generate_asset_pack(self):
        """Generate a complete pack of basic game assets"""
        print("🎮 Generating complete asset pack...")
        
        assets = []
        
        # Basic shapes
        assets.append(self.create_basic_cube(name="cube_basic"))
        assets.append(self.create_sphere(name="sphere_basic"))
        assets.append(self.create_cylinder(name="cylinder_basic"))
        
        # Environment
        assets.append(self.create_terrain(name="terrain_hills"))
        assets.append(self.create_tree(name="tree_basic"))
        
        # Building
        assets.append(self.create_building_block(name="building_basic"))
        
        # Create a manifest file
        manifest = {
            "name": "Basic Game Asset Pack",
            "description": "Collection of basic 3D assets for game development",
            "assets": [str(asset.name) for asset in assets],
            "format": "GLB",
            "created_with": "GLB Asset Generator"
        }
        
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"📋 Asset manifest saved: {manifest_path}")
        print(f"🎉 Generated {len(assets)} assets successfully!")
        
        return assets

def main():
    parser = argparse.ArgumentParser(description='Generate GLB assets for game development')
    parser.add_argument('--output', '-o', default='assets', help='Output directory')
    parser.add_argument('--type', '-t', choices=['cube', 'sphere', 'cylinder', 'terrain', 'tree', 'building', 'pack'], 
                       default='pack', help='Type of asset to generate')
    parser.add_argument('--name', '-n', default='asset', help='Name for the generated asset')
    parser.add_argument('--size', '-s', type=float, default=1.0, help='Size parameter for the asset')
    
    args = parser.parse_args()
    
    generator = GLBAssetGenerator(args.output)
    
    if args.type == 'cube':
        generator.create_basic_cube(size=args.size, name=args.name)
    elif args.type == 'sphere':
        generator.create_sphere(radius=args.size, name=args.name)
    elif args.type == 'cylinder':
        generator.create_cylinder(radius=args.size, name=args.name)
    elif args.type == 'terrain':
        generator.create_terrain(width=args.size*10, height=args.size*10, name=args.name)
    elif args.type == 'tree':
        generator.create_tree(name=args.name)
    elif args.type == 'building':
        generator.create_building_block(width=args.size*2, height=args.size*3, depth=args.size*2, name=args.name)
    elif args.type == 'pack':
        generator.generate_asset_pack()
    
    print("\n🚀 Ready to import into your game engine!")
    print(f"📂 Assets saved in: {generator.output_dir}")

if __name__ == "__main__":
    main() 
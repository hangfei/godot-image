# GLB Asset Generator for Game Development

🎮 Generate 3D assets in GLB format for game engines like **Godot**, **Unity**, **Unreal Engine**, and more!

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install trimesh numpy networkx pillow
```

### 2. Generate a Complete Asset Pack
```bash
python3 generate_assets.py --type pack
```

### 3. Generate Individual Assets
```bash
# Create a cube
python3 generate_assets.py --type cube --name my_cube --size 2.0

# Create terrain
python3 generate_assets.py --type terrain --name hills --size 1.5

# Create a tree
python3 generate_assets.py --type tree --name oak_tree
```

## 📦 Available Asset Types

| Type | Description | Example Usage |
|------|-------------|---------------|
| `cube` | Basic textured cube with checkerboard pattern | `--type cube --size 2.0` |
| `sphere` | UV sphere with gradient texture | `--type sphere --size 1.5` |
| `cylinder` | Cylinder with wood-like texture | `--type cylinder --size 1.0` |
| `terrain` | Procedural terrain with hills | `--type terrain --size 2.0` |
| `tree` | Simple tree with trunk and foliage | `--type tree` |
| `building` | Building block with brick texture | `--type building --size 1.5` |
| `pack` | Complete set of all assets | `--type pack` |

## 🎨 Features

- **PBR Materials**: Physically Based Rendering materials with textures
- **Procedural Textures**: Auto-generated textures (checkerboard, wood, grass, brick, etc.)
- **GLB Format**: Compatible with all major game engines
- **Customizable**: Adjustable sizes and parameters
- **Ready to Use**: Import directly into your game engine

## 📁 Output Structure

```
assets/
├── cube_basic.glb          # Basic cube
├── sphere_basic.glb        # UV sphere  
├── cylinder_basic.glb      # Cylinder
├── terrain_hills.glb       # Terrain mesh
├── tree_basic.glb          # Simple tree
├── building_basic.glb      # Building block
└── manifest.json           # Asset information
```

## 🎮 Game Engine Import

### Godot
1. Copy `.glb` files to your project's `assets/` folder
2. In FileSystem dock, select the `.glb` file
3. In Import tab, choose import settings
4. Click "Reimport"
5. Drag into your scene

### Unity
1. Copy `.glb` files to `Assets/Models/`
2. Unity will auto-import them
3. Drag from Project window to Scene

### Unreal Engine
1. Import via Content Browser
2. Choose "Import All" for textures and materials
3. Place in your level

## 🛠️ Command Line Options

```bash
python3 generate_assets.py [OPTIONS]

Options:
  --output, -o    Output directory (default: assets)
  --type, -t      Asset type to generate (default: pack)
  --name, -n      Name for the asset (default: asset)
  --size, -s      Size parameter (default: 1.0)
  --help, -h      Show help message
```

## 📝 Examples

### Create Custom Assets
```bash
# Large terrain for open world
python3 generate_assets.py --type terrain --size 5.0 --name world_terrain

# Small building for city scene  
python3 generate_assets.py --type building --size 0.5 --name house

# Giant sphere for planets
python3 generate_assets.py --type sphere --size 10.0 --name planet
```

### Quick Test
```bash
# Run the example script
python3 generate_assets_example.py
```

## 🧩 Integration with Pygame Automation

The asset generator works alongside the pygame automation system:

1. **Generate assets** with this tool
2. **Import into Godot** for your game
3. **Test your game** with the pygame automation Docker container
4. **Iterate and improve** your assets

## 🔧 Extending the Generator

The code is modular and extensible:

- Add new asset types in `GLBAssetGenerator` class
- Create custom texture generators
- Add material variations
- Implement procedural generation algorithms

## 📋 Dependencies

- `trimesh` - 3D mesh processing
- `numpy` - Mathematical operations  
- `pillow` - Texture generation
- `networkx` - Graph operations (trimesh dependency)

## 🎯 Perfect for:

- 🎮 **Game Prototyping** - Quick placeholder assets
- 🏗️ **Level Design** - Basic building blocks  
- 🌍 **Environment Art** - Terrain and nature assets
- 📚 **Learning** - Understanding 3D asset pipelines
- ⚡ **Rapid Development** - Fast iteration cycles

---

**Ready to create amazing games? Start generating assets!** 🚀 
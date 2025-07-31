# Split Ring Compound Planetary Gearbox Analysis

This project provides tools for optimizing and generating split ring compound planetary gearboxes with precise gear ratios and customizable parameters.

## Features

- **Gear Ratio Optimization**: Find optimal tooth counts for target gear ratios
- **Even Carrier Spacing**: Maintains 120° spacing for 3-planet configuration
- **OD-Based Module Calculation**: Automatically calculate gear module from target outer diameter
- **3D CAD Generation**: Generate complete gearbox models in FreeCAD with STEP file exports
- **YAML Configuration**: Seamless parameter transfer between optimization and CAD generation

## Installation

### Prerequisites

1. **Python 3.7+** with pip
2. **FreeCAD 0.21.2+** for 3D model generation

### Python Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

### FreeCAD Setup

1. **Install FreeCAD**: Download from [freecad.org](https://www.freecad.org/)
2. **Install Gear Plugin**: 
   - Launch FreeCAD
   - Go to **Tools > Addon Manager**
   - Search for and install "**freecad.gears**"
   - Restart FreeCAD

## Usage

### 1. Gear Ratio Optimization

Use `optimize_gear_ratio.py` to find optimal tooth counts for your target gear ratio:

#### Basic Usage

```bash
# Find minimum tooth count within 5% tolerance (default)
python optimize_gear_ratio.py 66.1

# Find minimum error solution
python optimize_gear_ratio.py 66.1 --min-error

# Custom tolerance for minimum tooth count
python optimize_gear_ratio.py 66.1 --tolerance 2.0
```

#### Advanced Options

```bash
# Target outer diameter (automatically calculates module)
python optimize_gear_ratio.py 66.1 --target-od 30.0

# Allow non-standard module values (default: round to 0.1mm)
python optimize_gear_ratio.py 66.1 --target-od 29.5 --nonstandard-module

# Custom gear parameters
python optimize_gear_ratio.py 66.1 --module 0.8 --pressure-angle 25 --profile-shift 0.1
```

#### Command Line Options

- `target_ratio` (required): Desired gear ratio
- `--min-error`: Use minimum error algorithm instead of minimum tooth count
- `--tolerance`: Error tolerance percentage for min-tooth algorithm (default: 5.0)
- `--module`: Gear module/pitch in mm (default: 0.5)
- `--pressure-angle`: Pressure angle in degrees (default: 20)
- `--profile-shift`: Profile shift for stage 1 (default: 0.0508)
- `--target-od`: Target outer diameter in mm (overrides --module)
- `--nonstandard-module`: Allow non-standard module values

#### Output

The script generates:
- **Console output**: Gear configuration and performance metrics
- **srcp.yaml**: Configuration file for FreeCAD generation

Example output:
```
=== MINIMUM TOOTH COUNT (5.0% tolerance) ===
Target ratio: 66.1
Actual ratio: 67.500000
Error: 2.1180%
Sun teeth: 8
Planet 1 teeth: 10
Ring 1 teeth: 28
Planet 2 teeth: 9
Ring 2 teeth: 27
Configuration written to srcp.yaml
```

### 2. FreeCAD 3D Model Generation

Use `GearGeneratorFreecad.py` to generate 3D models from optimized parameters:

#### Setup

1. Launch FreeCAD
2. Create a new document
3. Go to **Macro > Macros...**
4. Navigate to this project directory
5. Select `GearGeneratorFreecad.py`
6. Click **Execute**

#### Behavior

- **With srcp.yaml**: Uses optimized parameters from gear ratio optimization
- **Without srcp.yaml**: Uses default hardcoded parameters
- **Automatic Export**: Creates STEP files in `/STEP/` subdirectory

#### Generated Components

- **Sun gear**: Central driving gear
- **Planet gears**: 3x planet gears (2 stages each)  
- **Ring gears**: 2x internal ring gears
- **Proper meshing**: All gears properly positioned and rotated

#### Export Files

Individual components:
- `sun.step` - Sun gear
- `r1.step` - Ring 1 
- `r2.step` - Ring 2
- `p1Stack.step` - Planet 1 stack
- `p2Stack.step` - Planet 2 stack  
- `p3Stack.step` - Planet 3 stack

Complete assembly:
- `all.step` - Complete gearbox

## Workflow

### Typical Usage Pattern

1. **Optimize gear ratio**:
   ```bash
   python optimize_gear_ratio.py 75.0 --target-od 35.0
   ```

2. **Generate 3D model**:
   - Open FreeCAD
   - Run `GearGeneratorFreecad.py` macro
   - Export/modify as needed

3. **Use STEP files** in your CAD software for further design work

### Configuration File (srcp.yaml)

The YAML file contains all parameters for seamless integration:

```yaml
gear_ratios:
  target_ratio: 66.1
  actual_ratio: 67.5
  error_percent: 2.118
tooth_counts:
  sun_teeth: 8
  p1_teeth: 10
  r1_teeth: 28
  p2_teeth: 9
  r2_teeth: 27
gear_parameters:
  module: 0.8
  pressure_angle: 20.0
  profile_shift: 0.0508
```

## Theory

### Split Ring Compound Planetary

This gearbox architecture uses two ring gears with slightly different tooth counts to achieve high gear ratios in a compact package. The compound planetary design allows for:

- **High gear ratios** (typically 50:1 to 200:1+)
- **Compact size** compared to traditional multi-stage gearboxes
- **High torque density** 
- **Even load distribution** across multiple planet gears

### Constraints

- **120° carrier spacing**: Ensures even load distribution with 3 planets
- **Proper meshing**: All gear combinations must have integer tooth counts
- **Geometric constraints**: Planet gears must fit within the ring gears

## Troubleshooting

### Common Issues

1. **"No solution found within tolerance"**: 
   - Increase tolerance percentage
   - Try `--min-error` mode for best achievable accuracy

2. **FreeCAD macro errors**:
   - Ensure freecad.gears plugin is installed
   - Check Python console for detailed error messages
   - Verify srcp.yaml exists in the same directory

3. **Import errors**:
   - Run `pip install -r requirements.txt`
   - Check Python version compatibility

### Getting Help

- Check the console output for detailed error messages
- Verify all prerequisites are installed
- Ensure file paths are accessible to both Python and FreeCAD

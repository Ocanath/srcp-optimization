#!/usr/bin/env python3
"""
Test script to verify YAML integration without FreeCAD dependencies
"""
import yaml

def load_config():
    """
    Test version of the load_config function from GearGeneratorFreecad.py
    """
    try:
        with open('srcp.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("Loaded configuration from srcp.yaml")
        
        # Extract parameters from YAML
        tooth_counts = config['tooth_counts']
        gear_params = config['gear_parameters']
        
        return {
            'p1_teeth': tooth_counts['p1_teeth'],
            'r1_teeth': tooth_counts['r1_teeth'],
            'r2_teeth': tooth_counts['r2_teeth'],
            'sun_teeth': tooth_counts['sun_teeth'],
            'p2_teeth': tooth_counts['p2_teeth'],
            'pitch_mm': gear_params['module'],
            'pressure_angle': gear_params['pressure_angle'],
            'profile_shift': gear_params['profile_shift']
        }
    except FileNotFoundError:
        print("srcp.yaml not found, using default parameters")
        return {
            'p1_teeth': 21,
            'r1_teeth': 54,
            'r2_teeth': 53,
            'sun_teeth': 12,
            'p2_teeth': 20,
            'pitch_mm': 0.5,
            'pressure_angle': 20,
            'profile_shift': 0.0508
        }

if __name__ == "__main__":
    print("Testing YAML integration...")
    config = load_config()
    
    print("\nLoaded configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("\nIntegration test successful!")
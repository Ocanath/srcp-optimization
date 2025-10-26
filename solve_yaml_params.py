#!/usr/bin/env python3
"""
YAML Parameter Solver for Multi-Module Gearboxes

Reads a candidate YAML file with missing parameters (module, ring_teeth, or planet_teeth)
and solves for the missing value using the carrier radius constraint (cr1 = cr2).

Usage:
    python solve_yaml_params.py <input_yaml> [--output <output_yaml>]

Example:
    python solve_yaml_params.py wrist-cand-1.yaml
    python solve_yaml_params.py wrist-cand-1.yaml --output srcp.yaml
"""

import yaml
import sympy as sp
import argparse
import os
from optimize_gear_ratio import get_carrier_radius, check_stage_validity


def detect_missing_params(stack_params):
    """
    Detect which parameters are missing from a stack configuration.

    Args:
        stack_params: Dictionary with stack parameters

    Returns:
        List of missing parameter names
    """
    required_params = ['module', 'ring_teeth', 'planet_teeth']
    missing = []

    for param in required_params:
        if param not in stack_params or stack_params[param] is None:
            missing.append(param)

    return missing


def solve_missing_module(stack1, stack2, missing_in_stack):
    """
    Solve for missing module using carrier radius constraint.

    Uses: (nr1 - np1) * m1 = (nr2 - np2) * m2

    Args:
        stack1: Stack 1 parameters dict
        stack2: Stack 2 parameters dict
        missing_in_stack: 1 or 2, indicates which stack has missing module

    Returns:
        Solved module value
    """
    if missing_in_stack == 1:
        # Solve for m1: m1 = m2 * (nr2 - np2) / (nr1 - np1)
        m2 = stack2['module']
        nr1 = stack1['ring_teeth']
        np1 = stack1['planet_teeth']
        nr2 = stack2['ring_teeth']
        np2 = stack2['planet_teeth']

        m1 = m2 * (nr2 - np2) / (nr1 - np1)
        return m1
    else:
        # Solve for m2: m2 = m1 * (nr1 - np1) / (nr2 - np2)
        m1 = stack1['module']
        nr1 = stack1['ring_teeth']
        np1 = stack1['planet_teeth']
        nr2 = stack2['ring_teeth']
        np2 = stack2['planet_teeth']

        m2 = m1 * (nr1 - np1) / (nr2 - np2)
        return m2


def solve_missing_ring_teeth(stack1, stack2, missing_in_stack):
    """
    Solve for missing ring_teeth using carrier radius constraint.

    Uses: (nr1 - np1) * m1 = (nr2 - np2) * m2

    Args:
        stack1: Stack 1 parameters dict
        stack2: Stack 2 parameters dict
        missing_in_stack: 1 or 2, indicates which stack has missing ring_teeth

    Returns:
        Solved ring_teeth value (rounded to nearest integer)
    """
    if missing_in_stack == 1:
        # Solve for nr1: nr1 = np1 + m2 * (nr2 - np2) / m1
        m1 = stack1['module']
        np1 = stack1['planet_teeth']
        m2 = stack2['module']
        nr2 = stack2['ring_teeth']
        np2 = stack2['planet_teeth']

        nr1 = np1 + m2 * (nr2 - np2) / m1
        return round(nr1)
    else:
        # Solve for nr2: nr2 = np2 + m1 * (nr1 - np1) / m2
        m1 = stack1['module']
        nr1 = stack1['ring_teeth']
        np1 = stack1['planet_teeth']
        m2 = stack2['module']
        np2 = stack2['planet_teeth']

        nr2 = np2 + m1 * (nr1 - np1) / m2
        return round(nr2)


def solve_missing_planet_teeth(stack1, stack2, missing_in_stack):
    """
    Solve for missing planet_teeth using carrier radius constraint.

    Uses: (nr1 - np1) * m1 = (nr2 - np2) * m2

    Args:
        stack1: Stack 1 parameters dict
        stack2: Stack 2 parameters dict
        missing_in_stack: 1 or 2, indicates which stack has missing planet_teeth

    Returns:
        Solved planet_teeth value (rounded to nearest integer)
    """
    if missing_in_stack == 1:
        # Solve for np1: np1 = nr1 - m2 * (nr2 - np2) / m1
        m1 = stack1['module']
        nr1 = stack1['ring_teeth']
        m2 = stack2['module']
        nr2 = stack2['ring_teeth']
        np2 = stack2['planet_teeth']

        np1 = nr1 - m2 * (nr2 - np2) / m1
        return round(np1)
    else:
        # Solve for np2: np2 = nr2 - m1 * (nr1 - np1) / m2
        m1 = stack1['module']
        nr1 = stack1['ring_teeth']
        np1 = stack1['planet_teeth']
        m2 = stack2['module']
        nr2 = stack2['ring_teeth']

        np2 = nr2 - m1 * (nr1 - np1) / m2
        return round(np2)


def solve_and_complete_config(input_yaml_path, output_yaml_path='srcp.yaml'):
    """
    Read input YAML, solve for missing parameters, and write complete config.

    Args:
        input_yaml_path: Path to input YAML with potentially missing params
        output_yaml_path: Path to output YAML file (default: srcp.yaml)
    """
    # Read input YAML
    with open(input_yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    stack1 = config.get('stack_1_params', {})
    stack2 = config.get('stack_2_params', {})

    # Detect missing parameters
    missing_stack1 = detect_missing_params(stack1)
    missing_stack2 = detect_missing_params(stack2)

    print(f"Reading: {input_yaml_path}")
    print(f"Stack 1 missing: {missing_stack1 if missing_stack1 else 'None'}")
    print(f"Stack 2 missing: {missing_stack2 if missing_stack2 else 'None'}")
    print()

    # Validate: only one parameter should be missing total
    total_missing = len(missing_stack1) + len(missing_stack2)
    if total_missing == 0:
        print("No missing parameters - configuration is complete!")
        print("Copying to output file...")
    elif total_missing > 1:
        print(f"ERROR: Too many missing parameters ({total_missing})")
        print("This solver can only handle ONE missing parameter at a time.")
        return False
    else:
        # Solve for the missing parameter
        if missing_stack1:
            param = missing_stack1[0]
            stack_num = 1
        else:
            param = missing_stack2[0]
            stack_num = 2

        print(f"Solving for stack_{stack_num}_params.{param}...")

        try:
            if param == 'module':
                solved_value = solve_missing_module(stack1, stack2, stack_num)
            elif param == 'ring_teeth':
                solved_value = solve_missing_ring_teeth(stack1, stack2, stack_num)
            elif param == 'planet_teeth':
                solved_value = solve_missing_planet_teeth(stack1, stack2, stack_num)

            print(f"Solved: {param} = {solved_value}")
            print()

            # Update the configuration
            if stack_num == 1:
                stack1[param] = solved_value
            else:
                stack2[param] = solved_value

        except Exception as e:
            print(f"ERROR: Could not solve for {param}: {e}")
            return False

    # Verify carrier radius constraint
    cr1 = get_carrier_radius(stack1['planet_teeth'], stack1['ring_teeth'], stack1['module'])
    cr2 = get_carrier_radius(stack2['planet_teeth'], stack2['ring_teeth'], stack2['module'])

    print("Verification:")
    print(f"  Carrier radius 1: {cr1:.6f} mm")
    print(f"  Carrier radius 2: {cr2:.6f} mm")
    print(f"  Difference: {abs(cr1 - cr2):.6e} mm")

    if abs(cr1 - cr2) > 1e-9:
        print("  WARNING: Carrier radii do not match! IMPOSSIBLE GEARBOX, SOLUTION NOT FOUND" )
    else:
        print("  ✓ Carrier radii match!")
    print()

    # Check stage validity (assumes 3 planets for 120° spacing)
    sun_teeth_1 = stack1['ring_teeth'] - 2 * stack1['planet_teeth']
    
    valid1 = check_stage_validity(3, stack1['ring_teeth'], sun_teeth_1)
    

    print("Stage Validity (3 planets, 120° spacing):")
    print(f"  Stack 1: {'✓ Valid' if valid1 else '✗ Invalid'} (sun_teeth={sun_teeth_1})")
    print()

	

    # Write output YAML
    output_config = {
        'stack_1_params': stack1,
        'stack_2_params': stack2
    }

    with open(output_yaml_path, 'w') as f:
        yaml.dump(output_config, f, default_flow_style=False, sort_keys=False)

    print(f"Complete configuration written to: {output_yaml_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Solve for missing parameters in multi-module gearbox YAML configs'
    )
    parser.add_argument('input_yaml', help='Input YAML file with missing parameter')
    parser.add_argument('--output', default='srcp.yaml', help='Output YAML file (default: srcp.yaml)')

    args = parser.parse_args()

    if not os.path.exists(args.input_yaml):
        print(f"ERROR: Input file not found: {args.input_yaml}")
        return 1

    success = solve_and_complete_config(args.input_yaml, args.output)
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())

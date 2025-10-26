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


def solve_for_missing_parameter(stack1, stack2, param_name, missing_in_stack):
    """
    Solve for missing parameter using sympy and carrier radius constraint.

    Uses sympy to symbolically solve: cr1 - cr2 = 0

    Args:
        stack1: Stack 1 parameters dict
        stack2: Stack 2 parameters dict
        param_name: Name of missing parameter ('module', 'ring_teeth', 'planet_teeth')
        missing_in_stack: 1 or 2, indicates which stack has missing parameter

    Returns:
        Solved parameter value (float for module, int for teeth counts)
    """
    # Create sympy symbols
    nr1_sym, nr2_sym = sp.symbols('nr1 nr2', positive=True, integer=True)
    np1_sym, np2_sym = sp.symbols('np1 np2', positive=True, integer=True)
    m1_sym, m2_sym = sp.symbols('m1 m2', positive=True, real=True)

    # Get symbolic carrier radius expressions
    cr1_sym = get_carrier_radius(np1_sym, nr1_sym, m1_sym)
    cr2_sym = get_carrier_radius(np2_sym, nr2_sym, m2_sym)

    # Create constraint equation: cr1 - cr2 = 0
    constraint = cr1_sym - cr2_sym

    # Determine which symbol to solve for
    if missing_in_stack == 1:
        if param_name == 'module':
            solve_for = m1_sym
        elif param_name == 'ring_teeth':
            solve_for = nr1_sym
        else:  # planet_teeth
            solve_for = np1_sym
    else:  # missing_in_stack == 2
        if param_name == 'module':
            solve_for = m2_sym
        elif param_name == 'ring_teeth':
            solve_for = nr2_sym
        else:  # planet_teeth
            solve_for = np2_sym

    # Solve symbolically for the missing parameter
    solution = sp.solve(constraint, solve_for)

    if not solution:
        raise ValueError(f"No solution found for {param_name}")

    # Take the first solution (usually only one for linear equations)
    symbolic_solution = solution[0]

    # Substitute known values
    substitutions = {}

    if missing_in_stack == 1:
        # Missing parameter is in stack 1, substitute all stack 2 values
        if param_name != 'module':
            substitutions[m1_sym] = stack1.get('module')
        if param_name != 'ring_teeth':
            substitutions[nr1_sym] = stack1.get('ring_teeth')
        if param_name != 'planet_teeth':
            substitutions[np1_sym] = stack1.get('planet_teeth')

        substitutions[m2_sym] = stack2['module']
        substitutions[nr2_sym] = stack2['ring_teeth']
        substitutions[np2_sym] = stack2['planet_teeth']
    else:
        # Missing parameter is in stack 2, substitute all stack 1 values
        substitutions[m1_sym] = stack1['module']
        substitutions[nr1_sym] = stack1['ring_teeth']
        substitutions[np1_sym] = stack1['planet_teeth']

        if param_name != 'module':
            substitutions[m2_sym] = stack2.get('module')
        if param_name != 'ring_teeth':
            substitutions[nr2_sym] = stack2.get('ring_teeth')
        if param_name != 'planet_teeth':
            substitutions[np2_sym] = stack2.get('planet_teeth')

    # Substitute and evaluate numerically
    numerical_solution = symbolic_solution.subs(substitutions).evalf()

    # Convert to appropriate type
    if param_name == 'module':
        return float(numerical_solution)
    else:
        # Round to nearest integer for tooth counts
        return int(round(numerical_solution))


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
        print(f"Using sympy to solve: cr1 - cr2 = 0")

        try:
            solved_value = solve_for_missing_parameter(stack1, stack2, param, stack_num)

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
        print("  OK: Carrier radii match!")
    print()

    # Check stage validity (assumes 3 planets for 120° spacing)
    sun_teeth_1 = stack1['ring_teeth'] - 2 * stack1['planet_teeth']
    
    valid1 = check_stage_validity(3, stack1['ring_teeth'], sun_teeth_1)
    

    print("Stage Validity (3 planets, 120° spacing):")
    print(f"  Stack 1: {'OK: Valid' if valid1 else 'FAIL: Invalid'} (sun_teeth={sun_teeth_1})")
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

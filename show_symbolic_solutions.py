#!/usr/bin/env python3
"""
Display the symbolic solutions derived by sympy for the carrier radius constraint.

This shows the algebraic expressions that sympy derives when solving cr1 - cr2 = 0
for each of the three solvable parameters (module, ring_teeth, planet_teeth).
"""

import sympy as sp
from optimize_gear_ratio import get_carrier_radius


# Create sympy symbols
nr1, nr2 = sp.symbols('nr1 nr2', positive=True, integer=True)
np1, np2 = sp.symbols('np1 np2', positive=True, integer=True)
m1, m2 = sp.symbols('m1 m2', positive=True, real=True)

# Get symbolic carrier radius expressions
cr1 = get_carrier_radius(np1, nr1, m1)
cr2 = get_carrier_radius(np2, nr2, m2)

# Create constraint equation
constraint = cr1 - cr2

print("="*70)
print("SYMBOLIC SOLUTIONS FOR MULTI-MODULE CARRIER RADIUS CONSTRAINT")
print("="*70)
print()
print("Constraint: cr1 = cr2")
print("Where: cr = (ring_teeth - planet_teeth) * module / 2")
print()

# Solve for each parameter
print("Solving for m2 (module of stack 2):")
print("-" * 70)
m2_solution = sp.solve(constraint, m2)[0]
sp.pprint(sp.Eq(m2, m2_solution))
print()
print()

print("Solving for m1 (module of stack 1):")
print("-" * 70)
m1_solution = sp.solve(constraint, m1)[0]
sp.pprint(sp.Eq(m1, m1_solution))
print()
print()

print("Solving for nr2 (ring_teeth of stack 2):")
print("-" * 70)
nr2_solution = sp.solve(constraint, nr2)[0]
sp.pprint(sp.Eq(nr2, nr2_solution))
print()
print()

print("Solving for nr1 (ring_teeth of stack 1):")
print("-" * 70)
nr1_solution = sp.solve(constraint, nr1)[0]
sp.pprint(sp.Eq(nr1, nr1_solution))
print()
print()

print("Solving for np2 (planet_teeth of stack 2):")
print("-" * 70)
np2_solution = sp.solve(constraint, np2)[0]
sp.pprint(sp.Eq(np2, np2_solution))
print()
print()

print("Solving for np1 (planet_teeth of stack 1):")
print("-" * 70)
np1_solution = sp.solve(constraint, np1)[0]
sp.pprint(sp.Eq(np1, np1_solution))
print()
print()

print("="*70)
print("These are the exact symbolic solutions used by solve_yaml_params.py")
print("="*70)

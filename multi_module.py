from optimize_gear_ratio import get_gear_ratio, get_carrier_radius
import sympy as sp

nr1, nr2, np1, np2 = sp.symbols('nr1 nr2 np1 np2', positive=True, integer=True)
m1, m2 = sp.symbols('m1 m2', positive=True, real=True)


cr1 = get_carrier_radius(np1, nr1, m1)
cr2 = get_carrier_radius(np2, nr2, m2)


# # Substitute known values into cr1 and cr2
# cr1_sub = cr1.subs(values)
# cr2_sub = cr2.subs(values)

# print("cr1 after substitution:")
# sp.pprint(cr1_sub)
# print("\ncr2 after substitution:")
# sp.pprint(cr2_sub)

# Solve for m2 where cr1 - cr2 = 0 (i.e., cr1 = cr2)
m2_solution = sp.solve(cr1 - cr2, m2)

print("\nSolution for m2:")
sp.pprint(m2_solution)


# # Set known values
# values = {
#     nr1: 53,
#     np1: 21,
#     nr2: 52,
#     np2: 21,
#     m1: 0.5
# }

# m2_solution_sub = m2_solution.subs(values)
# sp.pprint(m2_solution_sub)

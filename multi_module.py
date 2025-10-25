from optimize_gear_ratio import get_sundrive_gear_ratio, get_carrierdrive_gear_ratio, get_carrier_radius
import sympy as sp

nr1, nr2, np1, np2 = sp.symbols('nr1 nr2 np1 np2', positive=True, integer=True)
m1, m2 = sp.symbols('m1 m2', positive=True, real=True)


cr1 = get_carrier_radius(np1, nr1, m1)
cr2 = get_carrier_radius(np2, nr2, m2)

# Solve for m2 where cr1 - cr2 = 0 (i.e., cr1 = cr2)
m2_solution = sp.solve(cr1 - cr2, m2)

print("\nSolution for m2:")
sp.pprint(m2_solution)



Gs = get_sundrive_gear_ratio(nr1, nr2, np1, np2, m1, m2)
# sp.pprint(G)

Gc = get_carrierdrive_gear_ratio(nr1, nr2, np1, np2, m2, m2)
# Define the constraints
constraints = {
	np2: np1,
	nr2: nr1 - 1
}
Gc_constrained = Gc.subs(constraints).simplify()
print(f"If np2 = np1 and nr2 = nr1-1")
sp.pprint(Gc_constrained)
m2_constrained = m2_solution[0].subs(constraints).simplify()
sp.pprint(m2_constrained)





# Set known values
values = {
    nr1: 55,
    np1: 16,
    nr2: 54,
    np2: 16,
    m1: 0.5
}
Gs_num = Gs.subs(values).evalf()
print(f"Sun revolutions to one revolution of output ring: {Gs_num}")

Gc_num = Gc.subs(values).evalf()
print(Gc_num)
print(f"Carrier revolutions to one revolution of output ring: {Gc_num}")
# m2_solution is a list, so get the first element
m2_solution_sub = m2_solution[0].subs(values).evalf()

print("\nm2 numerical value:")
print(m2_solution_sub)

values[m2] = m2_solution_sub

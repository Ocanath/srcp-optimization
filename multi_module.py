from optimize_gear_ratio import get_sundrive_gear_ratio, get_carrierdrive_gear_ratio, get_carrier_radius, check_stage_validity
import sympy as sp

nr1, nr2, np1, np2 = sp.symbols('nr1 nr2 np1 np2', positive=True, integer=True)
m1, m2 = sp.symbols('m1 m2', positive=True, real=True)


cr1 = get_carrier_radius(np1, nr1, m1)
cr2 = get_carrier_radius(np2, nr2, m2)

# Solve for m2 where cr1 - cr2 = 0 (i.e., cr1 = cr2)
m2_solution = sp.solve(cr1 - cr2, m2)

print("\nGeneral Solution for m2, with equal carrier radius constraint:")
sp.pprint(sp.Eq(sp.Symbol('m2'), m2_solution[0]))
print("")

Gs = get_sundrive_gear_ratio(nr1, nr2, np1, np2, m1, m2)
Gc = get_carrierdrive_gear_ratio(nr1, nr2, np1, np2, m2, m2)


print(f"If np2 = np1 and nr2 = nr1-1:\n"+'='*60)
# Define the constraints
constraints = {
	np2: np1,
	# nr1: nr2 + 1
}
Gc_constrained = Gc.subs(constraints).simplify()
Gs_constrained = Gs.subs(constraints).simplify()
sp.pprint(sp.Eq(sp.Symbol('G_carrier'), Gc_constrained))
print("")
sp.pprint(sp.Eq(sp.Symbol('G_sun'), Gs_constrained))
print("")
m2_constrained = m2_solution[0].subs(constraints).simplify()
sp.pprint(sp.Eq(sp.Symbol('m2'), m2_constrained))
print('='*60)




# Set known values
values = {
    nr1: 58,
    np1: 16,
    nr2: 49,
    np2: 14,
    m1: 0.5
}
print(f"Valid: {check_stage_validity(3, values[nr1], values[nr1] - 2*values[np1])}")
Gs_num = Gs.subs(values).evalf()
print(f"Sun revolutions to one revolution of output ring: {Gs_num}")

Gc_num = Gc.subs(values).evalf()
print(f"Carrier revolutions to one revolution of output ring: {Gc_num}")
# m2_solution is a list, so get the first element
m2_solution_sub = m2_solution[0].subs(values).evalf()

print(f"m2 numerical value: {m2_solution_sub}")




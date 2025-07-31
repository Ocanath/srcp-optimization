import sympy as sp

p1_teeth, r1_teeth, r2_teeth, sun_teeth, p2_teeth, pitch_mm = sp.symbols('p1_teeth r1_teeth r2_teeth sun_teeth p2_teeth pitch')


sun_teeth = r1_teeth - 2*p1_teeth
p2_teeth = r2_teeth - sun_teeth - p1_teeth

r1_diameter = r1_teeth * pitch_mm



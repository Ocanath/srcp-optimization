import sympy as sp

p1_teeth, r1_teeth, r2_teeth, sun_teeth, p2_teeth, pitch_mm = sp.symbols('N_p1 N_r1 N_r2 N_sun N_p2 M')


sun_teeth = r1_teeth - 2*p1_teeth
p2_teeth = r2_teeth - sun_teeth - p1_teeth

r_r1 = r1_teeth * pitch_mm / 2
r_r2 = r2_teeth * pitch_mm / 2
r_s = sun_teeth * pitch_mm / 2
r_p11 = p1_teeth * pitch_mm / 2
r_p12 = p1_teeth * pitch_mm / 2
r_p2 = p2_teeth * pitch_mm / 2

I1 = (r_r1*r_p11)/(r_s*r_p12)
I2 = (r_r1*r_p2)/(r_r2*r_p12)

G = (1 - I2)/(1 + I1)

overallRatio = 1/G

ratio_simple = sp.simplify(overallRatio)
print(str(ratio_simple))


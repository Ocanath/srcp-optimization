import numpy as np


"""
	Set to 1 if you want the planet to have 1 tooth less than the matching pitch
	depth of the ring, for tolerance. Set to 0 if you want the 'normal'/canonical 
	pitch mating distance
"""
drop_tooth_ring1 = 0	# 1 = backlash/tolerance using drop tooth technique. 0 = no backlash but might not work due to tolerance of manufactured gear
drop_tooth_ring2 = 0	

"""
set the desired number of ring and planet teeth, as well as pitch
"""
p1_teeth = 21
r1_teeth = 54
r2_teeth = 53
sun_teeth = r1_teeth - drop_tooth_ring1*2 - 2*p1_teeth
p2_teeth = r2_teeth - sun_teeth - p1_teeth - drop_tooth_ring2*2	#should be always p1 -1?
pitch_mm = 0.5


"""
set the number of desired planets
"""
num_planets = 3

r_r1 = r1_teeth * pitch_mm / 2
r_r2 = r2_teeth * pitch_mm / 2
r_s = sun_teeth * pitch_mm / 2
r_p11 = p1_teeth * pitch_mm / 2
r_p12 = p1_teeth * pitch_mm / 2
r_p2 = p2_teeth * pitch_mm / 2

I1 = (r_r1*r_p11)/(r_s*r_p12)
I2 = (r_r1*r_p2)/(r_r2*r_p12)

G = (1 - I2)/(1 + I1)


carrier_planets_to_sun_distance = ((p1_teeth + drop_tooth_ring1) * pitch_mm / 2) + (sun_teeth * pitch_mm / 2)

print( "sun teeth", sun_teeth)
print("planet 1 teeth", p1_teeth)
print ("ring 1 teeth", r1_teeth)
print("planet 2 teeth", p2_teeth)
print ("ring 2 teeth", r2_teeth)
if(drop_tooth_ring1 != 0):
	print("Drop tooth backlash present in stage 1")
if(drop_tooth_ring2 != 0):
	print("Drop tooth backlash present in stage 2")
overallRatio = 1/G	#number of revolutions of the sun for one revolution of the output ring
print ("gear ratio (sun:output ring)", overallRatio)
print("r2 pitch diameter", r2_teeth*pitch_mm)
print ("OD in mm", max(r1_teeth, r2_teeth)*pitch_mm)
print("Carrier distance between sun and planet: " + str(carrier_planets_to_sun_distance) + "mm")
sunToCarrier = 1/(sun_teeth/(r1_teeth+sun_teeth))
print("sun to carrier ratio", sunToCarrier)
print("If carrier is driven directly:", overallRatio/sunToCarrier)
print("Max diameter of center bore for coax plug:", sun_teeth*pitch_mm)

vdrive = 12
print("WK3505 max speed in rpm at this gear ratio w."+str(vdrive)+"V driver", vdrive*72/(overallRatio/sunToCarrier), "required RPM is 12.60")

"""
	The following code determines whether an eccentric carrier is 
	required, and computes the optimal carrier angles that will make it work
"""
def get_carrier_angles(num_planets, r1_teeth, sun_teeth):
	angdiv = (r1_teeth + sun_teeth)/num_planets
	if(np.floor(angdiv) == angdiv):
		print("carrier spacing is " + str(360/num_planets))
		ang = 360/num_planets
		return [ang,ang,ang]
	else:
		print("Even spacing impossible. Computing optimal eccentric carrier angle...")
		set = []	#this is the set of all angles which satisfy 
		for n in range(1,10000000000):	#can change to while loop. this guarantees termination i guess? very kludged
			anglep2p = (360/(r1_teeth + sun_teeth))*n
			anglep2p = np.mod(anglep2p + 180, 360) - 180
			if(np.floor(anglep2p) == anglep2p):
				# print(anglep2p)
				set.append(anglep2p)
				if(len(set) > 0):
					if(anglep2p < 0):
						break
		triplets = []
		for i in range(0,len(set)):
			for j in range(0,len(set)):
				if(i != j):
					val = 360 - (set[i] + set[j])
					for k in range(0,len(set)):
						if(set[k] == val):
							# print("carrier option: (" + str(set[i]) + ", " + str(set[j]) + ", " + str(set[k]) + ")")
							triplet_val = [set[i].copy(),set[j].copy(),set[k].copy()]
							triplet_val.sort()
							if triplet_val not in triplets:
								triplets.append(triplet_val)
		print(triplets[len(triplets)-1])
		return triplets[len(triplets)-1]


print("\n\nComputing required angles for carrier:")

triplet = get_carrier_angles(num_planets, r1_teeth, sun_teeth)


# ring2_secondcarrier_angle = np.round(triplet[2]/(360/r2_teeth))*360/r2_teeth
# print("R2 center tooth to align angle is: "+str(ring2_secondcarrier_angle))
# p2_angle_in_ring2_frame = ring2_secondcarrier_angle - (360/p2_teeth)/2
# print("P2 angle (where plane intersects tooth center) is: "+str(p2_angle_in_ring2_frame)+" wrt center plane of ring2")



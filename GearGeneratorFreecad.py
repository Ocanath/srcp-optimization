import FreeCAD as App
import Part
import freecad.gears.commands
import numpy as np
import os   #optional, part of the automatic .step file exports that occurs at the end
import yaml


"""
Notes:

This is a macro for generating a split ring compound planetary gearbox in FreeCAD.
It requires Freecad 0.21.2 (or higher?) and the extremely excellent freecad gear plugin: https://github.com/looooo/freecad.gears

In order to run it:

1. Launch FreeCAD
2. If not installed gear plugin, do it from within FreeCAD AddOn manager, follow the prompts and restart
3. Open a new document
4. Go to macros, and change location to the root directory of this repo
5. Select this file and run it from within FreeCAD. It should generate your gearbox.
"""

print("Starting gear generator macro")

# Load configuration from srcp.yaml if it exists, otherwise use defaults
def load_config():
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        yaml_path = os.path.join(script_dir, 'srcp.yaml')
        
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"Loaded configuration from {yaml_path}")
        
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
        script_dir = os.path.dirname(os.path.realpath(__file__))
        yaml_path = os.path.join(script_dir, 'srcp.yaml')
        print(f"srcp.yaml not found at {yaml_path}, using default parameters")
        return {
            'p1_teeth': 21,
            'r1_teeth': 54,
            'r2_teeth': 53,
            'sun_teeth': 12,  # r1_teeth - 2*p1_teeth = 54 - 42 = 12
            'p2_teeth': 20,   # r2_teeth - sun_teeth - p1_teeth = 53 - 12 - 21 = 20
            'pitch_mm': 0.5,
            'pressure_angle': 20,
            'profile_shift': 0.0508
        }

# Load gear parameters
gear_config = load_config()
p1_teeth = gear_config['p1_teeth']
r1_teeth = gear_config['r1_teeth']
r2_teeth = gear_config['r2_teeth']
sun_teeth = gear_config['sun_teeth']
p2_teeth = gear_config['p2_teeth']
pitch_mm = gear_config['pitch_mm']
pressure_angle = gear_config['pressure_angle']
profile_shift = gear_config['profile_shift']

# Fixed parameters (not from YAML)
planet_bore = min(p1_teeth, p2_teeth)//4
noclearance = False

#mechanical design specific parameters
r1_height = 2.5   #mm
r2_height = 3.5
p2_height = 3.5
r2_bearing_inner_race_ID = 30   #inner race ID of the bearing grabbing the top ring. If there's at least half a millimeter of clearance to this ID from the pitch diameter of the ring, we'll adjust the thickness to match this ID
r2_r1_offset = 0.1

#generator-specific options 
num_points = 20

#Helper functions for interfacing freecad to numpy and general math
def Hz(angle):
    return np.array( [
        [np.cos(angle), -np.sin(angle), 0, 0],
        [np.sin(angle), np.cos(angle),  0, 0],
        [0,             0,              1, 0],
        [0,             0,              0, 1]
    ])

def NumpyMatrixToFreecadMatrix(np_m):
    fc_mat = App.Matrix()
    # Define a mapping from matrix indices to FreeCAD attribute names:
    attr_names = [
        ["A11", "A12", "A13", "A14"],
        ["A21", "A22", "A23", "A24"],
        ["A31", "A32", "A33", "A34"],
        ["A41", "A42", "A43", "A44"]
    ]

    for i in range(4):
        for j in range(4):
            setattr(fc_mat, attr_names[i][j], np_m[i, j])
    return fc_mat

def DeleteAllGears():
    #clear the gears currently in the document
    doc = FreeCAD.activeDocument()
    num_deleted = 0
    if doc is not None:
        for obj in list(doc.Objects):
            num_deleted = num_deleted + 1
            if obj.TypeId == "Part::FeaturePython":
                doc.removeObject(obj.Name)
        doc.recompute()
        print("Deleted", num_deleted, "Objects")



#compute the carrier circle diameter
carrier_planets_to_sun_distance = (p1_teeth * pitch_mm / 2) + (sun_teeth * pitch_mm / 2)    #carrier radius


#create the placement matrices for the first stage planets
m_c1_1 = Hz(0)
m_c1_1[0][3] = carrier_planets_to_sun_distance
#create the next two placement matrixes by rotating the first placement matrix by the carrier spacing (assumed to be even, so 120 and 240)
ca = 120
m_c2_1 = Hz(ca*np.pi/180).dot(m_c1_1)    #pre-multiply by 120 degrees rotation in z to put the gear in the right position
m_c2_1 = m_c2_1.dot(Hz(-ca*np.pi/180*r1_teeth/p1_teeth))   #post multiply by the amount the gear would have rotated while meshed when being brought over to the carrier location
ca = 120*2
m_c3_1 = Hz(ca*np.pi/180).dot(m_c1_1)    #placement matrix for second planet
m_c3_1 = m_c3_1.dot(Hz(-ca*np.pi/180*r1_teeth/p1_teeth))


DeleteAllGears()

#Ring 1
r1 = freecad.gears.commands.CreateInternalInvoluteGear.create()
r1.numpoints = num_points
r1.num_teeth = r1_teeth
r1.module = pitch_mm     #mm 
r1.pressure_angle = pressure_angle  #degrees
r1.properties_from_tool = True    #"if helix_angle is given and properties_from_tool is enabled, gear parameters are internally recomputed for the rotated gear"
r1.thickness = r1.module*5   #mm. material added past the *addendum*? six teeth's worth seems decent
r1.height = r1_height   #mm
r1.shift = profile_shift
if(noclearance == True):
	r1.clearance = 0
	r1.head = 0

#helper function to re-call .create with the correct parameters
def CreateP1Planet():
    #Planet 1, stage 1
    p1 = freecad.gears.commands.CreateInvoluteGear.create()
    p1.numpoints = num_points
    p1.module = pitch_mm
    p1.pressure_angle = pressure_angle
    p1.num_teeth = p1_teeth
    p1.height = r1.height
    p1.properties_from_tool = True
    p1.axle_hole = True
    p1.axle_holesize = planet_bore    #mm
    p1.shift = -profile_shift
    if(noclearance == True):
        p1.clearance = 0
        p1.head = 0
    return p1



#Planet 1, stage 1
p1_1 = CreateP1Planet()
m = NumpyMatrixToFreecadMatrix(m_c1_1)
p1_1.Placement = FreeCAD.Placement(m)

#Planet 2, stage 1
p2_1 = CreateP1Planet()
m = NumpyMatrixToFreecadMatrix(m_c2_1)
p2_1.Placement = FreeCAD.Placement(m)

#Planet 3, stage 1
p3_1 = CreateP1Planet()
m = NumpyMatrixToFreecadMatrix(m_c3_1)
p3_1.Placement = FreeCAD.Placement(m)







#Ring 2 (stage 2)
r2 = freecad.gears.commands.CreateInternalInvoluteGear.create()
r2.num_teeth = r2_teeth
r2.module = pitch_mm     #mm 
r2.numpoints = num_points
r2.pressure_angle = pressure_angle  #degrees
r2.properties_from_tool = True    #"if helix_angle is given and properties_from_tool is enabled, gear parameters are internally recomputed for the rotated gear"
r2.height = r2_height   #mm
r2.shift = profile_shift
r2.thickness = r2.module*5   #mm. material added past the *addendum*? six teeth's worth seems decent
if(noclearance == True):
	r2.clearance = 0
	r2.head = 0

#recompute before adjusting the thickness again
App.ActiveDocument.recompute()
Gui.SendMsgToActiveView("ViewFit")
# dist_to_r2_bearing = FreeCAD.Units.Quantity(r2_bearing_inner_race_ID, "mm") - r2.pitch_diameter
# if(dist_to_r2_bearing > 0.5):
#     r2.thickness = (dist_to_r2_bearing)/2   #mm. material added past the *addendum*? six teeth's worth seems decent
#     print("Adjusted r2 thickness to match bearing")
# else:
#     print("Aborting due to pitch diameter being larger than top bearing ID.")
#locate ring 2
r2loc = Hz(0)
r2loc[2][3] = r1_height+r2_r1_offset
r2.Placement = FreeCAD.Placement(NumpyMatrixToFreecadMatrix(r2loc))


#helper function to re-call .create with the correct parameters
def CreateP2Planet():
    #Planet 1, stage 1
    p2 = freecad.gears.commands.CreateInvoluteGear.create()
    p2.module = pitch_mm
    p2.pressure_angle = pressure_angle
    p2.numpoints = num_points
    p2.num_teeth = p2_teeth
    p2.height = p2_height
    p2.properties_from_tool = True
    p2.axle_hole = True
    p2.axle_holesize = planet_bore    #mm
    p2.shift = -profile_shift
    if(noclearance == True):
        p2.clearance = 0
        p2.head = 0
    return p2

#create stack2 base planet (zero rotation/clocked with ring1)
p1_2 = CreateP2Planet()
p2_base_loc = Hz(0)
p2_base_loc[2][3] = p1_1.height
m_c1_2 = m_c1_1.dot(p2_base_loc) 
p1_2.Placement = FreeCAD.Placement(NumpyMatrixToFreecadMatrix(m_c1_2))

#locate second planet by rotating the first planet by 120 about the world Z axis, and about itself by the amount the gear would travel while doing that rotation
p2_2 = CreateP2Planet()
m_c2_2 = Hz(120*np.pi/180).dot(m_c1_2)
m_c2_2 = m_c2_2.dot(Hz(-120*np.pi/180*r2_teeth/p2_teeth))
p2_2.Placement = FreeCAD.Placement(NumpyMatrixToFreecadMatrix(m_c2_2))

#locate the third planet by doing the same operation to the second planet! 
p3_2 = CreateP2Planet()
m_c3_2 = Hz(120*np.pi/180).dot(m_c2_2)
m_c3_2 = m_c3_2.dot(Hz(-120*np.pi/180*r2_teeth/p2_teeth))
p3_2.Placement = FreeCAD.Placement(NumpyMatrixToFreecadMatrix(m_c3_2))

#recompute!
App.ActiveDocument.recompute()
Gui.SendMsgToActiveView("ViewFit")



#End gear generation. Begin automatic export of gears to .step files
###################################################################################################################################################


# Determine the directory of the current script
try:
    script_dir = os.path.dirname(os.path.realpath(__file__))+str("/STEP/")
except NameError:
    raise RuntimeError("The __file__ variable is not defined. Cannot determine the script's directory.")

print("Starting exports")
doc = FreeCAD.activeDocument()
objs = [
    doc.getObject(p3_2.Name),
    doc.getObject(p3_1.Name)
]
step_name = "p3Stack.step"
export_path = os.path.join(script_dir, step_name)
print("Exporting as", export_path)
Part.export(objs, export_path) #r"C:\Users\Ocanath Robotman\Desktop\PLANETSTEP\p3Stack.step"


objs = [
    doc.getObject(p2_2.Name),
    doc.getObject(p2_1.Name)
]
step_name = "p2Stack.step"
export_path = os.path.join(script_dir, step_name)
print("Exporting as", export_path)
Part.export(objs, export_path) #r"C:\Users\Ocanath Robotman\Desktop\PLANETSTEP\p3Stack.step"


doc = FreeCAD.activeDocument()
objs = [
    doc.getObject(p1_2.Name),
    doc.getObject(p1_1.Name)
]
step_name = "p1Stack.step"
export_path = os.path.join(script_dir, step_name)
print("Exporting as", export_path)
Part.export(objs, export_path) #r"C:\Users\Ocanath Robotman\Desktop\PLANETSTEP\p3Stack.step"


doc = FreeCAD.activeDocument()
objs = [
    doc.getObject(r1.Name)
]
step_name = "r1.step"
export_path = os.path.join(script_dir, step_name)
print("Exporting as", export_path)
Part.export(objs, export_path) #r"C:\Users\Ocanath Robotman\Desktop\PLANETSTEP\p3Stack.step"


doc = FreeCAD.activeDocument()
objs = [
    doc.getObject(r2.Name)
]
step_name = "r2.step"
export_path = os.path.join(script_dir, step_name)
print("Exporting as", export_path)
Part.export(objs, export_path) #r"C:\Users\Ocanath Robotman\Desktop\PLANETSTEP\p3Stack.step"




doc = FreeCAD.activeDocument()
objs = [
    doc.getObject(r1.Name),
    doc.getObject(r2.Name),
    doc.getObject(p1_1.Name),
    doc.getObject(p2_1.Name),
    doc.getObject(p3_1.Name),
    doc.getObject(p1_2.Name),
    doc.getObject(p2_2.Name),
    doc.getObject(p3_2.Name)
]
step_name = "all.step"
export_path = os.path.join(script_dir, step_name)
print("Exporting as", export_path)
Part.export(objs, export_path) #r"C:\Users\Ocanath Robotman\Desktop\PLANETSTEP\p3Stack.step"

print("Done!")
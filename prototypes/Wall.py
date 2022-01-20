
import uuid
import time
import tempfile

import ifcopenshell
import numpy
import apiai
import speech_recognition as sr
import re


##IFC Definitions and imports
#Variables directions
O = 0., 0., 0.
X = 1., 0., 0.
Y = 0., 1., 0.
Z = 0., 0., 1.


#open a file/Import this from mail file somehow!!!!
ifcfile = ifcopenshell.open("./one.ifc")

# Obtain references to instances defined in template !!! Define the filename with code
owner_history = ifcfile.by_type("IfcOwnerHistory")[0]
project = ifcfile.by_type("IfcProject")[0]
context = ifcfile.by_type("IfcGeometricRepresentationContext")[0]
filename = "one.ifc"


# Helper function definitions

# Creates an IfcAxis2Placement3D from Location, Axis and RefDirection specified as Python tuples
def create_ifcaxis2placement(ifcfile, point=O, dir1=Z, dir2=X):
    point = ifcfile.createIfcCartesianPoint(point)
    dir1 = ifcfile.createIfcDirection(dir1)
    dir2 = ifcfile.createIfcDirection(dir2)
    axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

# Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
def create_ifclocalplacement(ifcfile, point=O, dir1=Z, dir2=X, relative_to=None):
    axis2placement = create_ifcaxis2placement(ifcfile,point,dir1,dir2)
    ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to,axis2placement)
    return ifclocalplacement2

# Creates an IfcPolyLine from a list of points, specified as Python tuples
def create_ifcpolyline(ifcfile, point_list):
    ifcpts = []
    for point in point_list:
        point = ifcfile.createIfcCartesianPoint(point)
        ifcpts.append(point)
    polyline = ifcfile.createIfcPolyLine(ifcpts)
    return polyline
    
# Creates an IfcExtrudedAreaSolid from a list of points, specified as Python tuples
def create_ifcextrudedareasolid(ifcfile, point_list, ifcaxis2placement, extrude_dir, extrusion):
    polyline = create_ifcpolyline(ifcfile, point_list)
    ifcclosedprofile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    ifcdir = ifcfile.createIfcDirection(extrude_dir)
    ifcextrudedareasolid = ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
    return ifcextrudedareasolid
    
create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

# IFC hierarchy creation
site_placement = create_ifclocalplacement(ifcfile)
site = ifcfile.createIfcSite(create_guid(), owner_history, "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)

building_placement = create_ifclocalplacement(ifcfile, relative_to=site_placement)
building = ifcfile.createIfcBuilding(create_guid(), owner_history, 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)

storey_placement = create_ifclocalplacement(ifcfile, relative_to=building_placement)
elevation = 0.0
building_storey = ifcfile.createIfcBuildingStorey(create_guid(), owner_history, 'Storey', None, None, storey_placement, None, None, "ELEMENT", elevation)

container_storey = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])
container_site = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Site Container", None, site, [building])
container_project = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Project Container", None, project, [site])

## Write the template to a temporary file 
# temp_handle, temp_filename = tempfile.mkstemp(suffix=".ifc")
# with open(temp_filename, "w+") as f:
#     f.write(template)
 


##Voice Recognition Defs and Imports
# Voice to text
def get_voice():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 0.8
        r.dynamic_energy_threshold = True
        audio = r.listen(source)
        
    raw_text = r.recognize_google(audio)
    return raw_text

import pyttsx3;
def tts (text):
    engine = pyttsx3.init();
    engine.say(text);
    # engine.setProperty('voice', voices[2].id)
    engine.setProperty("rate", 155)
    engine.runAndWait() ;



#Wall Input Conversations
def wall_inputs():
    text = []
    tts (f"Please enter X dimension\n")
    text = get_voice()
    x_dimension = float(re.findall('\d*\.?\d+', text)[0])
    tts (f" X dimension is {x_dimension}")
    
    

    text = []
    tts (f"Please enter y dimension\n")
    text = get_voice()
    y_dimension = float(re.findall('\d*\.?\d+', text)[0])
    #print(y_dimension)
    tts (f" Y dimension is {y_dimension}")
    

    text = []
    tts (f"Please enter the height\n")
    text = get_voice()
    z_dimension = float(re.findall('\d*\.?\d+', text)[0])
    #print(z_dimension)
    tts (f" Height is {z_dimension}")
    

    return x_dimension, y_dimension, z_dimension

####
x_dimension, y_dimension, z_dimension = wall_inputs()

#center cordinates

def create_origin():
    text = []
    tts (f"Please enter the closest point to origin\n")
    text = get_voice()
    origin_x = float(re.findall('\d*\.?\d+', text)[0])
    origin_y = float(re.findall('\d*\.?\d+', text)[1])
    tts (f"Closest point is {origin_x} comma {origin_x}")
    # def Convert(string):
    #     closest_point = list(string.split(" "))
    #     return closest_point
    return origin_x, origin_y


#coordinate creation
point_list_extrusion_area = [(origin_x, origin_y, 0.0), (x_dimension + origin_x, origin_y, 0.0), (x_dimension + origin_x, y_dimension + origin_y, 0.0), (origin_x, y_dimension+ origin_y, 0.0), (origin_x, origin_y, 0.0)]



#Create Wall
wall_placement = create_ifclocalplacement(ifcfile, relative_to=storey_placement)
polyline = create_ifcpolyline(ifcfile, [(0.0, 0.0, 0.0), (5.0, 0.0, 0.0)])
axis_representation = ifcfile.createIfcShapeRepresentation(context, "Axis", "Curve2D", [polyline])

extrusion_placement = create_ifcaxis2placement(ifcfile, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
solid = create_ifcextrudedareasolid(ifcfile, point_list_extrusion_area, extrusion_placement, (0.0, 0.0, 1.0), z_dimension)
body_representation = ifcfile.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])

product_shape = ifcfile.createIfcProductDefinitionShape(None, None, [axis_representation, body_representation])

wall = ifcfile.createIfcWallStandardCase(create_guid(), owner_history, "Wall", "An awesome wall", None, wall_placement, product_shape, None)

# Write the contents of the file to disk
ifcfile.write(filename)
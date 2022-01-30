import ifcopenshell
import numpy
import apiai
import speech_recognition as sr
import re
import pyttsx3
import webbrowser
import uuid
import time
import tempfile


class VoiceAssistant():

    def __init__(self):
        
        self.text_to_voice ('Hi, how can I help you')
        self.raw_text_init = self.get_voice()

        self.ifc_file_name = "two_wall"
        self.sensitive_keywords = ["colour", "dimension", "element", "height", "open", " create", "file", "report"]
        self.colours = ["red","blue","yellow"]   
        self.dimensions = ["x","y","height"]
        self.elements = ["wall","window","door"]
        self.files = ["4","5","6"]
        self.reports = ["height","something","something"] 
        self.commands = ["create", "delete", "change"]    

    def text_to_voice (self, text):

        engine = pyttsx3.init();
        engine.say(text);
        # engine.setProperty('voice', voices[2].id)
        engine.setProperty("rate", 155)
        engine.runAndWait() ;


    def get_voice (self):

        raw_text = {}
        r = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
            r.pause_threshold = 0.8
            # r.dynamic_energy_threshold = True
            audio = r.listen(source)
            raw_text = r.recognize_google(audio, key="AIzaSyBhrbvZFL508AEqoM1vlue-Xt3RdaQU7Bk", language = "en-US")
        return raw_text


    def nlp(self):

        command_type = [x for x in self.sensitive_keywords if x in self.raw_text_init]
        command_sup = []

        if command_type[:] == 'colour':
            command_sup = [x for x in self.colours if x in self.raw_text_init]

        elif command_type[:] == 'dimension':
            command_sup = [x for x in self.dimensions if x in self.raw_text_init]

        elif command_type[:] == 'element' or command_type[:] == 'create':
            command_sup = [x for x in self.elements if x in self.raw_text_init]

        elif command_type[:] == 'file' or command_type[:] == 'open':
            command_sup = [x for x in self.files if x in self.raw_text_init]

        elif command_type[:] == 'report':
            command_sup = [x for x in self.reports if x in self.raw_text_init]

        return command_type, command_sup



    def open_file(self):

        self.text_to_voice (f' Can you please give me the file name')
        get_voice_text = self.get_voice()
        file_name_ = re.findall('\d*\.?\d+',get_voice_text)[0]

        if [x for x in file_name_ if x in self.files]:
            
            self.text_to_voice (f'Ok, I will open the file {file_name_}')
            webbrowser.open(f'.\data\ifc_files\{file_name_}.txt')

        else:
            
            while bool([x for x in file_name_ if x in self.files])==False:
                
                self.text_to_voice (f' Sorry, but I can only open file {self.files}, do you want to open one of them?')
                get_voice_text = self.get_voice()
                file_name_ = re.findall('\d*\.?\d+',get_voice_text)[0]
                if [x for x in file_name_ if x in self.files]:
                    self.text_to_voice (f'Ok, I will open the file {file_name_}')
                    webbrowser.open(f'.\data\ifc_files\{file_name_}.txt')

    def change_wall_color(self):
        
        self.text_to_voice (f' Can you please give me the desired colour')
        get_voice_text = self.get_voice()
        colour_name_ = [x for x in self.colours if x in get_voice_text ]

        if [x for x in self.colours if x in get_voice_text]:
            
            self.text_to_voice (f'Ok, I will change the colour to {colour_name_}')
            """a command to change the colour of the wall"""
            
        else:
            
            while bool([x for x in self.colours if x in get_voice_text])==False:
                
                self.text_to_voice (f' Sorry, but I can only change to colour to {self.colours},Can you please give me the desired colour?')
                get_voice_text = self.get_voice()
                colour_name_ = [x for x in self.colours if x in get_voice_text]
                
                if [x for x in colour_name_ if x in self.colours]:
                    
                    self.text_to_voice (f'Ok, I will change the colour to {colour_name_}')
                    """a command to change the colour of the wall"""




    """ This block of code creates a wall"""

    #Variables directions
    O = 0., 0., 0.
    X = 1., 0., 0.
    Y = 0., 1., 0.
    Z = 0., 0., 1.


    #open a file/Import this from mail file somehow!!!!
    ifcfile = ifcopenshell.open("./data/ifc_files/one.ifc")

    # Obtain references to instances defined in template !!! Define the filename with code
    owner_history = ifcfile.by_type("IfcOwnerHistory")[0]
    project = ifcfile.by_type("IfcProject")[0]
    context = ifcfile.by_type("IfcGeometricRepresentationContext")[0]
    filename = "one.ifc"

    # Creates an IfcAxis2Placement3D from Location, Axis and RefDirection specified as Python tuples
    def create_ifcaxis2placement(self, ifcfile, point=O, dir1=Z, dir2=X):
        point = ifcfile.createIfcCartesianPoint(point)
        dir1 = ifcfile.createIfcDirection(dir1)
        dir2 = ifcfile.createIfcDirection(dir2)
        axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
        return axis2placement

    # Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
    def create_ifclocalplacement(self, ifcfile, point=O, dir1=Z, dir2=X, relative_to=None):
        axis2placement = self.create_ifcaxis2placement(ifcfile,point,dir1,dir2)
        ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to,axis2placement)
        return ifclocalplacement2

    # Creates an IfcPolyLine from a list of points, specified as Python tuples
    def create_ifcpolyline(self, ifcfile, point_list):
        ifcpts = []
        for point in point_list:
            point = ifcfile.createIfcCartesianPoint(point)
            ifcpts.append(point)
        polyline = ifcfile.createIfcPolyLine(ifcpts)
        return polyline
        
    # Creates an IfcExtrudedAreaSolid from a list of points, specified as Python tuples
    def create_ifcextrudedareasolid(self,ifcfile, point_list, ifcaxis2placement, extrude_dir, extrusion):
        polyline = self.create_ifcpolyline(ifcfile, point_list)
        ifcclosedprofile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
        ifcdir = ifcfile.createIfcDirection(extrude_dir)
        ifcextrudedareasolid = ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
        return ifcextrudedareasolid
        
    
    def create_wall(self):

        create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

        site_placement = self.create_ifclocalplacement(self.ifcfile)
        site = self.ifcfile.createIfcSite(create_guid(), self.owner_history, "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)

        building_placement = self.create_ifclocalplacement(self.ifcfile, relative_to=site_placement)
        building = self.ifcfile.createIfcBuilding(create_guid(), self.owner_history, 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)

        storey_placement = self.create_ifclocalplacement(self.ifcfile, relative_to=building_placement)
        elevation = 0.0
        building_storey = self.ifcfile.createIfcBuildingStorey(create_guid(), self.owner_history, 'Storey', None, None, storey_placement, None, None, "ELEMENT", elevation)

        container_storey = self.ifcfile.createIfcRelAggregates(create_guid(),self.owner_history, "Building Container", None, building, [building_storey])
        container_site = self.ifcfile.createIfcRelAggregates(create_guid(), self.owner_history, "Site Container", None, site, [building])
        container_project = self.ifcfile.createIfcRelAggregates(create_guid(), self.owner_history, "Project Container", None, self.project, [site])

        text = []
        self.text_to_voice (f"Please give me the X dimension\n")
        text = self.get_voice()
        x_dimension = float(re.findall('\d*\.?\d+', text)[0])
        # text_to_voice (f" X dimension is {x_dimension}")
        self.text_to_voice (f" OK")

        text = []
        self.text_to_voice (f"Please give me the y dimension\n")
        text = self.get_voice()
        y_dimension = float(re.findall('\d*\.?\d+', text)[0])
        #print(y_dimension)
        # text_to_voice (f" Y dimension is {y_dimension}")
        self.text_to_voice (f" OK")

        text = []
        self.text_to_voice (f"Please give me the the height\n")
        text = self.get_voice()
        z_dimension = float(re.findall('\d*\.?\d+', text)[0])
        #print(z_dimension)
        # text_to_voice (f" Height is {z_dimension}")
        self.text_to_voice (f" OK")

        text = []
        self.text_to_voice (f"Please give me the x and y values of the closest point to origin\n")
        text = self.get_voice()
        origin_x = float(re.findall('\d*\.?\d+', text)[0])
        origin_y = float(re.findall('\d*\.?\d+', text)[1])
        # text_to_voice (f"Closest point is {origin_x} comma {origin_x}")
        self.text_to_voice (f" OK, I will create the element")
        # text_to_voice (f" OK, now I can add a wall that its X dimension is {x_dimension}, y dimension is {y_dimension}, height is {z_dimension}, and the origin coordination is {origin_x} ans {origin_x} ")

        #coordinate creation
        point_list_extrusion_area = [(origin_x, origin_y, 0.0), (x_dimension + origin_x, origin_y, 0.0), (x_dimension + origin_x, y_dimension + origin_y, 0.0), (origin_x, y_dimension+ origin_y, 0.0), (origin_x, origin_y, 0.0)]

        #Create Wall
        wall_placement = self.create_ifclocalplacement(self.ifcfile, relative_to=storey_placement)
        polyline = self.create_ifcpolyline(self.ifcfile, [(0.0, 0.0, 0.0), (5.0, 0.0, 0.0)])
        axis_representation = self.ifcfile.createIfcShapeRepresentation(self.context, "Axis", "Curve2D", [polyline])

        extrusion_placement = self.create_ifcaxis2placement(self.ifcfile, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
        solid = self.create_ifcextrudedareasolid(self.ifcfile, point_list_extrusion_area, extrusion_placement, (0.0, 0.0, 1.0), z_dimension)
        body_representation = self.ifcfile.createIfcShapeRepresentation(self.context, "Body", "SweptSolid", [solid])

        product_shape = self.ifcfile.createIfcProductDefinitionShape(None, None, [axis_representation, body_representation])

        wall = self.ifcfile.createIfcWallStandardCase(create_guid(), self.owner_history, "Wall", "An awesome wall", None, wall_placement, product_shape, None)

        # Write the contents of the file to disk
        self.ifcfile.write(self.filename)

        return x_dimension, y_dimension, z_dimension, origin_x, origin_y

                
    def change_dimension(self):
        pass


    def create_element(self):

        self.create_wall()

        # command_type_of_vta, command_sup_of_vta = self.nlp()

        # if command_sup_of_vta[0] == 'wall':
        #     self.create_wall()
            
        # elif command_sup_of_vta[0] == 'window':
        #     self.text_to_voice ('Sorry But I am only one semester old, and cannot do that now!')
            
        # elif command_sup_of_vta[0] == 'door':
        #     self.text_to_voice ('Sorry But I am only one semester old, and cannot do that now!')

        # else:
        #     self.text_to_voice("Sorry, but for any reason I could not understand your command completely")

    
    def get_height_limit(self, ifc_file_name):

        ifcfile = ifcopenshell.open(f"./{ifc_file_name}.ifc")
        walls = ifcfile.by_type('IfcWall')
        answers = ["yes", "no"]
        self.text_to_voice (f"What is the height limit\n")
        text = []
        text = self.get_voice()
        element_limit = int(re.findall('\d*\.?\d+', text)[0])

        short_wall_index = []
        for i in range(0, len(walls)):
            wall_height = walls[i].Representation.Representations[1].Items[0][3]
            if wall_height < element_limit:
                short_wall_index.append(i)

        self.text_to_voice (f"You have {len(walls)} walls and {len(short_wall_index)} of them are shorter than {element_limit} meter.") 
        self.text_to_voice (f"Would you like to hear the ids\n")

        raw_text = self.get_voice()
        
        if ([x for x in answers if x in raw_text][0]) == 'yes':
            for i in short_wall_index:
                print(i, walls[i])
            self.text_to_voice (f"The IDs are {short_wall_index} ")

        elif ([x for x in answers if x in raw_text][0]) == 'no':

            self.text_to_voice (f"ok ")


    def get_action(self):

        command_type_of_vta, command_sup_of_vta = self.nlp()

        print(command_type_of_vta, command_sup_of_vta)

        if command_type_of_vta[0] == 'colour' or command_type_of_vta[0] == 'change':
            self.change_wall_color()
            
        elif command_type_of_vta[0] == 'dimension':
            self.change_dimension()
            
        elif command_type_of_vta[0] == 'element' or command_type_of_vta[0] == 'create':
            self.create_element()
            
        elif command_type_of_vta[0] == 'file' or command_type_of_vta[0] == 'open':
            self.open_file()
            print("I reached to open file elif")

        elif command_type_of_vta[0] == 'report' or command_type_of_vta[0] == 'height':
            self.get_height_limit(self.ifc_file_name) 

        else:
            self.text_to_voice("Sorry, but for any reason I could not understand your command")

        print("I reached get action")

    def voice_to_action(self):
        # self.text_to_voice ('Hi, how can I help you')
        # raw_text_vat = self.get_voice()
        self.get_action()
        print("I reached voice to action")


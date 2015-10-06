################################################################################
#
# specsw.py
#
################################################################################

from specs import SPECS, SPECSGroup, SPECSRegion
import os
import xml.etree.cElementTree as ET
from time import asctime, localtime

Au4f_name = "Au4f"
VERBOSE = 0
xmlheader = '''<?xml version="1.0"?>
<!-- CORBA XML document created by XMLSerializer2 1.6 at 2015-07-21 16:24:09 UTC, from SL 2.78-r28574 built 2012-08-10 09:11:32 UTC -->
<!DOCTYPE any [
<!ELEMENT any (any|typecode|sequence|array|struct|union|exception|string|objectref|enum|boolean|char|octet|short|ushort|long|ulong|float|double)?>
<!ATTLIST any name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED version CDATA #IMPLIED>
<!ELEMENT typecode (any|typecode|sequence|array|struct|union|exception|string|objectref|enum|boolean|char|octet|short|ushort|long|ulong|float|double)?>
<!ATTLIST typecode name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT sequence ((any|typecode|sequence|array|struct|union|exception|string|objectref)+|(enum|boolean|char|octet|short|ushort|long|ulong|float|double))?>
<!ATTLIST sequence name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED length NMTOKEN #REQUIRED bound NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT array ((any|typecode|sequence|array|struct|union|exception|string|objectref)+|(enum|boolean|char|octet|short|ushort|long|ulong|float|double))?>
<!ATTLIST array name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED length NMTOKEN #REQUIRED label NMTOKEN #IMPLIED>
<!ELEMENT struct (any|typecode|sequence|array|struct|union|exception|string|objectref|enum|boolean|char|octet|short|ushort|long|ulong|float|double)*>
<!ATTLIST struct name NMTOKEN #IMPLIED type_id CDATA #REQUIRED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT union (any|typecode|sequence|array|struct|union|exception|string|objectref|enum|boolean|char|octet|short|ushort|long|ulong|float|double)*>
<!ATTLIST union name NMTOKEN #IMPLIED type_id CDATA #REQUIRED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT exception (any|typecode|sequence|array|struct|union|exception|string|objectref|enum|boolean|char|octet|short|ushort|long|ulong|float|double)*>
<!ATTLIST exception name NMTOKEN #IMPLIED type_id CDATA #REQUIRED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT string (#PCDATA)>
<!ATTLIST string name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED bound NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT objectref (#PCDATA)>
<!ATTLIST objectref name NMTOKEN #IMPLIED type_id CDATA #REQUIRED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT enum (#PCDATA)>
<!ATTLIST enum name NMTOKEN #IMPLIED type_id CDATA #REQUIRED type_name NMTOKEN #IMPLIED values NMTOKENS #REQUIRED label NMTOKEN #IMPLIED>
<!ELEMENT boolean (#PCDATA)>
<!ATTLIST boolean name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT char (#PCDATA)>
<!ATTLIST char name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT octet (#PCDATA)>
<!ATTLIST octet name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT short (#PCDATA)>
<!ATTLIST short name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT ushort (#PCDATA)>
<!ATTLIST ushort name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT long (#PCDATA)>
<!ATTLIST long name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT ulong (#PCDATA)>
<!ATTLIST ulong name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT float (#PCDATA)>
<!ATTLIST float name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
<!ELEMENT double (#PCDATA)>
<!ATTLIST double name NMTOKEN #IMPLIED type_id CDATA #IMPLIED type_name NMTOKEN #IMPLIED label NMTOKEN #IMPLIED>
]>
'''

class SPECS_W(SPECS):
    """ Represent a SPECSLab .xml output as a python object. Construct with:

        specs_obj = specs.SPECS(my_xml_file)

    """

    def __init__(self, filename, verbose=None):
        """ Constructor, takes the xml file path. """
        
        if verbose:
            global VERBOSE 
            VERBOSE = 1

        self.filename = filename

        if VERBOSE: 
            print self.__class__.__name__ + "::Loading Specs XML " + filename
        
        """ Constructor, takes the xml file path. """
        
        tree = ET.ElementTree()
        self.tree = tree
        
        try:
          self.xmlroot = tree.parse(filename)
        except NameError:
          print "SPECS init error: could not open this file as an xml tree."
          return None
        except ET.ParseError:
          # We probably need to decode from Windows cp1252 string encoding.
          f = open(filename, 'r')
          contents = f.readlines()
          f.close()
          contents = "".join(contents).decode("cp1252").encode("utf-8")
          self.xmlroot = tree.parse(StringIO(contents))

        # The version impacts on properties of the document so we need to read it
        # here.
        self.xmlversion = self.xmlroot.get('version')

        # For convenience, store groups as a list and provide a member function
        # to access by name - same for regions.
        self.groups = []
        for group in list(self.xmlroot[0]):
            # All the subelements will be individual groups (called a RegionGroup in
            # SPECS parlance) but we must check in case the file format changes.
            if group.get('type_name') == "RegionGroup":
                self.groups.append(SPECSGroup_W(group))
    
    def writeCalibratedXml(self, working_dir=None):
        global xmlheader
        if working_dir == None:
            working_dir = os.getcwd()
        filepath, filename = os.path.split(self.filename) 
        mainname, extname = os.path.splitext(filename)
        newfilename = os.path.join( working_dir, mainname + '-calibrated.xml')    
        noheaderilename = os.path.join( working_dir, mainname + '-noheader.xml')
        self.tree.write( noheaderilename)
        with file(noheaderilename, 'r') as original: data = original.read()
        with file(newfilename, 'w') as modified: modified.write(xmlheader + data)
        original.close()
        modified.close()
        return newfilename

class SPECSGroup_W(SPECSGroup):
    """ Encapsulates a "RegionGroup" struct from the SPECS XML format. """

    def __init__(self, xmlgroup):

        self.xmlgroup = xmlgroup

        super(self.__class__, self).__init__(xmlgroup)
        if VERBOSE: 
            print self.__class__.__name__ + "::Loading Group " + self.name
        del self.regions
        self.regions = []
        for region in list(xmlgroup[1]):
            if region.get('type_name') == "RegionData":
                self.regions.append(SPECSRegion_W(region))

class SPECSRegion_W(SPECSRegion):
    """ Encapsulates a "RegionData" struct from the SPECS XML format. """

    def __init__(self, xmlregion):

        self.xmlregion = xmlregion
        self.isClibrated = False
        super(self.__class__, self).__init__(xmlregion)
        if VERBOSE: print self.__class__.__name__ + "::Loading Region " + self.name
        # get time
        time = xmlregion.find(".//ulong[@name='time']")
        self.time = int(time.text)

    def setXmlExcitationEnergy(self, excitation_energy):
        rdef = self.xmlregion.find(".//struct[@type_name='RegionDef']")
        for elem in rdef:
            if elem.attrib['name'] == "excitation_energy":
                elem.text = excitation_energy

    def setXmlKineticEnergy(self, kinetic_energy):
        rdef = self.xmlregion.find(".//struct[@type_name='RegionDef']")
        for elem in rdef:
            if elem.attrib['name'] == "kinetic_energy":
                elem.text = kinetic_energy

    def setXmlRegionDataName(self, name):
        self.xmlregion[0].text = name

    def calculate_binding_axis(self,excitation_energy):
        self.binding_axis = excitation_energy - self.kinetic_axis
    
    def getPeakLocation(self):
        peak_loc_elem = self.xmlregion.find(".//struct[@name='x']//double[@name='value']")
        if peak_loc_elem == None:
            raise ValueError("could not find Peak Location in %r %r" % ( Au4f_name, asctime(localtime(self.time))))
        return float(peak_loc_elem.text)   


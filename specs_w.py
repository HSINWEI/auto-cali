################################################################################
#
# specsw.py
#
################################################################################

from specs import SPECS, SPECSGroup, SPECSRegion
import os
import xml.etree.cElementTree as ET

VERBOSE = 0

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
    
    def writeCalibratedXml(self):
        mainname, extname = os.path.splitext(self.filename)
        newfilename = mainname + '-calibrated.xml'
        self.tree.write(newfilename)
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

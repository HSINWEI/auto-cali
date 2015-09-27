################################################################################
#
# specs.py
#
# Parse the XML output of SPECSLab v2 into a python object.
#
################################################################################
#
# Copyright 2013 Kane O'Donnell
#
#     This library is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this library.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
#
# NOTES
#
# 1. I hate XML!
#
# 1b. This is version 2 of the library - I have tried to be more version-
#    agnostic in the XML parsing here so we aren't as sensitive to file format.
#
# 2. This library is not complete - plan is to incrementally add more member
#    elements to the classes as necessary.
#
# 3. There are functions for things like Shirley background subtraction at the
#    end of the file after the classes. These are tuned to work with the outputs
#    of SPECS but will work more generally if necessary.
#
# 4. The fundamental issue to deal with here is that there are different
#    versions of the SPECS XML format (1.3 and 1.6 are the most prevalent as of
#    the 1st of October 2012) and they store the data in slightly different
#    ways. So we often don't pull things directly from the XML tree by position
#    but rather we search for them or iterate through a list and check props
#    before we act on a given element.
#
# 5. This version converted to be pep8 compliant with autopep8
#
################################################################################

from __future__ import division
# import xml.etree.ElementTree        # required by py2exe
import xml.etree.ElementTree as ET
from StringIO import StringIO
from numpy import array, linspace, arange, zeros, ceil, amax, amin, argmax, argmin, abs
from numpy import seterr, trunc
# from numpy.linalg import norm
# from scipy.interpolate import interp1d
import os

DEBUG = False
OPTION = 2

# We do not allow divide by zeros at all: raise an error if it happens.
seterr(divide='raise')

################################################################################
#
# CLASSES
#
################################################################################


class SPECS(object):
    """ Represent a SPECSLab .xml output as a python object. Construct with:

        specs_obj = specs.SPECS(my_xml_file)

    """

    def __init__(self, filename, verbose):
        """ Constructor, takes the xml file path. """
        if (verbose): 
            global DEBUG
            DEBUG = True

        self.filename = filename
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
                self.groups.append(SPECSGroup(group))
    
    def writeCalibratedXml(self):
        file_main, file_extension = os.path.splitext(self.filename)
        newfilename = file_main+'-calibrated.xml'
        self.tree.write(newfilename)
        return newfilename

class SPECSGroup(object):
    """ Encapsulates a "RegionGroup" struct from the SPECS XML format. """

    def __init__(self, xmlgroup):

        self.xmlgroup = xmlgroup
        self.name = xmlgroup[0].text
        
        if DEBUG:
            print "======================= ", self.name, " ========================"

        self.regions = []
        for region in list(xmlgroup[1]):
            if region.get('type_name') == "RegionData":
                self.regions.append(SPECSRegion(region))


class SPECSRegion(object):
    """ Encapsulates a "RegionData" struct from the SPECS XML format. """

    def __init__(self, xmlregion):

        self.xmlregion = xmlregion
        self.name = xmlregion[0].text
        self.num_cycles = int(xmlregion[7].attrib['length'])
        if DEBUG:
            print "======================= ", self.name, " ========================"

        self.raw_counts = []
        self.scaling_factors = []
        self.extended_channels = []

        # First grab the counts for this region: this is the most important part.
        # The counts can't be used directly as they incorporate all nine channels
        # in a single array and need to be chopped and aligned first.
        # Improvement from v1: we search directly for the named sequence rather
        # than iterating generally.
        for elem in xmlregion.findall(".//sequence[@type_name='CountsSeq']"):
            self.raw_counts.append(
                array([int(x) for x in elem[0].text.split()]))

        # Scaling factors for the counts.
        # for elem in xmlregion.findall(".//sequence[@name='scaling_factors']"):
        #     self.scaling_factors.append(
        #         array([float(x) for x in elem[0].text.split()]))

        # Look for Extended Channels in a YCurveSeq set.
        for ycs in xmlregion.findall(".//sequence[@type_name='YCurveSeq']"):
            for ycurve in ycs:
                if "Extended Channel" in ycurve[0].text:
                    for channel in ycurve.iter('sequence'):
                        if channel.attrib['name'] == "data":
                            tmp = array(
                                [float(x) for x in channel[0].text.split()])
                            self.extended_channels.append(tmp)

        # Grab the transmission function. This is *not* to be trusted but SPECS
        # might implicitly use it for display within the SPECS program itself so
        # we need to read it.
        trans = xmlregion.find(".//sequence[@name='transmission']")
        if trans is not None and len(trans) > 0:
            try:
                self.transmission = array(
                    [float(x) for x in trans[0].text.split()])
            except ValueError:
                # SPECS sometimes says the transmission is "Infinity", obviously not a
                # useful number so we explicitly set the transmission to be None here.
                self.transmission = None
        else:
            self.transmission = None

        # Iterate over all the elements in the RegionDef struct.
        # Note: should ONLY BE ONE of these, so use find rather than findall.
        rdef = xmlregion.find(".//struct[@type_name='RegionDef']")
        for elem in rdef:
            if elem.attrib['name'] == "scan_mode":
                self.scan_mode = elem[0].text
            elif elem.attrib['name'] == "dwell_time":
                self.dwell_time = float(elem.text)
            elif elem.attrib['name'] == "analyzer_lens":
                self.analyzer_lens = elem.text
            elif elem.attrib['name'] == "scan_delta":
                self.scan_delta = float(elem.text)
            elif elem.attrib['name'] == "excitation_energy":
                self.excitation_energy = float(elem.text)
            elif elem.attrib['name'] == "pass_energy":
                self.pass_energy = float(elem.text)
            elif elem.attrib['name'] == "kinetic_energy":
                self.kinetic_energy = float(elem.text)
            elif elem.attrib['name'] == "values_per_curve":
                self.values_per_curve = int(elem.text)
            elif elem.attrib['name'] == "effective_workfunction":
                self.effective_workfunction = float(elem.text)

        # The kinetic energy and binding energy axes:
        ke_upper = self.kinetic_energy + (self.values_per_curve -
                                          1) * self.scan_delta
        self.kinetic_axis = linspace(
            self.kinetic_energy, ke_upper, self.values_per_curve)
        self.binding_axis = self.excitation_energy - self.kinetic_axis

        # Excitation axis (for NEXAFS)
        exc_upper = self.excitation_energy + (
            self.values_per_curve - 1) * self.scan_delta
        self.excitation_axis = linspace(
            self.excitation_energy, exc_upper, self.values_per_curve)

        # Time axis
        self.time_axis = arange(self.values_per_curve) * self.dwell_time

        # MCD head and tail are the extra elements added to the beginning and
        # end of the scan.
        self.mcd_head = int(xmlregion.find(".//*[@name='mcd_head']").text)
        self.mcd_tail = int(xmlregion.find(".//*[@name='mcd_tail']").text)

        # Get the detector information for the energy position of each channeltron.
        self.detector_channel_shifts = []
        self.detector_channel_positions = []
        self.detector_channel_gains = []

        detectors = xmlregion.find(".//sequence[@type_name='DetectorSeq']")
        for elem in detectors:
            if elem.attrib['type_name'] == "Detector":
                for subelem in elem.iter():
                    if "name" in subelem.attrib.keys():
                        if subelem.attrib['name'] == "position":
                            self.detector_channel_positions.append(
                                float(subelem.text))
                        if subelem.attrib['name'] == "shift":
                            self.detector_channel_shifts.append(
                                float(subelem.text))
                        if subelem.attrib['name'] == 'gain':
                            self.detector_channel_gains.append(
                                float(subelem.text))

        self.detector_channel_shifts = array(self.detector_channel_shifts)
        self.detector_channel_positions = array(
            self.detector_channel_positions)
        self.detector_channel_gains = array(self.detector_channel_gains)

        # Use the pass energy to calculate detector calibration.
        self.detector_channel_offsets = self.pass_energy * \
            self.detector_channel_shifts

        num_detectors = len(self.detector_channel_offsets)

        # Now, we need to know the analyzer mode, because how we add the channeltron data
        # together depends on whether we are sweeping the kinetic energy in the analyzer or
        # not.
        scanmode = xmlregion.find(".//struct[@type_name='ScanMode']")
        self.scan_mode = scanmode[0].text

        # Calculate so and si (based on the SPECS document "Acquiring Data with
        # Multidetector systems"). Don't really need si or t.
        try:
            so = self.detector_channel_offsets[-1]
            #si = self.detector_channel_offsets[0]
            h = int(trunc(so / self.scan_delta + 0.5))
        except IndexError:
            print "IndexError in unpacking: ", num_detectors
        #t = int(trunc(-si / self.scan_delta + 0.5))

        # Now use the h value to calculate the index offsets for each of the channels.
        # (This isn't used for ConstantFinalState)
        start_energies = []
        for i in range(num_detectors):
            start_energies.append(self.kinetic_energy - h * self.scan_delta +
                                  self.detector_channel_offsets[i])
        idxs = []
        for i in range(num_detectors):
            idxs.append(int(trunc((self.kinetic_energy -
                        start_energies[i]) / self.scan_delta + 0.5)))

        # We now need to separate the raw counts into channels and assign each counts value
        # to a nominal energy value again according to the SPECS document referenced above,
        # using the "Nearest-Neighbour" method.
        self.counts = zeros((self.values_per_curve))
        self.channel_counts = zeros(
            (self.values_per_curve, len(self.detector_channel_offsets)))

        for c in self.raw_counts:
            tmp_channels = []
            for i in range(num_detectors):
                tmp_channels.append(c[i::num_detectors])
            # IMPORTANT: If FixedAnalyzerTransmission or FixedRetardingRatio, we need to use
            # the nearest-neighbour method to align the channeltron energies. I have only
            # implemented the method for FixedAnalyzerTransission at the moment - the FRR
            # implementation is different and rather more difficult and no one ever uses it.
            if self.scan_mode != "FixedAnalyzerTransmission":
                for i in range(num_detectors):
                    self.counts += array(tmp_channels[i])
                    self.channel_counts[:, i] += array(tmp_channels[i])
            else:
                for i in range(self.values_per_curve):
                    for j in range(num_detectors):
                        try:
                            self.counts[i] += tmp_channels[j][i + idxs[j]]
                            self.channel_counts[
                                i, j] += tmp_channels[j][i + idxs[j]]
                        except IndexError:
                            print "SPECSRegion: Darn, an index error unpacking the channeltron data. This was not supposed to happen!"

        # Trim the extended channels if they are present. There should not be any
        # calibration issue here - SPECS just treats the extended channels as if
        # they are channeltrons and therefore gives them extra data points on either
        # side as indicated by MCD head and tail. One could leave the extra points
        # in without any hassle but you would then not match the actual excitation
        # or kinetic energy range specified by the end-user.
        for i in range(len(self.extended_channels)):
            if self.mcd_tail == 0:
                c = self.extended_channels[i]
                self.extended_channels[i] = c[self.mcd_head:len(c)]
            else:
                self.extended_channels[i] = self.extended_channels[
                    i][self.mcd_head:-self.mcd_tail]

        # If there are extended channels, reshape them into an array.
        if self.extended_channels:
            if DEBUG:
                print "Extended channels: ", len(self.extended_channels)
                print "Extended channel data length: ", len(
                    self.extended_channels[0])
            tmparr = zeros(
                (len(self.extended_channels[0]), len(self.extended_channels)))
            for i, tmpex in enumerate(self.extended_channels):
                tmparr[:, i] = tmpex
            self.extended_channels = tmparr
        else:
            self.extended_channels = None

        # Extract the comment from the parameter list.
        for elem in xmlregion[9].iter("struct"):
            if elem[0].text == "Comment":
                self.comment = elem[1].text
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

    def setXmlRegionDataName(self,name):
        self.xmlregion[0].text = name

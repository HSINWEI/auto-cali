import xml.etree.ElementTree as ET
import specs
from numpy import argmax
# import time
# from scipy.interpolate import interp1d
import sys

DEBUG = False
# predefine variables
Au4f_binding_energy = 83.96
Au4f_name = "Au4f"

def processSingleXml(filename, verbose=None):
    try:
        print "Process " + filename
        sys.stdout.flush()
        specs_obj = specs.SPECS(filename, verbose)
    except:
        print "        Cannot open " + filename
        return

    # get Au4f (time, peak energy)
    Au4fPeaks = []
    for group in  specs_obj.groups:
        for region in group.regions:   
            if region.name[:len(Au4f_name)] == Au4f_name:
                peak_index = argmax(region.counts)
                peak_energy = region.kinetic_axis[peak_index]
    #             print region.name + ' peak energy ' + str(peak_energy)
    #             f1 = interp1d(region.kinetic_axis,region.counts,kind='slinear')
    #             ke_upper = region.kinetic_energy + (region.values_per_curve -
    #                                           1) * region.scan_delta
    #             kinetic_axis_new = numpy.linspace(region.kinetic_energy, ke_upper, num=region.values_per_curve*10)
    # 
    #             peak_index = numpy.argmax(f1(kinetic_axis_new))
    #             peak_energy = kinetic_axis_new[peak_index]
    #             print region.name + ' peak energy interp nearest ' + str(peak_energy)
    # 
    #             mytime = time.asctime(time.localtime(region.time))
    #             print mytime
                Au4fPeak = {'time':region.time, 'energy':peak_energy}
                Au4fPeaks.append(Au4fPeak)
   
    # find sample data region and calibrate it's energy 
    for group in  specs_obj.groups:
        for region in group.regions:
            if region.name[:len(Au4f_name)] == Au4f_name:
                # this is Au4f data region
                if verbose: print "\t" + region.name
            else: 
                # this is sample data region
                if verbose: print "\t" + region.name
                # find prior Au4f and posterior Au4f
                for i in range(len(Au4fPeaks)):
                    if region.time < Au4fPeaks[i]['time'] and region.time > Au4fPeaks[i-1]['time']:
                        t1 = Au4fPeaks[i-1]['time']
                        t2 = Au4fPeaks[i]['time']
                        e1 = Au4fPeaks[i-1]['energy']
                        e2 = Au4fPeaks[i]['energy']
                        tt = region.time 
                        ee = e1 + (e2-e1)/(t2-t1)*(tt-t1)
                        calibrated_ex = ee + Au4f_binding_energy
                        binding_energy = calibrated_ex - region.kinetic_energy 
                        if verbose: 
                            print "\t\t" + "excitation_energy original   " + str(region.excitation_energy)
                            print "\t\t" + "excitation_energy calibrated " + '{:.2f}'.format(calibrated_ex)
                            print "\t\t" + "binding energy               " + '{:.2f}'.format(calibrated_ex)
                        
                        # denote energy is patched
                        region.setXmlRegionDataName(region.name + " calibrated binding energy")
                        # fill calibrated excitation energy
                        region.setXmlExcitationEnergy('{:.2f}'.format(calibrated_ex))
                        # fill kinetic energy filed with binding energy
                        region.setXmlKineticEnergy('{:.2f}'.format(binding_energy))
                        break

    # save as a new xml file
    newfilename = specs_obj.writeCalibratedXml()
    del specs_obj
    return newfilename 

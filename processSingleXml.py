import xml.etree.ElementTree as ET
import specs_w
from numpy import argmax
from time import asctime, localtime
# from scipy.interpolate import interp1d
import sys
import csv

DEBUG = False
# predefine variables
Au4f_binding_energy = 83.96
Au4f_name = "Au4f"
def processSingleXml(filename, verbose=None):
    try:
        print "\nProcessing " + filename
        sys.stdout.flush()
        specs_obj = specs_w.SPECS_W(filename, verbose)
    except IOError as e:
        print '        ' + str(e)
        return

    if specs_obj == None:
        return
    # get Au4f (time, peak energy)
    Au4fPeaks = []
    for group in  specs_obj.groups:
        for region in group.regions:   
            if region.name[:len(Au4f_name)] == Au4f_name:
                peak_index = argmax(region.counts)
                peak_max = region.kinetic_axis[peak_index]
                peak_energy = region.getPeakLocation()
                region.excitation_energy = peak_energy + Au4f_binding_energy 
                if verbose:
                    print "{:24s} {} Epeak {:.2f} => Eexc {:.2f} ;; Emax-Epeak={:.2f}-{:.2f}={: .2f}".format("Found "+region.name, asctime(localtime(region.time)), peak_energy, region.excitation_energy, peak_max, peak_energy, peak_max-peak_energy)
                Au4fPeak = {'time':region.time, 'peak':peak_energy, 'eexc':region.excitation_energy}
                Au4fPeaks.append(Au4fPeak)
   
    # find sample data region and calibrate it's energy 
    for group in  specs_obj.groups:
        for region in group.regions:
            if region.name[:len(Au4f_name)] == Au4f_name:
                # this is Au4f data region
                if verbose: 
                    print "{:24s} {}\tEexc {:.2f}".format(region.name, asctime(localtime(region.time)), region.excitation_energy)
            else:
                # this is sample data region
                # find prior Au4f and posterior Au4f
                for i in range(len(Au4fPeaks)):
                    if region.time < Au4fPeaks[i]['time'] and region.time > Au4fPeaks[i - 1]['time']:
                        t1 = Au4fPeaks[i - 1]['time']
                        t2 = Au4fPeaks[i]['time']
                        e1 = Au4fPeaks[i - 1]['eexc']
                        e2 = Au4fPeaks[i]['eexc']
                        tt = region.time 
                        calibrated_eexc = e1 + (e2 - e1) / (t2 - t1) * (tt - t1)
                        if verbose: 
                            print "{:24s} {}\tEexc {:.2f}\tEorg {:.2f}".format(region.name, asctime(localtime(region.time)), calibrated_eexc, region.excitation_energy)
                        
                        # denote energy is patched
                        region.setXmlRegionDataName(region.name + " energy calibration")
                        # fill calibrated excitation_energy energy
                        region.setXmlExcitationEnergy('{:.2f}'.format(calibrated_eexc))
                        # recalculate binding axis  
                        region.calculate_binding_axis(calibrated_eexc)
                        region.isClibrated = True
                        
                        with open(region.name + ".txt", 'w') as f:
                            writer = csv.writer(f, delimiter='\t')
                            writer.writerows(zip(region.binding_axis,region.counts))
                            f.close()

                        break
                if not region.isClibrated and verbose:
                    print "{:24s} Cannot find matched {} pair to calibrate {}".format(region.name, Au4f_name, region.name)
                        
                    
    # save as a new xml file
    newfilename = specs_obj.writeCalibratedXml()
    del specs_obj
    return newfilename 

import specs_w
from numpy import argmax
from time import asctime, localtime

Au4f_binding_energy = 83.96
Au4f_name = "Au4f"

filename = "d:\\auto-cali\\01.G400-CL.xml"
verbose = True
specs_obj = specs_w.SPECS_W(filename, verbose)

# get Au4f (time, peak energy)
Au4fPeaks = []
for group in  specs_obj.groups:
    for region in group.regions:   
        if region.name[:len(Au4f_name)] == Au4f_name:
            peak_index = argmax(region.counts)
            peak_energy = region.kinetic_axis[peak_index]
            region.excitation_energy = peak_energy + Au4f_binding_energy
            peak_loc = region.getPeakLocation() 
            if verbose:
                print "{:24s} {} Emax {:.3f} Epeak {:.3f} Eerr {:.3f} => Eexc {:.2f}".format("Found " + region.name, asctime(localtime(region.time)), peak_energy, peak_loc, peak_energy-peak_loc, region.excitation_energy)
            Au4fPeak = {'time':region.time, 'peak':peak_energy, 'eexc':region.excitation_energy}
            Au4fPeaks.append(Au4fPeak)


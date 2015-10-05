import specs_w
from numpy import argmax, linspace
from time import asctime, localtime
from scipy.interpolate import interp1d
import numpy as np

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
            peak_max_index = argmax(region.counts)
            peak_max = region.kinetic_axis[peak_max_index]
            peak_loc = region.getPeakLocation()
            fit_half_numof_elem = 10
            start_index = peak_max_index - fit_half_numof_elem +1
            end_index = peak_max_index + fit_half_numof_elem
            x = region.kinetic_axis[start_index:end_index]
            y = region.counts[start_index:end_index]
            f = interp1d(x, y, kind='quadratic')
            f3_cof = np.polyfit(x, y, deg=4)
            ke_upper = region.kinetic_energy + (region.values_per_curve - 1) * region.scan_delta
            xnew = linspace( region.kinetic_axis[start_index], region.kinetic_axis[end_index-1], region.values_per_curve*1000)
            f3_xnew = np.polyval(f3_cof, xnew)
            peak_fit = xnew[argmax(f3_xnew)]

            import matplotlib.pyplot as plt
            plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew, f3_xnew, '--')
            plt.legend(['data', 'linear', 'cubic'], loc='best')
            
            print "{:24s} {} Peak_max {:.3f} Peak_fit {:.3f} Peak_loc {:.3f} max-loc {:.3f} fit-loc {:.3f}".format("Found " + region.name, asctime(localtime(region.time)), peak_max, peak_fit, peak_loc, peak_max-peak_loc, peak_fit-peak_loc)
            plt.show()

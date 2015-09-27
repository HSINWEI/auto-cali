usage: auto-cali.exe [-h] [-v] [-V] [xml [xml ...]]

 -- Apply interpolation excitation energy to sample data
    
  Generate calibrated Specs XML file(s).
  
  In each sample's "Region Edit",
  1. Replace "Eexc" with interpolation excitation energy
  2. Replace "Energy Start" with binding energy
     binding energy = interpolation excitation energy - original "Energy Start" 
     
  Created by Chen, HsinWei on 2015-09-27.

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE

positional arguments:
  xml            SpecsLab xml file(s) [default: None]

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  set verbosity level [default: None]
  -V, --version  show program's version number and exit

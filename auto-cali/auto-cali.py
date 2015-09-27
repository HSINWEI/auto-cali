#!/usr/local/bin/python2.7
# encoding: utf-8
'''
 -- shortdesc

 is a description

It defines classes_and_methods

@author:     Chen, HsinWei

@copyright:  2015 NSRRC. All rights reserved.

@license:    license

@contact:    chen.hsinwei@nsrrc.org.tw
@deffield    updated: Updated
'''
from processSingleXml import processSingleXml 
import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from sre_constants import SUCCESS

__all__ = []
__version__ = 0.1
__date__ = '2015-09-27'
__updated__ = '2015-09-27'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Chen, HsinWei on %s.
  Copyright 2015 NSRRC. All rights reserved.

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="xmlfiles", help="SpecsLab xml file(s) [default: %(default)s]", metavar="xml", nargs='+')
        # Process arguments
        args = parser.parse_args()

        xmlfiles = args.xmlfiles
        verbose = args.verbose

        if verbose > 0:
            print("Verbose mode on")
        
        generated_files = []
        for filename in xmlfiles:
            newxmlfilename = processSingleXml(filename,verbose)
            if newxmlfilename:
                generated_files.append(newxmlfilename) 

        print "\nGenerated {} file(s):".format(len(generated_files))
        for filename in generated_files:
            print "    " + filename
        
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = '_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
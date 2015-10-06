#!/usr/local/bin/python2.7
# encoding: utf-8
'''
 -- Apply interpolation excitation energy to sample data

 is a description

It defines classes_and_methods

@author:	 Chen, HsinWei

@copyright:  None

@license:	None

@contact:	chen.hsinwei@nsrrc.org.tw
@deffield	updated: Updated
'''
from processSingleXml import processSingleXml 
import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.2
__date__ = '2015-10-06'
__updated__ = '2015-10-06'

DEBUG = 0
TESTRUN = 0
PROFILE = 0
PAUSE = 0

class CLIError(Exception):
	'''Generic exception to raise and log different fatal errors.'''
	def __init__(self, msg):
		super(CLIError).__init__(type(self))
		self.msg = "E: %s" % msg
	def __str__(self):
		return self.msg
	def __unicode__(self):
		return self.msg

def main(argv=None):  # IGNORE:C0111
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
	
  1. Generate calibrated Specs XML file(s).
     In each sample's "Region Edit",
     Replace "Eexc" with interpolation excitation energy
  2. Generate two columns txt files: binding energy, intensity 
	 
  Created by Chen, HsinWei on %s.

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

	try:
		# Setup argument parser
		parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
		parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
		parser.add_argument('-V', '--version', action='version', version=program_version_message)
		parser.add_argument(dest="xmlfiles", help="SpecsLab xml file(s) [default: %(default)s]", metavar="xml", nargs='*')
		parser.add_argument('-d', dest="workDir", help="destination directory for output result files [default: %(default)s]", metavar="working directory", default='.')
		parser.add_argument("-p", "--pause", dest="pause", action="count", help="Pause after calibration accomplished")
		# Process arguments
		args = parser.parse_args()

		xmlfiles = args.xmlfiles
		verbose = args.verbose
		workDir = os.path.abspath(args.workDir)
		PAUSE = args.pause
		if not os.path.exists(workDir):
			print "-d \"%s\"" % workDir
			print "        The destination directory \"%s\" does not exist.\n        Create it." % workDir
			if PAUSE:
				raw_input("\nPress ENTER to exit\n")
			return 0
		
		if len(xmlfiles) == 0:
			parser.print_help()
			return 0

		if verbose > 0:
			print("Verbose mode on")
		
		generated_files = []
		for xmlfilename in xmlfiles:
			# get relative directory from xmlfilename	
			xmlfilename_path, xmlfilename_file = os.path.split(xmlfilename)
			xmlfile_main, xmlfile_ext = os.path.splitext(xmlfilename_file)
			basedir = os.path.basename(xmlfilename_path)
			# join working directory and relative directory  
			destDir = os.path.join(workDir, basedir, xmlfile_main)
			try: 
				os.makedirs(destDir)
			except os.error as e:
				print "The leaf directory %r already exists" % os.path.join(os.path.abspath(destDir))
				raise os.error

			os.chdir(destDir)
			newxmlfilename = processSingleXml(xmlfilename, verbose)
			if newxmlfilename:
				generated_files.append(os.path.abspath(newxmlfilename)) 

		print "\nGenerated {} file(s):".format(len(generated_files))
		for filename in generated_files:
			print "	" + filename
		if PAUSE:
			raw_input("\nPress ENTER to exit\n")
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
		if PAUSE:
			raw_input("\nPress ENTER to exit\n")

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
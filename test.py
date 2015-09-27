from processSingleXml import processSingleXml
import specs
import sys
if __name__ == '__main__':
    for filename in sys.argv[1:]:
        processSingleXml(filename)
        specs_obj = specs.SPECS(filename)
        
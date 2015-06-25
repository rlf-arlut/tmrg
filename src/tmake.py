#!/usr/bin/env python
import logging
from optparse import *
import traceback
import pprint
import os
import glob
import logging
import filecmp
import copy
import ConfigParser
from verilogElaborator import *
from toolset import *
import os.path
import imp
import os
import datetime

def getModificationDate(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

# targets
# -see
# -pla

# -sim
# -syn
# -syn-sim
# -pnr
# -pnr-sim

# -tmr
# -tmr-sim
# -tmr-syn
# -tmr-pnr
# -tmr-syn-sim
# -tmr-pnr-sim
#
# options
# -gui
#
class TMAKE:
    def __init__(self,options, args):
        self.__init_rules()
        self.args=args
        self.options=options

    def __init_rules(self):
        #scan class looking for elaborator functions
        self.rules={}
        for member in dir(self):
            if member.find("target_")==0:
                token=member[len("target_"):].lower().replace("_","-")
                self.rules[token]=getattr(self,member)
                print token
                #self.logger.debug("Found elaborator for %s"%token)
        pass
    def sim(self,files):
        pass

    def target_sim(self):
        pass

    def target_tmr_sim(self):
        self.tmr()
        self.sim(files)

    def target_tmr_pnt_sim(self):
        self.tmr()
        self.tmr_pnr()
        self.sim()

    def run(self):
        if os.path.isfile("manifest"):
            self.manifest = imp.load_source('manifest', 'manifest')

        for target in self.manifest.targets:
            print target
            targetDict=self.manifest.targets[target]
            for fileName in targetDict["rtl_files"].split():
                fileNameFull=os.path.join(targetDict["rtl_dir"],fileName)
                print fileName,fileNameFull
                print getModificationDate(fileNameFull)
        possible_targets=[]
        for arg in self.args:
            for target in self.manifest.targets:
                for rule in self.rules:
                    targetRule=target+"-"+rule
                    if arg==targetRule:
                        print "!",targetRule
        return

########################################################################################################################

def version():
  verstr="$Id$"
  return verstr

def main():
    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(version="TMAKE %s"%tmrg_version(), usage="%prog [options] fileName", epilog=epilog)

    parser.add_option("-v",  "--verbose",          dest="verbose",      action="count",   default=0, help="More verbose output (use: -v, -vv, -vvv..)")
    parser.add_option("",  "--doc",               dest="doc",  action="store_true",   default=False, help="Open documentation in web browser")

    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)

    try:
        (options, args) = parser.parse_args()

        if options.verbose==0:
            logging.getLogger().setLevel(logging.WARNING)
        if options.verbose==1:
            logging.getLogger().setLevel(logging.INFO)
        elif options.verbose==2:
            logging.getLogger().setLevel(logging.DEBUG)

        tmake=TMAKE(options, args)

        if options.doc:
            startDocumentation()
            return

        tmake.run()

    except ErrorMessage as e:
        logging.error(str(e))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.info("The exception was raised from:")
        for l in traceback.format_tb(exc_traceback):
            for ll in l.split("\n"):
              logging.info(ll)
        logging.info(ll)



if __name__=="__main__":
    main()

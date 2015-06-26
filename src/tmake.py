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
from textwrap import TextWrapper

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
        self.logger = logging.getLogger('TMAKE')
        self.logger.info("Command line arguments : %s"%(str(args)))
        self.logger.info("Command line options : %s"%(str(options)))
        self.args=args
        self.options=options
        self.workingDir=os.getcwd()
        self.logger.info("Working directory : %s"%self.workingDir)
        self.workDir=os.path.join(self.workingDir,"work")
        self.logger.info("Work directory : %s"%self.workDir)

        self.__init_rules()


    def __init_rules(self):
        #scan class looking for elaborator functions
        self.rules={}
        for member in dir(self):
            if member.find("target_")==0:
                token=member[len("target_"):].lower().replace("_","-")
                self.rules[token]=getattr(self,member)
                self.logger.debug("Found rule for '%s'"%token)
        pass

    def sim(self,target):
        pass

    def tmr(self,target):
        pass

    def runCommand(self,cmd):
        self.logger.info("Executing")

        wrapper = TextWrapper(initial_indent="",)
        wrapper.subsequent_indent=" "*(len(cmd.split()[0])+1)
        wrapper.width=120
        for line in wrapper.wrap(cmd):
            self.logger.info(line)
        os.system(cmd)

    def ensureDirectory(self,target,rule):
        self.ruleDir=os.path.join(self.workDir,target,rule)
        if not os.path.exists(self.ruleDir) and not os.path.isdir(self.ruleDir):
            self.logger.info("Directory '%s' does not exists. Creating it."%self.ruleDir)
            os.makedirs(self.ruleDir)
        os.chdir(self.ruleDir)
        self.logger.info("Entering '%s'"%self.ruleDir)
    def target_sim(self, target):
        """Simulate RTL design"""
        self.logger.info("Executing sim for target %s"%target)
        self.ensureDirectory(target,"sim")

        rtlFiles=[]
        targetDict=self.manifest.targets[target]
        self.logger.info("RTL files : ")
        for fileName in targetDict["rtl_files"].split():
            fileNameFull=os.path.join(self.workingDir,targetDict["rtl_dir"],fileName)
            rtlFiles.append(fileNameFull)
            self.logger.info("  %s"%(fileNameFull))
        cmd="iverilog "+ " ".join(rtlFiles)
        self.runCommand(cmd)

    def target_tmr(self, target):
        """Triplicate RTL design"""
        self.logger.info("Executing tmr for target %s"%target)

    def target_tmr_pnr(self, target):
        """Place&Route triplicated netlist"""
        self.target_tmr(target)
        self.logger.info("Executing tmr-pnr for target %s"%target)

    def target_tmr_sim(self, target):
        """Simulate triplicated RTL design"""
        self.target_tmr(target)
        self.logger.info("Executing tmr-sim for target %s"%target)

    def target_tmr_pnr_sim(self, target):
        """Simulate triplicated post place&route RTL netlist"""
        self.target_tmr_pnr(target)
        self.logger.info("Executing tmr-pnr-sim for target %s"%target)

    def printDebug(self):
        self.logger.info("Targets : %s"%(" ".join(sorted(self.manifest.targets))))
        self.logger.info("Rules:")
        for rule in self.rules:
            ruleHelpStr = self.rules[rule].__doc__
            self.logger.info(" %-12s : %s"%(rule,ruleHelpStr))

    def getModificationDate(self,files):
        for fileName in files:
            fileNameFull=os.path.join(self.targetDict["rtl_dir"],fileName)
            print fileName,fileNameFull
            print getModificationDate(fileNameFull)


    def run(self):
        self.manifest=None
        for manifestFileName in ("manifest","Manifest","MANIFEST"):
            if os.path.isfile(manifestFileName):
                self.logger.info("Loading manifest from '%s'"%manifestFileName)
                self.manifest = imp.load_source('manifest', manifestFileName)
        if not self.manifest:
            self.logger.error("Manifest file does not exists.")
            return


        self.logger.info("Targets : %s"%(" ".join(sorted(self.manifest.targets))))

        possible_targets=[]

        if len(self.args)==0:
            self.logger.info("No targets specified. Printing debug.")
            self.printDebug()
            return

        for arg in self.args:
            found=False
            for target in self.manifest.targets:
                for rule in self.rules:
                    targetRule=target+"-"+rule
                    if arg==targetRule:
                        self.rules[rule](target)
                        found=True
            if not found:
                self.logger.error("Unknown target '%s'"%arg)
        return

########################################################################################################################

def version():
  verstr="$Id$"
  return verstr

def main():
    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(version="TMAKE %s"%tmrg_version(), usage="%prog [options] fileName", epilog=epilog)

    parser.add_option("-v","--verbose",          dest="verbose",      action="count",   default=0, help="More verbose output (use: -v, -vv, -vvv..)")
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

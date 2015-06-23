#!/usr/bin/env python
import logging
from optparse import *
#import tempita
#import pygraphviz as pgv
import traceback
import pprint
import os
import glob
import logging
from tmrg import VerilogFormater,readFile,resultLine,TMR
import random
import re
from verilogElaborator import *
from toolset import *

class TBG(VerilogElaborator):
    def __init__(self,options, args):
        VerilogElaborator.__init__(self,options, args,cnfgName="seeg")

    def generate(self):
        logging.debug("")
        oStr=""

        for module in self.modules:
            oStr+="module %s_test;\n"%module
            #initial declaration
            for ioName in self.modules[module]["io"]:
                io=self.modules[module]["io"][ioName]
                if io["type"]=="input":
                    oStr+="  reg %s %s;\n"%(io["range"], ioName)
                elif io["type"]=="output":
                    oStr+="  wire %s %s;\n"%(io["range"], ioName)
                else:
                    self.logger.warning("Unsuported IO type: %s"%io["type"])
            #dut instantiation
            oStr+="\n  %s DUT(\n"%module
            sep="    "
            #initial declaration
            for ioName in self.modules[module]["io"]:
                oStr+="%s.%s(%s)"%(sep,ioName, ioName)
                sep=",\n    "
            oStr+="\n  );\n"

            #initial
            oStr+="\n  initial\n"
            oStr+="    begin\n"
            for ioName in self.modules[module]["io"]:
                io=self.modules[module]["io"][ioName]
                if io["type"]=="input":
                    oStr+="      %s=0;\n"%(ioName)
            oStr+="    end\n"

            oStr+="endmodule\n"

        print oStr

        #generateFromTemplate(fname,tfile, values)


def main():
    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(version="TBG %s"%tmrg_version(), usage="%prog [options] fileName", epilog=epilog)
    parser.add_option("-v", "--verbose",       dest="verbose",   action="count",   default=0, help="More verbose output (use: -v, -vv, -vvv..)")
    parser.add_option("",   "--doc",           dest="doc",       action="store_true",   default=False, help="Open documentation in web browser")
    parser.add_option("-l", "--lib",           dest="libs",      action="append",   default=[], help="Library")

    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)

    try:
        (options, args) = parser.parse_args()

        if options.verbose==0:
            logging.getLogger().setLevel(logging.WARNING)
        if options.verbose==1:
            logging.getLogger().setLevel(logging.INFO)
        elif options.verbose==2:
            logging.getLogger().setLevel(logging.DEBUG)

        if options.doc:
            startDocumentation()
            return

        if len(args)!=1:
            raise OptParseError("You have to specify verilog file name. ")

        try:
            tbg=TBG(options, args)
            tbg.parse()
            tbg.elaborate()
            tbg.generate()
        except ParseException, err:
            logging.error("")
            logging.error(err.line)
            logging.error( " "*(err.column-1) + "^")
            logging.error( err)
            for l in traceback.format_exc().split("\n"):
                logging.error(l)

    except ErrorMessage as er:
        logging.error(er)
    except OptParseError as er:
        logging.error(er)

if __name__=="__main__":
    main()

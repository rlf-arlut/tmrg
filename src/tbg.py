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

class TBG(TMR):
    def __init__(self,options, args):
        TMR.__init__(self,options, args)

    def generate(self):
        logging.debug("")
        oStr=""

        for module in self.modules:
            oStr+="module %s_test;\n"%module

            oStr+="\n// - - - - - - - - - - - - - - Parameters section  - - - - - - - - - - - - - - \n"

            parameters=""
            psep="\n    "
            for k in self.modules[module]["params"]:
                oStr+="  parameter %s = %s;\n"%(k,self.modules[module]["params"][k]["value"])
                parameters+="%s.%s(%s)"%(psep,k,k)
                psep=",\n    "

            if len(parameters): parameters=" #("+parameters+")\n "

            oStr+="\n// - - - - - - - - - - - - - - Input/Output section  - - - - - - - - - - - - - \n"
            #initial declaration
            for ioName in self.modules[module]["io"]:
                io=self.modules[module]["io"][ioName]
                if io["type"]=="input":
                    oStr+="  reg %s %s;\n"%(io["range"], ioName)
                elif io["type"]=="output":
                    oStr+="  wire %s %s;\n"%(io["range"], ioName)
                else:
                    self.logger.warning("Unsuported IO type: %s"%io["type"])

            oStr+="\n// - - - - - - - - - - - - - Device Under Test section - - - - - - - - - - - -\n"
            oStr+="\n`ifdef TMR\n"
            #initial declaration
            for ioName in self.modules[module]["io"]:
                if self.modules[module]["nets"][ioName]["tmr"]:
                    io=self.modules[module]["io"][ioName]
                    if io["type"]=="input":
                        oStr+="  // fanout for %s\n"%(ioName)
                        for ext in self.EXT:
                            oStr+="  wire %s %s%s=%s;\n"%(io["range"], ioName,ext,ioName)
                    elif io["type"]=="output":
                        oStr+="  // voter for %s\n"%(ioName)
                        for ext in self.EXT:
                            oStr+="  wire %s %s%s;\n"%(io["range"], ioName,ext)
                        oStr+="  assign %s = (%sA & %sB) | (%sB & %sC) | (%sA & %sC);\n"%(ioName,ioName,ioName,ioName,ioName,ioName,ioName)
                    else:
                        self.logger.warning("Unsuported IO type: %s"%io["type"])


            #dut tmr instantiation
            oStr+="  %sTMR%s DUT (\n"%(module,parameters)
            sep="    "
            #initial declaration
            for ioName in self.modules[module]["io"]:
                if self.modules[module]["nets"][ioName]["tmr"]:
                    for ext in self.EXT:
                        oStr+="%s.%s%s(%s%s)"%(sep,ioName,ext, ioName,ext)
                        sep=",\n    "
            oStr+="\n  );\n"
            oStr+="`else\n"
            #dut instantiation
            oStr+="  %s%s DUT (\n"%(module,parameters)
            sep="    "
            #initial declaration
            for ioName in self.modules[module]["io"]:
                oStr+="%s.%s(%s)"%(sep,ioName, ioName)
                sep=",\n    "
            oStr+="\n  );\n"
            oStr+="`endif\n"


            oStr+="\n// - - - - - - - - - - - - Timing annotation section - - - - - - - - - - - - - \n"
            oStr+="""`ifdef SDF
  initial
    $sdf_annotate("r2g.sdf", DUT, ,"sdf.log", "MAXIMUM");
`endif
"""

            oStr+="\n// - - - - - - - - - - - - Single Event Effect section - - - - - - - - - - - -\n"
            oStr+="""`ifdef SEE
  `include "see.v"
`endif
"""



            #initial
            oStr+="\n// - - - - - - - - - - - - - Actual testbench section  - - - - - - - - - - - -\n"
            oStr+="  initial\n"
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
    parser.add_option("-c",  "--config",           dest="config",       action="append",   default=[], help="Load config file")
    parser.add_option("-w",  "--constrain",        dest="constrain",    action="append",   default=[], help="Load config file")

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

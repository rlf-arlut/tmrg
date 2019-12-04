#!/usr/bin/env python3

# Copyright (c) CERN and the TMRG authors.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import glob
import logging
import os
import pprint
import traceback
import random
import re

from optparse import *

from .verilog_elaborator import *
from .top import readFile
from .tmrg import TMR
from .toolset import tmrg_version, epilog


class TBG(TMR):
    def __init__(self, options, args):
        TMR.__init__(self, options, args)

    def loadVoterDefinition(self, voterName="majorityVoterTB"):
        vfile = os.path.join(self.scriptDir,  self.config.get("tmrg", "voter_definition"))
        self.logger.info("Taking voter declaration from %s" % vfile)
        return readFile(vfile).replace("majorityVoter", voterName)

    def generate(self):
        logging.debug("")
        oStr = ""
        for module in self.modules:
            clocks = []
            resets = []
            voterName = module+"Voter"
            oStr += "`ifdef TMR\n"+self.loadVoterDefinition(voterName=voterName)+"`endif\n\n"
            oStr += "module %sWrapper;\n" % module

            oStr += "\n// - - - - - - - - - - - - - - Parameters section  - - - - - - - - - - - - - - \n"

            parameters = ""
            psep = "\n    "
            for k in self.modules[module]["params"]:
                if self.modules[module]["params"][k]['type'] == 'localparam':
                    continue
                oStr += "  parameter %s = %s;\n" % (k, self.modules[module]["params"][k]["value"])
                parameters += "%s.%s(%s)" % (psep, k, k)
                psep = ",\n    "

            if len(parameters):
                parameters = "\n`ifndef NETLIST\n  #("+parameters+"\n  )\n`endif\n "

            oStr += "\n// - - - - - - - - - - - - - - Input/Output section  - - - - - - - - - - - - - \n"

            for ioName in sorted(self.modules[module]["io"]):
                io = self.modules[module]["io"][ioName]
                if io["type"] == "input":
                    oStr += "  input %s %s;\n" % (io["range"], ioName)
                elif io["type"] == "output":
                    oStr += "  output %s %s;\n" % (io["range"], ioName)
                else:
                    self.logger.warning("Unsuported IO type: %s" % io["type"])

            oStr += "\n// - - - - - - - - - - - - - Device Under Test section - - - - - - - - - - - -\n"
            oStr += "\n`ifdef TMR\n"

            for ioName in sorted(self.modules[module]["io"]):
                if self.modules[module]["nets"][ioName]["tmr"]:
                    io = self.modules[module]["io"][ioName]
                    if io["type"] == "input":
                        oStr += "  // fanout for %s\n" % (ioName)
                        for ext in self.EXT:
                            oStr += "  wire %s %s%s=%s;\n" % (io["range"], ioName, ext, ioName)
                    elif io["type"] == "output":
                        oStr += "  // voter for %s\n" % (ioName)
                        for ext in self.EXT:
                            oStr += "  wire %s %s%s;\n" % (io["range"], ioName, ext)
                        oStr += "  wire %stmrErr;\n" % (ioName)

                        _len = self.modules[module]["nets"][ioName]["len"]
                        width = ""
                        if _len != "1":
                            width += "#(.WIDTH(%s)) " % _len

                        oStr += "  %s %s%s (\n" % (voterName, width, ioName+"Voter")
                        oStr += "    .inA(%sA),\n" % (ioName)
                        oStr += "    .inB(%sB),\n" % (ioName)
                        oStr += "    .inC(%sC),\n" % (ioName)
                        oStr += "    .out(%s),\n" % (ioName)
                        oStr += "    .tmrErr(%stmrErr)\n" % (ioName)
                        oStr += "  );\n"

                    else:
                        self.logger.warning("Unsuported IO type: %s" % io["type"])

            # dut tmr instantiation
            oStr += "  %sTMR%s DUT (\n" % (module, parameters)
            sep = "    "
            for ioName in sorted(self.modules[module]["io"]):
                if self.modules[module]["nets"][ioName]["tmr"]:
                    for ext in self.EXT:
                        oStr += "%s.%s%s(%s%s)" % (sep, ioName, ext, ioName, ext)
                        sep = ",\n    "
                else:
                    oStr += "%s.%s(%s)" % (sep, ioName, ioName)
                    sep = ",\n    "
            oStr += "\n  );\n"
            oStr += "`else\n"

            # dut instantiation
            oStr += "  %s%s DUT (\n" % (module, parameters)
            sep = "    "

            for ioName in sorted(self.modules[module]["io"]):
                oStr += "%s.%s(%s)" % (sep, ioName, ioName)
                sep = ",\n    "
            oStr += "\n  );\n"
            oStr += "`endif\n"

            oStr += "\n// - - - - - - - - - - - - Timing annotation section - - - - - - - - - - - - - \n"
            oStr += """`ifdef NETLIST
  initial
`ifdef TMR
    $sdf_annotate("%sTMR.sdf", DUT, ,"sdf.log");
`else
    $sdf_annotate("%s.sdf", DUT, ,"sdf.log");
`endif
`endif
""" % (module, module)

            oStr += "\n// - - - - - - - - - - - - - - - VDD section - - - - - - - - - - - - - - - - - \n"
            oStr += """
`ifdef VCD
  initial begin
     $dumpfile("%s.vcd");
     $dumpvars(0, DUT);
  end
`endif
""" % (module)

            oStr += "endmodule\n"
        if self.options.outputFname != "":
            self.logger.info("Writing testbench to %s" % self.options.outputFname)
            f = open(self.options.outputFname, "w")
            f.write(oStr)
            f.close()
        else:
            print(oStr)


def main():
    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(version="WRG %s" % tmrg_version(), usage="%prog [options] fileName", epilog=epilog)
    parser.add_option("-v", "--verbose",       dest="verbose",   action="count",
                      default=0, help="More verbose output (use: -v, -vv, -vvv..)")
    parser.add_option("",   "--doc",           dest="doc",       action="store_true",
                      default=False, help="Open documentation in web browser")
    parser.add_option("-l", "--lib",           dest="libs",      action="append",   default=[], help="Library")
    parser.add_option("-c",  "--config",           dest="config",
                      action="append",   default=[], help="Load config file")
    parser.add_option("-w",  "--constrain",        dest="constrain",
                      action="append",   default=[], help="Load config file")
    parser.add_option("-o",  "--output-file",      dest="outputFname",    default="", help="Output file name")
    parser.add_option("",  "--generate-report",    dest="generateBugReport",
                      action="store_true",   default=False, help="Generate bug report")
    parser.add_option("", "--stats", dest="stats", action="store_true", help="Print statistics")
    parser.add_option("", "--include", dest="include", action="store_true", default="false",
                      help="Include include files")
    parser.add_option("",   "--inc-dir",           dest="inc_dir",
                      action="append", default=[], help="Include directories")
    parser.add_option("",   "--top-module",        dest="top_module",
                      action="store", default="",  help="Specify top module name")

    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)

    try:
        (options, args) = parser.parse_args()

        if options.verbose == 0:
            logging.getLogger().setLevel(logging.WARNING)
        if options.verbose == 1:
            logging.getLogger().setLevel(logging.INFO)
        elif options.verbose == 2:
            logging.getLogger().setLevel(logging.DEBUG)

        if options.doc:
            startDocumentation()
            return

        if len(args) != 1:
            raise OptParseError("You have to specify verilog file name. ")

        tbg = TBG(options, args)
        tbg.parse()
        tbg.elaborate(allowMissingModules=True)
        tbg.generate()
    except ErrorMessage as er:
        logging.error(er)
        os._exit(1)
    except OptParseError as er:
        logging.error(er)
        os._exit(2)


if __name__ == "__main__":
    main()

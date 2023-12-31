#!/usr/bin/env python2

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

from .tmrg import readFile, resultLine, TMR, makeSureDirExists
from .verilog_elaborator import *
from .toolset import *
import logging
import traceback
import pprint
import os
import glob
import logging
import random
import re
import getpass
import socket
import getpass
import socket
import time
import datetime
import hashlib
import zipfile
from optparse import *


class SEE(VerilogElaborator):
    def __init__(self, options, args):
        VerilogElaborator.__init__(self, options, args, cnfgName="seeg")

    def generate(self):
        logging.debug("")

        def outputSetNets(module, prefix=""):
            res = []
            # we want to affect net only on the bottom of the hierarhy
            if len(self.modules[module]["instances"]) == 0:
                for net in self.modules[module]["io"]:
                    _type = self.modules[module]["io"][net]["type"]
                    if _type == "output":
                        _len = self.modules[module]["io"][net]["len"]
                        _range = self.modules[module]["io"][net]["range"]
                        _ilen = int(_len)
                        if _ilen == 1:
                            res.append(prefix+net)
                        else:
                            # work around
                            nn = _range[1:-1].split(":")
                            i1 = int(nn[0])
                            i2 = int(nn[1])
                            mmin = min((i1, i2))
                            mmax = max((i1, i2))
                            for i in range(mmin, mmax+1):
                                res.append(prefix+net+"[%d]" % i)
            else:
                # in other case we loop over hierarchy
                for instId in self.modules[module]["instances"]:
                    inst = self.modules[module]["instances"][instId]['instance']
                    if ("[" in instId) or ("-" in instId):
                        instId = "\\"+instId+" "
                    if inst in self.modules:
                        res += outputSetNets(inst, prefix=prefix+instId+".")
            return res

        def outputSeuNets(module, prefix=""):
            res = []
            # we want to affect nets only on the bottom of the hierarhy
            if len(self.modules[module]["instances"]) == 0:
                if "seu_set" in self.modules[module]["constraints"]:
                    res.append(prefix+self.modules[module]["constraints"]["seu_set"])
                if "seu_reset" in self.modules[module]["constraints"]:
                    res.append(prefix+self.modules[module]["constraints"]["seu_reset"])
            else:
                # in other case we loop over hierarchy
                for instId in self.modules[module]["instances"]:
                    inst = self.modules[module]["instances"][instId]['instance']
                    if ("[" in instId) or ("-" in instId):
                        instId = "\\"+instId+" "
                    if inst in self.modules:
                        res += outputSeuNets(inst, prefix=prefix+instId+".")
            return res

        setNets = outputSetNets(self.topModule, "DUT.")
        if self.options.inputsSet or self.config.getboolean("seeg", "inputsSet"):
            for net in self.modules[self.topModule]["io"]:
                if self.modules[self.topModule]["io"][net]["type"] == "input":
                    setNets.append("DUT.%s" % net)
        logging.info("Found '%d' SET nets in the design" % len(setNets))

        seuNets = outputSeuNets(self.topModule, "DUT.")
        logging.info("Found '%d' SEU nets in the design" % len(seuNets))

        logging.info("")

        if self.options.exlude != "":
            logging.info("Loading excluded file from from '%s'" % self.options.exlude)
            if not os.path.isfile(self.options.exlude):
                logging.warning("File does not exists. Constrains will not be applied.")
            else:
                f = open(self.options.exlude, "r")
                toExlude = []
                for l in f.readlines():
                    if len(l.strip()) == 0:
                        continue
                    if l[0] == "#":
                        continue
                    toExlude.append(l.rstrip())
                f.close()
                logging.info("Found %d excluding rules" % len(toExlude))

                def exclude(nets, rules):
                    reducedNets = []
                    for net in sorted(nets):
                        matched = 0
                        for rule in rules:
                            result = re.match(rule, net)
                            if result:
                                logging.debug("Excluding net '%s' because of rule '%s'" % (net, rule))
                                matched = 1
                                break
                        if not matched:
                            reducedNets.append(net)
                    return reducedNets

                seuNets = exclude(seuNets, toExlude)
                setNets = exclude(setNets, toExlude)

        def verboseNets(desc, nets):
            logging.debug("%s%d" % (desc, len(nets)))
            l = "  "
            for n in nets:
                l += n+" "
                if len(l) > 100:
                    logging.debug(l)
                    l = "  "
            logging.debug(l)

        verboseNets("Nets to be affected by SET : ", setNets)
        verboseNets("Nets to be affected by SEU : ", seuNets)

        wireid = 0

        values = {}
        values['see_full_list'] = ""
        values['set_display_net'] = ""
        values['set_force_net'] = ""
        values['set_release_net'] = ""
        for wireid, net in enumerate(setNets):
            values['set_force_net'] += "    %4d : force %s = ~%s;\n" % (wireid, net, net)
            values['set_release_net'] += "    %4d : release %s;\n" % (wireid, net)
            values['set_display_net'] += '   %4d : $display("%s");\n' % (wireid, net)
            values['see_full_list'] += "// %4d : %s\n" % (wireid, net)

        values['set_max_net'] = "%d" % len(setNets)
        values['set_force_net'] = values['set_force_net'].rstrip()
        values['set_release_net'] = values['set_release_net'].rstrip()
        values['set_display_net'] = values['set_display_net'].rstrip()

        if len(values['set_force_net']) == 0:
            logging.warning("No SET wires!")
            values['set_force_net'] = "    // No SET wires found !\n"
            values['set_release_net'] = "    // No SET wires found !\n"
            values['set_display_net'] = "    // No SET wires found !\n"
        else:
            values['set_force_net'] = "    case (wireid)\n" + values['set_force_net'] + "\n    endcase\n"
            values['set_release_net'] = "    case (wireid)\n" + values['set_release_net'] + "\n    endcase\n"
            values['set_display_net'] = "    case (wireid)\n" + values['set_display_net'] + "\n    endcase\n"

        values['seu_display_net'] = ""
        values['seu_force_net'] = ""
        values['seu_release_net'] = ""
        for wireid, net in enumerate(seuNets):
            values['seu_force_net'] += "    %4d : force %s = ~%s;\n" % (wireid, net, net)
            values['seu_release_net'] += "    %4d : release %s;\n" % (wireid, net)
            values['seu_display_net'] += '   %4d : $display("%s");\n' % (wireid, net)
            values['see_full_list'] += "// %4d : %s\n" % (len(setNets)+wireid, net)

        values['seu_max_net'] = "%d" % len(seuNets)
        values['seu_force_net'] = values['seu_force_net'].rstrip()
        values['seu_release_net'] = values['seu_release_net'].rstrip()
        values['seu_display_net'] = values['seu_display_net'].rstrip()

        if len(values['seu_force_net']) == 0:
            logging.warning("No SEU wires!")
            values['seu_force_net'] = "    // No SEU wires found !\n"
            values['seu_release_net'] = "    // No SEU wires found !\n"
            values['seu_display_net'] = "    // No SEU wires found !\n"
        else:
            values['seu_force_net'] = "    case (wireid)\n" + values['seu_force_net'] + "\n    endcase\n"
            values['seu_release_net'] = "    case (wireid)\n" + values['seu_release_net'] + "\n    endcase\n"
            values['seu_display_net'] = "    case (wireid)\n" + values['seu_display_net'] + "\n    endcase\n"

        values['see_full_list'] += "\n"
        tfile = os.path.join(self.scriptDir,  self.config.get("seeg", "template"))
        logging.info("Taking template from '%s'" % tfile)

        fname = self.options.ofile
        logging.info("SEE file is stored to '%s'" % fname)

        generateFromTemplate(fname, tfile, values)


def main():
    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(version="SEEG %s" % tmrg_version(), usage="%prog [options] fileName", epilog=epilog)
    parser.add_option("-v", "--verbose",       dest="verbose",   action="count",
                      default=0, help="More verbose output (use: -v, -vv, -vvv..)")
    parser.add_option("",   "--doc",           dest="doc",       action="store_true",
                      default=False, help="Open documentation in web browser")
    parser.add_option("-l", "--lib",           dest="libs",      action="append",   default=[], help="Library")
    parser.add_option("",   "--spaces",        dest="spaces",    default=2, type=int)
    parser.add_option("-e", "--exclude",       dest="exlude",    default="", help="Exlude nets from output file")
    parser.add_option("-o", "--output-file",   dest="ofile",    default="see.v", help="Output file name")
    parser.add_option("",   "--inputs-set",    dest="inputsSet", action="store_true",
                      default=False, help="Generete SET also on inputs of the module")
    parser.add_option("",  "--generate-report",    dest="generateBugReport",
                      action="store_true",   default=False, help="Generate bug report")
    parser.add_option("",  "--include",            dest="include",    action="store_true",
                      default=False,   help="Include include files")
    parser.add_option("",   "--inc-dir",           dest="inc_dir",      action="append", default=[],
                      help="Directory where to look for include files (use option --include to actualy include the files during preprocessing)")
    parser.add_option("",  "--stats",              dest="stats",    action="store_true",   help="Print statistics")
    parser.add_option("",   "--top-module",        dest="top_module",
                      action="store", default="",  help="Specify top module name")

    logFormatter = logging.Formatter('[%(levelname)-7s] %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.WARNING)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    exit_code = 0
    try:
        (options, args) = parser.parse_args()

        if options.generateBugReport:
            bugReportDir = "bugReport_%s_%s" % (getpass.getuser(), time.strftime("%d%m%Y_%H%M%S"))
            options.bugReportDir = bugReportDir
            makeSureDirExists(bugReportDir)
            fileHandlerBug = logging.FileHandler(os.path.join(bugReportDir, "log.txt"))
            fileHandlerBug.setFormatter(logFormatter)
            fileHandlerBug.setLevel(logging.DEBUG)
            logging.getLogger().addHandler(fileHandlerBug)
            logging.info("Creating debug report in location '%s'" % bugReportDir)
            logging.debug("Creating log file '%s'" % options.log)

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
            raise OptParseError("You have to specify netlist file name. (like r2g.v)")

        if not options.ofile:
            raise OptParseError("You have to specify output file name.")

        seeg = SEE(options, args)
        seeg.parse()
        seeg.elaborate()
        seeg.generate()
    except ErrorMessage as er:
        logging.error(er)
        exit_code = 1
    except OptParseError as er:
        logging.error(er)
        exit_code = 2
    rootLogger.handlers = []
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

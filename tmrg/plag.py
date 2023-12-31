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
import time
import datetime
import hashlib
import zipfile
from optparse import *
from string import Template
from .verilog_elaborator import *
from .toolset import *
from .tmrg import TMR, makeSureDirExists


class PLA(VerilogElaborator):
    def __init__(self, options, args):
        VerilogElaborator.__init__(self, options, args, cnfgName="plag")
        # command line specified config files
        for fname in self.options.config:
            if os.path.exists(fname):
                logging.debug("Loading command line specified config file from %s" % fname)
                self.config.read(fname)
                if self.options.generateBugReport:
                    bn = os.path.basename(fname)
                    fcopy = os.path.join(self.options.bugReportDir, "cmd_%s.cfg" % bn)
                    logging.debug("Coping  command line specified config file from '%s' to '%s'" % (fname, fcopy))
                    shutil.copyfile(fname, fcopy)
            else:
                raise ErrorMessage("Command line specified config file does not exists at %s" % fname)

    def generate(self):
        logging.debug("")

        instances = self.getAllInsttances(self.topModule, self.topModule)
        logging.info("Found '%d' instances in the design" % len(instances))

        cells = self.config.get("plag", "cells")
        if self.options.cells != "":
            cells = self.options.cells
        logging.info("Cells : %s" % cells)
        cells = cells.split()

        filteredInstances = []
        for instId, cell in instances:
            if cell in cells:
                filteredInstances.append(instId)
        instances = filteredInstances
        logging.info("")

        if self.options.exlude != "":
            logging.info("Loading exlude file from from '%s'" % self.options.exlude)
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

                instances = exclude(instances, toExlude)

        def verboseIstance(desc, inst):
            logging.debug("%s%d" % (desc, len(inst)))
            l = "  "
            for n in inst:
                l += n+" "
                if len(l) > 100:
                    logging.debug(l)
                    l = "  "
            logging.debug(l)

        verboseIstance("Instances to be placed : ", instances)

        body = ""
        POST = ("A", "B", "C")

        def getGroup(s):
            for c in reversed(s):
                if c in POST:
                    return c
            return ""

        for ins in sorted(instances):
            group = getGroup(ins)
            body += "addInstToInstGroup tmrGroup%s {%s}\n" % (group, ins)

        fname = self.options.ofile
        logging.info("SEE file is stored to '%s'" % fname)
        f = open(fname, "w")
        f.write(body)
        f.close()


def main():
    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(version="PLAG %s" % tmrg_version(), usage="%prog [options] fileName", epilog=epilog)
    parser.add_option("-v", "--verbose",       dest="verbose",   action="count",
                      default=0, help="More verbose output (use: -v, -vv, -vvv..)")
    parser.add_option("",   "--doc",           dest="doc",       action="store_true",
                      default=False, help="Open documentation in web browser")
    parser.add_option("-c",  "--config",           dest="config",
                      action="append",   default=[], help="Load config file")
    parser.add_option("-l", "--lib",           dest="libs",      action="append",   default=[], help="Library")
    parser.add_option("",   "--spaces",        dest="spaces",    default=2, type=int)
    parser.add_option("-e", "--exclude",       dest="exlude",    default="", help="Exlude nets from output file")
    parser.add_option("-o", "--output-file",   dest="ofile",    default="tmrPlace.tcl", help="Output file name")
    parser.add_option("",   "--cells",         dest="cells",     default="", help="Cells to be placed")
    parser.add_option("",  "--generate-report",    dest="generateBugReport",
                      action="store_true",   default=False, help="Generate bug report")
    parser.add_option("",  "--stats",              dest="stats",    action="store_true",   help="Print statistics")
    parser.add_option("",  "--include",            dest="include",    action="store_true",
                      default="false",   help="Include include files")
    parser.add_option("", "--inc-dir", dest="inc_dir", action="append", default=[], help="Include directories")
    parser.add_option("", "--log",                 dest="log",
                      default="",             help="Store detailed log to file")
    parser.add_option("",   "--top-module",        dest="top_module",
                      action="store", default="",  help="Specify top module name")

    logFormatter = logging.Formatter('[%(levelname)-7s] %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
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

        plag = PLA(options, args)
        plag.parse()
        plag.elaborate()
        plag.generate()
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

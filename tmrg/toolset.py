#!/usr/bin/env python2

import webbrowser
from string import Template
import os
import subprocess

epilog = """
TMRG toolset:
  tmrg - Triple Modular Redundancy Generator
         (triplicates verilog netlist)
  seeg - Single Event Effects Generator
         (helps in the verification of triplicated netlist)
  plag - Placement Generator
         (helps with placement of triplicated circuit)
  tbg  - Testbench Generator
         (creates template for the testbench)
"""


def generateFromTemplate(outFname, templateFname, values):
    f = open(templateFname, "r")
    temp = f.read()
    f.close()

    f = open(outFname, "w")
    f.write(Template(temp).substitute(values))
    f.close()


def startDocumentation():
    scriptDir = os.path.abspath(os.path.dirname(__file__))
    docDir = os.path.join(scriptDir, '../doc/build/html')
    docInx = os.path.abspath(docDir+"/index.html")
    webbrowser.open_new(docInx)


def runCommand(cmd, cwd):
    try:
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        out, err = p.communicate()
    except OSError as err:
        self.logger.info("Error running command '%s'" % cmd)
        self.logger.info(str(err))
        out, err = "", str(err)

    return out, err


def tmrg_version():
    if tmrg_version.str == "":
        d = os.path.dirname(__file__)
        tmrg_version.str, errors = runCommand('git rev-parse HEAD', cwd=d)
        tmrg_version.str = tmrg_version.str.rstrip()
    return tmrg_version.str


tmrg_version.str = ""  # static variable


def version():
    verstr = "$Id$"
    return verstr


def makeSureDirExists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

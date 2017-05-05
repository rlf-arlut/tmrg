#!/usr/bin/env python

import webbrowser
from string import Template
import os
import subprocess

epilog="""
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


def generateFromTemplate(outFname,templateFname, values):
  f=open(templateFname,"r")
  temp=f.read()
  f.close()

  f=open(outFname,"w")
  f.write(Template(temp).substitute(values))
  f.close()

def startDocumentation():
    scriptDir = os.path.abspath(os.path.dirname(__file__))
    docDir = os.path.join(scriptDir,'../doc/build/html')
    docInx = os.path.abspath( docDir+"/index.html")
    webbrowser.open_new(docInx)

def tmrg_version():
    if tmrg_version.str=="":
        d=os.path.dirname(__file__)
        tmrg_version.str=subprocess.check_output(['git', 'rev-parse', 'HEAD'],cwd=d).rstrip()
    return tmrg_version.str
tmrg_version.str="" # static variable

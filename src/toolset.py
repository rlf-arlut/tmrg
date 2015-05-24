#!/usr/bin/env python

import webbrowser
from string import Template

epilog="""
TMRG toolset:
  tmrg - Triple Modular Redundancy Generator
         (triplicates verilog netlist)
  seeg - Single Event Effects Generator
         (helps in the verification of triplicated netlist)
  plag - Placement Generator
         (helps with placement of triplicated circuit)
"""


def generateFromTemplate(outFname,templateFname, values):
  f=open(templateFname,"r")
  temp=f.read()
  f.close()

  f=open(outFname,"w")
  f.write(Template(temp).substitute(values))
  f.close()

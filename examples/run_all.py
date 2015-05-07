#!/usr/bin/env python
import glob
import os
import sys

os.system("rm -rf *TMR.v")
for fn in glob.glob("comb0*.v"):
  cmd="tmrg.py --tmr-dir=. -t %s"%fn
  print cmd
  os.system(cmd)

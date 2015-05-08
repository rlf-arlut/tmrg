#!/usr/bin/env python
import glob
import os
import sys

os.system("rm -rf *TMR.v *.new")
for prefix in ("comb","vote","fsm","mod"):
  for fn in glob.glob("%s0*.v"%prefix):
    cmd="tmrg.py --tmr-dir=. -t %s"%fn
    print cmd
    os.system(cmd)

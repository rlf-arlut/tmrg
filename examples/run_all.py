#!/usr/bin/env python
import glob
import os
import sys
import tempfile
import logging

def main():
    logging.getLogger().setLevel(INFO)
    cwd=os.getcwd()
    logging.info("Current working directory %s" % cwd)
    logging.getLogger()
    tmpDir=tempfile.mkdtemp()
    logging.info("Creating temporary directory %s"%tmpDir)
    os.chdir(tmpDir)
    print tmpDir
#os.system("rm -rf *TMR.v *.new")
#for prefix in ("comb","vote","fsm","mod"):
#  for fn in glob.glob("%s0*.v"%prefix):
#    print "#"*80
#    cmd="tmrg.py --tmr-dir=. -t %s "%fn
#    print "#",cmd
#    print "#"*80
#    os.system(cmd)

if __name__ == "__main__":
  main()


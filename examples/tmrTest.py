#!/usr/bin/env python
import glob
import os
import sys
from synthesizeModule import *



def tmrExperiment(fname):
    fbase,fext=os.path.splitext(os.path.basename(fname))
    fnameTMR=fbase+"TMR"+fext
    os.system("rm -rf %s"%fnameTMR)
    logging.info("Triplicating file %s"%fname)    
    cmd="tmrg.py --tmr-dir=. -t %s "%fname
    logging.info("  %s"%cmd)    
    os.system(cmd)

#    synthesizeModule(fname)
    print loadGateReport(fname) 

#    synthesizeModule(fnameTMR)
    print loadGateReport(fnameTMR)     
    
def main():
    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args)!=1:
       parser.error("You have to specify file name")
    tmrExperiment(args[0])


if __name__=="__main__":
  main()

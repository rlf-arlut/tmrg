#!/usr/bin/env python
import glob
import os
import sys
import logging
from optparse import OptionParser
from prettytable import *
from string import Template

def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)


def generateFromTemplate(outFname,templateFname, values):
  f=open(templateFname,"r")
  temp=f.read()
  f.close()

  f=open(outFname,"w")
  f.write(Template(temp).substitute(values))
  f.close()
    
def synthesizeModule(fname,gui=False):
    rtlFiles=fname
    fbase,fext=os.path.splitext(os.path.basename(fname))
    fdir=os.path.dirname(fname)
    workDir=os.path.join(fdir,fbase+"_rc")
    logging.info("Creating %s directory"%workDir)
    _mkdir(workDir)

    sdcFile=os.path.join(workDir,"constraint.sdc")
    rcFile=os.path.join(workDir,"rc.tcl")

    logging.info("Creating RC script %s"%rcFile)
    rcValues={"workDir":workDir,"rtlFiles":rtlFiles,"sdcFile":sdcFile,"exit":"exit"}
    if gui:
      rcValues["exit"]=""
    generateFromTemplate(rcFile,os.path.join(fdir,"rc/rc.tpl"),rcValues)

    logging.info("Creating SDC script %s"%sdcFile)
    sdcValues={"dont_touch":""}
    generateFromTemplate(sdcFile,os.path.join(fdir,"rc/constraint.tpl"),sdcValues)

    logging.info("Run RC")
    cmd="rc -files %s > %s/log.txt"%(rcFile,workDir)
    os.system(cmd)

def loadGateReport(fname):
    ret={}
    fbase,fext=os.path.splitext(os.path.basename(fname))
    fdir=os.path.dirname(fname)
    workDir=os.path.join(fdir,fbase+"_rc")
    gateFile=os.path.join(workDir,"syn2gen.gate")
    logging.info("Loading report from %s"%gateFile)
    if not os.path.isfile(gateFile):
      logging.warning("File does not exists")
      return ret
    
    f=open(gateFile,"r")
    part=0
    for l in f.readlines():
      if l.find("--")==0: 
        part+=1
        continue
      if part==1:
        ll=l.split()
        gate = ll[0]
        instances = int(ll [1])
        area = float(ll[2])
        ret[gate]={"instances":instances,"area":area}
    f.close()
    return ret



def tmrExperiment(fname):
    fbase,fext=os.path.splitext(os.path.basename(fname))
    fdir=os.path.dirname(fname)
    fnameTMR=os.path.join(fdir,fbase+"TMR"+fext)
    os.system("rm -rf %s"%fnameTMR)
    logging.info("Triplicating file %s"%fname)    
    cmd="tmrg.py --tmr-dir=examples -t %s "%fname
    logging.info("  %s"%cmd)    
    os.system(cmd)

    synthesizeModule(fname)
    module=loadGateReport(fname) 

    synthesizeModule(fnameTMR)
    moduleTMR=loadGateReport(fnameTMR)     
    tab = PrettyTable(["cell", "instances", "area", "instancesTMR", "areaTMR"],horizontal_char='-',hrules=ALL)
    tab.min_width["cell"]=20;
    tab.min_width["instances"]=20;
    tab.min_width["area"]=20;
    tab.min_width["instancesTMR"]=20;
    tab.min_width["areaTMR"]=20;
    tab.align["cell"] = "l" # Left align city names
            #print "%-12s:"%dname
    area=0.0
    areaTMR=0.0
    instances=0
    instancesTMR=0
    mkeys=module.keys()
    mTMRkeys=moduleTMR.keys()
    for cellName in sorted(list(set(mkeys + mTMRkeys))):
       i = 0
       a = 0.0
       iTMR = 0
       aTMR = 0.0
       if cellName in module:
         i=module[cellName]["instances"]
         a=module[cellName]["area"]
       if cellName in moduleTMR:
         iTMR=moduleTMR[cellName]["instances"]
         aTMR=moduleTMR[cellName]["area"]       
       tab.add_row([cellName,i,a,iTMR,aTMR])
       area+=a
       areaTMR+=aTMR
       instances+=i
       instancesTMR+=iTMR
    tab.add_row(["total",instances,area,instancesTMR,areaTMR])
#            tab.padding_width = 1 # One space between column edges and contents (default)
    lines=str(tab).replace("#","=").split("\n")
    lines[0]=lines[-1]

    frst=os.path.join(fdir,fbase+".rst")
    
    logging.info("Writing results file %s"%frst)    
    f=open(frst,"w")
    f.write("\n".join(lines))
    f.write("\n TMR area gain %.1f %%"%(100.0*areaTMR/area))
    f.close()
def main():
    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args)!=1:
       parser.error("You have to specify file name")
    tmrExperiment(args[0])


if __name__=="__main__":
  main()

#!/usr/bin/env python
import glob
import os
import sys
import shutil
filePath =os.path.dirname(__file__)
srcPath = os.path.abspath(os.path.join(filePath,"../src"))
sys.path.append(srcPath)

import logging
from optparse import OptionParser
from prettytable import *
from string import Template

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

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

def readFile(fname):
  f=open(fname,"r")
  temp=f.read()
  f.close()
  return temp

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
    for f in glob.glob('%s/*'%workDir):
      os.remove(f)

    fsdc=os.path.join(fdir,fbase+".sdc")
    userSDC=""
    if os.path.isfile(fsdc):
      logging.info("Loading SDC file from %s"%fsdc)
      userSDC=readFile(fsdc)
    
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
    sdcValues={"dont_touch":userSDC}
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
    logging.info("")
    logging.info("Triplicating file %s"%fname)    
    cmd="tmrg.py --tmr-dir=examples %s "%fname
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
    f.write("\n\n TMR area gain %.1f %%\n\n"%(100.0*areaTMR/area))
    f.close()

def loadLogFile(fname):
    f=open(fname)
    r= f.readlines()
    f.close()
    return r

def logFile(fname,i=""):
    f=open(fname)
    cnt=0
    for l in f.readlines():
        logging.error(i+l.rstrip())
        cnt+=1
    f.close()
    return cnt


def tmrExperimentIverilog(fname):
    fbase,fext=os.path.splitext(os.path.basename(fname))
    fdir=os.path.dirname(fname)
    fnameTMR=os.path.join(fdir,fbase+"TMR"+fext)
    os.system("rm -rf %s"%fnameTMR)
    logging.info("")
    logging.info("#"*100)
    logging.info("# Triplicating file %s"%fname)
    logging.info("#"*100)

    flog=os.path.join(fdir,fbase+".ilog")
    cmd="iverilog %s 2> %s "%(fname,flog)
    logging.info("  %s "%(cmd))
    os.system(cmd)
    er1=logFile(flog)

    tlog=os.path.join(fdir,fbase+".tlog")
    cmd="tmrg.py --tmr-dir=examples %s 2> %s"%(fname,tlog)
    logging.info("  %s"%cmd)
    os.system(cmd)
    er2=logFile(tlog)

    flogTMR=os.path.join(fdir,fbase+"TMR.ilog")
    cmd="iverilog %s 2> %s "%(fnameTMR,flogTMR)
    logging.info("  %s "%(cmd))
    os.system(cmd)
    er3=logFile(flogTMR)

    return er1,er2,er3

def runIverilog(iverilog,fin):
    if iverilog!=None:
        fbase,ext=os.path.splitext(fin)
        flog=fbase+".ilog"
        logging.debug("[iverilog %s]"%fin)
        logging.debug("    fin :%s"%fin)
        logging.debug("    flog:%s"%flog)
        cmd="%s %s 2> %s "%(iverilog,fin,flog)
        logging.debug("    cmd :%s "%(cmd))
        os.system(cmd)
        errors=loadLogFile(flog)
        os.system(cmd)
        if len(errors)==0:
            logging.info("iverilog %s : OK"%fin)
            return True
        else:
            logging.error("iverilog %s : ERROR"%fin)
            for e in errors:
              logging.error("    %s"%e.rstrip())
    return False

def runTmr(tmrg,fin,opts):
    if tmrg!=None:
        fbase,ext=os.path.splitext(fin)
        flog=fbase+".tlog"
        logging.debug("[tmrg %s]"%fin)
        logging.debug("    fin :%s"%fin)
        logging.debug("    flog:%s"%flog)
        cmd="%s %s %s 2> %s "%(tmrg,opts,fin,flog)
        logging.debug("    cmd :%s "%(cmd))
        os.system(cmd)
        errors=loadLogFile(flog)
        os.system(cmd)
        if len(errors)==0:
            logging.info("tmrg %s : OK"%fin)
            return True
        else:
            logging.error("tmrg %s : ERROR"%fin)
            for e in errors:
              logging.error("    %s"%e.rstrip())
            return False
    return True

def logErrors(errors,i):
    for e in errors:
        logging.error("%s%s"%(i,e))

def main():
    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)
    parser = OptionParser()
    parser.add_option("-v",  "--verbose",          dest="verbose",      action="count",   default=0, help="More verbose output (use: -v, -vv, -vvv..)")
    parser.add_option("-a", "--all", action="store_true", dest="all")
    parser.add_option("-i", "--iverilog", action="store_true", dest="iverilog")
    (options, args) = parser.parse_args()

    if options.verbose==0:
        logging.getLogger().setLevel(logging.INFO)
    elif options.verbose==1:
        logging.getLogger().setLevel(logging.DEBUG)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    tmrg=which("tmrg")
    if tmrg ==None:
        logging.error("No 'tmrg' on a PATH.")
        return
    logging.debug("tmrg : %s"%tmrg)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    iverilog=which("iverilog")
    if iverilog ==None:
        logging.warning("No 'iverilog' on a PATH.")
    else:
        logging.debug("iverilog : %s"%iverilog)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    rc=which("rc")
    if rc ==None:
        logging.warning("No 'rc' on a PATH.")
    else:
        logging.debug("rc : %s"%rc)


    if options.all:
        args=[]
        for fn in sorted(glob.glob("*.v")):
            args.append(fn)
    else:
        if len(args)!=1:
            parser.error("You have to specify at least one file name")

    #try:
    sourceIverilogFails=[]
    tmrgFails=[]
    tmrIverilogFails=[]
    filesCount=0
    if 1:

        for fname in args:
            filesCount+=1
            rtlFiles=fname
            logging.info("")
            logging.info("#"*100)
            logging.info("# File : %s"%fname)
            logging.info("#"*100)
            fbase,fext=os.path.splitext(os.path.basename(fname))
            fdir=os.path.dirname(fname)
            workDir=os.path.join(fdir,"work",fbase)
            logging.info("Dir  : %s"%workDir)
            _mkdir(workDir)
            for f in glob.glob('%s/*'%workDir):
                os.remove(f)
            noTmrFile=os.path.join(workDir,fname)
            shutil.copyfile(fname,noTmrFile)
            good=runIverilog(iverilog,noTmrFile)
            if not good:
                sourceIverilogFails.append(fname)
                continue
            good=runTmr(tmrg,noTmrFile,opts="--tmr-dir %s"%workDir)
            if not good:
                tmrgFails.append(fname)
                continue
            tmrFile=os.path.join(workDir,fbase+"TMR"+fext)
            good=runIverilog(iverilog,tmrFile)
            if not good:
                tmrIverilogFails.append(fname)
                continue


        logging.info("")
        logging.info("#"*100)
        logging.info("# Summary")
        logging.info("#"*100)

        logging.info("examples executed   : %d"%filesCount)
        logging.info("iverilog errors     : %d"%len(sourceIverilogFails))
        logErrors(sourceIverilogFails,i="                      ")
        logging.info("tmrg errors         : %d"%len(tmrgFails))
        logErrors(tmrgFails,i="                      ")
        logging.info("iverilog TMR errors : %d"%len(tmrIverilogFails))
        logErrors(tmrIverilogFails,i="                      ")
#        else:
#            for fn in sorted(glob.glob("examples/*.v")):
#                if fn.find("TMR")>=0 : continue
#                tmrExperiment(fn)

#    except:
#        print "ER"
#        pass


if __name__=="__main__":
  main()

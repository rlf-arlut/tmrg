#!/usr/bin/env python
import glob
import os
import sys
import tempfile
import logging
import commands
from difflib import *

from distutils.spawn import find_executable


def main():
    FORMAT = '[%(levelname)-8s] %(message)s'
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(logging.INFO)
    cwd=os.getcwd()
    logging.info("Current working directory %s" % cwd)
    srcFiles=[]
    tmrFiles=[]
    errCode=0
    for fname in glob.glob("*.v"):
        ffname=os.path.join(cwd,fname)
        if fname.find("TMR")<0:
            srcFiles.append(ffname)
        else:
            tmrFiles.append(ffname)
    tmpDir=tempfile.mkdtemp()
    logging.info("Creating temporary directory %s"%tmpDir)
    os.chdir(tmpDir)
    tests=0
    tmrg=find_executable("tmrg")[:-4]+"../src/tmrg.py"
    cmd = "python-coverage erase"
    err, outLog = commands.getstatusoutput(cmd)
#    if 1 :
    for f in srcFiles:

        logging.info("Checking '%s'"%f)
        cmd = "iverilog %s"%f
        err,outLog = commands.getstatusoutput(cmd)
        if err:
            errCode+=1
            logging.info("  | Error code %d"%err)
            for l in outLog.split("\n"):
                logging.info("  | %s"%l)

        logging.info("Triplicating '%s'" % f)
        cmd = "python-coverage run -a --include '*verilog*,*src/tmrg*' %s --no-header %s" % (tmrg,f)
        err, outLog = commands.getstatusoutput(cmd)
        if err or len(outLog)>0:
            errCode += 1
            logging.info("  | Error code %d" % err)
            for l in outLog.split("\n"):
                logging.info("  | %s" % l)

        core = os.path.basename(f)
        coreTMR = core.replace(".v", "TMR.v")
        outTmr = os.path.join(tmpDir, coreTMR)
        absTMR = os.path.join(cwd, coreTMR)

        logging.info("Checking '%s'"%outTmr)
        cmd = "iverilog %s"%outTmr
        err,outLog = commands.getstatusoutput(cmd)
        if err:
            errCode+=1
            logging.info("  | Error code %d"%err)
            for l in outLog.split("\n"):
                logging.info("  | %s"%l)


        if absTMR in tmrFiles:
            logging.info("File '%s' exists. Checking ..."%absTMR)
            diffs=0
            for line in unified_diff(open(absTMR).read(), open(outTmr).read()):
                logging.info("  | %s"%line.rstrip())
                diffs+=1
            if diffs:
                logging.info("  | Diffs found")
                logging.info("  | ")
                logging.info("  | Reference '%s' "%absTMR)
                for i,l in enumerate(open(absTMR).readlines()):
                    logging.info("  | [%d] %s"%(i,l.rstrip()))
                logging.info("  | ")
                logging.info("  | Output '%s'"%outTmr)
                for i,l in enumerate(open(outTmr).readlines()):
                    logging.info("  | [%d] %s"%(i,l.rstrip()))
                logging.info("  | ")
                errCode+=1
        tests+=1

    otherTests=[("--include --inc-dir %s/../ %s/../include.v"%(cwd,cwd),0),
                ("--help",1),
                (" %s/../libtest.v  --lib=%s/../lib.v"%(cwd,cwd),0)]

    for test,verbose in otherTests:
        logging.info("Runnging '%s'" % test)
        cmd = "python-coverage run -a --include '*verilog*,*src/tmrg*' %s %s" % (tmrg,test)
#        print cmd
        err, outLog = commands.getstatusoutput(cmd)
#        print outLog
        if err or (not verbose and len(outLog)>0):
            errCode += 1
            logging.info("  | Error code %d" % err)
            for l in outLog.split("\n"):
                logging.info("  | %s" % l)
    logging.info("Files checked : %d"%tests)
    if errCode:
        logging.error("Erorrs %d "%errCode)
    cmd = "python-coverage report -m "
    err,outLog = commands.getstatusoutput(cmd)
    logging.info("")
    logging.info("Coverage")
    for l in outLog.split("\n"):
        logging.info("  | %s"%l)
    if 0:
      for cov in outLog.split('\n')[2:-2]:
        print cov
        cov=cov.replace(",","")
        covs=cov.split()
        fname=covs[0]+".py"
        lines=[]
        for lino in covs[4:]:
          if lino.find("-")>0:
            _from=int(lino[:lino.find('-')])
            _to=int(lino[lino.find('-')+1:])
#            print lino,_from,_to
            for i in range(_from,_to+1):
               lines.append(i)
          else:
            lines.append(int(lino))
#          print fname,lino,lines
        f=open(fname)
        for lno,l in enumerate(f.readlines()):
          lineno=lno+1
          if lineno in lines:
            logging.info("%-30s %4d : ! %s"%(fname,lno,l.rstrip()))
          if  (not lineno in lines ) and ((lineno+1 in lines) or (lineno-1 in lines)):
            logging.info("%-30s %4d :   %s"%(fname,lno,l.rstrip()))
    os._exit(errCode)

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


#!/usr/bin/env python
import glob
import os
import sys
import tempfile
import logging
import commands
from difflib import *
from distutils.spawn import find_executable

simpleTests=[
"verilog/alwaysComma.v",
"verilog/case01.v",
"verilog/function.v",
"verilog/index.v",
"verilog/lib.v",
"verilog/params3.v",
"verilog/test03.v",
"verilog/translate.v",
"verilog/always.v",
"verilog/case02.v",
"verilog/davide_bug2.v",
"verilog/generate.v",
"verilog/initial01.v",
"verilog/logic.v",
"verilog/params4.v",
"verilog/testsRadu.v",
"verilog/var.v",
"verilog/ansiPorts.v",
"verilog/comb00.v",
"verilog/defines.v",
"verilog/hier01.v",
"verilog/inlineif01.v",
"verilog/mux.v",
"verilog/params.v",
"verilog/tmr1.v",
"verilog/wire.v",
"verilog/arrays.v",
"verilog/comb02.v",
"verilog/for.v",
"verilog/hier02.v",
"verilog/instantiation.v",
"verilog/netdeclaration.v",
"verilog/portDeclaration.v",
"verilog/tmr2.v",
"verilog/assigment.v",
"verilog/compDirectives.v",
"verilog/fsm01.v",
"verilog/hier03.v",
"verilog/instTmrError.v",
"verilog/notxor.v",
"verilog/slice01.v",
"verilog/tmr3.v",
"verilog/begin.v",
"verilog/complexInst.v",
"verilog/function2.v",
"verilog/params2.v",
"verilog/test02.v",
"verilog/tmrError01.v",
"../examples/clockGating01.v",
"../examples/comb02.v",
"../examples/comb05.v",
"../examples/dff.v",
"../examples/fsm03.v",
"../examples/inst02.v",
"../examples/resetBlock02.v",
"../examples/tmrOut01.v",
"../examples/clockGating02.v",
"../examples/comb03.v",
"../examples/comb06.v",
"../examples/fsm01.v",
"../examples/fsm04.v",
"../examples/inst03.v",
"../examples/resetBlock03.v",
"../examples/vote01.v",
"../examples/comb01.v",
"../examples/comb04.v",
"../examples/comb07.v",
"../examples/fsm02.v",
"../examples/inst01.v",
"../examples/resetBlock01.v",
"../examples/resetBlock04.v",
"../examples/vote02.v"
]
# "verilog/customVoterCell.v",

#"verilog/include.v",

#"verilog/libtest.v",

def runSimpleTests():
    cwd=os.getcwd()
    logging.info("Current working directory %s" % cwd)
    srcFiles=[]
    tmrFiles=[]
    errors=0
    for fname in simpleTests:
        ffname=os.path.join(cwd,fname)
        srcFiles.append(ffname)
    tmpDir=tempfile.mkdtemp()
    logging.info("Creating temporary directory %s"%tmpDir)
    os.chdir(tmpDir)
    tests=0
    tmrg=find_executable("tmrg")[:-4]+"../src/tmrg.py"
#    if 1 :
    for i,f in enumerate(srcFiles):
        logging.info("[%02d/%02d] Simple test for '%s'"%(i+1,len(srcFiles),f))
        logging.info("        iverilog for the source ('%s')"%f)
        cmd = "iverilog %s"%f
        err,outLog = commands.getstatusoutput(cmd)
        if err:
            errors+=1
            logging.info("  | Error code %d"%err)
            for l in outLog.split("\n"):
                logging.info("  | %s"%l)

        logging.info("        Triplicating '%s'" % f)
        cmd = "python-coverage run -a --include '*verilog*,*src/tmrg*' %s --no-header %s" % (tmrg,f)
        err, outLog = commands.getstatusoutput(cmd)
        if err or len(outLog)>0:
            errors += 1
            logging.info("  | Error code %d" % err)
            for l in outLog.split("\n"):
                logging.info("  | %s" % l)

        core = os.path.basename(f)
        coreTMR = core.replace(".v", "TMR.v")
        outTmr = os.path.join(tmpDir, coreTMR)
        absTMR = os.path.join(cwd, coreTMR)

        logging.info("        iverilog of triplicated file ('%s')"%outTmr)
        cmd = "iverilog %s"%outTmr
        err,outLog = commands.getstatusoutput(cmd)
        if err:
            errors+=1
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
                errors+=1
        tests+=1
    return errors
def coverageClean():
    logging.info("Cleanning coverate reports")
    cmd = "python-coverage erase"
    err, outLog = commands.getstatusoutput(cmd)

def coverageSummary():
    cmd = "python-coverage report -m "
    err,outLog = commands.getstatusoutput(cmd)
    logging.info("")
    logging.info("Coverage")
    for l in outLog.split("\n"):
        logging.info("  | %s"%l)
    if 0:
      for i in range(10):
        logging.info("")
      logging.info("Not tested code:")
      for cov in outLog.split('\n')[2:-2]:
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



def main():
    FORMAT = '[%(levelname)-8s] %(message)s'
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(logging.INFO)
    errors=0
    coverageClean()
    errors+=runSimpleTests()   
    coverageSummary()
    os._exit(errors)

def others():
    otherTests=[("--include --inc-dir %s/../ %s/../include.v"%(cwd,cwd),0),
                ("--help",1),
                (" %s/../libtest.v  --lib=%s/../lib.v"%(cwd,cwd),0),
                (" %s/comb04.v --constrain 'default do_not_triplicate comb04'"%(cwd),0),
                (" %s/comb04.v --constrain 'triplicate comb04.out'"%(cwd),0),
                (" %s/comb04.v --constrain 'do_not_touch comb04'"%(cwd),0),
                #(" %s/comb04.v --constrain 'dupa  comb04.out'"%(cwd),0),
                #(" %s/../comb04.v --constrain 'tmr_error true comb04'"%(cwd,cwd),0),
                ]

    for test,verbose in otherTests:
        logging.info("Runnging '%s'" % test)
        cmd = "python-coverage run -a --include '*verilog*,*src/tmrg*' %s %s" % (tmrg,test)
#        print cmd
        err, outLog = commands.getstatusoutput(cmd)
#        print outLog
        if err or (not verbose and len(outLog)>0):
            errors += 1
            logging.info("  | Error code %d" % err)
            for l in outLog.split("\n"):
                logging.info("  | %s" % l)
    logging.info("Files checked : %d"%tests)
    if errors:
        logging.error("Erorrs %d "%errors)
    cmd = "python-coverage report -m "
    err,outLog = commands.getstatusoutput(cmd)
    logging.info("")
    logging.info("Coverage")
    for l in outLog.split("\n"):
        logging.info("  | %s"%l)
    if 0:
      for i in range(10):
        logging.info("")
      logging.info("Not tested code:")
      for cov in outLog.split('\n')[2:-2]:
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
    os._exit(errors)

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

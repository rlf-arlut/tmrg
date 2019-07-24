#!/usr/bin/env python3
import glob
import os
import sys
import tempfile
import logging
import subprocess
import shlex
from difflib import *
from distutils.spawn import find_executable

FORMAT = '[%(levelname)-8s] %(message)s'
logging.basicConfig(format=FORMAT)
logging.getLogger().setLevel(logging.INFO)
top=os.getcwd()
tmpDir=os.path.join(top,"tmp")
logging.info("Creating temporary directory %s"%tmpDir)
if not os.path.exists(tmpDir):
    os.makedirs(tmpDir)

def getstatusoutput(cmd):
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    return int(p.returncode), stdout.decode('utf8')

simpleTests=(
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
  "verilog/generate01.v",
  "verilog/assigment03.v",
  "verilog/generate04.v",
  "verilog/initial01.v",
  "verilog/logic.v",
  "verilog/params4.v",
  "verilog/params5.v",
  "verilog/testsRadu.v",
  "verilog/var.v",
  "verilog/instanceInOut.v",
  "verilog/ansiPorts.v",
  "verilog/comb00.v",
  "verilog/defines.v",
  "verilog/hier01.v",
  "verilog/sysCall.v",
  "verilog/inlineif01.v",
  "verilog/mux.v",
  "verilog/params.v",
  "verilog/tmr1.v",
  "verilog/wire.v",
  "verilog/arrays.v",
  "verilog/comb02.v",
  "verilog/forLoop.v",
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
  "verilog/noports.v",
  "../examples/slice.v",
  "verilog/tmr3.v",
  "verilog/ifdef.v",
  "verilog/begin.v",
  "verilog/complexInst.v",
  "verilog/function2.v",
  "verilog/params2.v",
  "verilog/test02.v",
  "verilog/tmrError01.v",
  "verilog/tmrError04.v",
  "verilog/tmrError05.v",
  "../examples/clockGating01.v",
  "../examples/comb02.v",
  "../examples/comb05.v",
  "../examples/dff.v",
  "../examples/fsm03.v",
  "../examples/inst02.v",
  "../examples/resetBlock02.v",
  "../examples/tmrOut01.v",
  "../examples/clockGating02.v",
  "../examples/clockGating02.v",
  "../examples/configcell.v",
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
  "../examples/vote02.v",
  "../examples/pipelineWithSeuCoutner.v",
  "verilog/tmrErrorExclude.v",
  "verilog/vectorRange.v",
  "verilog/generate05.v",
  "verilog/wor01.v",
  "verilog/wor02.v",
  "reg_initial_value1.v",
  "reg_initial_value2.v",
  "reg_initial_value3.v",
)


configurationTests=(
   {"name":"First test",
    "verilog":""" module comb( input [7:0]  in, output [7:0] out );
                 assign out=~in;
                 endmodule
              """,
    "configurations":(
        {"file":"[comb]\ndefault : triplicate",
         "comment":"// tmrg default triplicate",
         "cmdline":'-w "default triplicate"'},

        {"file":"[comb]\ndefault : do_not_triplicate",
         "comment":"// tmrg default do_not_triplicate",
         "cmdline":'-w "default do_not_triplicate comb"'},

        {"file":"[comb]\ndefault : do_not_triplicate\nin:triplicate",
         "comment":"// tmrg default do_not_triplicate\n //tmrg triplicate in",
         "cmdline":'-w "default do_not_triplicate comb" -w "triplicate comb.in" '},

        {"file":"[comb]\ndefault : triplicate\nin:do_not_triplicate",
         "comment":"// tmrg default triplicate\n //tmrg do_not_triplicate in",
         "cmdline":'-w "default triplicate comb" -w "do_not_triplicate comb.in" '},

        {"file":"[comb]\ndo_not_touch : true",
         "comment":"// tmrg do_not_touch",
         "cmdline":'-w "do_not_touch comb" '},
    )
  },
)



def check():
  return ""

otherTests=(
  ("tmrg","--help",1,None),
  ("plag","--help",1,None),
  ("seeg","--help",1,None),
  ("tbg", "--help",1,None),

  ("tmrg","-h",1,None),
  ("plag","-h",1,None),
  ("seeg","-h",1,None),
  ("tbg", "-h",1,None),

  ("tmrg","--version",1,None),
  ("plag","--version",1,None),
  ("seeg","--version",1,None),
  ("tbg", "--version",1,None),

  ("tmrg"," --include --inc-dir %s/verilog/ %s/verilog/include.v"%(top,top),0, check),
  ("tmrg","%s/verilog/libtest.v  --lib=%s/verilog/lib.v"%(top,top),0,None),
  ("tmrg","--stats %s/verilog/fsm01.v"%(top),1,None),
  ("tmrg","%s/verilog/leftSideConcatenation.v"%(top),1,None), # should print error message
  ("tmrg","--log fsm01.log -vv %s/verilog/fsm01.v"%(top),1,None), #TODO check if file exists
  ("tmrg","--generate-report %s/verilog/fsm01.v"%(top),1,None), #TODO check if file exists
  ("tmrg","%s/verilog/hier/m1.v %s/verilog/hier/m2.v %s/verilog/hier/m3.v %s/verilog/hier/m4.v %s/verilog/hier/m5.v %s/verilog/hier/top.v "%(top,top,top,top,top,top),0,None), #TODO check it works after tmr

  ("seeg","%s/netlist/accTMR.v -l %s/libs/tcbn65lp.v --exclude %s/cnf/exclude.txt"%(top,top,top),0,None),
  ("plag","%s/netlist/accTMR.v -l %s/libs/tcbn65lp.v --exclude %s/cnf/exclude.txt --cells=\"DFCNQD1\""%(top,top,top),0,None), 
  ("plag","%s/netlist/accTMR.v -l %s/libs/tcbn65lp.v -c %s/cnf/plag.cfg "%(top,top,top),0,None), 
  ("tbg","%s/../examples/fsm01.v -o fsm01_test.v "%(top),0,None), 

  ("tmrg","%s/verilog/topModule.v"%top,1,None),

)

mustFailTests=(
#  ("tmrg","",1,None),
  ("seeg","",1,None),
  ("plag","",1,None),
  ("tbg", "",1,None),

  ("tmrg","nofile.v",1,None),
  ("seeg","nofile.v",1,None),
  ("plag","nofile.v",1,None),
  ("tbg", "nofile.v",1,None),

  ("tmrg","--no-such-option",1,None),
  ("seeg","--no-such-option",1,None),
  ("plag","--no-such-option",1,None),
  ("tbg", "--no-such-option",1,None),

  ("tmrg", "verilog/verilogError.v" ,1,None),
  ("seeg", "verilog/verilogError.v" ,1,None),
  ("plag", "verilog/verilogError.v" ,1,None),
  ("tbg",  "verilog/verilogError.v" ,1,None),

  ("tmrg","%s/verilog/hier/top.v "%(top),1,None),
  ("plag","%s/netlist/accTMR.v -l %s/libs/tcbn65lp.v -c do_not_exists "%(top,top),1,None),

 )


runCov = "python-coverage run -a --include '*verilog*,*tmrg*,*seeg*,*plag*' "

def runSimpleTests():
    srcFiles=[]
    tmrFiles=[]
    errors=0
    for fname in simpleTests:
        ffname=os.path.join(top,fname)
        srcFiles.append(ffname)
    #tmpDir=tempfile.mkdtemp()
    tests=0
    tmrg=find_executable("tmrg")#[:-4]+"../src/tmrg.py"
    for i,f in enumerate(srcFiles):
        logging.info("[%02d/%02d] Simple test for '%s'"%(i+1,len(srcFiles),f))
        logging.info("        iverilog for the source ('%s')"%f)
        cmd = "iverilog %s"%f
        err,outLog = getstatusoutput(cmd)
        if err:
            errors+=1
            logging.info("  | Error code %d"%err)
            for l in outLog.split("\n"):
                logging.info("  | %s"%l)

        logging.info("        Triplicating '%s'" % f)
        cmd = "%s %s --no-header %s" % (runCov, tmrg,f)
        err, outLog = getstatusoutput(cmd)
        if err or len(outLog)>0:
            errors += 1
            logging.info("  | Error code %d" % err)
            for l in outLog.split("\n"):
                logging.info("  | %s" % l)

        core = os.path.basename(f)
        coreTMR = core.replace(".v", "TMR.v")
        outTmr = os.path.join(tmpDir, coreTMR)
        absTMR = os.path.join(top, coreTMR)

        logging.info("        iverilog of triplicated file ('%s')"%outTmr)
        cmd = "iverilog %s"%outTmr
        err,outLog = getstatusoutput(cmd)
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
    logging.info("Errors : %d" % errors)

    return errors
def coverageClean():
    logging.info("Cleanning coverate reports")
    cmd = "python-coverage erase"
    cmd = "echo x"
    err, outLog = getstatusoutput(cmd)

def coverageSummary():
    cmd = "python-coverage report -m "
    err,outLog = getstatusoutput(cmd)
    logging.info("")
    logging.info("Coverage")
    for l in outLog.split("\n"):
        logging.info("  | %s"%l)
    f=open("covreport.txt","w")
    logging.info("Storing coverage report to 'covreport.txt'")
    linesHist={}
    if 1:
      f.write("Not tested code:\n")
      for cov in outLog.split('\n')[2:-2]:
        cov=cov.replace(",","")
        covs=cov.split()
        fname=covs[0]+".py"
        lines=[]
        for lino in covs[4:]:
          lineRange=1
          if lino.find("-")>0:
            _from=int(lino[:lino.find('-')])
            _to=int(lino[lino.find('-')+1:])
            lineRange=_to - _from + 1
            for i in range(_from,_to+1):
               lines.append(i)
          else:
            lines.append(int(lino))
          if not lineRange in linesHist: linesHist[lineRange]=0
          linesHist[lineRange]+=1
        if os.path.isfile(fname):
          fin=open(fname)
          for lno,l in enumerate(fin.readlines()):
            lineno=lno+1
            if lineno in lines:
              f.write("%-30s %4d : ! %s\n"%(fname,lno,l.rstrip()))
            if  (not lineno in lines ) and ((lineno+1 in lines) or (lineno-1 in lines)):
              f.write("%-30s %4d :   %s\n"%(fname,lno,l.rstrip()))
          fin.close()
    f.write("\n\nHistogram:\n")
    for k in sorted(linesHist):
        f.write("%d %d\n"%(k,linesHist[k]))
    f.close()

def runConfigurationTests():
    errors=0

    tmrgexec=find_executable("tmrg")#[:-4]+"../src/tmrg.py "
    tmrg = "%s %s --no-header  " % (runCov, tmrgexec)

    logging.info("Creating temporary directory %s"%tmpDir)
    for i,test in enumerate(configurationTests):
        logging.info("[%d/%d] Test '%s'"%(i+1, len(configurationTests),test["name"]))
        srcVerilog=configurationTests[i]["verilog"]
        for j,conf in enumerate(configurationTests[i]["configurations"]):
            logging.info("    [%d/%d] "%(j+1, len(configurationTests[i]["configurations"])))
            coreName="m%03d_%03d"%(i,j)

            fnameSrcFile="%s_file.v"%coreName
            fnameCnfFile="%s_file.cnf"%coreName
            logging.info("         File verilog : '%s' "%(fnameSrcFile))
            fSrcFile=open(fnameSrcFile,"w")
            fSrcFile.write(srcVerilog+"\n")
            fSrcFile.close()
            fCnf=open(fnameCnfFile,"w")
            fCnf.write(configurationTests[i]["configurations"][j]["file"]+"\n")
            fCnf.close()
            logging.info("         File config : '%s' "%(fnameCnfFile))
            cmd="%s %s --config=%s"%(tmrg,fnameSrcFile,fnameCnfFile)
            logging.info("         cmd : '%s' "%(cmd))
            err,outLog = getstatusoutput(cmd)
            if err:
                errors+=1
                logging.error("  | Error code %d"%err)
                for l in outLog.split("\n"):
                    logging.error("  | %s"%l)
            logging.info("")



            fnameComment="%s_comment.v"%coreName
            logging.info("         Verilog with comments: '%s' "%(fnameComment))
            fCommentSrc=open(fnameComment,"w")
            ssrc=srcVerilog.split("\n")
            fCommentSrc.write(ssrc[0]+"\n")
            fCommentSrc.write(configurationTests[i]["configurations"][j]["comment"]+"\n")
            fCommentSrc.write("\n".join(ssrc[1:]))
            fCommentSrc.close()
            cmd="%s %s "%(tmrg,fnameComment)
            logging.info("         cmd : '%s' "%(cmd))
            err,outLog = getstatusoutput(cmd)
            if err:
                errors+=1
                logging.error("  | Error code %d"%err)
                for l in outLog.split("\n"):
                    logging.error("  | %s"%l)
            logging.info("")


            fnameCmdline="%s_cmdline.v"%coreName
            logging.info("         Cmd line verilog : '%s' "%(fnameCmdline))
            fCmdFile=open(fnameCmdline,"w")
            fCmdFile.write(srcVerilog)
            fCmdFile.close()
            cmd="%s %s %s"%(tmrg,fnameCmdline,configurationTests[i]["configurations"][j]["cmdline"])
            logging.info("         cmd : '%s' "%(cmd))
            err,outLog = getstatusoutput(cmd)
            if err:
                errors+=1
                logging.info("  | Error code %d"%err)
                for l in outLog.split("\n"):
                    logging.info("  | %s"%l)
            logging.info("")



            fnameSrcFileTMR="%s_fileTMR.v"%coreName
            fnameCommentTMR="%s_commentTMR.v"%coreName
            fnameCmdlineTMR="%s_cmdlineTMR.v"%coreName

            def cmpFiles(fromfile,tofile):
                diffs=0
                for line in unified_diff(open(fromfile).read().split("\n"), open(tofile).read().split("\n"),
                                         fromfile=fromfile, tofile=tofile):
                    logging.info("  | %s"%line.rstrip())
                    diffs+=1
                if diffs:return 1
                return 0

            logging.info("         Comparing cnf file and comments ")
            errors+=cmpFiles(fnameSrcFileTMR,fnameCommentTMR)

            logging.info("         Comparing cnf file and cmd line ")
            errors+=cmpFiles(fnameSrcFileTMR,fnameCmdlineTMR)

            logging.info("         Comparing comments and cmd line ")
            errors+=cmpFiles(fnameCommentTMR,fnameCmdlineTMR)
    logging.info("Errors : %d" % errors)
    return errors



def runOthers(tests,mustFail=False):

    errors=0
    for appName,testArgs,verbose,checker in tests:
        logging.info("Runnging '%s %s'" % (appName,testArgs))
        appExec=find_executable(appName)#[:-4]+"/../src/%s.py "%appName
        cmd = "%s %s %s" % (runCov, appExec,testArgs)
        err, outLog = getstatusoutput(cmd)
        if mustFail:
          if err==0:
            logging.error("  | Test returned %d while it supose to fail!   " % err)
            errors += 1
          if (verbose and len(outLog)==0):
            logging.error("  | Test should be verbose but printed nothing!" )
            errors += 1
          if (not verbose and len(outLog)>0):
            logging.error("  | Test should be quite but printed:" )
            for l in outLog.split("\n"):
              logging.error("  |   %s" % l)
            errors += 1
        else:
          if err or (not verbose and len(outLog)>0) or (verbose and len(outLog)==0):
            errors += 1
            logging.error("  | Error code %d" % err)
            for l in outLog.split("\n"):
                logging.error("  | %s" % l)

        if checker!=None:
          err=checker()
          if err!="":
            errors += 1
            logging.error("  | Checker error: %s" % err)
    logging.info("Errors : %d" % errors)

    return errors

def main():
    errors=0
    logging.info("Current working directory %s" % top)
    os.chdir(tmpDir)
    coverageClean()
    logging.info("~"*80)
    errors+=runSimpleTests()
    logging.info("~"*80)
    errors+=runConfigurationTests()
    logging.info("~"*80)
    errors+=runOthers(otherTests)
    logging.info("~"*80)
    errors+=runOthers(mustFailTests,mustFail=True)
    logging.info("~"*80)
    logging.info("")
    logging.info("")
    if errors:
        logging.error("#"*80)
        logging.error("# Total Erorrs %d "%errors)
        logging.error("#"*80)
    else:
        logging.info("~"*80)
        logging.info("~ Total Erorrs %d "%errors)
        logging.info("~"*80)
    logging.info("")
    logging.info("")
    coverageSummary()
    os._exit(errors)

if __name__ == "__main__":
  main()

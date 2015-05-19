#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
import logging
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
    
def main():
#  try:
    gui=False
    
    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args)!=1:
      parser.error("You have to specify file name")
#  except:
  
    rtlFiles=args[0]
    fbase,fext=os.path.splitext(os.path.basename(args[0]))
    workDir=fbase+"_rc"
    logging.info("Creating %s directory"%workDir)
    _mkdir(workDir)

    sdcFile=os.path.join(workDir,"constraint.sdc")
    rcFile=os.path.join(workDir,"rc.tcl")

    logging.info("Creating RC script %s"%rcFile)
    rcValues={"workDir":workDir,"rtlFiles":rtlFiles,"sdcFile":sdcFile,"exit":"exit"}
    if gui:
      rcValues["exit"]=""
    generateFromTemplate(rcFile,"rc/rc.tpl",rcValues)

    logging.info("Creating SDC script %s"%sdcFile)
    sdcValues={"dont_touch":""}
    generateFromTemplate(sdcFile,"rc/constraint.tpl",sdcValues)

    logging.info("Run RC")
    cmd="rc -files %s"%rcFile
    os.system(cmd)
    

    
if __name__=="__main__":
  main()
    
  

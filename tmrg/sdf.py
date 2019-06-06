#!/usr/bin/env python2
import logging
from optparse import *
#import tempita
#import pygraphviz as pgv
#from vp import *
import traceback
import pprint
import os
import glob
import logging
#from tmrg import VerilogFormater,args2files,readFile,resultLine
import random
import re

class SEU(VerilogParser):
    def __init__(self):
        VerilogParser.__init__(self)
        self.seulogger = logging.getLogger('TMR')

def findTopModule(design):
    for module in design:
        for inst in design[module]["instances"]:
            inst_id=inst['identifier']
            if inst_id in design:
                design[inst_id]["instantiated"]+=1

    for module in design:
        if design[module]["instantiated"]==0:
            return module

def loadSlave(fname,modName):
  f=open(fname)
  ret=[]
  cells=0
  for l in f.readlines()[:-1]:
    if l.find("TIMESCALE")>=0:
      cells=1
      continue
    if cells:
      if l.find("(INSTANCE)")>=0:
        l="(INSTANCE "+modName+")"

      elif l.find("INSTANCE")>=0:
        p=l.find("INSTANCE")+len("INSTANCE")
        l1=l[:p+1].rstrip()

        l2=l[p+1:].lstrip()
        l=l1+" "+modName+"/"+l2
      ret.append(l)
  f.close()
  return ret
  
def main():
    parser = OptionParser(version="%prog 1.0", usage="%prog [options] fileName")
#    parser.add_option("", "--input-file",         dest="inputFile",   help="Input file name (*.v)", metavar="FILE")
#    parser.add_option("", "--output-file",        dest="outputFile",  help="Output file name (*.v)", metavar="FILE")
#    parser.add_option("-r", "--recursive",       action="store_true", dest="rec", default=True, help="Recurive.")
    parser.add_option("-p", "--parse",             action="store_true", dest="parse", default=True, help="Parse")
    parser.add_option("-f", "--format",            action="store_true", dest="format", default=False, help="Parse")
    parser.add_option("-i", "--info",              action="store_true", dest="info",  default=False, help="Info")
    parser.add_option("-q", "--trace",             action="store_true", dest="trace",  default=False, help="Trace formating")
    parser.add_option("",   "--spaces",            dest="spaces",       default=2, type=int )
    parser.add_option("",   "--rtl-dir",           dest="rtldir",       default="./rtl")
    parser.add_option("-v", "--verbose",           action="store_true", dest="verbose",  default=False, help="More verbose output")

    parser.add_option("-m", "--master-sdf",   dest="mainFname",    help="Master SDF file", metavar="FILE")
    parser.add_option("-o", "--output-sdf",   dest="outFname",     help="Output SDF file", metavar="FILE")
    parser.add_option("-n", "--module-sdf",   dest="modName",  action="append",    help="Output SDF file", metavar="FILE")
      
    #FORMAT = '%(message)s'
    logging.basicConfig(format='[%(name)s|%(levelname)s] %(message)s', level=logging.INFO)

    try:
        (options, args) = parser.parse_args()

        if not options.mainFname:
          raise OptionValueError("You have to specify master SDF file")
        if not options.outFname:
          raise OptionValueError("You have to specify ouput SDF file")
        if not options.modName:
          raise OptionValueError("You have to specify module name")
      

        if options.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        if len(args)==0:
            args=[options.rtldir]
        
        toReplace={}
        for sdfmod in options.modName:
          ss=sdfmod.split()
          if len(ss)!=2:
            raise OptionValueError("Wrong option %s (should be module name and file name)"%sdfmod)
          
          toReplace[ss[0]]=ss[1]
        modules={}
        for fname in args2files(args):
            try:
                logging.info("Processing file %s"%fname)
                vp=SEU()
                if options.parse or options.tmr or options.format:
                    tokens=vp.parseString(readFile(fname))

                #vp.applyDntConstrains(options.dnt)

                if options.info:
                    vp.printInfo()

                if options.format:
                    vf=VerilogFormater()
                    vf.setTrace(options.trace)
                    print vf.format(tokens).replace("\t"," "*options.spaces)
                modules[vp.module_name]=vp
            except ParseException, err:
                logging.error("")
                logging.error(err.line)
                logging.error( " "*(err.column-1) + "^")
                logging.error( err)
                for l in traceback.format_exc().split("\n"):
                    logging.error(l)

        if len(DESIGN)>=1:
            logging.info("Modules found %d"%len(DESIGN))
        else:
            return

        topModule=findTopModule(DESIGN)
        logging.info("Top module %s"%topModule)
        nets=[]
        
        def modules(module,prefix=""):
            res=[]
            for inst in DESIGN[module]["instances"]:
                instName=inst['instance']
                if "[" in  instName: instName="\\"+instName+" "
                instId=inst['identifier']
                res.append( (instId,prefix+instName) )
                if instId in DESIGN:

                    res+=modules(instId,prefix=prefix+instName+"/")
            return res
        mods=modules(topModule,"")
        logging.info("Module instantiations %d"%(len(mods)))        
        

        fo=open(options.outFname,"w")
        #copy master SDF
        fm=open(options.mainFname)
        for l in fm.readlines()[:-1]:
          fo.write(l)
        fm.close()

        
        for ins in mods:
          if ins[0] in toReplace:
            logging.info("Loading SDF file %s for %s"%(toReplace[ins[0]],ins[1]))

            slaveLines=loadSlave(toReplace[ins[0]],ins[1])
            fo.write("".join(slaveLines))  
        fo.write(")\n")              
        fo.close()        
        logging.info("Output file saved to %s",options.outFname)
    except ValueError:
        raise
    except OptionValueError as er:
        print er
#        G.write('simple.dot')
#        G.layout() # layout with default (neato)
#        G.draw('simple.png')

if __name__=="__main__":
    main()

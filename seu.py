#!/usr/bin/env python
import logging
from optparse import *
#import tempita
#import pygraphviz as pgv
from vp import *
import traceback
import pprint
import os
import glob
import logging
from tmrg import VerilogFormater,args2files,readFile,resultLine
import random

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

    #self.current_module["instantiated"]=0
def main():
    parser = OptionParser(version="%prog 1.0", usage="%prog [options] fileName")
#    parser.add_option("", "--input-file",         dest="inputFile",   help="Input file name (*.v)", metavar="FILE")
#    parser.add_option("", "--output-file",        dest="outputFile",  help="Output file name (*.v)", metavar="FILE")
#    parser.add_option("-r", "--recursive",       action="store_true", dest="rec", default=True, help="Recurive.")
    parser.add_option("-p", "--parse",             action="store_true", dest="parse", default=True, help="Parse")
    parser.add_option("-f", "--format",            action="store_true", dest="format", default=False, help="Parse")
    parser.add_option("-i", "--info",              action="store_true", dest="info",  default=False, help="Info")
    parser.add_option("-q", "--trace",             action="store_true", dest="trace",  default=False, help="Trace formating")
    parser.add_option("","--spaces",               dest="spaces",       default=2, type=int )
    parser.add_option("","--rtl-dir",              dest="rtldir",       default="./rtl")
    parser.add_option("-v",  "--verbose",          action="store_true", dest="verbose",  default=False, help="More verbose output")

    #FORMAT = '%(message)s'
    logging.basicConfig(format='[%(name)s|%(levelname)s] %(message)s', level=logging.INFO)

    try:
        (options, args) = parser.parse_args()


        if options.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        if len(args)==0:
            args=[options.rtldir]

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
        def outputNets(module,prefix=""):
            res=[]
            for net in DESIGN[module]["nets"]:
                res.append(prefix+net)
            for inst in DESIGN[module]["instances"]:
                instName=inst['instance']
                if "[" in  instName: instName="\\"+instName+" "
                instId=inst['identifier']
                if instId in DESIGN:
                    res+=outputNets(instId,prefix=prefix+instName+".")
            return res
        nets=outputNets(topModule,"DUT.")
        logging.info("Found %d nest in the design"%len(nets))

        # elif options.s2t:
        #     tmrtokens=vp.single2tmr()
        #     vf=VerilogFormater()
        #     vf.setTrace(options.trace)
        #     print vf.format(tmrtokens).replace("\t"," "*options.spaces)

        ofile=open("seu.v","w")

        for loop in range(1):
          added=[]
          while len(added)!=len(nets):
            port=""
            while port=="":
              port=random.choice(nets)
              if port in added:
                port=""
            added.append(port)
            s="""  // PORT
  SEUduration = ($random & 'hffff)*MAX_UPSET_TIME/65536;
  force PORT = ~PORT; // force procedural statement
  seu=1;
  #(SEUduration) release PORT;    // release procedural statement
  seu=0;
  nextSEUtime = ($random & 'hffff)*MAX_UPSET_TIME/65536;
  #(SEUDEL+nextSEUtime);"""
            s=s.replace("PORT",port)
            ofile.write(s+"\n")

          print
        ofile.close()
        for port in sorted(nets):
            print port

        #for port in ports:
        #    s="""always @(DUT.PORT)
        #  $fwrite(f,"PORT %d %d\\n",$time,DUT.PORT);"""
        #    s=s.replace("PORT",port)
        #    print s


    except ValueError:
        raise
#        G.write('simple.dot')
#        G.layout() # layout with default (neato)
#        G.draw('simple.png')

if __name__=="__main__":
    main()

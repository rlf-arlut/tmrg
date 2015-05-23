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
from tmrg import VerilogFormater,readFile,resultLine
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

    #self.current_module["instantiated"]=0
def main():
    parser = OptionParser(version="%prog 1.0", usage="%prog [options] fileName")
    parser.add_option("-v",  "--verbose",          dest="verbose",      action="count",   default=0, help="More verbose output (use: -v, -vv, -vvv..)")
#    parser.add_option("", "--input-file",         dest="inputFile",   help="Input file name (*.v)", metavar="FILE")
#    parser.add_option("", "--output-file",        dest="outputFile",  help="Output file name (*.v)", metavar="FILE")
#    parser.add_option("-r", "--recursive",       action="store_true", dest="rec", default=True, help="Recurive.")
    parser.add_option("-p", "--parse",             action="store_true", dest="parse", default=True, help="Parse")
    parser.add_option("-f", "--format",            action="store_true", dest="format", default=False, help="Parse")
    parser.add_option("-i", "--info",              action="store_true", dest="info",  default=False, help="Info")
    parser.add_option("-q", "--trace",             action="store_true", dest="trace",  default=False, help="Trace formating")
    parser.add_option("","--spaces",               dest="spaces",       default=2, type=int )
    parser.add_option("","--rtl-dir",              dest="rtldir",       default="./rtl")
    parser.add_option("-e",   "--exclude",         dest="exlude",       default="", help="Exlude nets from output file")
    parser.add_option("","--sequences",                dest="sequences",       default=1, type=int )
    #FORMAT = '%(message)s'

    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)

    try:
        (options, args) = parser.parse_args()

        if options.verbose==0:
            logging.getLogger().setLevel(logging.WARNING)
        if options.verbose==1:
            logging.getLogger().setLevel(logging.INFO)
        elif options.verbose==2:
            logging.getLogger().setLevel(logging.DEBUG)


        if len(args)!=1:
            raise OptParseError("You have to specify netlist file name. (like r2g.v)")

        fname=args[0]

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
                atr=DESIGN[module]["nets"][net]["atributes"]
                if "[" in  net: net="\\"+net+" "

                if atr!="": 
  #                print net,atr
                  #work around
                  nn=atr.split()
                  i1= int(nn[1])
                  i2= int(nn[3])
                  mmin = min ( (i1,i2) )
                  mmax = max ( (i1,i2) )
                  for i in range(mmin,mmax+1):
                    res.append(prefix+net+"[%d]"%i)
                else:                    
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
        if options.exlude!="":
            logging.info("Exluding nets from '%s'"%options.exlude)
            f=open(options.exlude,"r")
            toExlude=[]
            for l in f.readlines():
                if len(l.strip())==0: continue
                if l[0]=="#":continue
                toExlude.append(l.rstrip())
            f.close()
            logging.info("Found %d exluding rules"%len(toExlude))
            reducedNets=[]
            for port in sorted(nets):
                matched=0
                for pattern in toExlude:
                    result = re.match(pattern,port)
                    if result:
                        logging.info("Exluding net '%s' because of rule '%s'"%(port,pattern))
                        matched=1
                        break
                if not matched:
                    reducedNets.append(port)
             
            nets=reducedNets

        logging.debug("Nets to be affected by SEU:")
        l="  "
        for n in nets:
            l+=n+" "
            if len(l)>100:
                logging.debug(l)
                l="  "
        logging.debug(l)
       
        ofile=open("seuOld.v","w")
        seuCnt=1
        force="""task seu_force_net;
  input wireid;
  integer wireid;
  begin
  case (wireid)
"""

        release="""task seu_release_net;
  input wireid;
  integer wireid;
  begin
  case (wireid)
"""
 
        display="""task seu_display_net;
  input wireid;
  integer wireid;
  begin
  case (wireid)
"""
       
        for loop in range(options.sequences):
          added=[]
          while len(added)!=len(nets):
            port=""
            while port=="":
              port=random.choice(nets)
              if port in added:
                port=""
            added.append(port)
            
            s="""  // SEQ PORT
  nextSEUtime = ($random & 'hffff)*SEUDEL/65536;
  #(SEUDEL/2+nextSEUtime);
  SEUduration = ($random & 'hffff)*MAX_UPSET_TIME/65536;
  force PORT = ~PORT; // force procedural statement
  seu=1;
  #(SEUduration) release PORT;    // release procedural statement
  seu=0;
"""
            s=s.replace("PORT",port)
            s=s.replace("SEQ","%d"%seuCnt)
            ofile.write(s+"\n")

            s="""   SEQ : force PORT = ~PORT; """
            s=s.replace("PORT",port)
            s=s.replace("SEQ","%4d"%seuCnt)
            force+=s+"\n"

            s="""   SEQ : release PORT; """
            s=s.replace("PORT",port)
            s=s.replace("SEQ","%4d"%seuCnt)
            release+=s+"\n"

            s="""   SEQ : $display("PORT"); """
            s=s.replace("PORT",port)
            s=s.replace("SEQ","%4d"%seuCnt)
            display+=s+"\n"


            seuCnt+=1
          #print
        ofile.close()

        force+="""  endcase
end
endtask"""    

        release+="""  endcase
end
endtask""" 

        display+="""  endcase
end
endtask"""   

        seu_max=""" task seu_max_net;
  output wireid;
  integer wireid;
  begin
    wireid=SEQ;
  end
endtask
"""
        seu_max=seu_max.replace("SEQ","%4d"%seuCnt)
        
        ofile=open("seu.v","w")
        ofile.write(force+"\n"*3+release+"\n"*3+display+"\n"*3+seu_max)
        ofile.close()

        logging.info("SEU generated : %d"%seuCnt)
        #for port in ports:
        #    s="""always @(DUT.PORT)
        #  $fwrite(f,"PORT %d %d\\n",$time,DUT.PORT);"""
        #    s=s.replace("PORT",port)
        #    print s


    except OptParseError as er:
        logging.error(er)
#        G.write('simple.dot')
#        G.layout() # layout with default (neato)
#        G.draw('simple.png')

if __name__=="__main__":
    main()

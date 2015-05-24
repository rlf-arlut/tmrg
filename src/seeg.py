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
from tmrg import VerilogFormater,readFile,resultLine,TMR
import random
import re
from verilogElaborator import *
from string import Template

def generateFromTemplate(outFname,templateFname, values):
  f=open(templateFname,"r")
  temp=f.read()
  f.close()

  f=open(outFname,"w")
  f.write(Template(temp).substitute(values))
  f.close()

class SEE(VerilogElaborator):
    def __init__(self,options, args):
        VerilogElaborator.__init__(self,options, args,cnfgName="seeg")
    def generate(self):
        logging.debug("")
        nets=[]
        def outputSetNets(module,prefix=""):
            res=[]
            # we want to affect net only on the bottom of the hierarhy
            if len(self.modules[module]["instances"])==0:
                for net in self.modules[module]["io"]:
                    _type=self.modules[module]["io"][net]["type"]
                    if _type=="output":
                        _len=self.modules[module]["io"][net]["len"]
                        _range=self.modules[module]["io"][net]["range"]
                        _ilen=int(_len)

#                        print net,_len, type(_len),_range,_ilen,_type
                        if _ilen==1:
                            res.append(prefix+net)
                        else:
                            #work around
                            nn=atr.split()
                            i1= int(nn[1])
                            i2= int(nn[3])
                            mmin = min ( (i1,i2) )
                            mmax = max ( (i1,i2) )
                            for i in range(mmin,mmax+1):
                                res.append(prefix+net+"[%d]"%i)
            else:
                #in other case we loop over hierarchy
                for instId in self.modules[module]["instances"]:
#                    print "XX",instId,self.modules[module]["instances"][instId]
                    inst=self.modules[module]["instances"][instId]['instance']
                    if "[" in  instId: instId="\\"+instId+" "
                    if inst in self.modules:
                        res+=outputSetNets(inst,prefix=prefix+instId+".")
            return res
        def outputSeuNets(module,prefix=""):
            res=[]
            # we want to affect net only on the bottom of the hierarhy
            if len(self.modules[module]["instances"])==0:
                if "seu_set" in self.modules[module]["constraints"]:
                    res.append(prefix+self.modules[module]["constraints"]["seu_set"])
                if "seu_reset" in self.modules[module]["constraints"]:
                    res.append(prefix+self.modules[module]["constraints"]["seu_reset"])

            else:
                #in other case we loop over hierarchy
                for instId in self.modules[module]["instances"]:
#                    print "XX",instId,self.modules[module]["instances"][instId]
                    inst=self.modules[module]["instances"][instId]['instance']
                    if "[" in  instId: instId="\\"+instId+" "
                    if inst in self.modules:
                        res+=outputSeuNets(inst,prefix=prefix+instId+".")
            return res
        setNets=outputSetNets(self.topModule,"DUT.")

        seuNets=outputSeuNets(self.topModule,"DUT.")

        self.logger.info("Found '%d' SET nets in the design"%len(setNets))
        self.logger.info("Found '%d' SEU nets in the design"%len(seuNets))
        self.logger.info("")

        if self.options.exlude!="":
            logging.info("Loading exlude file from from '%s'"%self.options.exlude)
            if not  os.path.isfile(self.options.exlude):
                self.logger.warning("File does not exists. Constrains will not be applied.")
            else:
                f=open(self.options.exlude,"r")
                toExlude=[]
                for l in f.readlines():
                    if len(l.strip())==0: continue
                    if l[0]=="#":continue
                    toExlude.append(l.rstrip())
                f.close()
                logging.info("Found %d excluding rules"%len(toExlude))

                def exclude(nets,rules):
                    reducedNets=[]
                    for net in sorted(nets):
                        matched=0
                        for rule in rules:
                            result = re.match(rule,net)
                            if result:
                                logging.debug("Excluding net '%s' because of rule '%s'"%(net,rule))
                                matched=1
                                break
                        if not matched:
                            reducedNets.append(net)
                    return reducedNets

                seuNets=exclude(seuNets,toExlude)
                setNets=exclude(setNets,toExlude)

        logging.debug("Nets to be affected by SET : %d"%(len(setNets)))
        l="  "
        for n in setNets:
            l+=n+" "
            if len(l)>100:
                logging.debug(l)
                l="  "
        logging.debug(l)

        logging.debug("Nets to be affected by SEU : %d"%(len(seuNets)))
        l="  "
        for n in seuNets:
            l+=n+" "
            if len(l)>100:
                logging.debug(l)
                l="  "
        logging.debug(l)

        wireid=0

        values={}
        values['set_display_net']=""
        values['set_force_net']=""
        values['set_release_net']=""
        for wireid,net in enumerate(setNets):
            values['set_force_net']  +="    %4d : force %s = ~%s;\n"%(wireid,net,net)
            values['set_release_net']+="    %4d : release %s;\n"%(wireid,net)
            values['set_display_net']+='   %4d : $display("%s");\n'%(wireid,net)
        values['set_max_net']="%d"%len(setNets)
        values['set_force_net']  =values['set_force_net'].rstrip()
        values['set_release_net']=values['set_release_net'].rstrip()
        values['set_display_net']=values['set_display_net'].rstrip()


        values['seu_display_net']=""
        values['seu_force_net']=""
        values['seu_release_net']=""
        for wireid,net in enumerate(seuNets):
            values['seu_force_net']  +="    %4d : force %s = ~%s;\n"%(wireid,net,net)
            values['seu_release_net']+="    %4d : release %s;\n"%(wireid,net)
            values['seu_display_net']+='   %4d : $display("%s");\n'%(wireid,net)
        values['seu_max_net']="%d"%len(seuNets)
        values['seu_force_net']  =values['seu_force_net'].rstrip()
        values['seu_release_net']=values['seu_release_net'].rstrip()
        values['seu_display_net']=values['seu_display_net'].rstrip()


        tfile=os.path.join( self.scriptDir,  self.config.get("seeg","template"))
        self.logger.info("Taking template from '%s'"%tfile)

        fname=self.options.ofile
        self.logger.info("SEE file is stored to '%s'"%fname)


        generateFromTemplate(fname,tfile, values)


def main():
    parser = OptionParser(version="%prog 1.0", usage="%prog [options] fileName")
    parser.add_option("-v", "--verbose",        dest="verbose",      action="count",   default=0, help="More verbose output (use: -v, -vv, -vvv..)")
    parser.add_option("-l", "--lib",            dest="libs",       action="append",   default=[], help="Library")
    parser.add_option("",   "--spaces",         dest="spaces",       default=2, type=int )
    parser.add_option("-e", "--exclude",        dest="exlude",       default="", help="Exlude nets from output file")
    parser.add_option("-o", "--output-file",    dest="ofile" ,       default="", help="Output file name")

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

        if not options.ofile:
            raise OptParseError("You have to specify output file name.")

        fname=args[0]

        try:
            seeg=SEE(options, args)
            seeg.parse()
            seeg.elaborate()
            seeg.generate()
        except ParseException, err:
            logging.error("")
            logging.error(err.line)
            logging.error( " "*(err.column-1) + "^")
            logging.error( err)
            for l in traceback.format_exc().split("\n"):
                logging.error(l)

    except ErrorMessage as er:
        logging.error(er)
    except OptParseError as er:
        logging.error(er)

if __name__=="__main__":
    main()

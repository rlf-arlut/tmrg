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


#!/usr/bin/env python
import logging
from optparse import *
from vp import *
import traceback
import pprint
import os
import glob
import logging
from verilogFormater import VerilogFormater
import filecmp
import copy
import ConfigParser

class ErrorMessage(BaseException):
    def __init__(self,s):
        BaseException.__init__(self,s)



class VerilogElaborator():
    def __init__(self,options, args):
        self.options=options
        self.args=args
        self.vp=VerilogParser()
        self.vf=VerilogFormater()
        self.EXT=('A','B','C')
        self.tmrErr={}
        self.logger = logging.getLogger('TMR')
        self.__voterPresent=False
        self.__fanoutPresent=False

        if self.options.verbose==0:
            self.logger.setLevel(logging.WARNING)
        if self.options.verbose==1:
            self.logger.setLevel(logging.INFO)
        elif self.options.verbose>=2:
            self.logger.setLevel(logging.DEBUG)
        self.files={}
        self.libFiles={}
        self.__init_callbacks()


        self.trace=True

        self.config = ConfigParser.ConfigParser()
        self.scriptDir = os.path.abspath(os.path.dirname(__file__))
        self.logger.debug("Script path : %s"%self.scriptDir)

        #master clonfig file
        masterCnfg=os.path.join(self.scriptDir,"../etc/tmrg.cfg")
        if os.path.exists(masterCnfg):
            self.logger.debug("Loading master config file from %s"%masterCnfg)
            self.config.read(masterCnfg)
        else:
            self.logger.warning("Master config file does not exists at %s"%masterCnfg)

        #user config file
        userCnfg=os.path.expanduser('~/.tmrg.cfg')
        if os.path.exists(userCnfg):
            self.logger.debug("Loading user config file from %s"%userCnfg)
            self.config.read(userCnfg)
        else:
            self.logger.info("User config file does not exists at %s"%userCnfg)


    def __init_callbacks(self):
        #scan class looking for elaborator functions
        self.elaborator={}
        for member in dir(self):
            if member.find("_VerilogElaborator__elaborate_")==0:
                token=member[len("_VerilogElaborator__elaborate_"):].lower()
                self.elaborator[token]=getattr(self,member)
                self.logger.debug("Found elaborator for %s"%token)



    def __elaborate_regdecl(self,tokens):
        #tokens=tokens[0] #self.registers
        _atrs=""
        _range=self.vf.format(tokens[2])
        _len=self.__getLenStr(tokens[2])

        if _len!="1":
            details="(range:%s len:%s)"%(_range,_len)
        else:
            details=""

        for reg in tokens[-1]:
             name=reg[0]
             #self.registers[name]=
             #print  {"atributes":_atrs,"range":_range, "len":_len ,"tmr":True}
             #self.debugInModule("gotReg: %s %s" % (name,details), type="regs")
             if not name in  self.current_module["nets"]:
                 self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len,  "type":"reg" }

    def __elaborate_moduleinstantiation(self,tokens):
        #toks=toks[0]
        identifier=tokens[0]
        instance = tokens[2][0][0][0]
        _range=""
        _len="1"
        #self.debugInModule("'%s' (type:%s)"%(instance,identifier),type="instance")
#            print "+",instname, module
        #self.instances[instance]={"atributes":identifier,"tmr":True}
        #print instance
        self.current_module["instances"][instance]={ "instance":identifier,"range":_range, "len":_len}
        #self.current_module["instantiated"]=0

    def __elaborate_always(self,tokens):
        self.__elaborate(tokens[1])

    def __elaborate_input(self,tokens):
         #tokens=tokens[0]
         _dir=tokens[0]
         _atrs=""
         _range=self.vf.format(tokens[1])
         _len=self.__getLenStr(tokens[1])

         if _len!="1":
             details="(range:%s len:%s)"%(_range,_len)
         else:
             details=""

         for name in tokens[-1]:
             if not name in  self.current_module["nets"]:
                 self.current_module["io"][name]={"atributes":_atrs,"range":_range, "len":_len, "type":"input" }
             if not name in  self.current_module["nets"]:
                 self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len,"type":"wire"}

    def __elaborate_output(self,tokens):
         #tokens=tokens[0]
         _dir=tokens[0]
         _atrs=""
         _range=self.vf.format(tokens[1])
         _len=self.__getLenStr(tokens[1])

         if _len!="1":
             details="(range:%s len:%s)"%(_range,_len)
         else:
             details=""

         for name in tokens[-1]:
             if not name in  self.current_module["nets"]:
                 self.current_module["io"][name]={"atributes":_atrs,"range":_range, "len":_len, "type":"output" }
             if not name in  self.current_module["nets"]:
                 self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len,"type":"wire"}
             #if not name in  self.current_module["nets"]:
             #    self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len,"type":"wire"}

    def __elaborate_netdecl1(self,tokens):
#            tokens=tokens[0]
            _atrs=""
            _range=self.vf.format(tokens[1])
            _len=self.__getLenStr(tokens[1])
            type=tokens[0]
            for name in tokens[3]:
                self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len , "type":type}
                if _len!="1":
                    details="(range:%s len:%s)"%(_range,_len)
                else:
                    details=""
#                self.debugInModule("gotNet: %s %s" % (name,details), type="nets")
#                if not name in  self.current_module["nets"]:
#                     self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len}

    def __elaborate_netdecl3(self,tokens):
#             print tokens
            _atrs=""
            _range=self.vf.format(tokens[2])
            _len=self.__getLenStr(tokens[2])

            for assgmng in tokens[4]:
                name=assgmng[0][0]
                right=assgmng[2]
                idRight=right[0][0]
                dnt=False
                for ex in self.EXT:
                    if name==idRight+ex: dnt=True
#                print idRight,dnt
 #               self.nets[name]={"atributes":_atrs,"range":_range, "len":_len ,"tmr":True}
#                if _len!="1":
#                    details="(range:%s len:%s)"%(_range,_len)
#                else:
#                    details=""
#                self.debugInModule("gotNet: %s %s" % (name,details), type="nets")
                if not name in  self.current_module["nets"]:
                    self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len , 'type':'wire'}
                    if dnt:
                        self.current_module["nets"][name]["dnt"]=True
                        self.logger.debug("Net %s will not be touched!"%name)


    def __elaborate_directive_default(self,tokens):
        tmr=False
        if tokens[0].lower() =='triplicate':
            tmr=True
        self.current_module["constraints"]["default"]=tmr

    def __elaborate_directive_do_not_triplicate(self,tokens):
        for net in tokens:
            self.current_module["constraints"][net]=False

    def __elaborate_directive_triplicate(self,tokens):
        for net in tokens:
            self.current_module["constraints"][net]=True

    def __elaborate_directive_do_not_touch(self,tokens):
        self.current_module["constraints"]["dnt"]=True

    def __elaborate_directive_tmr_error(self,tokens):
        en=False
        if tokens[0].lower() in ('true','enable'):
            en=True
        self.current_module["constraints"]["tmr_error"]=en


    def __elaborate(self,tokens):
        """ Elaborates tokens
        :param tokens: tokens to be parsed
        :return:
        """
        if isinstance(tokens, ParseResults):
            name=str(tokens.getName()).lower()
            if len(tokens)==0: return
            if self.trace: self.logger.debug( "[%-20s] len:%2d  str:'%s' >"%(name,len(tokens),str(tokens)[:80]))
            if name in self.elaborator:
                self.elaborator[name](tokens)
            else:
                self.logger.debug("No elaborator for %s"%name)
                if len(tokens):
                    for t in tokens:
                        self.__elaborate(t)


    def exc(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.logger.error("")
        self.logger.error("TMR exception:")
        #for l in traceback.format_tb(exc_traceback):
        for l in traceback.format_exception(exc_type, exc_value,
                                          exc_traceback):
            for ll in l.split("\n"):
              self.logger.error(ll)
        self.logger.error(ll)

                #traceback.format_exception_only(type(an_error), an_error)




    def addFile(self,fname):
        tokens=self.vp.parseFile(fname)
#        print tokens
        self.files[fname]=tokens
    def addLibFile(self,fname):
        tokens=self.vp.parseFile(fname)
#        print tokens
        self.libFiles[fname]=tokens


    def __getLenStr(self,toks):
            rangeLen="1"
            if len(toks)<2:
                return rangeLen
            left=toks[-2]
            right=toks[-1]
            rangeLen="%s - %s + 1"%(self.vf.format(left), self.vf.format(right))
            try:
                rangeInt=eval(rangeLen)
                rangeLen="%d"%rangeInt
            except:
                pass
            return rangeLen



    def moduleSummary(self,module):
        def printDict(d,dname=""):
            if len(d)==0: return

            tab = PrettyTable([dname, "range", "tmr"])
            tab.min_width[dname]=50;
            tab.min_width["range"]=20;
            tab.min_width["tmr"]=10;
            tab.align[dname] = "l" # Left align city names

            #print "%-12s:"%dname
            for k in d:
                item=d[k]
                #print k,item
                range=item["range"]
                if "tmr" in item: tmr=item["tmr"]
                else: tmr="-"
                if "dnt" in item: tmr="DNT"
                tab.add_row([k,range, tmr])
            tab.padding_width = 1 # One space between column edges and contents (default)
            for l in str(tab).split("\n"):
                self.logger.info(l)

        printDict(module["nets"],    "Nets")
#        printDict(module["io"],      "IO")
        printDict(module["instances"], "Instantiations")


    def parse(self):
        """ Parse files
        :return:
        """
        def args2files(args):
            files=[]
            for name in args:
                if os.path.isfile(name):
                    files.append(name)
                elif os.path.isdir(name):
                    for fname in glob.glob("%s/*.v"%name):
                        files.append(fname)
                else:
                    self.logger.error("File or directory does not exists %s"%name)

            return files

        for fname in args2files(self.args):
            try:
                logging.info("Processing file %s"%fname)
                self.addFile(fname)
            except ParseException, err:
                logging.error("")
                logging.error(err.line)
                logging.error( " "*(err.column-1) + "^")
                logging.error( err)
                for l in traceback.format_exc().split("\n"):
                    logging.error(l)
                raise ErrorMessage("Error during parsing")

        for fname in self.options.libs:
            try:
                logging.info("Processing file %s"%fname)
                self.addLibFile(fname)
            except ParseException, err:
                logging.error("")
                logging.error(err.line)
                logging.error( " "*(err.column-1) + "^")
                logging.error( err)
                for l in traceback.format_exc().split("\n"):
                    logging.error(l)
                raise ErrorMessage("Error during parsing")


    def elaborate(self):
        """ Elaborate the design
        :return:
        """
        self.modules={}
        # elaborate all modules
        for fname in sorted(self.files):
            self.logger.info("")
            self.logger.info("Elaborating %s"%(fname))
            tokens=self.files[fname]
#            print tokens
            for module in tokens:
                moduleHdr=module[0]
                moduleName=moduleHdr[1]
                modulePorts=moduleHdr[2]
                for port in modulePorts:
                    pass
                    #print port
                self.logger.debug("")
                self.logger.debug("= "*50)
                self.logger.info("Module %s (%s)"%(moduleName,fname))
                self.logger.debug("= "*50)
                self.current_module={"instances":{},"nets":{},"name":moduleName,"io":{},"constraints":{},"instantiated":0,'file':fname,"fanouts":{}, "voters":{}}
                for moduleItem in module[1]:
                    self.__elaborate(moduleItem)
                self.modules[moduleName]=copy.deepcopy(self.current_module)

        for fname in sorted(self.libFiles):
            self.logger.info("")
            self.logger.info("Elaborating library %s"%(fname))
            tokens=self.libFiles[fname]
#            print tokens
            for module in tokens:
                moduleHdr=module[0]
                moduleName=moduleHdr[1]
                modulePorts=moduleHdr[2]
                for port in modulePorts:
                    pass
                    #print port
                self.logger.debug("")
                self.logger.debug("= "*50)
                self.logger.info("Module %s (%s)"%(moduleName,fname))
                self.logger.debug("= "*50)
                self.current_module={"instances":{},"nets":{},"name":moduleName,"io":{},"constraints":{},"instantiated":0,'file':fname,"fanouts":{}, "voters":{}, "lib":fname}
                for moduleItem in module[1]:
                    self.__elaborate(moduleItem)
                self.modules[moduleName]=copy.deepcopy(self.current_module)


        # display summary
        if len(self.modules)>1:
            self.logger.info("")
            self.logger.info("Modules found %d"%len(self.modules))
            libDetails={}
            for module in sorted(self.modules):
                if "lib" not in self.modules[module]:
                    self.logger.info(" - %s (%s)"%(module,self.modules[module]["file"]))
                else:
                    lib=self.modules[module]["lib"]
                    if not lib in libDetails:
                        libDetails[lib]=[]
                    libDetails[lib].append(module)
            for lib in libDetails:
                self.logger.info("Lib %s : %s" %(lib," ".join(libDetails[lib])))

#        for module in sorted(self.modules):
#            self.logger.info("")
#            self.logger.info("Module:%s"%module)
#            self.moduleSummary(self.modules[module])

        # check if all modules are known
        self.logger.info("")
        self.logger.info("Checking the design hierarchy")
        elaborationError=False
        for module in self.modules:
            for instName in self.modules[module]["instances"]:
                instance=self.modules[module]["instances"][instName]["instance"]
                if instance in self.modules:
                    self.modules[instance]["instantiated"]+=1
                else:
                    self.logger.error("Unknown module instantiaition! In module %s, instance name %s instance type %s."%(module,instName,instance))
                    elaborationError=True
        tops=0
        self.topFile=""
        self.topModule=""
        for module in self.modules:
            if "lib" in self.modules[module]: continue
            if self.modules[module]["instantiated"]==0:
                self._printHierary(module)
                self.topModule=module
                self.topFile=self.modules[module]["file"]
                tops+=1
        if tops!=1:
            elaborationError=True
            self.logger.error("The design has multiple top cells! Output may not be correct!")

        if elaborationError:
            raise ErrorMessage("Serious error during elaboration.")


    def _printHierary(self,topModule):
        def _printH(module,i=""):
            i+="  |"
            for instName in self.modules[module]["instances"]:
                inst=self.modules[module]["instances"][instName]["instance"]
                if inst in self.modules:
                    self.logger.info(i+"- "+instName+":"+inst)
                    _printH(inst,i)
                else:
                    self.logger.info(i+"- [!] "+instName+":"+inst)

        self.logger.info("[%s]"%topModule)
        _printH(topModule)



class SEU(VerilogElaborator):
    def __init__(self,options, args):
        VerilogElaborator.__init__(self,options, args)
        self.seulogger = logging.getLogger('SEU')

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

    parser.add_option("-l",  "--lib",            dest="libs",       action="append",   default=[], help="Library")

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
            seug=SEU(options, args)
            seug.parse()
            seug.elaborate()
        except ParseException, err:
            logging.error("")
            logging.error(err.line)
            logging.error( " "*(err.column-1) + "^")
            logging.error( err)
            for l in traceback.format_exc().split("\n"):
                logging.error(l)


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


    except ErrorMessage as er:
        logging.error(er)

    except OptParseError as er:
        logging.error(er)
#        G.write('simple.dot')
#        G.layout() # layout with default (neato)
#        G.draw('simple.png')

if __name__=="__main__":
    main()

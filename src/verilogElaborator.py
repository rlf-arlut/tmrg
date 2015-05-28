#!/usr/bin/env python
import logging
from optparse import *
import traceback
import pprint
import os
import glob
import logging
import filecmp
import copy
import ConfigParser
from verilogParser import *
from verilogFormater import VerilogFormater

class ErrorMessage(BaseException):
    def __init__(self,s):
        BaseException.__init__(self,s)


def readFile(fname):
    if os.path.isfile(fname):
        f=open(fname,"r")
        body=f.read()
        f.close()
        return body
    else:
        logging.error("File '%s' does not exists"%fname)
        return ""

def resultLine(tokens,sep=""):
    s=""
    if isinstance(tokens, ParseResults):
        for i in tokens:
             s+=resultLine(i)+sep
    else:
        s+=tokens
    return s

def diffFiles(fname1,fname2):
    path=os.path.realpath(__file__)
    dir=os.path.dirname(path)
    icdiff=os.path.join(dir,'icdiff')
    os.system("%s %s %s"%(icdiff,fname1,fname2))



class VerilogElaborator():
    def __init__(self,options, args,cnfgName):
        self.options=options
        self.args=args
        self.vp=VerilogParser()
        self.vf=VerilogFormater()
        self.logger = logging.getLogger('TMR')

        if self.options.verbose==0:
            self.logger.setLevel(logging.WARNING)
        if self.options.verbose==1:
            self.logger.setLevel(logging.INFO)
        elif self.options.verbose>=2:
            self.logger.setLevel(logging.DEBUG)
        self.files={}
        self.libFiles={}
        self.__init_elaborate_callbacks()


        self.trace=True

        self.config = ConfigParser.ConfigParser()
        self.scriptDir = os.path.abspath(os.path.dirname(__file__))
        self.logger.debug("Script path : %s"%self.scriptDir)

        #master clonfig file
        masterCnfg=os.path.join(self.scriptDir,"../etc/%s.cfg"%cnfgName)
        if os.path.exists(masterCnfg):
            self.logger.debug("Loading master config file from %s"%masterCnfg)
            self.config.read(masterCnfg)
        else:
            self.logger.warning("Master config file does not exists at %s"%masterCnfg)

        #user config file
        userCnfg=os.path.expanduser('~/.%s.cfg'%cnfgName)
        if os.path.exists(userCnfg):
            self.logger.debug("Loading user config file from %s"%userCnfg)
            self.config.read(userCnfg)
        else:
            self.logger.info("User config file does not exists at %s"%userCnfg)


    def __init_elaborate_callbacks(self):
        #scan class looking for elaborator functions
        self.elaborator={}
        for member in dir(self):
            if member.find("_elaborate_")==0:
                token=member[len("_elaborate_"):].lower()
                self.elaborator[token]=getattr(self,member)
                self.logger.debug("Found elaborator for %s"%token)



    def _elaborate_regdecl(self,tokens):
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

    def _elaborate_moduleinstantiation(self,tokens):
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

    def _elaborate_always(self,tokens):
        self._elaborate(tokens[1])

    def _elaborate_input(self,tokens):
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

    def _elaborate_inputhdr(self,tokens):
        self._elaborate_input(tokens)

    def _elaborate_output(self,tokens):
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

    def _elaborate_outputhdr(self,tokens):
         #tokens=tokens[0]
        self._elaborate_output(tokens)


    def _elaborate_netdecl1(self,tokens):
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

    def _elaborate_netdecl3(self,tokens):
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


    def _elaborate_directive_default(self,tokens):
        tmr=False
        if tokens[0].lower() =='triplicate':
            tmr=True
        self.current_module["constraints"]["default"]=tmr

    def _elaborate_directive_do_not_triplicate(self,tokens):
        for net in tokens:
            self.current_module["constraints"][net]=False

    def _elaborate_directive_triplicate(self,tokens):
        for net in tokens:
            self.current_module["constraints"][net]=True

    def _elaborate_directive_do_not_touch(self,tokens):
        self.current_module["constraints"]["dnt"]=True

    def _elaborate_directive_tmr_error(self,tokens):
        en=False
        if tokens[0].lower() in ('true','enable'):
            en=True
        self.current_module["constraints"]["tmr_error"]=en

    def _elaborate_directive_seu_set(self,tokens):
        self.current_module["constraints"]["seu_set"]=tokens[0]

    def _elaborate_directive_seu_reset(self,tokens):
        self.current_module["constraints"]["seu_reset"]=tokens[0]

    def _elaborate(self,tokens):
        """ Elaborates tokens
        :param tokens: tokens to be parsed
        :return:
        """
        if isinstance(tokens, ParseResults):
            name=str(tokens.getName()).lower()
            if len(tokens)==0: return
            self.logger.debug( "[%-20s] len:%2d  str:'%s' >"%(name,len(tokens),str(tokens)[:80]))
            if name in self.elaborator:
                self.elaborator[name](tokens)
            else:
                self.logger.debug("No elaborator for %s"%name)
                if len(tokens):
                    for t in tokens:
                        self._elaborate(t)


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
                self.logger.debug("")
                self.logger.debug("= "*50)
                self.logger.info("Module %s (%s)"%(moduleName,fname))
                self.logger.debug("= "*50)
                self.current_module={"instances":{},"nets":{},"name":moduleName,"io":{},"constraints":{},"instantiated":0,'file':fname,"fanouts":{}, "voters":{}}
                for port in modulePorts:
                    self._elaborate(port)

                for moduleItem in module[1]:
                    self._elaborate(moduleItem)
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
                    self._elaborate(moduleItem)
                self.current_module["constraints"]["dnt"]=True
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
                s="Lib %s : "%lib
                infoed=0
                for m in libDetails[lib]:
                    s+=m+" "
                    if len(s)>100:
                        if infoed<5:
                            self.logger.info(s)
                        else:
                            self.logger.debug(s)
                        s=""
                        infoed+=1
                if infoed<5:
                    self.logger.info(s)
                else:
                    self.logger.debug(s)



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

    def showSummary(self):
        for module in sorted(self.modules):
            self.logger.info("")
            self.logger.info("Module:%s"%module)
            self.moduleSummary(self.modules[module])

    def getAllInsttances(self,module,prefix=""):
        res=[]
        # we want store instances from the bottom of the hierarhy
        if len(self.modules[module]["instances"])==0:
                res.append( (prefix,module) )
        else:
            #in other case we loop over hierarchy
            for instId in self.modules[module]["instances"]:
                inst=self.modules[module]["instances"][instId]['instance']
                if "[" in  instId: instId="\\"+instId+" "
                if inst in self.modules:
                    res+=self.getAllInsttances(inst,prefix=prefix+"/"+instId)
        return res

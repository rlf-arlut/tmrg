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


class CmdConstrainParser:
    def __init__(self):
        # primitives
        self.semi = Literal(";")
        self.lpar = Literal("(")
        self.rpar = Literal(")")
        self.equals = Literal("=")
        self.constraints = {"triplicate":set(),"do_not_triplicate":set(), "default":True, "tmr_error":False}

        identLead = alphas+"$_"
        identBody = alphanums+"$_"
        identifier1 = Regex( r"\.?["+identLead+"]["+identBody+"]*(\.["+identLead+"]["+identBody+"]*)*"
                            ).setName("baseIdent")
        identifier2 = Regex(r"\\\S+").setParseAction(lambda t:t[0][1:]).setName("escapedIdent")
        identifier = (identifier1 | identifier2).setResultsName("id")

        self.directive_doNotTriplicate  =(  Suppress("do_not_triplicate") + OneOrMore(identifier)                ).setResultsName("directive_do_not_triplicate")
        self.directive_triplicate       =(  Suppress("triplicate")        + OneOrMore(identifier)                ).setResultsName("directive_triplicate")
        self.directive_default          =(  Suppress("default")           + oneOf("triplicate do_not_triplicate") + Group(Optional(identifier)) ).setResultsName("directive_default")
        self.directive_tmr_error        =(  Suppress("tmr_error")         + oneOf("true false") + Group(Optional(identifier))                   ).setResultsName("directive_tmr_error")

        self.directiveItem =  ( self.directive_triplicate |
                                self.directive_doNotTriplicate |
                                self.directive_default |
                                self.directive_tmr_error
                                )
    def parse(self,s):
        return self.directiveItem.parseString(s)


class TMR():
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

        #command line specified config files
        for fname in self.options.config:
            if os.path.exists(fname):
                self.logger.debug("Loading command line specified config file from %s"%fname)
                self.config.read(fname)
            else:
                self.logger.error("Command line specified config file does not exists at %s"%fname)

        if self.options.tmr_dir:
            self.logger.debug("Setting tmr_dir to %s"%self.options.tmr_dir)
            self.config.set("tmrg","tmr_dir",self.options.tmr_dir)

        if self.options.rtl_dir:
            self.logger.debug("Setting rtl_dir to %s"%self.options.rtl_dir)
            self.config.set("tmrg","rtl_dir",self.options.rtl_dir)


        if self.options.tmr_suffix:
            self.logger.debug("Setting tmr_suffix to %s"%self.options.tmr_suffix)
            self.config.set("tmrg","tmr_suffix",self.options.tmr_suffix)


        if self.config.has_option('tmrg', 'files'):
            files=self.config.get("tmrg","files").split(",")
            for file in files:
                file=file.strip()
                self.logger.debug("Adding file from config file %s"%file)
                self.args.append(file)
        # parse command line constrains
        ccp=CmdConstrainParser()
        self.cmdLineConstrains={}
        for c in self.options.constrain:
            tokens=ccp.parse(c)
            name=tokens.getName()
            if name=="directive_triplicate" or name=="directive_do_not_triplicate":
                tmrVal=False
                if name=="triplicate":tmrVal=True
                for _id in tokens:
                    if _id.find(".")>=0:
                        module,net=_id.split(".")
                        self.logger.info("Command line constrain '%s' for net '%s' in module '%s'"%(name, net,module))
                        if not module in self.cmdLineConstrains:
                            self.cmdLineConstrains[module]={}
                        self.cmdLineConstrains[module][net]=True
                    else:
                        self.logger.info("Command line constrain '%s' for net '%s'"%(name,net))
                        net=_id
                        if not "global" in self.cmdLineConstrains:
                            self.cmdLineConstrains["global"]={}
                        self.cmdLineConstrains["global"][net]=tmrVal
            elif name=="directive_default":
                tmrVal=False
                if tokens[0].lower()=="triplicate":
                    tmrVal=True
                if len(tokens[1])>0:
                    for module in tokens[1]:
                        self.logger.info("Command line constrain '%s' for module '%s' (value:%s)"%(name, module,str(tmrVal)))
                        if not module in self.cmdLineConstrains:
                            self.cmdLineConstrains[module]={}
                        self.cmdLineConstrains[module]["default"]=tmrVal
                else:
                    if not "global" in self.cmdLineConstrains:
                        self.cmdLineConstrains["global"]={}
                    self.cmdLineConstrains["global"]["default"]=tmrVal
            elif name=="directive_tmr_error":
                tmrErr=False
                if tokens[0].lower()=="true":
                    tmrErr=True
                if len(tokens[1])>0:
                    for module in tokens[1]:
                        self.logger.info("Command line constrain '%s' for module '%s' (value:%s)"%(name, module,str(tmrErr)))
                        if not module in self.cmdLineConstrains:
                            self.cmdLineConstrains[module]={}
                        self.cmdLineConstrains[module]["tmr_error"]=tmrErr
                else:
                    if not "global" in self.cmdLineConstrains:
                        self.cmdLineConstrains["global"]={}
                    self.cmdLineConstrains["global"]["default"]=tmrErr
            else:
                self.logger.warning("Unknown constrain '%s'"%name)

        if len(self.args)==0:
            rtl_dir=self.config.get("tmrg","rtl_dir")
            self.logger.debug("No input arguments specified. All files from rtl_dir (%s) will be parsed."%rtl_dir)
            self.args=[rtl_dir]
    def __init_callbacks(self):
        #scan class looking for elaborator functions
        self.elaborator={}
        for member in dir(self):
            if member.find("_TMR__elaborate_")==0:
                token=member[len("_TMR__elaborate_"):].lower()
                self.elaborator[token]=getattr(self,member)
                self.logger.debug("Found elaborator for %s"%token)

        #scan class looking for triplicator functions
        self.triplicator={}
        for member in dir(self):
            if member.find("_TMR__triplicate_")==0:
                token=member[len("_TMR__triplicate_"):].lower()
                self.triplicator[token]=getattr(self,member)
                self.logger.debug("Found triplicator for %s"%token)


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


    def __triplicate_directive_default(self,tokens):
        return []

    def __triplicate_directive_triplicate(self,tokens):
        return []

    def __triplicate_directive_do_not_triplicate(self,tokens):
        return []

    def __triplicate_directive_do_not_touch(self,tokens):
        return []

    def __triplicate_directive_tmr_error(self,tokens):
        return []

    def __triplicate(self,tokens,i=""):
        debug=0
        if debug:print i,"__",tokens.getName(),tokens
        if isinstance(tokens, ParseResults):
            name=str(tokens.getName()).lower()
            if len(tokens)==0: return tokens
            if name in self.triplicator:
                if debug:print i,"tpc>",tokens
                tokens=self.triplicator[name](tokens)
            else:
                self.logger.debug("No triplicator for %s"%name)
                newTokens=ParseResults([],name=tokens.getName())
                for j in range(len(tokens)):
                    if debug:print i,"in >",tokens[j]
                    if isinstance(tokens[j], ParseResults):
                        tmrToks=self.__triplicate(tokens[j],i+"  ")
                        if isinstance(tmrToks,list):
                            for otokens in tmrToks:
                                newTokens.append(otokens)
                                if debug:print i,"out>",otokens
                        else:
                            newTokens.append(tmrToks)
                    else:
                        newTokens.append(tokens[j])
                        if debug:print i,"str>",tokens[j]
                if debug:print i,"ret",newTokens.getName(),newTokens
                return newTokens
        else:
            #we have a string!
            pass
        return tokens


    def __triplicate_Always(self,tokens):
        #seq=self._isAlwaysSeq(t)
        result=[]
        #check if the module needs triplication
        #print t,self.checkIfTmrNeeded(t)
        tmr=self.checkIfTmrNeeded(tokens)
        ids=self.getLeftRightHandSide(tokens)

        self.logger.debug("[Always block]")
        self.logger.debug("      Left :"+" ".join(sorted(ids["left"])))
        self.logger.debug("      Right:"+" ".join(sorted(ids["right"])))
        self.logger.debug("      TMR  :"+str(tmr))
        if not tmr:
            self._addVotersIfTmr(ids["right"],addWires="output")
            return tokens

        self._addFanoutsIfTmr(ids["right"],addWires="output")


        for i in self.EXT:
            cpy=tokens.deepcopy()
            for name in list(ids["right"])+list(ids["left"]):
#                print name
#                if self.checkIfContains(cpy,name):
                _to_name=name+i
                self.replace(cpy,name,_to_name)
            result.append(cpy)
        #print "cpy",cpy,len(cpy)
        return result

    def __triplicate_continuousassign(self,tokens):
        #check if the module needs triplication
        tmr=self.checkIfTmrNeeded(tokens)
        ids=self.getLeftRightHandSide(tokens)

        self.logger.debug("[Continuous Assign block]")
        self.logger.debug("      Left :"+" ".join(sorted(ids["left"])))
        self.logger.debug("      Right:"+" ".join(sorted(ids["right"])))
        self.logger.debug("      TMR  :"+str(tmr))

        if not tmr:
            self._addVotersIfTmr(ids["right"],group="",addWires="output")
            return tokens

        self._addFanoutsIfTmr(ids["right"],addWires="output")

        result=[]
        for i in self.EXT:
            cpy=tokens.deepcopy()
            #self._appendToAllIds(cpy,post=i)
            for name in list(ids["right"]) + list(ids["left"]) :
                _to_name=name+i
                self.replace(cpy,name,_to_name)

            result.append(cpy)
        return result

#        dList=tokens[0][2]
#        newtokens=ParseResults([],name=dList.getName())
#        for ca in dList:
#            print ca
#            leftHand=ca[0]
#            if self.hasAnythingToTMR(leftHand):
#               for post in self.EXT:
##                   print ca
#                   ca2=ca.deepcopy()
#                   for var in self.toTMR:
#                       print var
#                       self.replace(ca2,var,var+post)
#                   newtokens.append(ca2)
#            else:
#                newtokens.append(ca)
#        tokens[0][2]=newtokens
        #print "TMR",delimitedList
        return tokens


#        else:
#            self.logger.error("Unable to add fanout %s (name already exists)"%inst)
#            self.logger.debug("    %s -> %s %s %s "%(_in,outA,outB,outC))



    def __triplicate_NetDecl3(self,tokens):
        def tmr_reg_list(tokens):
            newtokens=ParseResults([],name=tokens.getName())
            for element in tokens:
                if self.hasAnythingToTMR(element):
                    for post in self.EXT:
                        element2=element.deepcopy()
                        for var in self.toTMR:
                           self.replace(element2,var,var+post)
                        newtokens.append(element2)
                else:
                       newtokens.append(element)
            return newtokens

        ids=self.getLeftRightHandSide(tokens)
        vote=False

        #left=tokens[0][4][0][0][0]
        left=tokens[4][0][0][0]

        right=tokens[4][0][2][0][0]

        # check if this is explicit fanout
        eFanout=False
        for ext in self.EXT:
            if left==right+ext:eFanout=True
        if eFanout:
            self.logger.info("Removing declaration of '%s' (it comes from a fanout of %s)"%(left,right))
            return ParseResults([],name=tokens.getName())


        #check if this is part of explicit voter
        eVoter=False
        eGroup=""
        eNet=""
        for net in self.current_module["nets"]:
            for ext in self.EXT:
                if net+ext == left:
                    eVoter=True
                    eGroup=ext
                    eNet=net
        if eVoter:
            self.logger.info("Explicit fanin '%s' part of '%s' (group %s)"%(left,eNet,eGroup))
            for name in list(ids["right"]):
                self._addVoter(name,"","output")
            return tokens
        eFanin=False
        for ext in self.EXT:
            if left+ext==right:eFanin=True
        if eFanin:
            self.logger.info("Removing declaration of '%s' (it was declared for fanin)"%(left))
            return ParseResults([],name=tokens.getName())


        # FIX ME !!!!!!!!!! quick and dirty !!!!!!
        if "tmrError" == left and self.current_module["nets"]["tmrError"]:
            self.logger.info("Removing declaration of %s"%(left))
            return []

        #if left.find("TmrError")>=0 or left[-1]=="A" or left[-1]=="B" or left[-1]=="C":
        #    self.logger.info("Removing declaration of %s"%(left))
        #    return ParseResults([],name=tokens.getName())

        if len(self.voting_nets):
            if (right, left) in self.voting_nets:
                vote=True

        if vote:
              self.logger.info("TMR voting %s -> %s (bits:%s)"%(right,left,self.current_module["nets"][right]["len"]))
              newtokens=ParseResults([],name=tokens.getName())

              a=right+self.EXT[0]
              b=right+self.EXT[1]
              c=right+self.EXT[2]
              for ext in self.EXT:
                  voterInstName="%sVoter%s"%(right,ext)
                  name_voted="%s%s"%(left,ext)
                  netErrorName="%sTmrError%s"%(right,ext)
#                  print self.properties["nets"][right]
                  self._addVoterExtended(voterInstName=voterInstName,
                                 inA=a,
                                 inB=b,
                                 inC=c,
                                 out=name_voted,
                                 tmrError=netErrorName,
                                 range=self.current_module["nets"][right]["range"],
                                 len=self.current_module["nets"][right]["len"],
                                 group=ext,
                                 addWires="output")
              tokens=newtokens
              return tokens
        # in any other case, triplicate right hand side
        result = []
#        print ids["right"]
        for i in self.EXT:
#            print i
            cpy=tokens.deepcopy()
            for name in list(ids["right"])+list(ids["left"]):
                _to_name=name+i
                self.replace(cpy,name,_to_name)
            result.append(cpy)
#        print tokens
        return result

    def __triplicate_NetDecl1(self,tokens):
        tokens[3]=self._tmr_list(tokens[3])
        return tokens

    def __triplicate_RegDecl(self,tokens):
        def tmr_reg_list(tokens):
            newtokens=ParseResults([],name=tokens.getName())
            for element in tokens:
#                print element
                if element[0] in self.toTMR:
                    for post in self.EXT:
                        newtokens2=element.deepcopy()
                        newtokens2[0]=element[0]+post
                        newtokens.append(newtokens2)
                else:
                    newtokens.append(element)
            return newtokens
        tmr=self.checkIfTmrNeeded(tokens)
        ids=self.getLeftRightHandSide(tokens)

        self.logger.debug("[reg block]")
        self.logger.debug("      Left :"+" ".join(sorted(ids["left"])))
        self.logger.debug("      Right:"+" ".join(sorted(ids["right"])))
        self.logger.debug("      TMR  :"+str(tmr))
        if not tmr:
            return tokens

        result = []
        for i in self.EXT:
            cpy=tokens.deepcopy()
            for name in list(ids["right"])+list(ids["left"]):
                _to_name=name+i
                self.replace(cpy,name,_to_name)
            result.append(cpy)

        return result

    def __triplicate_ModuleInstantiation(self,tokens):
        try:
            identifier=tokens[0]
            instance = tokens[2][0][0][0]

            self.logger.debug("[module instances]")
            self.logger.debug("      ID  :"+identifier)
            self.logger.debug("      Ins :"+instance)

                #["constraints"]
            # if we know the instance
            if not identifier in self.modules:
                self.logger.error("")
                self.logger.info("      Module %s is unknown"%identifier)
                raise ErrorMessage("      Module %s is unknown"%identifier)

            if "dnt" in self.modules[identifier]["constraints"]:
                self.logger.debug("      Module '%s' will not be touched (id:%s)"%(identifier,instance))
                tmr=self.current_module["instances"][instance]["tmr"]
                if tmr:
                    ret=[]
                    # triplicate istances
                    for post in self.EXT:
                        instCpy=tokens.deepcopy()
                        instCpy[2][0][0][0]=instCpy[2][0][0][0]+post # change instance name
                        for port in instCpy[2][0][1]:
                            port[0][2][0][0]=port[0][2][0][0]+post
                        ret.append(instCpy)

                    for port in tokens[2][0][1]:
                        dname=port[0][0][1:]
                        dtype=self.modules[identifier]["io"][dname]['type']
                        sname=port[0][2][0][0]
                        stmr=self.current_module["nets"][sname]["tmr"]
                        self.logger.debug("      %s (%s) -> %s (tmr:%s)"%(dname,dtype,sname,str(stmr)))
                        if not stmr:
                            if dtype=="input":
                                self._addVoter(sname,addWires="output")
                            else :
                                self._addFanout(sname,addWires="input")

                    return ret
                else:
                    for port in tokens[2][0][1]:
                        dname=port[0][0][1:]
                        dtype=self.modules[identifier]["io"][dname]['type']
                        sname=port[0][2][0][0]
                        stmr=self.current_module["nets"][sname]["tmr"]
                        self.logger.debug("      %s (%s) -> %s (tmr:%s)"%(dname,dtype,sname,str(stmr)))
                        if stmr:
                            if dtype=="input":
                                self._addVoter(sname,addWires="output")
                            else :
                                self._addFanout(sname,addWires="input")
            else:
#                self.logger.info("Module %s is known"%identifier)
                identifierTMR=identifier+"TMR"
                tokens[0]=identifierTMR
#                self.logger.debug("ModuleInstantiation %s -> %s"%(moduleName,newModuleName))
                tokensIns=ParseResults([],name=tokens[2].getName())

                for instance in tokens[2]:
                        iname=instance[0][0]
                        instance2=instance.deepcopy()
                        newPorts=ParseResults([],name=instance2[1].getName())

                        for port in instance2[1]:
                            dport=port[0][0][1:] #skip dot
                            sport=port[0][2][0][0]
                            dportTmr=self.modules[identifier]["nets"][dport]["tmr"]
                            sportTmr=self.current_module["nets"][sport]["tmr"]

                            self.logger.debug("      %s (tmr:%s) -> %s (tmr:%s)"%(dport,dportTmr,sport,sportTmr))
                            if not dportTmr:
                                newPorts.append(port)
                                if sportTmr:
                                    if self.modules[identifier]["io"][dport]["type"]=="input":
                                        self._addVoter(sport,group="")
#                                        print "voter"
                                    else:
                                        self._addFanout(sport,addWires="input")
#                                        print "fanout"
                            elif dportTmr:
                                for post in self.EXT:
                                    portCpy=port.deepcopy()
                                    portCpy[0][0]="."+dport+post
                                    portCpy[0][2][0][0]=sport+post
                                    newPorts.append(portCpy)
                                if not sportTmr:
                                    if self.modules[identifier]["io"][dport]["type"]=="output":
                                        self._addVoter(sport,addWires="input")
                                    else:
                                        self._addFanout(sport)
                            ### TODO ADD TMR ERROR !!!!!!!!!!!!
                        if "tmrError" in self.modules[identifier]["nets"]:
                            #print iname
                            for post in self.EXT:
                                netName="%stmrError%s"%(iname,post)
                                tmrErrOut=self.vp.modulePortConnection.parseString(".tmrError%s(%s)"%(post,netName))[0]
                                self._addTmrErrorWire(post,netName)
                                newPorts.append(tmrErrOut)

                        instance2[1]=newPorts
                        tokensIns.append(instance2)
                tokens[2]=tokensIns
                return tokens


            #tmr=self.current_module["instances"][instance]["tmr"]

#             self.logger.debug("      TMR :"+str(tmr))
#             if not tmr:
#                 newIns=ParseResults([],name=tokens.getName())
#                 self.logger.error("Fanouts / voters are missing!")
# #                for inst in tokens:
# #                    name=inst[2][0][0][0]
# #                    for post in self.EXT:
# #                        instCpy=inst.deepcopy()
# #                        instCpy[2][0][0][0]=name+post
# #                        self.replaceAll(instCpy[2],post,dot=0)
# #                        newIns.append(instCpy)
# #                tokens=newIns
#             else: #triplicate insances
#                 results=[]
#                 # triplicate instances
#                 for post in self.EXT:
#                     instCpy=tokens.deepcopy()
#                     instCpy[2][0][0][0]=instance+post
#                     for port in instCpy[2][0][1]:
#                         #print port,port[0][2][0][0]
#                         port[0][2][0][0]=port[0][2][0][0]+post
#                         #print port
#                     results.append(instCpy)
#                 # add voting / fanouts
#                 self.logger.error("Fanouts / voters are missing!")
#                 return results
            return tokens
        except:
            self.exc()


    def __triplicate_module(self,tokens):
        try:
            header=tokens[0]
            moduleName=header[1]
            if "dnt" in   self.modules[moduleName]["constraints"]:
                self.logger.info("Module '%s' is not to be touched"%moduleName)
                return tokens
            self.current_module=self.modules[moduleName]
            header[1]=str(moduleName)+"TMR"
            self.logger.debug("")
            self.logger.debug("= "*50)
            self.logger.debug("Module %s -> %s"%(moduleName,header[1]))
            self.logger.debug("= "*50)

            self.logger.debug("- module body "+"- "*43)

            moduleBody=tokens[1]
            moduleBody=self.__triplicate(moduleBody)
            tokens[1]=moduleBody

            self.logger.debug("- module header "+"- "*42)

            #triplicate module header | add tmr signals
            if len(header)>2:
                ports=header[2]
                newports=ParseResults([],name=ports.getName())
                for port in ports:
                    portName=port[0]
                    doTmr=self.current_module["nets"][portName]["tmr"]
                    portstr="Port %s -> "%(portName)

                    if doTmr:
                        sep=""
                        for post in self.EXT:
                            newport=portName+post
                            newports.append(newport)
                            portstr+=sep+newport
                            sep=", "
                    else:
                        newports.append(port)
                    self.logger.debug(portstr)
                if "tmrError" in self.current_module["nets"]:
                    groups = set(self.current_module["voters"].keys()) | set(self.tmrErr.keys())
                    for group in sorted(groups):
                        newport="tmrError%s"%group
                        newports.append( newport )
                        self.logger.debug("Port %s"%(newport))
                header[2]=newports

            self.logger.debug("- voters & fanouts  "+"- "*40)
            groups = set(self.current_module["voters"].keys()) | set(self.tmrErr.keys())
            for group in sorted(groups):
                errSignals=set()

#                comment=ParseResults(["TMR group %s"%group],name="lineComment")
#                body.append(comment)
                if group in self.current_module["voters"]:
                    for voter in self.current_module["voters"][group]:
                        inst=voter
                        voter=self.current_module["voters"][group][voter]
                        self.logger.info("Instializaing voter %s"%inst)
                        _range=voter["range"]

                        _len=voter["len"]
                        _out=voter["out"]
                        _err=voter["err"]
                        _a=voter["inA"]
                        _b=voter["inB"]
                        _c=voter["inC"]
                        addWires=voter["addWires"]
                        if addWires=="output":
                            self.logger.debug("Adding output wire %s"%(_out))
                            moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_out))[0])
                            #moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_a))[0])
                            #moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_b))[0])
                            #moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_c))[0])
                        elif addWires=="input":
                            self.logger.debug("Adding input wires %s, %s , %s"%(_a,_b,_c))
                            moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_a))[0])
                            moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_b))[0])
                            moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_c))[0])

                        width=""
                        if _len!="1":
                            width+="#(.WIDTH(%s)) "%_len

                        if "tmrError" in self.current_module["nets"]:
                            moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s;"%(_err))[0])
                            moduleBody.append(self.vp.moduleInstantiation.parseString("majorityVoter %s%s (.inA(%s), .inB(%s), .inC(%s), .out(%s), .tmrErr(%s));"%
                                                                               (width,inst,_a,_b,_c,_out,_err) )[0]);
                            errSignals.add(_err)
                        else:
                            moduleBody.append(self.vp.moduleInstantiation.parseString("majorityVoter %s%s (.inA(%s), .inB(%s), .inC(%s), .out(%s));"%
                                                                               (width,inst,_a,_b,_c,_out) )[0]);



                #after all voters are added, we can create or them all
                if "tmrError" in self.current_module["nets"]:
                    moduleBody.insert(0,self.vp.netDecl1.parseString("wire tmrError%s;"%group)[0])
                    moduleBody.insert(0,self.vp.outputDecl.parseString("output tmrError%s;"%group)[0])
                    if group in self.tmrErr:
                        errSignals=errSignals |self.tmrErr[group]
                    sep=""
                    asgnStr="assign tmrError%s="%group
                    if len(errSignals):
                        for signal in sorted(errSignals):
                            asgnStr+=sep+signal
                            sep="|"
                    else:
                        asgnStr+="1'b0"
                    asgnStr+=";"
#                    print asgnStr
                    moduleBody.append(self.vp.continuousAssign.parseString(asgnStr)[0])



            for fanout in self.current_module["fanouts"]:
                    inst=fanout
                    fanout=self.current_module["fanouts"][inst]
    #                print voter
                    self.logger.info("Instializaing fanout %s"%inst)
                    _range=fanout["range"]
                    _len=fanout["len"]
                    _in=fanout["in"]
                    _a=fanout["outA"]
                    _b=fanout["outB"]
                    _c=fanout["outC"]
                    addWires=fanout["addWires"]
                    if addWires=="output":
                        self.logger.debug("Adding output wires %s, %s , %s"%(_a,_b,_c))
                        moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_a))[0])
                        moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_b))[0])
                        moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_c))[0])
                    elif addWires=="input":
                        self.logger.debug("Adding input wire %s"%(_in))
                        moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_in))[0])
#
    #                     comment=ParseResults(["cadence set_dont_touch %s"%name_voted],name="lineComment")
    #                   newtokens.insert(0,comment)
    #                   voterInstName="%sVoter%s"%(right,ext)

                    #moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s;"%(_err))[0])

                    width=""
                    if _len!="1":
                        width+="#(.WIDTH(%s)) "%_len
                    moduleBody.append(self.vp.moduleInstantiation.parseString("fanout %s%s (.in(%s), .outA(%s), .outB(%s), .outC(%s));"%
                                                                       (width,inst,_in,_a,_b,_c) )[0]);

            return tokens
        except:
            self.exc()

    def __triplicate_output(self,tokens):
        before=str(tokens[2])
        tokens[2]=self._tmr_list(tokens[2])
        after=str(tokens[2])
        self.logger.debug("Output %s->%s"%(before,after))
        return tokens

    def __triplicate_input(self,tokens):
        before=str(tokens[2])
        tokens[2]=self._tmr_list(tokens[2])
        after=str(tokens[2])
        self.logger.debug("Input %s->%s"%(before,after))
        return tokens

    def checkIfContains(self,tokens,label):
        def _check(tokens,label):
            if isinstance(tokens, ParseResults):
                for tok in tokens:
                    res=_check(tok,label)
                    if res:return True
                return False
            else:
                return label==tokens
        return _check(tokens,label)

    def replace(self,tokens,_from,_to):
        def _replace(tokens,_from,_to):
            if isinstance(tokens, ParseResults):
                for i in range(len(tokens)):
                    if isinstance(tokens[i], ParseResults):
                        res=_replace(tokens[i],_from,_to)
                    else:
                        if tokens[i]==_from:
                            tokens[i]=_to
        return _replace(tokens,_from,_to)

    def replaceDot(self,tokens,post):
        def _replace(tokens,post):
            if isinstance(tokens, ParseResults):
                for i in range(len(tokens)):
                    if isinstance(tokens[i], ParseResults):
                        res=_replace(tokens[i],post)
                    else:
                        if tokens[i][0]=='.':
                            tokens[i]+=post
        return _replace(tokens,post)


    def replaceAll(self,tokens,post,dot=1):
        for var in self.toTMR:
            self.replace(tokens,var,var+post)
        if dot:
            self.replaceDot(tokens,post)
        return tokens


    def getLeftRightHandSide(self,t,res=None):
        #print "getLeftRightHandSide", res, t
        if res==None: res={"left":set(),"right":set()}

        def _extractID(t,res=None):
            if res==None: res=set()
            if isinstance(t, ParseResults):
               name=str(t.getName()).lower()
               if name=="subscridentifier":
                   if not t[0] in self.current_module["nets"]:
                     self.logger.warning("Unknown net %s"%t[0])
                   if not "dnt" in self.current_module["nets"][t[0]]:
                       res.add(t[0])
               else:
                   for i in range(len(t)):
                       res=_extractID(t[i],res=res)
            return res
#        print "#",type(t),t
        if isinstance(t, ParseResults):
            name=str(t.getName()).lower()
            #print name, len(t), t
            if len(t)==0: return res
            if name in ("assgnmt", "nbassgnmt"):
                left_id=t[0][0]
                res["left"].add(left_id)
                #print   _extractID(t[2])
                res["right"].update( _extractID(t[2]))
            elif name in ("regdecl"):
                for tt in t[3]:
                    left_id=tt[0]
                    res["left"].add(left_id)

            elif name == "subscridentifier":
                    res["right"].add( t[0] )
            else:
                for i in range(len(t)):
#                    print "#(%d)>"%i,t[i]
                    res=self.getLeftRightHandSide(t[i],res=res)

        return res


    def checkIfTmrNeeded(self,t):
        res=self.getLeftRightHandSide(t)
        leftTMR=False
        leftNoTMR=False

        for net in res["left"]:
            if net in self.current_module["nets"]:
                if self.current_module["nets"][net]["tmr"]:
                    leftTMR=True
                if not self.current_module["nets"][net]["tmr"]:
                    leftNoTMR=True
            else:
                self.logger.warning("Unknown net %s"%i)
        if leftTMR and leftNoTMR:
            self.logger.error("Block contains both type of elements (should and should not be triplicated!). ")
            self.logger.error("This request will not be properly processed!")
            self.logger.error("Elements: %s"%(" ".join(sorted(res["left"]))))
            return False
        return leftTMR



    def tmrNbAssgnmt(self,t):
        # cpy=t.deepcopy()
        # #print cpy
        # #cpy[3]="dupa";
        # for v in self.toTMR:
        # #if self.checkIfContains(cpy,"rst"):
        #     print "shot!"
        #     self.replace(cpy,v,v+"A")
        #print t
        return t

    def _tmr_list(self,tokens):
        newtokens=ParseResults([],name=tokens.getName())
        for element in tokens:
            if element in self.current_module["nets"]:
                if self.current_module["nets"][element]["tmr"]:
                    for post in self.EXT:
                        newtokens.append(element+post)
                else:
                    newtokens.append(element)
            else:
                self.logger.warning("Net %s unknown!"%element)
                newtokens.append(element)
        return newtokens



    def hasAnythingToTMR(self,tokens):
        toTMR=0
        for varToTMR in self.toTMR:
            if self.checkIfContains(tokens,varToTMR):
                toTMR=1
                break
        return toTMR

    def _addVoterExtended(self,voterInstName,inA,inB,inC,out,tmrError,range,len,group,addWires=""):
        if not group in self.current_module["voters"]:
            self.current_module["voters"][group]={}
            self.logger.info("Creating TMR error group %s"%group)
        if not voterInstName in self.current_module["voters"][group]:
            self.logger.debug("Adding voter '%s' to group '%s'"%(voterInstName,group))
            self.logger.debug("    %s %s %s -> %s & %s"%(inA,inB,inC,out,tmrError))
            self.current_module["voters"][group][voterInstName]={
                                 "inA":inA,
                                 "inB":inB,
                                 "inC":inC,
                                 "out":out,
                                 "err":tmrError,
                                 "range":range,
                                 "len":len,
                                 "group":group,
                               "addWires":addWires}
            self.__voterPresent=True

    def _addVoter(self,netID,group="",addWires=""):
        if not group in self.current_module["voters"]:
            self.current_module["voters"][group]={}
            self.logger.info("Creating TMR error group %s"%group)

        voterInstName="%sVoter"%(netID)
        if not voterInstName in self.current_module["voters"][group]:
            nameVoted="%s"%(netID)
            netErrorName="%sTmrError"%(netID)
            inA=netID+self.EXT[0]
            inB=netID+self.EXT[1]
            inC=netID+self.EXT[2]
            range=self.current_module["nets"][netID]["range"]
            len=self.current_module["nets"][netID]["len"]

            self.logger.debug("Adding voter '%s' to group '%s'"%(voterInstName,group))
            self.logger.debug("    %s %s %s -> %s & %s"%(inA,inB,inC,nameVoted,netErrorName))
            self.current_module["voters"][group][voterInstName]={
                               "inA"  :inA,
                               "inB"  :inB,
                               "inC"  :inC,
                               "out"  :nameVoted,
                               "err"  :netErrorName,
                               "range":range,
                               "len"  :len,
                               "group":group,
                               "addWires":addWires}
            self.__voterPresent=True

#        else:
#            self.logger.error("Unable to add volter %s (name already exists)"%inst)
#            self.logger.error("    %s %s %s -> %s & %s"%(inA,inB,inC,out,tmrError))


    def _addVotersIfTmr(self,idList,group="",addWires="output"):
            for netID in idList:
                if self.current_module["nets"][netID]["tmr"]:
                    self._addVoter(netID,group=group,addWires=addWires)


    def _addFanout(self,netID,addWires=""):
        inst=netID+"Fanout"
        if not netID in self.current_module["nets"]:
             self.logger.warning("Net %s unknown in addFanout!"%netID)
             return

        if not inst in self.current_module["fanouts"]:
            _in=netID
            outA=netID+self.EXT[0]
            outB=netID+self.EXT[1]
            outC=netID+self.EXT[2]
            range=self.current_module["nets"][netID]["range"]
            len=self.current_module["nets"][netID]["len"]

            self.logger.debug("Adding fanout %s"%inst)
            self.logger.debug("    %s -> %s %s %s "%(_in,outA,outB,outC))
            self.current_module["fanouts"][inst]={"in":_in,
                               "outA":outA,
                               "outB":outB,
                               "outC":outC,
                               "range":range,
                               "len":len,
                               "addWires":addWires}
            self.__fanoutPresent=True

    def _addFanouts(self,idList,addWires=""):
        for netId in idList:
            self._addFanout(netId,addWires=addWires)

    #  list of IDs
    def _addFanoutsIfTmr(self,idList,addWires=""):
            for netId in idList:
                if not self.current_module["nets"][netId]["tmr"]:
                    self._addFanout(netId,addWires=addWires)

    def _appendToAllIds(self,t,post):
        if isinstance(t, ParseResults):
            name=str(t.getName()).lower()
            #print name, len(t), t
            if len(t)==0: return
            elif name == "subscridentifier":
                t[0]=t[0]+post
            else:
                for i in range(len(t)):
                    res=self._appendToAllIds(t[i],post=post)



    def _addTmrErrorWire(self,post,netName):
        if not post in self.tmrErr:
            self.tmrErr[post]=set()
        self.tmrErr[post].add(netName)



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


    def tmrTop(self,tokens):
        return tokens



    def addFile(self,fname):
        tokens=self.vp.parseFile(fname)
#        print tokens
        self.files[fname]=tokens

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
        # display summary
        if len(self.modules)>1:
            self.logger.info("")
            self.logger.info("Modules found %d"%len(self.modules))
            for module in self.modules:
                self.logger.info(" - %s (%s)"%(module,self.modules[module]["file"]))

        #apply constrains
        self.logger.info("")
        self.logger.info("Applying constrains")
      #  print self.cmdLineConstrains[module]
        for module in sorted(self.modules):
            self.logger.info("Module %s"%module)

            #tmr error output
            # global settings
            tmrErrOut=self.config.getboolean("global","tmr_error")
            s="configGlobal:%s"%(str(tmrErrOut))
            # from source code
            if "tmr_error" in self.modules[module]["constraints"]:
                tmrErrOut=self.modules[module]["constraints"]["tmr_error"]
                s+=" -> srcModule:%s"%(str(tmrErrOut))
            # from module configuration
            if self.config.has_section(module) and self.config.has_option(module,"tmr_error"):
                tmrErrOut=self.config.getboolean(module,"tmr_error")
                s+=" -> configModule:%s"%(str(tmrErrOut))
            # from command line arguments
            if module in self.cmdLineConstrains and "tmr_error" in self.cmdLineConstrains[module]:
                tmrErrOut=self.cmdLineConstrains[module][ "tmr_error"]
                s+=" -> cmdModule:%s"%(str(tmrErrOut))
            self.logger.info(" | tmrErrOut : %s (%s)"%(str(tmrErrOut),s))
            if tmrErrOut:
                self.modules[module]["nets"]["tmrError"]={"range":"",len:"1","tmr":True}


            for net in self.modules[module]["nets"]:
                tmr=False
                # default from global configuration
                globalTmr=self.config.get("global","default")
                if globalTmr.lower()=="triplicate":
                    tmr=True
                s="configGlobalDefault:%s"%(str(tmr))
                # default from source code
                if "default" in self.modules[module]["constraints"]:
                    tmr=self.modules[module]["constraints"]["default"]
                    s+=" -> srcModuleDefault:%s"%(str(tmr))

                # default from module configuration
                if self.config.has_section(module) and self.config.has_option(module,"default"):
                    modDefault=self.config.get(module,"default")
                    if modDefault.lower()=="triplicate":
                        tmr=True
                    else:
                        tmr=False
                    s+=" -> configModuleDefault:%s"%(str(tmr))

                # default from command line arguments
                if module in self.cmdLineConstrains and "default" in self.cmdLineConstrains[module]:
                    tmr=self.cmdLineConstrains[module]["default"]
                    s+=" -> cmdModuleDefault:%s"%(str(tmr))

                # net specific from source code
                if net in self.modules[module]["constraints"]:
                    tmr=self.modules[module]["constraints"][net]
                    s+=" -> src:%s"%(str(tmr))

                # net specific from configuration
                if self.config.has_section(module) and self.config.has_option(module,net):
                    conf=self.config.get(module,net)
                    if conf.lower()=="triplicate":
                        tmr=True
                    else:
                        tmr=False
                    s+=" -> config:%s"%(str(tmr))

                # net specific from command line
                if module in self.cmdLineConstrains and net in self.cmdLineConstrains[module]:
                    tmr=self.cmdLineConstrains[module][net]
                    s+=" -> cmd:%s"%(str(tmr))

                self.logger.info(" | net %s : %s (%s)"%(net,str(tmr),s))
                self.modules[module]["nets"][net]["tmr"]=tmr

            for inst in self.modules[module]["instances"]:
                tmr=False
                # default from global configuration
                globalTmr=self.config.get("global","default")
                if globalTmr.lower()=="triplicate":
                    tmr=True
                s="configGlobalDefault:%s"%(str(tmr))
                # default from module configuration
                if self.config.has_section(module) and self.config.has_option(module,"default"):
                    modDefault=self.config.get(module,"default")
                    if modDefault.lower()=="triplicate":
                        tmr=True
                    else:
                        tmr=False
                    s+=" -> configModuleDefault:%s"%(str(tmr))
                # default from source code
                if "default" in self.modules[module]["constraints"]:
                    tmr=self.modules[module]["constraints"]["default"]
                    s+=" -> srcModuleDefault:%s"%(str(tmr))

                # default from command line arguments
                if module in self.cmdLineConstrains and "default" in self.cmdLineConstrains[module]:
                    tmr=self.cmdLineConstrains[module]["default"]
                    s+=" -> cmdModuleDefault:%s"%(str(tmr))
                # inst specific from configuration
                if self.config.has_section(module) and self.config.has_option(module,inst):
                    conf=self.config.get(module,inst)
                    if conf.lower()=="triplicate":
                        tmr=True
                    else:
                        tmr=False
                    s+=" -> config:%s"%(str(tmr))
                # inst specific from source code
                if inst in self.modules[module]["constraints"]:
                    tmr=self.modules[module]["constraints"][inst]
                    s+=" -> src:%s"%(str(tmr))
                # inst specific from command line
                if module in self.cmdLineConstrains and inst in self.cmdLineConstrains[module]:
                    tmr=self.cmdLineConstrains[module][inst]
                    s+=" -> cmd:%s"%(str(tmr))

                self.logger.info(" | inst %s : %s (%s)"%(inst,str(tmr),s))
                self.modules[module]["instances"][inst]["tmr"]=tmr

        #apply special constrains by name conventions
        self.logger.info("")
        self.logger.info("Applying constrains by name")
        self.voting_nets=[]
        for module in sorted(self.modules):
            self.logger.info("Module %s"%module)
            for net1 in self.modules[module]["nets"]:
                for net2 in self.modules[module]["nets"]:
                    if net1+"Voted"==net2:
                        self.voting_nets.append((net1,net2))
                        self.logger.info("Full voting detected for nets %s -> %s"%(net1,net2))
                        if not self.modules[module]["nets"][net1]["tmr"] or  not self.modules[module]["nets"][net2]["tmr"]:
                            self.logger.warning("Nets for full voting should be triplicated!")
        if len(self.voting_nets):
            self.logger.info("Voting present (%d nets)"%(len(self.voting_nets)))


        for module in sorted(self.modules):
            self.logger.info("")
            self.logger.info("Module:%s"%module)
            self.moduleSummary(self.modules[module])

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

    def _addCommonModules(self,fname,voter=False,fanout=False):
        if not  self.__fanoutPresent and not self.__voterPresent : return
        if not self.config.getboolean("tmrg","add_common_definitions"): return
        self.logger.info("Declarations of voters and fanouts are being added to %s"%fname)
        f=open(fname,"a")

        if self.__voterPresent:
            vfile=os.path.join( self.scriptDir,  self.config.get("tmrg","voter_definition"))
            self.logger.info("Taking voter declaration from %s"%vfile)
            f.write("\n\n// %s\n"%vfile)
            f.write(readFile(vfile))

        if self.__fanoutPresent:
            ffile=os.path.join( self.scriptDir,  self.config.get("tmrg","fanout_definition"))
            self.logger.info("Taking fanout declaration from %s"%ffile)
            f.write("\n\n// %s\n"%ffile)
            f.write(readFile(ffile))
        f.close()

    def triplicate(self):
        """ Triplicate the design
        :return:
        """
        tmrSuffix="TMR"
        spaces=self.config.getint("tmrg","spaces")
        showdiff=True

        self.logger.debug("")
        self.logger.info("Triplciation starts here")
        for fname in sorted(self.files):
            file,ext=os.path.splitext(os.path.basename(fname))
            self.logger.info("")
            self.logger.debug("#"*100)
            self.logger.info("Triplicating file %s"%(fname))
            self.logger.debug("#"*100)
            tokens=self.files[fname]
            tmrTokens=ParseResults([],name=tokens.getName())
            for module in tokens:
                tmrModule=self.__triplicate(module)
                tmrTokens.append(tmrModule)

            fout=os.path.join(self.config.get("tmrg","tmr_dir"), file+tmrSuffix+ext)
            foutnew=fout+'.new'
            self.logger.debug("Saving result of triplication to %s"%foutnew)

            f=open(foutnew,"w")
            f.write(self.vf.format(tmrTokens).replace("\t"," "*self.config.getint("tmrg","spaces")))
            f.close()

        topFile,ext=os.path.splitext(os.path.basename(self.topFile))
        ftop=os.path.join(self.config.get("tmrg","tmr_dir"), topFile+tmrSuffix+ext+'.new')
        self._addCommonModules(ftop)


        for fname in sorted(self.files):
            file,ext=os.path.splitext(os.path.basename(fname))
            fout=os.path.join(self.config.get("tmrg","tmr_dir"), file+tmrSuffix+ext)
            foutnew=fout+'.new'
            if os.path.exists(fout):
                    if filecmp.cmp(fout,foutnew):
                        self.logger.info("File '%s' exists. Its content is up to date."%fout)
                        self.logger.debug("Removing temporary file %s."%foutnew)
                        os.remove(foutnew)
                    else:
                        if self.config.getboolean("tmrg","overwrite_files"):
                            self.logger.debug("Overwriting %s by %s"%(fout,foutnew))
                            os.rename(foutnew,fout)
                        else:
                            self.logger.warning("File '%s' exists. Saving output to '%s'"%(fout,foutnew))
                            if showdiff:
                                diffFiles(fout,foutnew)
            else:
                    self.logger.info("Saving output to '%s'"%(fout))
                    self.logger.debug("Rename %s to %s"%(foutnew,fout))
                    os.rename(foutnew,fout)
        self.genSDC()

    def genSDC(self):
        tmrSuffix="TMR"

        def _findVotersAndFanouts(module,i="",ret=[]):
            for fanoutInst in self.modules[module]["fanouts"]:
                fanout=self.modules[module]["fanouts"][fanoutInst]
                ret.append(i+"nets/"+fanout["outA"])
                ret.append(i+"nets/"+fanout["outB"])
                ret.append(i+"nets/"+fanout["outC"])
                ret.append(i+"nets/"+fanout["in"])

            for group in self.modules[module]["voters"]:
                for voterInst in self.modules[module]["voters"][group]:
                    voter=self.modules[module]["voters"][group][voterInst]
                    ret.append(i+"nets/"+voter["inA"])
                    ret.append(i+"nets/"+voter["inB"])
                    ret.append(i+"nets/"+voter["inC"])
                    ret.append(i+"nets/"+voter["out"])
            for instName in self.modules[module]["instances"]:
                i=i+"instances_hier/%s/"%instName
                inst=self.modules[module]["instances"][instName]["instance"]
                if inst in self.modules:
#                    self.logger.info(i+"- "+instName+":"+inst)
                    _findVotersAndFanouts(inst,i,ret)
                else:
#                    self.logger.info(i+"- [!] "+instName+":"+inst)
                     pass
            return ret

        if self.config.getboolean("tmrg","generate_sdc") or self.options.generate_sdc:
            topFile,ext=os.path.splitext(os.path.basename(self.topFile))
            fsdc=os.path.join(self.config.get("tmrg","tmr_dir"), topFile+tmrSuffix+".sdc")
            self.logger.info("Generating SDC constraints file i%s"%fsdc)
            header=""
            if self.config.getboolean("tmrg","sdc_headers") or self.options.sdc_headers:
               header="set sdc_version 1.3\n"
            # generate sdf file
            ret= _findVotersAndFanouts(self.topModule,i="/designs/%s/"%(self.topModule+tmrSuffix))
            f=open(fsdc,"w")
            f.write(header)
            if self.__voterPresent:
                f.write("set_dont_touch majorityVoter\n")
            if self.__fanoutPresent:
                f.write("set_dont_touch fanout\n")
            for l in ret:
                f.write("set_dont_touch %s\n"%l)
            f.close()




########################################################################################################################







def main():
    parser = OptionParser(version="%prog 0.1", usage="%prog [options] fileName")
    parser.add_option("-v",  "--verbose",          dest="verbose",      action="count",   default=0, help="More verbose output (use: -v, -vv, -vvv..)")
#    parser.add_option("", "--input-file",         dest="inputFile",   help="Input file name (*.v)", metavar="FILE")
#    parser.add_option("", "--output-file",        dest="outputFile",  help="Output file name (*.v)", metavar="FILE")
#    parser.add_option("-r", "--recursive",       action="store_true", dest="rec", default=True, help="Recurive.")
    parser.add_option("",  "--doc",               dest="doc",  action="store_true",   default=False, help="Open documentation in web browser")
    actionGroup = OptionGroup(parser, "Actions" )
    actionGroup.add_option("-p", "--parse-only",        action="store_true", dest="parse",     default=False, help="Parse")
    actionGroup.add_option("-e", "--elaborate",         action="store_true", dest="elaborate", default=False, help="Elaborate")
    #actionGroup.add_option("-t", "--triplicate",        action="store_true", dest="tmr",       default=False, help="Triplicate.")
    parser.add_option_group(actionGroup)
    #parser.add_option("-f", "--format",            dest="format",       action="store_true",default=False, help="Parse")
    #parser.add_option("-i", "--info",              dest="info",         action="store_true",   default=False, help="Info")
    #parser.add_option("-q", "--trace",             dest="trace",        action="store_true",   default=False, help="Trace formating")
    #parser.add_option("",   "--single2tmr",        dest="s2t",          action="store_true",   default=False, help="Single ended to TMR")
    #parser.add_option("-d", "--do-not-triplicate", dest="dnt",          action="append"  ,type="str")
    dirGroup = OptionGroup(parser, "Directories" )
    dirGroup.add_option("",   "--rtl-dir",           dest="rtl_dir",      action="store", default="")
    dirGroup.add_option("",   "--tmr-dir",           dest="tmr_dir",      action="store", default="")
    parser.add_option_group(dirGroup)

    tmrGroup = OptionGroup(parser, "Triplication" )

    tmrGroup.add_option("",    "--tmr-suffix",       dest="tmr_suffix",   action="store", default="")
#    parser.add_option("",    "--diff",             dest="showdiff",     action="store_true",  default=False, help="Show diff")
    tmrGroup.add_option("-c",  "--config",           dest="config",       action="append",   default=[], help="Load config file")
    tmrGroup.add_option("-w",  "--constrain",        dest="constrain",    action="append",   default=[], help="Load config file")
    tmrGroup.add_option("",  "--generate_sdc",       dest="generate_sdc",   action="store_true",   default=False, help="Generate SDC file for Design Compiler")
    tmrGroup.add_option("",  "--sdc_headers",        dest="sdc_headers",    action="store_true",   default=False, help="Append SDC headers")


    parser.add_option_group(tmrGroup)

   # print config.get("tmrg","tmr_dir")
   # print config.get("tmrg","tmr_signals")
   # print config.items("module")
    #FORMAT = '%(message)s'
    #logging.basicConfig(format='[%(name)s|%(levelname)5s] %(message)s', level=logging.INFO)
    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)

    try:
        (options, args) = parser.parse_args()

        if options.verbose==0:
            logging.getLogger().setLevel(logging.WARNING)
        if options.verbose==1:
            logging.getLogger().setLevel(logging.INFO)
        elif options.verbose==2:
            logging.getLogger().setLevel(logging.DEBUG)

        tmrg=TMR(options, args)

        if options.doc:
            import webbrowser
            url = 'http://cern.ch/tmrg'
            # Open URL in new window, raising the window if possible.
            webbrowser.open_new(url)
            return

        tmrg.parse()

        if options.parse: return

        tmrg.elaborate()

        if options.elaborate: return

        tmrg.triplicate()

    except ErrorMessage as e:
        logging.error(str(e))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.warning("The exception was raised from:")
        for l in traceback.format_tb(exc_traceback):
            for ll in l.split("\n"):
              logging.warning(ll)
        logging.warning(ll)

    # except :
    #     exc_type, exc_value, exc_traceback = sys.exc_info()
    #     logging.error("1")
    #     logging.error("")
    #     #for l in traceback.format_tb(exc_traceback):
    #     for l in traceback.format_exception(exc_type, exc_value,
    #                                       exc_traceback):
    #         for ll in l.split("\n"):
    #           logging.error(ll)
    #     logging.error(ll)
    #

if __name__=="__main__":
    main()
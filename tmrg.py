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


def readFile(fname):
    f=open(fname,"r")
    body=f.read()
    f.close()
    return body

def resultLine(tokens,sep=""):
    s=""
    if isinstance(tokens, ParseResults):
        for i in tokens:
             s+=resultLine(i)+sep
    else:
        s+=tokens
    return s

class CmdConstrainParser:
    def __init__(self):
        # primitives
        self.semi = Literal(";")
        self.lpar = Literal("(")
        self.rpar = Literal(")")
        self.equals = Literal("=")
        self.constraints = {"triplicate":set(),"do_not_triplicate":set(), "default":True, "tmr_error":True}

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
        self.voters={}
        self.fanout={}
        self.tmrErr={}
        self.logger = logging.getLogger('TMR')
        if self.options.verbose==0:
            self.logger.setLevel(logging.WARNING)
        if self.options.verbose==1:
            self.logger.setLevel(logging.INFO)
        elif self.options.verbose>=2:
            self.logger.setLevel(logging.DEBUG)
        self.files={}

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

        self.trace=True

        self.config = ConfigParser.ConfigParser()
        scriptDir = os.path.abspath(os.path.dirname(__file__))
        self.logger.debug("Script path : %s"%scriptDir)

        #master clonfig file
        masterCnfg=os.path.join(scriptDir,"tmrg.cfg")
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
            if name=="directive_triplicate" or name=="do_not_triplicate":
                tmrVal=False
                if name=="triplicate":tmrVal=True
                for _id in tokens:
                    if _id.find(".")>=0:
                        module,net=_id.split(".")
                        self.logger.info("Command line constrain for net %s in module %s"%(net,module))
                        if not module in self.cmdLineConstrains:
                            self.cmdLineConstrains[module]={}
                        self.cmdLineConstrains[module][net]=True
                    else:
                        self.logger.info("Command line constrain for net %s"%(net))
                        net=_id
                        if not "global" in self.cmdLineConstrains:
                            self.cmdLineConstrains["global"]={}
                        self.cmdLineConstrains["global"][net]=tmrVal
            elif name=="directive_default":
                tmrVal=False
                if tokens[0].lower()=="triplicate":
                    tmrVal=False
                if len(tokens[1])>0:
                    for module in tokens[1]:
                        if not module in self.cmdLineConstrains:
                            self.cmdLineConstrains[module]={}
                        self.cmdLineConstrains[module]["default"]=tmrVal
                else:
                    if not "global" in self.cmdLineConstrains:
                        self.cmdLineConstrains["global"]={}
                    self.cmdLineConstrains["global"]["default"]=tmrVal

        if len(self.args)==0:
            rtl_dir=self.config.get("tmrg","rtl_dir")
            self.logger.debug("No input arguments specified. All files from rtl_dir (%s) will be parsed."%rtl_dir)
            self.args=[rtl_dir]

    def parse(self):
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

    def __elaborate(self,tokens):
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

    def triplicate(self,tokens):
        #self.properties=copy.deepcopy(self.current_module)
        #self.alwaysStmt.setParseAction( self.tmrAlways )
        #self.nbAssgnmt.setParseAction(self.tmrNbAssgnmt)

        #self.module.setParseAction(self.tmrModule)
        #self.verilogbnf.setParseAction(self.tmrTop)
        #self.outputDecl.setParseAction(self.tmrOutput)
        #self.inputDecl.setParseAction(self.tmrInput)
        #self.regDecl.setParseAction(self.tmrRegDecl)
        #self.continuousAssign.setParseAction(self.tmrContinuousAssign)
        #self.netDecl3.setParseAction(self.tmrNetDecl3)
        #self.netDecl1.setParseAction(self.tmrNetDecl1)
        #self.moduleInstantiation.setParseAction(self.tmrModuleInstantiation)
        #tmrt=self.verilogbnf.parseString(self.verilog)
        return self.__triplicate(tokens)

    def __triplicate_directive_default(self,tokens):
        return []

    def __triplicate_directive_triplicate(self,tokens):
        return []

    def __triplicate_directive_do_not_triplicate(self,tokens):
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
                for tt in t[0][3]:
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

    def tmrAlways(self,t):
        seq=self._isAlwaysSeq(t)
        result=ParseResults([])
        #check if the module needs triplication
        #print t,self.checkIfTmrNeeded(t)
        tmr=self.checkIfTmrNeeded(t)
        ids=self.getLeftRightHandSide(t)

        self.logger.debug("[Always block]")
        self.logger.debug("      Left :"+" ".join(sorted(ids["left"])))
        self.logger.debug("      Right:"+" ".join(sorted(ids["right"])))
        self.logger.debug("      TMR  :"+str(tmr))
        if not tmr:
            self._addVotersIfNeeded(ids["right"])
            return t

        for i in self.EXT:
            cpy=t.deepcopy()
            for name in self.toTMR:
#                print name
                if self.checkIfContains(cpy,name):
                    _to_name=name+i

#                     if seq:
#                         state_reg=""
#                         for regName,regNameNext in self.fsm_regs:
#                             if name==regNameNext:
#                                 state_reg=regName
# #                        print "state ",state_reg
#                         if state_reg!="":
#                             _to_name=state_reg+"Voted"+i
# #                    print "->",_to_name
#
                    self.replace(cpy,name,_to_name)
            result+=cpy
        #print "cpy",cpy,len(cpy)
        return result

    def tmrNbAssgnmt(self,t):
        # cpy=t.deepcopy()
        # #print cpy
        # #cpy[3]="dupa";
        # for v in self.toTMR:
        # #if self.checkIfContains(cpy,"rst"):
        #     print "shot!"
        #     self.replace(cpy,v,v+"A")
        print t
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

    def hasAnythingToTMR(self,tokens):
        toTMR=0
        for varToTMR in self.toTMR:
            if self.checkIfContains(tokens,varToTMR):
                toTMR=1
                break
        return toTMR

    def _addVotersIfNeeded(self,right):
            for rid in right:
                if self.current_module["nets"][rid]["tmr"]:

                    group=""
                    if group in self.voters and rid in self.voters[group]:
                        continue
                    self.logger.debug("      voter needed for signal %s"%rid)

                    voterInstName="%sVoter"%(rid)
                    name_voted="%s"%(rid)
                    netErrorName="%sTmrError"%(rid)
                    a=rid+self.EXT[0]
                    b=rid+self.EXT[1]
                    c=rid+self.EXT[2]
                    self._addVoter(inst=voterInstName,
                                     inA=a,
                                     inB=b,
                                     inC=c,
                                     out=name_voted,
                                     tmrError=netErrorName,
                                     range=self.current_module["nets"][rid]["range"],
                                     len=self.current_module["nets"][rid]["len"],
                                     group=group)

    # right - list of IDs
    def _addFanoutIfNeeded(self,right):
            for rid in right:
                #if not rid in self.toTMR:
                if not rid in self.current_module["nets"]:
                    self.logger.warning("Net %s unknown in addFanout!"%rid)
                    continue
                if not self.current_module["nets"][rid]["tmr"]:

                    group=""
                    if group in self.fanout and rid in self.fanout[group]:
                        continue
                    self.logger.debug("      fanout needed for signal %s"%rid)

                    inst=rid+"Fanout"
                    _in=rid
                    outA=rid+self.EXT[0]
                    outB=rid+self.EXT[1]
                    outC=rid+self.EXT[2]
                    range=self.current_module["nets"][rid]["range"]
                    len=self.current_module["nets"][rid]["len"]
                    self._addFanout(inst,_in,outA,outB,outC,range=range,len=len)

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



    def __triplicate_continuousassign(self,tokens):
        #check if the module needs triplication
        tmr=self.checkIfTmrNeeded(tokens)
        ids=self.getLeftRightHandSide(tokens)

        self.logger.debug("[Continuous Assign block]")
        self.logger.debug("      Left :"+" ".join(sorted(ids["left"])))
        self.logger.debug("      Right:"+" ".join(sorted(ids["right"])))
        self.logger.debug("      TMR  :"+str(tmr))

        if not tmr:
            self._addVotersIfNeeded(ids["right"])
            return tokens

        self._addFanoutIfNeeded(ids["right"])

        result=[]
        for i in self.EXT:
            cpy=tokens.deepcopy()
            self._appendToAllIds(cpy,post=i)
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

    def _addFanout(self,inst,_in,outA,outB,outC,range="",len="1"):
        if not inst in self.fanout:
            self.logger.debug("Adding fanout %s"%inst)
            self.logger.debug("    %s -> %s %s %s "%(_in,outA,outB,outC))
            self.fanout[inst]={"in":_in,
                               "outA":outA,
                               "outB":outB,
                               "outC":outC,
                               "range":range,
                               "len":len}
#        else:
#            self.logger.error("Unable to add fanout %s (name already exists)"%inst)
#            self.logger.debug("    %s -> %s %s %s "%(_in,outA,outB,outC))

    def _addVoter(self,inst,inA,inB,inC,out,tmrError,range="",len="1",group=""):
        if not group in self.voters:
            self.voters[group]={}
            self.logger.info("Creating TMR error group %s"%group)
        if not inst in self.voters[group]:
            self.logger.debug("Adding voter %s"%inst)
            self.logger.debug("    %s %s %s -> %s & %s"%(inA,inB,inC,out,tmrError))
            self.voters[group][inst]={"inA":inA,
                               "inB":inB,
                               "inC":inC,
                               "out":out,
                               "err":tmrError,
                               "range":range,
                               "len":len,
                               "group":group}
#        else:
#            self.logger.error("Unable to add volter %s (name already exists)"%inst)
#            self.logger.error("    %s %s %s -> %s & %s"%(inA,inB,inC,out,tmrError))


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
        vote=False

        #left=tokens[0][4][0][0][0]
        left=tokens[4][0][0][0]

        right=tokens[4][0][2][0][0]

        # FIX ME !!!!!!!!!! quick and dirty !!!!!!
        if left.find("TmrError")>=0 or left[-1]=="A" or left[-1]=="B" or left[-1]=="C":
            self.logger.info("Removing declaration of %s"%(left))
            return ParseResults([],name=tokens.getName())

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
                  self._addVoter(inst=voterInstName,
                                 inA=a,
                                 inB=b,
                                 inC=c,
                                 out=name_voted,
                                 tmrError=netErrorName,
                                 range=self.current_module["nets"][right]["range"],
                                 len=self.current_module["nets"][right]["len"],
                                 group=ext)

#                    atrs="" #temproray FIXME
#                    rangeLen=1 #temproray FIXME
#                     name_voted="%s%s"%(left,ext)
#                     comment=ParseResults(["cadence set_dont_touch %s"%name_voted],name="lineComment")
#                     newtokens.insert(0,comment)
#                     voterInstName="%sVoter%s"%(right,ext)
#
#                     newtokens.insert(1,self.netDecl1.parseString("wire %s %s;"%(atrs,name_voted))[0])
#                     newtokens.insert(2,self.netDecl1.parseString("wire %s;"%(netErrorName))[0])

#                    width=""
#                    if rangeLen>1:
#                        width+="#(.WIDTH(%d)) "%rangeLen
#                    newtokens.append(self.moduleInstantiation.parseString("majorityVoter %s%s (.inA(%s), .inB(%s), .inC(%s), .out(%s), .tmrErr(%s));"%
#                                                                     (width,voterInstName,a,b,c,name_voted,netErrorName) )[0]);

              tokens=newtokens

        else:
            tokens[4]=tmr_reg_list(tokens[4])

#        print tokens
        return tokens

    def __triplicate_NetDecl1(self,tokens):
        tokens[3]=self._tmr_list(tokens[3])
        return tokens

    def tmrRegDecl(self,tokens):
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


#        print tokens
        tokens[0][3]=tmr_reg_list(tokens[0][3])

#        print tokens
        return tokens
    def _addTmrErrorWire(self,post,netName):
        if not post in self.tmrErr:
            self.tmrErr[post]=set()
        self.tmrErr[post].add(netName)

    def tmrModuleInstantiation(self,tokens):
        try:
            moduleName=tokens[0][0]
            if moduleName in ("majorityVoter","fanout"): return

            #print moduleName
            if moduleName in ("powerOnReset","memoryAddrDec"):# triplicate module
                newIns=ParseResults([],name=tokens.getName())
                for inst in tokens:
                    name=inst[2][0][0][0]
                    for post in self.EXT:
#                        =inst[2][0][0][0]+post
#                        print inst
                        instCpy=inst.deepcopy()
                        instCpy[2][0][0][0]=name+post
                        self.replaceAll(instCpy[2],post,dot=0)
                        newIns.append(instCpy)
                tokens=newIns
            else: #triplicate IO
                newModuleName=moduleName+"TMR"
                tokens[0][0]=newModuleName
                self.logger.debug("ModuleInstantiation %s -> %s"%(moduleName,newModuleName))

                tokensIns=ParseResults([],name=tokens[0][2].getName())
                for instance in tokens[0][2]:
                        iname=instance[0][0]
                        instance2=instance.deepcopy()
                        newPorts=ParseResults([],name=instance2[1].getName())
                        for port in instance2[1]:
                            for post in self.EXT:
                                portCpy=port.deepcopy()
                                newPorts.append(self.replaceAll(portCpy,post))
                        if 1:
                            for post in self.EXT:
                                netName="%stmrError%s"%(iname,post)
                                tmrErrOut=self.modulePortConnection.parseString(".tmrError%s(%s)"%(post,netName))[0]
                                self._addTmrErrorWire(post,netName)
                                newPorts.append(tmrErrOut)

                        instance2[1]=newPorts
                        tokensIns.append(instance2)
                tokens[0][2]=tokensIns
            return tokens
        except:
            self.exc()

    def exc(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.logger.error("")
        self.logger.error("TMR exception:")
        for l in traceback.format_tb(exc_traceback):
            for ll in l.split("\n"):
              self.logger.error(ll)

    def __triplicate_module(self,tokens):
        try:
            header=tokens[0]
            moduleName=header[1]
            self.current_module=self.modules[moduleName]
            header[1]=str(moduleName)+"TMR"
            self.logger.debug("Module %s -> %s"%(moduleName,header[1]))

            moduleBody=tokens[1]
            moduleBody=self.__triplicate(moduleBody)
            tokens[1]=moduleBody

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
                if self.current_module["nets"]["tmrError"]:
                    groups = set(self.voters.keys()) | set(self.tmrErr.keys())
                    for group in sorted(groups):
                        newport="tmrError%s"%group
                        newports.append( newport )
                        self.logger.debug("Port %s"%(newport))
                header[2]=newports

            groups = set(self.voters.keys()) | set(self.tmrErr.keys())
            for group in sorted(groups):
                errSignals=set()

#                comment=ParseResults(["TMR group %s"%group],name="lineComment")
#                body.append(comment)
                if group in self.voters:
                  for voter in self.voters[group]:
                    inst=voter
                    voter=self.voters[group][voter]
                    self.logger.info("Instializaing voter %s"%inst)
                    _range=voter["range"]

                    _len=voter["len"]
                    _out=voter["out"]
                    _err=voter["err"]
                    _a=voter["inA"]
                    _b=voter["inB"]
                    _c=voter["inC"]
    #                     comment=ParseResults(["cadence set_dont_touch %s"%name_voted],name="lineComment")
    #                   newtokens.insert(0,comment)
    #                   voterInstName="%sVoter%s"%(right,ext)

                    moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s %s;"%(_range,_out))[0])
                    moduleBody.insert(0,self.vp.netDecl1.parseString("wire %s;"%(_err))[0])

                    width=""
                    if _len!="1":
                        width+="#(.WIDTH(%s)) "%_len
                    moduleBody.append(self.vp.moduleInstantiation.parseString("majorityVoter %s%s (.inA(%s), .inB(%s), .inC(%s), .out(%s), .tmrErr(%s));"%
                                                                       (width,inst,_a,_b,_c,_out,_err) )[0]);
                    errSignals.add(_err)



                moduleBody.insert(0,self.vp.netDecl1.parseString("wire tmrError%s;"%group)[0])
                #after all voters are added, we can create or them all
                if self.current_module["nets"]["tmrError"]:
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
                moduleBody.append(self.vp.continuousAssign.parseString(asgnStr)[0])



            for fanout in self.fanout:
                    inst=fanout
                    fanout=self.fanout[inst]
    #                print voter
                    self.logger.info("Instializaing voter %s"%inst)
                    _range=fanout["range"]
                    _len=fanout["len"]
                    _in=fanout["in"]
                    _a=fanout["outA"]
                    _b=fanout["outB"]
                    _c=fanout["outC"]
    #                     comment=ParseResults(["cadence set_dont_touch %s"%name_voted],name="lineComment")
    #                   newtokens.insert(0,comment)
    #                   voterInstName="%sVoter%s"%(right,ext)

#                    body.insert(0,self.netDecl1.parseString("wire %s %s;"%(_range,_out))[0])
#                    body.insert(0,self.netDecl1.parseString("wire %s;"%(_err))[0])

                    width=""
                    if _len!="1":
                        width+="#(.WIDTH(%s)) "%_len
                    moduleBody.append(self.vp.moduleInstantiation.parseString("fanout %s%s (.in(%s), .outA(%s), .outB(%s), .outC(%s));"%
                                                                       (width,inst,_in,_a,_b,_c) )[0]);

            return tokens
        except:
            self.exc()


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
            rangeLen="%s - %s + 1"%(self.formater.format(left), self.formater.format(right))
            try:
                rangeInt=eval(rangeLen)
                rangeLen="%d"%rangeInt
            except:
                pass
            return rangeLen

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
            self.current_module["instances"][identifier]={ "instance":instance,"range":_range, "len":_len}
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
 #               self.nets[name]={"atributes":_atrs,"range":_range, "len":_len ,"tmr":True}
#                if _len!="1":
#                    details="(range:%s len:%s)"%(_range,_len)
#                else:
#                    details=""
#                self.debugInModule("gotNet: %s %s" % (name,details), type="nets")
                if not name in  self.current_module["nets"]:
                     self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len , 'type':'wire'}


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
                tab.add_row([k,range, tmr])
            tab.padding_width = 1 # One space between column edges and contents (default)
            for l in str(tab).split("\n"):
                self.logger.info(l)

        printDict(module["nets"],    "Nets")
        printDict(module["io"],      "IO")
        printDict(module["instances"], "Instantiations")

    def elaborate(self):
        self.modules={}
        # elaborate all modules
        for fname in sorted(self.files):
            self.logger.info("")
            self.logger.info("Elaborating %s"%(fname))
            tokens=self.files[fname]
            for module in tokens:
                moduleHdr=module[0]
                moduleName=moduleHdr[1]
                modulePorts=moduleHdr[2]
                for port in modulePorts:
                    pass
                    #print port
                self.logger.info("")
                self.logger.info("Module %s:%s"%(fname,moduleName))
                self.current_module={"instances":{},"nets":{},"name":moduleName,"io":{},"constraints":{}}
                for moduleItem in module[1]:
                    self.__elaborate(moduleItem)
                self.modules[moduleName]=copy.deepcopy(self.current_module)
        # display summary
        if len(self.modules)>1:
            self.logger.info("")
            self.logger.info("Modules found %d"%len(self.modules))
            for module in self.modules:
                self.logger.info(" - %s"%module)
        #apply constrains
        self.logger.info("")
        self.logger.info("Applying constrains")
        for module in sorted(self.modules):
            self.logger.info("Module %s"%module)

            self.modules[module]["nets"]["tmrError"]={"range":"",len:"1","tmr":True}
            for net in self.modules[module]["nets"]:
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
                # net specific from configuration
                if self.config.has_section(module) and self.config.has_option(module,net):
                    conf=self.config.get(module,net)
                    if conf.lower()=="triplicate":
                        tmr=True
                    else:
                        tmr=False
                    s+=" -> config:%s"%(str(tmr))
                # net specific from source code
                if net in self.modules[module]["constraints"]:
                    tmr=self.modules[module]["constraints"][net]
                    s+=" -> src:%s"%(str(tmr))
                # net specific from command line
                if module in self.cmdLineConstrains and net in self.cmdLineConstrains[module]:
                    tmr=self.cmdLineConstrains[module][net]
                    s+=" -> cmd:%s"%(str(tmr))

                self.logger.info(" | net %s : %s (%s)"%(net,str(tmr),s))
                self.modules[module]["nets"][net]["tmr"]=tmr

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


    def tmr(self):
        tmrSuffix="TMR"
        spaces=2
        showdiff=True

        self.logger.info("")
        self.logger.info("Triplciation starts here")
        for fname in sorted(self.files):
            file,ext=os.path.splitext(os.path.basename(fname))
            self.logger.info("")
            self.logger.info("Triplicating file %s"%(fname))
            tokens=self.files[fname]
            tmrTokens=ParseResults([],name=tokens.getName())
            for module in tokens:
                tmrModule=self.triplicate(module)
                tmrTokens.append(tmrModule)
            fout=os.path.join(self.config.get("tmrg","tmr_dir"), file+tmrSuffix+ext)

            if os.path.exists(fout):
                    foutnew=fout+'.new'
                    f=open(foutnew,"w")
                    f.write(self.vf.format(tmrTokens).replace("\t"," "*self.config.getint("tmrg","spaces")))
                    f.close()
                    if not filecmp.cmp(fout,foutnew):
                        self.logger.warning("File '%s' exists. Saving output to '%s'"%(fout,foutnew))
                        if showdiff:
                            diffFiles(fout,foutnew)
                    else:
                        self.logger.info("File '%s' exists. Its content is up to date."%fout)
                        os.remove(foutnew)
            else:
                    self.logger.info("Saving output to '%s'"%(fout))
                    f=open(fout,"w")
                    f.write(self.vf.format(tmrTokens).replace("\t"," "*self.config.getint("tmrg","spaces")))
                    f.close()

########################################################################################################################




def readLinesFromFile(fname):
    f=open(fname,"r")
    lines=f.readlines()
    f.close()
    return lines

def diffFiles(fname1,fname2):
    path=os.path.realpath(__file__)
    dir=os.path.dirname(path)
    icdiff=os.path.join(dir,'icdiff')
    os.system("%s %s %s"%(icdiff,fname1,fname2))

def main():
    parser = OptionParser(version="%prog 1.0", usage="%prog [options] fileName")
#    parser.add_option("", "--input-file",         dest="inputFile",   help="Input file name (*.v)", metavar="FILE")
#    parser.add_option("", "--output-file",        dest="outputFile",  help="Output file name (*.v)", metavar="FILE")
#    parser.add_option("-r", "--recursive",       action="store_true", dest="rec", default=True, help="Recurive.")
    actionGroup = OptionGroup(parser, "Actions" )
    actionGroup.add_option("-p", "--parse-only",        action="store_true", dest="parse",     default=False, help="Parse")
    actionGroup.add_option("-e", "--elaborate",         action="store_true", dest="elaborate", default=False, help="Elaborate")
    actionGroup.add_option("-t", "--triplicate",        action="store_true", dest="tmr",       default=False, help="Triplicate.")
    parser.add_option_group(actionGroup)
    parser.add_option("-f", "--format",            dest="format",       action="store_true",default=False, help="Parse")
    parser.add_option("-i", "--info",              dest="info",         action="store_true",   default=False, help="Info")
    parser.add_option("-q", "--trace",             dest="trace",        action="store_true",   default=False, help="Trace formating")
    parser.add_option("",   "--single2tmr",        dest="s2t",          action="store_true",   default=False, help="Single ended to TMR")
    parser.add_option("-d", "--do-not-triplicate", dest="dnt",          action="append"  ,type="str")
    parser.add_option("",   "--spaces",            dest="spaces",       default=2, type=int )
    parser.add_option("",   "--rtl-dir",           dest="rtl_dir",      action="store", default="")
    parser.add_option("",   "--tmr-dir",           dest="tmr_dir",      action="store", default="")
    parser.add_option("",    "--tmr-suffix",       dest="tmr_suffix",   action="store", default="")
    parser.add_option("-v",  "--verbose",          dest="verbose",      action="count",   default=0, help="More verbose output")
    parser.add_option("",    "--diff",             dest="showdiff",     action="store_true",  default=False, help="Show diff")
    parser.add_option("-c",  "--config",           dest="config",       action="append",   default=[], help="Load config file")
    parser.add_option("-w",  "--constrain",        dest="constrain",    action="append",   default=[], help="Load config file")


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

        tmrg.parse()

        if options.parse:
            return
        if options.elaborate or options.tmr:
            tmrg.elaborate()


        if options.tmr:
            tmrg.tmr()

        # elif options.s2t:
        #     tmrtokens=vp.single2tmr()
        #     vf=VerilogFormater()
        #     vf.setTrace(options.trace)
        #     print vf.format(tmrtokens).replace("\t"," "*options.spaces)

    except ValueError:
        raise
#        G.write('simple.dot')
#        G.layout() # layout with default (neato)
#        G.draw('simple.png')

if __name__=="__main__":
    main()

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
from verilogFormater import VerilogFormater

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


class TMR(VerilogParser):
    def __init__(self):
        VerilogParser.__init__(self)
        self.EXT=('A','B','C')
        self.voters={}
        self.fanout={}
        self.tmrlogger = logging.getLogger('TMR')

    def _triplicate(self,tokens):
#        print "t",type(tokens),tokens
        if isinstance(tokens, ParseResults):
            name=str(tokens.getName()).lower()
            if len(tokens)==0: return tokens
#            res=ParseResults(None)
            for tok in tokens:
                self._triplicate(tok)
#                res+=tok
#            returtokens
        else:
            #we have a string!
            if tokens=='in1':
                tokens="dupa"
                self.logger.error("Problem in _triplicate")
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
#            print name, len(t), t
            if len(t)==0: return res
            if name in ("assgnmt", "nbassgnmt"):
                left_id=t[0][0]
                res["left"].add(left_id)
                #print   _extractID(t[2])
                res["right"].update( _extractID(t[2]))
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

        for i in res["left"]:
            if i in self.toTMR:
                leftTMR=True
            else:
                leftNoTMR=True
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
            for rid in ids["right"]:
                if rid in self.toTMR:
                    group=""
                    if group in self.voters and rid in self.voters[group]:
                        continue
                    self.logger.debug("      voter needed for sigbak %s"%rid)

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
                                     range=self.properties["nets"][rid]["range"],
                                     len=self.properties["nets"][rid]["len"],
                                     group=group)
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
        return t

    def _tmr_list(self,tokens):
        newtokens=ParseResults([],name=tokens.getName())
        for element in tokens:
            if element in self.toTMR:
                for post in self.EXT:
                    newtokens.append(element+post)
            else:
                newtokens.append(element)
        return newtokens

    def tmrOutput(self,tokens):
        self.tmrlogger.debug("Output %s"%str(tokens[0][2]))
        tokens[0][2]=self._tmr_list(tokens[0][2])
        return tokens

    def tmrInput(self,tokens):
        self.tmrlogger.debug("input %s"%str(tokens[0][2]))
        tokens[0][2]=self._tmr_list(tokens[0][2])
        return tokens

    def hasAnythingToTMR(self,tokens):
        toTMR=0
        for varToTMR in self.toTMR:
            if self.checkIfContains(tokens,varToTMR):
                toTMR=1
                break
        return toTMR


    def tmrContinuousAssign(self,tokens):
        dList=tokens[0][2]
        newtokens=ParseResults([],name=dList.getName())
        for ca in dList:
            leftHand=ca[0]
            if self.hasAnythingToTMR(leftHand):
               for post in self.EXT:
#                   print ca
                   ca2=ca.deepcopy()
                   for var in self.toTMR:
#                       print var
                       self.replace(ca2,var,var+post)
                   newtokens.append(ca2)
            else:
                newtokens.append(ca)
        tokens[0][2]=newtokens
        #print "TMR",delimitedList
        return tokens

    def _addFanout(self,inst,_in,outA,outB,outC,out,range="",len="1"):
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


    def tmrNetDecl3(self,tokens):
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
        left=tokens[0][4][0][0][0]
        right=tokens[0][4][0][2][0][0]

        # FIX ME !!!!!!!!!! quick and dirty !!!!!!
        if left.find("TmrError")>=0 or left[-1]=="A" or left[-1]=="B" or left[-1]=="C":
            self.logger.info("Removing declaration of %s"%(left))
#            print tokens
            return ParseResults([],name=tokens.getName())

#        print left,right, self.voting_nets
        if len(self.voting_nets):
#            self.logger.info("!!!!!!! %s %s"%(str(self.avoting), str(self.avoting_nets)))

            if (right, left) in self.voting_nets:
                vote=True

        if vote:
              self.logger.info("TMR voting %s -> %s"%(right,left))
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
                                 range=self.properties["nets"][right]["range"],
                                 len=self.properties["nets"][right]["len"],
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
            tokens[0][4]=tmr_reg_list(tokens[0][4])

#        print tokens
        return tokens

    def tmrNetDecl1(self,tokens):
        tokens[0][3]=self._tmr_list(tokens[0][3])
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
#        print tokens
        tokens[0][2]=tmr_reg_list(tokens[0][2])
#        print tokens
        return tokens

    def tmrModuleInstantiation(self,tokens):
        try:
            moduleName=tokens[0][0]
            if moduleName in ("majorityVoter"): return

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
                self.tmrlogger.debug("ModuleInstantiation %s -> %s"%(moduleName,newModuleName))

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
                                self.tmrErr[post].append(netName)
                                newPorts.append(tmrErrOut)

                        instance2[1]=newPorts
                        tokensIns.append(instance2)
                tokens[0][2]=tokensIns
            return tokens
        except:
            self.exc()

    def exc(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.tmrlogger.error("")
        self.tmrlogger.error("TMR exception:")
        for l in traceback.format_tb(exc_traceback):
            for ll in l.split("\n"):
              self.tmrlogger.error(ll)

    def tmrModule(self,tokens):
        try:
            header=tokens[0][0]
            header[1][0]=str(header[1][0])+"TMR"
            self.tmrlogger.debug("Module")
            if len(header)>2:
                ports=header[2]
    #            print ports.getName()
                newports=ParseResults([],name=ports.getName())
                for port in ports:
                    triplicated=False
                    for varToTMR in self.toTMR:
                        if self.checkIfContains(port,varToTMR):
                            for ext in self.EXT:
                                cpy=port.deepcopy()
                                self.replace(cpy,varToTMR,varToTMR+ext)
                                newports.append(cpy)
                            triplicated=True
                            break
                    if not triplicated:
                        newports.append(port)
                if self.constraints["tmr_error"]:
                    for group in self.voters:
                        newports.append("tmrError%s"%group )
                header[2]=newports
            body=tokens[0][1]

            if 0 and self.fsm:
                for r1,r2 in self.fsm_regs:
                    if r2 in self.toTMR:
                        a=r2+self.EXT[0]
                        b=r2+self.EXT[1]
                        c=r2+self.EXT[2]

                        atrs=self.registers[r1]["atributes"]

                        rangeLen=1
                        if len(atrs.strip())>0:
    #                        print atrs
                            prange=self.range.parseString(atrs)
                            rangeLen=int(prange[1])-int(prange[3] ) +1

                        for ext in self.EXT:
                            name_voted="%sVoted%s"%(r1,ext)
                            comment=ParseResults(["cadance set_dont_touch %s"%name_voted],name="lineComment")
                            body.insert(0,comment)
                            voterInstName="%sVoter%s"%(r1,ext)
                            netErrorName="%sTmrError%s"%(r1,ext)
                            body.insert(1,self.netDecl1.parseString("wire %s %s;"%(atrs,name_voted))[0])
                            body.insert(2,self.netDecl1.parseString("wire %s;"%(netErrorName))[0])

                            width=""
                            if rangeLen>1:
                                width+="#(.WIDTH(%d)) "%rangeLen
                            body.append(self.moduleInstantiation.parseString("majorityVoter %s%s (.inA(%s), .inB(%s), .inC(%s), .out(%s), .tmrErr(%s));"%
                                                                             (width,voterInstName,a,b,c,name_voted,netErrorName) )[0]);

                            self.tmrErr[ext].append(netErrorName)


            for group in sorted(self.voters):
                errSignals=[]
                for voter in self.voters[group]:
                    inst=voter
                    voter=self.voters[group][voter]
    #                print voter
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

                    body.insert(0,self.netDecl1.parseString("wire %s %s;"%(_range,_out))[0])
                    body.insert(0,self.netDecl1.parseString("wire %s;"%(_err))[0])

                    width=""
                    if _len!="1":
                        width+="#(.WIDTH(%s)) "%_len
                    body.append(self.moduleInstantiation.parseString("majorityVoter %s%s (.inA(%s), .inB(%s), .inC(%s), .out(%s), .tmrErr(%s));"%
                                                                       (width,inst,_a,_b,_c,_out,_err) )[0]);
                    errSignals.append(_err)

                body.insert(0,self.netDecl1.parseString("wire tmrError%s;"%group)[0])
                #after all voters are added, we can create or them all
                if self.constraints["tmr_error"]:
                    body.insert(0,self.outputDecl.parseString("output tmrError%s;"%group)[0])

                sep=""
                asgnStr="assign tmrError%s="%group
                if len(errSignals):
                    for signal in errSignals:
                        asgnStr+=sep+signal
                        sep="|"
                else:
                    asgnStr+="1'b0"
                asgnStr+=";"
                body.append(self.continuousAssign.parseString(asgnStr)[0])
            return tokens
        except:
            self.exc()


    def tmrTop(self,tokens):
        return tokens

    def triplicate(self):
        self.properties=self.current_module

        self.alwaysStmt.setParseAction( self.tmrAlways )
        self.nbAssgnmt.setParseAction(self.tmrNbAssgnmt)
        self.module.setParseAction(self.tmrModule)
        self.verilogbnf.setParseAction(self.tmrTop)
        self.outputDecl.setParseAction(self.tmrOutput)
        self.inputDecl.setParseAction(self.tmrInput)
        self.regDecl.setParseAction(self.tmrRegDecl)
        self.continuousAssign.setParseAction(self.tmrContinuousAssign)
        self.netDecl3.setParseAction(self.tmrNetDecl3)
        self.netDecl1.setParseAction(self.tmrNetDecl1)
        self.moduleInstantiation.setParseAction(self.tmrModuleInstantiation)
        tmrt=self.verilogbnf.parseString(self.verilog)
        return tmrt
########################################################################################################################

    def s2tOutput(self,tokens):
#        print tokens
        for name in tokens[0][2]:
            a=name+self.EXT[0]
            b=name+self.EXT[1]
            c=name+self.EXT[2]

            atrs=self.outputs[name]["atributes"]
            tokens.append(self.netDecl1.parseString("wire %s %s;"%(atrs,a))[0])
            tokens.append(self.netDecl1.parseString("wire %s %s;"%(atrs,b))[0])
            tokens.append(self.netDecl1.parseString("wire %s %s;"%(atrs,c))[0])

            voted=name
            voterInstName=name+"Voter"

            rangeLen=1

            width=""
            rangeLen=1
            if len(atrs.strip())>0:
                 #print atrs
                 prange=self.range.parseString(atrs)
                 rangeLen=int(prange[1])-int(prange[3] ) +1
            if rangeLen>1:
                width+="#(.WIDTH(%d)) "%rangeLen
            vstr="majorityVoter %s%s (.inA(%s), .inB(%s), .inC(%s), .out(%s));"%(width,voterInstName,a,b,c,voted)
            voter=self.moduleInstantiationCpy.parseString(vstr)[0]
            print vstr
            #print "x",xx
            tokens.append(voter)
        #tokens.append
        return tokens

    def s2tInput(self,tokens):
#        print tokens
        for name in tokens[0][2]:
            for ext in self.EXT:
                asgnStr="wire %s%s=%s;"%(name,ext,name)
                tokens.append(self.netDecl3.parseString(asgnStr)[0])

        return tokens

    def s2tModule(self,tokens):
        return tokens

    def single2tmr(self):

        self.outputDecl.setParseAction(self.s2tOutput)
        self.inputDecl.setParseAction(self.s2tInput)

        self.module.setParseAction(self.s2tModule)
        #self.moduleInstantiation.setParseAction(lambda: [])
        #self.netDecl3.setParseAction(lambda: [])
        #self.netDecl1.setParseAction(lambda: [])
        self.regDecl.setParseAction(lambda:[])

        tmrt=self.verilogbnf.parseString(self.verilog)
        return tmrt

def args2files(args):
    files=[]
    for name in args:
        if os.path.isfile(name):
            files.append(name)
        elif os.path.isdir(name):
            for fname in glob.glob("%s/*.v"%name):
                files.append(fname)
    return files


def main():
    parser = OptionParser(version="%prog 1.0", usage="%prog [options] fileName")
#    parser.add_option("", "--input-file",         dest="inputFile",   help="Input file name (*.v)", metavar="FILE")
#    parser.add_option("", "--output-file",        dest="outputFile",  help="Output file name (*.v)", metavar="FILE")
#    parser.add_option("-r", "--recursive",       action="store_true", dest="rec", default=True, help="Recurive.")
    parser.add_option("-t", "--triplicate",        action="store_true", dest="tmr", default=False, help="Triplicate.")
    parser.add_option("-p", "--parse",             action="store_true", dest="parse", default=True, help="Parse")
    parser.add_option("-f", "--format",            action="store_true", dest="format", default=False, help="Parse")
    parser.add_option("-i", "--info",              action="store_true", dest="info",  default=False, help="Info")
    parser.add_option("-q", "--trace",             action="store_true", dest="trace",  default=False, help="Trace formating")
    parser.add_option("",   "--single2tmr",        action="store_true", dest="s2t",  default=False, help="Single ended to TMR")
    parser.add_option("-d", "--do-not-triplicate", action="append",     dest="dnt",type="str")
    parser.add_option("","--spaces",               dest="spaces",       default=2, type=int )
    parser.add_option("","--rtl-dir",              dest="rtldir",       default="./rtl")
    parser.add_option("","--tmr-dir",              dest="tmrdir",       default="./tmr")
    parser.add_option("","--tmr-suffix",           dest="tmrSuffix",    default="TMR")
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
                vp=TMR()
                if options.parse or options.tmr or options.format:
                    tokens=vp.parseString(readFile(fname))

                vp.applyDntConstrains(options.dnt)

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

        if len(modules)>1:
            logging.info("Modules found %d"%len(modules))

        if options.tmr:
            logging.info("Triplciation starts here")
            vf=VerilogFormater()

            for module_name in modules:
                vp=modules[module_name]
                logging.info("Triplicating module '%s'"%module_name)
                tmrtokens=vp.triplicate()
                vf.setTrace(options.trace)
                fout=os.path.join(options.tmrdir,module_name+options.tmrSuffix+".v")
                if os.path.exists(fout):
                    foutnew=fout+'.new'
                    logging.warning("File '%s' exists. Saving output to '%s'"%(fout,foutnew))
                    fout=foutnew
                else:
                    logging.warning("Saving output to '%s'"%(fout))
                f=open(fout,"w")
                f.write(vf.format(tmrtokens).replace("\t"," "*options.spaces))
                f.close()

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

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


class TMR():
    def __init__(self):
        self.vp=VerilogParser()
        self.vf=VerilogFormater()
        self.EXT=('A','B','C')
        self.voters={}
        self.fanout={}
        self.tmrErr={}
        self.logger = logging.getLogger('TMR')
        self.files={}
        self.elaborator={}
        #scan class looking for formater functions
        for member in dir(self):
            if member.find("_TMR__elaborate_")==0:
                token=member[len("_TMR__elaborate_"):].lower()
                self.elaborator[token]=getattr(self,member)
                self.logger.debug("Found elaborator for %s"%token)
        self.trace=True

    def __elaborate(self,tokens):
        if isinstance(tokens, ParseResults):
            name=str(tokens.getName()).lower()
            if self.trace: self.logger.debug( "[%-20s] len:%2d  str:'%s' >"%(name,len(tokens),str(tokens)[:80]))
            if len(tokens)==0: return ""
            if name in self.elaborator:
                self.elaborator[name](tokens)
            else:
                self.logger.debug("No elaborator for %s"%name)


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
            if element in self.toTMR:
                for post in self.EXT:
                    newtokens.append(element+post)
            else:
                newtokens.append(element)
        return newtokens

    def tmrOutput(self,tokens):
        self.logger.debug("Output %s"%str(tokens[0][2]))
        tokens[0][2]=self._tmr_list(tokens[0][2])
        return tokens

    def tmrInput(self,tokens):
        self.logger.debug("input %s"%str(tokens[0][2]))
        tokens[0][2]=self._tmr_list(tokens[0][2])
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
                if rid in self.toTMR:
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
                                     range=self.properties["nets"][rid]["range"],
                                     len=self.properties["nets"][rid]["len"],
                                     group=group)

    # right - list of IDs
    def _addFanoutIfNeeded(self,right):
            for rid in right:
                if not rid in self.toTMR:
                    group=""
                    if group in self.fanout and rid in self.fanout[group]:
                        continue
                    self.logger.debug("      fanout needed for signal %s"%rid)

                    inst=rid+"Fanout"
                    _in=rid
                    outA=rid+self.EXT[0]
                    outB=rid+self.EXT[1]
                    outC=rid+self.EXT[2]
                    range=self.properties["nets"][rid]["range"]
                    len=self.properties["nets"][rid]["len"]
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



    def tmrContinuousAssign(self,tokens):


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

        result=ParseResults([])
        for i in self.EXT:
            cpy=tokens.deepcopy()
            self._appendToAllIds(cpy,post=i)
            result+=cpy
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
              self.logger.info("TMR voting %s -> %s (bits:%s)"%(right,left,self.properties["nets"][right]["len"]))
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

    def tmrModule(self,tokens):
        try:
            header=tokens[0][0]
            header[1][0]=str(header[1][0])+"TMR"
            self.logger.debug("Module")
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
                            comment=ParseResults(["cadence set_dont_touch %s"%name_voted],name="lineComment")
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

            groups = set(self.voters.keys()) | set(self.tmrErr.keys())
            for group in sorted(groups):
                errSignals=set()

#                comment=ParseResults(["TMR group %s"%group],name="lineComment")
#                body.append(comment)
                if group in self.voters:
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
                    errSignals.add(_err)



                body.insert(0,self.netDecl1.parseString("wire tmrError%s;"%group)[0])
                #after all voters are added, we can create or them all
                if self.constraints["tmr_error"]:
                    body.insert(0,self.outputDecl.parseString("output tmrError%s;"%group)[0])
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
                body.append(self.continuousAssign.parseString(asgnStr)[0])

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
                    body.append(self.moduleInstantiation.parseString("fanout %s%s (.in(%s), .outA(%s), .outB(%s), .outC(%s));"%
                                                                       (width,inst,_in,_a,_b,_c) )[0]);

            return tokens
        except:
            self.exc()


    def tmrTop(self,tokens):
        return tokens

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
                 #if not name in  self.current_module["nets"]:
                 #    self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len,"type":"wire"}
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
            print tab

        printDict(self.current_module["nets"],    "Nets")
        printDict(self.current_module["io"],      "IO")
        printDict(self.current_module["instances"], "Instantiations")
    def elaborate(self):
        self.modules={}
        for fname in sorted(self.files):
            self.logger.info("Elaborating %s"%(fname))
            tokens=self.files[fname]
            for module in tokens:
                moduleHdr=module[0]
                moduleName=moduleHdr[1]
                modulePorts=moduleHdr[2]
                for port in modulePorts:
                    pass
                    #print port
                self.logger.info("Module %s"%moduleName)
                self.current_module={"instances":{},"nets":{},"name":moduleName,"io":{}}
                for moduleItem in module[1]:
                    self.__elaborate(moduleItem)
                self.moduleSummary(self.current_module)
                self.modules[moduleName]=self.current_module
        if len(self.modules)>1:
            logging.info("Modules found %d"%len(self.modules))
            for module in self.modules:
                logging.info(" - %s"%module)

        pass

    def tmr(self):
        tmrSuffix="TMR"
        spaces=2
        showdiff=True
        logging.info("Triplciation starts here")
        for fname in sorted(self.files):
            file,ext=os.path.splitext(os.path.basename(fname))
            self.logger.info("Triplicating %s"%(fname))
            tokens=self.files[fname]
            for module in tokens:
                print ">",module
                tmrtokens=self.triplicate(module)

    #             vf.setTrace(options.trace)
            fout=os.path.join(self.tmrdir, file+tmrSuffix+ext)
            print fout
            if os.path.exists(fout):
                    foutnew=fout+'.new'
                    f=open(foutnew,"w")
                    f.write(self.vf.format(tmrtokens).replace("\t"," "*spaces))
                    f.close()
                    if not filecmp.cmp(fout,foutnew):
                        logging.warning("File '%s' exists. Saving output to '%s'"%(fout,foutnew))
                        if showdiff:
                            diffFiles(fout,foutnew)
            else:
                    logging.warning("Saving output to '%s'"%(fout))
                    f=open(fout,"w")
                    f.write(self.vf.format(tmrtokens).replace("\t"," "*options.spaces))
                    f.close()
    def setTmrDir(self,tmrdir):
        self.tmrdir=tmrdir
########################################################################################################################


def args2files(args):
    files=[]
    for name in args:
        if os.path.isfile(name):
            files.append(name)
        elif os.path.isdir(name):
            for fname in glob.glob("%s/*.v"%name):
                files.append(fname)
    return files

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
    parser.add_option("",   "--rtl-dir",           dest="rtldir",       default="./rtl")
    parser.add_option("",   "--tmr-dir",           dest="tmrdir",       default="./tmr")
    parser.add_option("",    "--tmr-suffix",       dest="tmrSuffix",    default="TMR")
    parser.add_option("-v",  "--verbose",          dest="verbose",      action="count",   default=0, help="More verbose output")
    parser.add_option("",    "--diff",             dest="showdiff",     action="store_true",  default=False, help="Show diff")
    parser.add_option("-c",  "--config",           dest="config",       action="append",   default=[], help="Load config file")
    parser.add_option("-w",  "--constrain",        dest="constrain",    action="append",   default=[], help="Load config file")


   # print config.get("tmrg","tmr_dir")
   # print config.get("tmrg","tmr_signals")
   # print config.items("module")
    #FORMAT = '%(message)s'
    logging.basicConfig(format='[%(name)s|%(levelname)s] %(message)s', level=logging.INFO)

    try:
        (options, args) = parser.parse_args()


        if options.verbose==0:
            logging.getLogger().setLevel(logging.WARNING)
        if options.verbose==1:
            logging.getLogger().setLevel(logging.INFO)
        elif options.verbose==2:
            logging.getLogger().setLevel(logging.DEBUG)


        config = ConfigParser.ConfigParser()
        config.read(['tmrg.cfg', os.path.expanduser('~/.tmrg.cfg')])

        logging.info
        print options.config

        if len(args)==0:
            args=[options.rtldir]

        tmrg=TMR()
        tmrg.setTmrDir(options.tmrdir)
        for fname in args2files(args):
            try:
                logging.info("Processing file %s"%fname)
                tmrg.addFile (fname)
#                vp.applyDntConstrains(options.dnt)
#                if options.format:
#                    vf=VerilogFormater()
#                    vf.setTrace(options.trace)
#                    print vf.format(tokens).replace("\t"," "*options.spaces)
#                modules[vp.module_name]=vp
            except ParseException, err:
                logging.error("")
                logging.error(err.line)
                logging.error( " "*(err.column-1) + "^")
                logging.error( err)
                for l in traceback.format_exc().split("\n"):
                    logging.error(l)
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

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

class VerilogFormater:
    formater={}
    def setTrace(self,t):
        self.trace=t
    def _format_Top(self,tokens,i=""):
        oStr="// file automaticly generated\n"
        for i in tokens:
            oStr+=self.format(i)
        return oStr
    def _format_lineComment(self,tokens,i=""):
        return i+"// %s\n"%tokens[0]

    def _format_Default(self,tokens,i=""):
        return "default (%s)\n"%(tokens.getName())

    def _format_Id(self,tokens,i=""):
        oStr=str(tokens[0])
        return oStr
    def _formatIo(self,tokens,i=""):
        oStr=""
        label=str(tokens[0])
        spec=self.format(tokens[1])
        if spec!="":spec+=" "
        ports=tokens[2]
        for port in ports:
            oStr+="%s %s%s;\n"%(label,spec,port)
        return oStr

    def _format_Input(self,tokens,i=""):
        return self._formatIo(tokens)

    def _format_InOut(self,tokens,i=""):
        return self._formatIo(tokens)

    def _format_Output(self,tokens,i=""):
        return self._formatIo(tokens)

    def _formatIoHdr(self,tokens,i=""):
        oStr=""
        label=str(tokens[0])
        spec=self.format(tokens[1])
        ports=tokens[2]
        for port in ports:
            oStr+="%s %s %s"%(label,spec,port)
        return oStr


    def _format_inputhdr(self,tokens,i=""):
        return self._formatIoHdr(tokens)
    def _format_outputhdr(self,tokens,i=""):
        return self._formatIoHdr(tokens)
    def _format_inouthdr(self,tokens,i=""):
        return self._formatIoHdr(tokens)

    def _format_RegDecl(self,tokens,i=""):
        oStr=""
        label=str(tokens[0])
        spec=self.format(tokens[1])
        if spec!="":spec+=" "
        ports=tokens[2]
        for port in ports:
            oStr+="%s %s%s;\n"%(label,spec,port[0])
        return oStr

    def _format_netDecl3(self,tokens,i=""):
        oStr=""
        label=str(tokens[0])
        drives=self.format(tokens[1])
        spec=self.format(tokens[2])
        delay=self.format(tokens[3])
        if drives!="":drives+=" "
        if spec!="":spec+=" "
        if delay!="":delay+=" "
        ports=tokens[4]
        for port in ports:
            port_str=self.format(port)
            oStr+="%s %s%s%s%s;\n"%(label,drives,spec,delay,port_str)
        return oStr

    def _format_netDecl1(self,tokens,i=""):
        oStr=""
       # print ">",tokens
        nettype=str(tokens[0])
        range=self.format(tokens[1])
        delay=self.format(tokens[2])
        if range!="":range+=" "
        if delay!="":delay+=" "
        ports=tokens[3]

        for port in ports:
            port_str=self.format(port)
            #print nettype,range,delay,port_str
            oStr+="%s %s%s%s;\n"%(nettype,range,delay,port_str)
        return oStr


    def _format_Range(self,tokens,i=""):
        #print "~~~~~~~~",tokens
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr

    def _format_Always(self,tokens,i=""):
        oStr="\n"+i
        eventCtrl=self.format(tokens[0])
        stmt=self.format(tokens[1],i+"\t")
        oStr+="always %s\n"%eventCtrl
        oStr+=i+"\t%s\n"%stmt
        return oStr

    def _format_subscrRef(self,tokens,i=""):
        if len(tokens)==0:
            return ""
        oStr="["
        sep=""
        for t in tokens:
            oStr+=sep+self.format(t,i)
            sep+=":"
        oStr+="]"
        return oStr

    def _format_subscrIndxRef(self,tokens,i=""):
        if len(tokens)==0:
            return ""
        oStr="["
        for t in tokens:
            oStr+=self.format(t,i)
        oStr+="]"
        return oStr
    def _format_subscrIdentifier(self,tokens,i=""):

        oStr=""
        for sid in tokens:
            oStr+=self.format(sid)
        return oStr

    def _format_BeginEnd(self,tokens,i=""):
        oStr="begin\n"
        for stmt in tokens:
            oStr+=i+"\t"+self.format(stmt,i+"\t")+"\n"
        oStr+=i+"end"
        return oStr
    def _format_taskEnable(self,tokens,i=""):
        oStr=""
        id=tokens[0]
        oStr="%s"%id
        if len(tokens[1]):
            oStr+="("
            sep=""
            for v in tokens[1]:
                oStr+=sep+self.format(v,i)
                sep=", "
            oStr+=")"
        oStr+=";"
        return oStr

    def _format_delayStm(self,tokens,i=""):
        oStr=""
        delay=self.format(tokens[0])
        stm=self.format(tokens[1])
        oStr+="%s %s"%(delay,stm)
        return oStr

    def _format_task(self,tokens,i=""):
#        print "task tokens",tokens
        tid=self.format(tokens[0])
        oStr="task %s;\n"%tid
        for tfDecl in tokens[1]:
            oStr+="\t"+self.format(tfDecl,i+"\t")
        stmt = tokens[2]
        oStr+="\t"+self.format(stmt,i+"\t")+"\n"
        oStr+="endtask\n"
        return oStr

    def _format_EventCtrl(self,tokens,i=""):
        oStr=""
#        print tokens
        for el in tokens[0]:
#            print el,self.format(el)
            oStr+=self.format(el)
        return oStr

    def _format_DelimitedList(self,tokens,i=""):
        oStr=""
        sep=""
#        print tokens
        for el in tokens:
            oStr+=sep+self.format(el)
            sep+=", "
        return oStr

    def _format_DelimitedOrList(self,tokens,i=""):
        oStr=""
        sep=""
        for el in tokens:
            oStr+=sep+self.format(el)
            sep=" or "
        return oStr

    def _format_EventTerm(self,tokens,i=""):
        oStr=""
        sep=""
        for el in tokens:
            oStr+=sep+self.format(el)
            sep=" "
        return oStr

    def _format_if(self,tokens,i=""):
        oStr=""
#        print tokens
        if len(tokens)==1:
            stm=tokens[0]
        else:
            stm=tokens
        cond=stm[1]
        ifAction=stm[2]
        oStr+="if %s\n"%self.format(cond)
        oStr+=i+"\t%s"%self.format(ifAction,i+"\t")
        return oStr

    def _format_concat(self,tokens,i=""):
        oStr="{"
        sep=""
        for t in tokens:
            oStr+=sep+self.format(t)
            sep=","
        oStr+="}"
#        print oStr
        return oStr

    def _format_caseItem(self,tokens,i=""):
        #print "caseitem",tokens
        expr=self.format(tokens[0])
        stm=self.format(tokens[2],i+"\t")
        if stm.find("\n")>=0:
            stm="\n%s%s"%(i+"\t",stm)
        return "%s : %s"%(expr,stm)

    def _format_case(self,tokens,i=""):
#        print tokens
        label=tokens[0]
        cond=self.format(tokens[1])
        oStr="%s (%s)\n"%(label,cond)
        for t in tokens[2]:
            oStr+=i+"\t"+self.format(t,i+"\t")+"\n"
        oStr+=i+tokens[3]
        return oStr


    def _format_funcCall(self,tokens,i=""):
        identifier = tokens[0]
        oStr="%s("%identifier
        for expr in tokens[2]:
            oStr+=self.format(expr,i=i)
        oStr+=")"
        return oStr


    def _format_IfElse(self,tokens,i=""):
        oStr=""
#        print tokens
        if len(tokens)==1:
            stm=tokens[0]
        else:
            stm=tokens
        cond=stm[1]
        ifAction=stm[2]
        elseAction=stm[4]
        oStr+="if %s\n"%self.format(cond)
        oStr+=i+"\t%s\n"%self.format(ifAction,i+"\t")
        oStr+=i+"else\n"
        oStr+=i+"\t%s"%self.format(elseAction,i+"\t")
# #             prettyPrint(f,ifact, ident+1)
# #             f.write(IS*ident+"else\n")
#             prettyPrint(f,elseact, ident+1)
        return oStr

    def _format_parameterValueAssignment(self,tokens,i=""):
        if len(tokens[0])>1:
            oStr="#(\n"+i
            sep=""
            for param in tokens[0]:
                oStr+=sep+self.format(param)
                sep=",\n"+i
            oStr+="\n)\n"
            return oStr
        else:
            oStr="#("
            oStr+=self.format(tokens[0][0])
            oStr+=") "
            return oStr

    def _format_primary(self,tokens,i=""):
        oStr=""
        for t in tokens:
            oStr+=self.format(t,i="")
        return oStr
    def _format_moduleInstance(self,tokens,i=""):
#        moduleInstance = Group( Group ( identifier + Group(Optional(range)) ) + moduleArgs ).setResultsName("moduleInstance")
        id=self.format(tokens[0][0])
        range=self.format(tokens[0][1])
        args=self.format(tokens[1])
        return "%s %s%s"%(id,range,args);

    def _format_moduleArgs(self,tokens,i=""):
        i+="\t"
        oStr="(\n"+i
        sep=""
        for t in tokens:
            oStr+=sep+self.format(t,i)
            sep=",\n"+i
        oStr+="\n)"
        return oStr

    def _format_modulePortConnection(self,tokens,i=""):

        return self.format(tokens[0],i)

    def _format_moduleInstantiation(self,tokens,i=""):
        ostr=""
        identifier=self.format(tokens[0])
        if len(tokens)>2:
          parameterValueAssignment = self.format(tokens[1],i=i+"\t")
          modulesList=tokens[2]
        else:
          parameterValueAssignment=""
          modulesList=tokens[1]

        for modIns in modulesList:

              modInsStr=self.format(modIns)
              ostr+="\n%s %s%s;\n"%(identifier,parameterValueAssignment,modInsStr);

        return ostr

    def _format_Module(self,tokens,i=""):
        header=tokens[0]
        modname=header[1][0]
        oStr="module %s"%modname
        sep=""
        if len(header)>2:
            ports=header[2]
            oStr+="(\n"
            for port in ports:
                oStr+=sep+"\t"+self.format(port)
                sep=",\n"
            oStr+="\n)"
        oStr+=";\n"

        moduleBody=tokens[1]
        for moduleItem in moduleBody:
            oStr+=self.format(moduleItem)
        oStr+="endmodule\n"
        return oStr


    def _format_NbAssgnmt(self,tokens,i=""):
        #tokens=tokens[0]
        lval=self.format(tokens[0])
        delay=self.format(tokens[2])
        if delay!="": delay+=" "
        expr=self.format(tokens[3])
        oStr="%s <= %s%s;"%(lval,delay,expr)

        return oStr

    def _format_Expr(self,tokens,i=""):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr

    def _format_Delay(self,tokens,i=""):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr
    
    def _format_Condition(self,tokens,i=""):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr

    def _format_paramAssgnmt(self,tokens,i=""):
        id=self.format(tokens[0])
        val=self.format(tokens[2])
        oStr="%s=%s"%(id,val)
        return oStr.rstrip()

    def _format_paramdecl(self,tokens,i=""):
#        print tokens
        oStr=""
        range=self.format(tokens[1])
#        print tokens[2]
        for p in tokens[2]:
            oStr+=tokens[0]+" "
            if range:
                oStr+="%s "%range
            oStr+=self.format(p)+";\n"
#            print p
        return oStr

    def _format_localparamdecl(self,tokens,i=""):
        return self._format_paramdecl(tokens)

    def _format_delayOrEventControl(self,tokens,i=""):
        oStr=""
#        print tokens
        return oStr

    def _format_integerDecl(self,tokens,i=""):
        oStr=""
        label=tokens[0]
        for var in tokens[1]:
            oStr+="%s %s;\n"%(label,self.format(var))
        return oStr

    def _format_assgnmtStm(self,tokens,i=""):
        oStr=self.format(tokens[0])+";"
        return oStr

    def _format_assgnmt(self,tokens,i=""):
        oStr=""
#        print "!!!!!!!",len(tokens),tokens
        lvalue=self.format(tokens[0])
        delayOrEventControl=self.format(tokens[1])+" "
        expr=self.format(tokens[2])

        oStr="%s = %s%s"%(lvalue,delayOrEventControl,expr)
        return oStr
    def _format_driveStrength(self,tokens,i=""):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr

    def _format_continuousAssign(self,tokens,i=""):
        oStr=""
        driveStrength = self.format(tokens[0])
        if driveStrength:driveStrength+=" "
        delay = self.format(tokens[1])
        if delay:delay+=" "
        for asg in tokens[2]:
            asg_str=self.format(asg)
            oStr+="assign %s%s%s;\n"%(driveStrength,delay,asg_str)
        return oStr

    def _format_net3(self,tokens,i=""):
        oStr=""
#        print tokens
        return oStr

    def _format_initialStmt(self,tokens,i=""):
        oStr="initial\n\t%s\n"%self.format(tokens[1],i+"\t")
        return oStr

    def _format_gate(self,tokens,i=""):
        oStr=""
 #       print tokens
        return oStr

    def __init__(self):
        #scan class looking for formater functions
        for member in dir(self):
            if member.find("_format_")==0:
                token=member[len("_format_"):].lower()
                self.formater[token]=getattr(self,member)
        self.trace=False

    def format(self,tokens,i=""):
        if isinstance(tokens, ParseResults):
            name=str(tokens.getName()).lower()
            if self.trace: print "[%-20s] len:%2d  str:'%s' >"%(name,len(tokens),str(tokens)[:80])
            if len(tokens)==0: return ""
            if name in self.formater:
                outStr=self.formater[name](tokens,i)
            else:
                outStr=self.formater["default"](tokens,i)
        else:
            outStr=tokens
        return outStr

def prettyPrint(f,tokens, ident = 0):
    IS="  "

    def formInputOutput(f,tokens, ident = 0,label="input"):
            spec=""
            if len(tokens)>2:
                spec=resultLine(tokens[1]).rstrip()
                ports=tokens[2]
            else:
                ports=tokens[1];
            for port in ports:
                f.write(IS*ident+"%s %s %s;\n"%(label,spec,port))



class TMR(VerilogParser):
    def __init__(self):
        VerilogParser.__init__(self)
        self.EXT=('A','B','C')
        self.tmrErr={}
        for ext in self.EXT:
           self.tmrErr[ext]=[]
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


    def replaceAll(self,tokens,post):
        for var in self.toTMR:
            self.replace(tokens,var,var+post)
        self.replaceDot(tokens,post)
        return tokens

    def tmrAlways(self,t):
        seq=self._isAlwaysSeq(t)

        #self.naiveCopy(t)
        #x=cpy[0][0][0][2][0]
        #x[0]="dupa"
        result=ParseResults([])
        #check if the module needs triplication
        needsTmr=False
        for name in self.toTMR:
            if self.checkIfContains(t,name):
                needsTmr=True
                break
#        print t,needsTmr

        # if we dont need to triplicate we just return input tokens
        if not needsTmr:
            return t

        for i in self.EXT:
            cpy=t.deepcopy()
            for name in self.toTMR:
#                print name
                if self.checkIfContains(cpy,name):
                    _to_name=name+i

                    if seq:
                        state_reg=""
                        for regName,regNameNext in self.fsm_regs:
                            if name==regNameNext:
                                state_reg=regName
#                        print "state ",state_reg
                        if state_reg!="":
                            _to_name=state_reg+"Voted"+i
#                    print "->",_to_name

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
        self.tmrlogger.debug("Input %s"%str(tokens[0][2]))
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
            newModuleName=moduleName+"TMR"
            tokens[0][0]=newModuleName
            self.tmrlogger.debug("ModuleInstantiation %s -> %s"%(moduleName,newModuleName))

            #print moduleName
            if moduleName in ("powerOnReset","memoryAddrDec"):# triplicate module
                newIns=ParseResults([],name=tokens.getName())
                for inst in tokens:
                    for post in self.EXT:
                        instCpy=inst.deepcopy()
                        self.replaceAll(instCpy,post)
                        newIns.append(instCpy)
                tokens=newIns
            else: #triplicate IO
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
                if self.errorOut:
                    newports.append("tmrErrorA" )
                    newports.append("tmrErrorB" )
                    newports.append("tmrErrorC" )
                header[2]=newports
            body=tokens[0][1]

            if self.fsm:
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

            if self.errorOut:
                for ext in self.EXT:
                    if len(self.tmrErr[ext]):
                        body.insert(0,self.outputDecl.parseString("output tmrError%s;"%ext)[0])
                        sep=""
                        asgnStr="assign tmrError%s="%ext
                        for signal in self.tmrErr[ext]:
                            asgnStr+=sep+signal
                            sep="|"
                        asgnStr+=";"
                        #self.tmrlogger.debug(asgnStr)
                        body.append(self.continuousAssign.parseString(asgnStr)[0])
            #print self.errorOut
            #print self.tmrErr
                           # body.append(self.netDecl3.parseString("wire [1:0] %s = (%s&%s) | (%s&%s) | (%s&%s);"%(name_voted,a,b,b,c,a,c))[0])
            return tokens
        except:
            self.exc()




    def tmrTop(self,tokens):
        return tokens
    def triplicate(self):
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
    parser.add_option("-d", "--do-not-triplicate", action="append", dest="dnt",type="str")
    parser.add_option("","--spaces",               dest="spaces", default=2, type=int )
    parser.add_option("","--rtl-dir",              dest="rtldir", default="./rtl")
    #FORMAT = '%(message)s'
    logging.basicConfig(format='[%(name)s|%(levelname)s] %(message)s', level=logging.DEBUG)

    try:
        (options, args) = parser.parse_args()
        if len(args)==0:
            args=[options.rtldir]

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

                if options.tmr:
                    tmrtokens=vp.triplicate()
                    vf=VerilogFormater()
                    vf.setTrace(options.trace)
                    print vf.format(tmrtokens).replace("\t"," "*options.spaces)
                elif options.s2t:
                    tmrtokens=vp.single2tmr()
                    vf=VerilogFormater()
                    vf.setTrace(options.trace)
                    print vf.format(tmrtokens).replace("\t"," "*options.spaces)


            except ParseException, err:
                print err.line
                print " "*(err.column-1) + "^"
                print err
                print traceback.format_exc()
                return
            except ParseSyntaxException, err:
                print err.line
                print " "*(err.column-1) + "^"
                print err
                print
                return

#            if vp.module_name!="":
#                vp.toHTML(fname+".html")
    except ValueError:
        raise
#        G.write('simple.dot')
#        G.layout() # layout with default (neato)
#        G.draw('simple.png')

if __name__=="__main__":
    main()

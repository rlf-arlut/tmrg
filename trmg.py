#!/usr/bin/env python

from optparse import *
#import tempita
#import pygraphviz as pgv
from vp import *

import pprint

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

    def _format_Range(self,tokens,i=""):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr

    def _format_Always(self,tokens,i=""):
        oStr=""
        eventCtrl=self.format(tokens[0])
        stmt=self.format(tokens[1],i+"\t")
        oStr+="always %s\n"%eventCtrl
        oStr+=i+"\t%s\n"%stmt
        return oStr
    def _format_subscrIdentifier(self,tokens,i=""):
        oStr=tokens[0]
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
        for el in tokens[0]:
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
            sep+=" or "
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

    def _format_case(self,tokens,i=""):
#        print tokens
        label=tokens[0]
        cond=self.format(tokens[1])
        oStr="%s (%s)\n"%(label,cond)
        for t in tokens[2]:
            oStr+=i+"\t"+self.format(t)+"\n"
        oStr+=i+tokens[3]
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
            if self.trace: print "[%-20s] len:%2d  str:'%s' >"%(name,len(tokens),str(tokens)[:50])
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


    #print type(value)
    #if isinstance(value, list):
  #      print ident+"  <LEN :%d"%(len(value))
#        for e in value:
#            prettyPrint(e, ident+'  ')
#    else:
#        print ident+'%s' %(value), type(value)

class TMR(VerilogParser):
    def __init__(self):
        VerilogParser.__init__(self)
        self.EXT=('A','B','C')

    def _triplicate(self,tokens):
        print "t",type(tokens),tokens
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
                print "x"
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
        tokens[0][2]=self._tmr_list(tokens[0][2])
        return tokens

    def tmrInput(self,tokens):
        tokens[0][2]=self._tmr_list(tokens[0][2])
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

    def tmrModule(self,tokens):
        header=tokens[0][0]
        header[1][0]=str(header[1][0])+"TMR"
        #print "H!", tokens[0]
        if len(header)>2:
            ports=header[2]
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

            header[2]=newports
        body=tokens[0][1]
        if self.fsm:
            for r1,r2 in self.fsm_regs:
                if r2 in self.toTMR:
                    a=r2+self.EXT[0]
                    b=r2+self.EXT[1]
                    c=r2+self.EXT[2]
                    for ext in self.EXT:
                        name_voted="%sVoted%s"%(r1,ext)
                        comment=ParseResults(["cadance set_dont_touch %s"%name_voted],name="lineComment")
                        body.append(comment)
                        body.append(self.netDecl3.parseString("wire [1:0] %s = (%s&%s) | (%s&%s) | (%s&%s);"%(name_voted,a,b,b,c,a,c))[0])
        return tokens

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
        tmrt=self.verilogbnf.parseString(self.verilog)
        return tmrt

def main():
    parser = OptionParser(version="%prog 1.0", usage="%prog [options] fileName")
#    parser.add_option("", "--input-file",         dest="inputFile",   help="Input file name (*.v)", metavar="FILE")
#    parser.add_option("", "--output-file",        dest="outputFile",  help="Output file name (*.v)", metavar="FILE")
#    parser.add_option("-r", "--recursive",       action="store_true", dest="rec", default=True, help="Recurive.")
    parser.add_option("-t", "--triplicate",        action="store_true", dest="tmr", default=False, help="Triplicate.")
    parser.add_option("-p", "--parse",             action="store_true", dest="parse", default=True, help="Parse")
    parser.add_option("-f", "--format",            action="store_true", dest="format", default=True, help="Parse")
    parser.add_option("-i", "--info",              action="store_true", dest="info",  default=False, help="Info")
    parser.add_option("-q", "--trace",             action="store_true", dest="trace",  default=False, help="Trace formating")
    parser.add_option("-d", "--do-not-triplicate", action="append", dest="dnt",type="str")
    parser.add_option("","--spaces",               dest="spaces", default=2, type=int )

    try:
        (options, args) = parser.parse_args()
        if len(args)!=1:
            parser.error("You have to specify filename!")

        fname = args[0]
        try:
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
                print "/"+"*"*80
                print " * TMR"
                print " "+ "*"*80+"/"
                tmrtokens=vp.triplicate()
                vf=VerilogFormater()
                vf.setTrace(options.trace)
                print vf.format(tmrtokens).replace("\t"," "*options.spaces)

        except ParseException, err:
            print err.line
            print " "*(err.column-1) + "^"
            print err
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

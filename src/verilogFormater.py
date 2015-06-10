from pyparsing import *
class VerilogFormater:
    formater={}
    def setTrace(self,t):
        self.trace=t
    def _format_Top(self,tokens,i=""):
        oStr=""#"// file automaticly generated\n"
        for i in tokens:
            oStr+=self.format(i)
        return oStr
    def _format_lineComment(self,tokens,i=""):
        return i+"// %s\n"%tokens[0]

    def _format_Default(self,tokens,i=""):
        return "default (%s : %s)\n"%(tokens.getName(),tokens)

    def _format_Id(self,tokens,i=""):
        oStr=str(tokens[0])
        return oStr

    def _format_None(self,tokens,i=""):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)+" "
        return oStr

    def _formatIo(self,tokens,i=""):
        oStr=""
        label=str(tokens[0])
        spec=self.format(tokens[1])
        #if spec!="":spec+=" "
        spec+=self.format(tokens[2])
        if spec!="":spec+=" "
        ports=tokens[3]
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
        spec+=self.format(tokens[2])
        ports=tokens[3]
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
        spec=self.format(tokens[2])
        if spec!="":spec+=" "
        for port in tokens[3]:
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
        oStr="["
        oStr+=self.format(tokens[-2])
        oStr+=":"
        oStr+=self.format(tokens[-1])
        oStr+="]"
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
        modname=header[1]
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
        delay=self.format(tokens[1])
        if delay!="": delay+=" "
        expr=self.format(tokens[2])
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
        val=self.format(tokens[1])
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

    def _format_directive_do_not_touch(self,tokens,i=""):
        return ""

    def _format_directive_do_not_triplicate(self,tokens,i=""):
        return ""

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
    def __call__(self,tokens,i=""):
        return self.format(tokens,i)

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


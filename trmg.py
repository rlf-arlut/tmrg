#!/usr/bin/env python

from optparse import *
#import tempita
#import pygraphviz as pgv
from vp import *

toptest = """
     // dupa
        module TOP( in, out );
        input [7:0] in;
     reg d;
        output [5:0] out; //xx
        COUNT_BITS8 count_bits( .IN( in ), .C( out ) );
        always @(posedge clk)
          begin
            x<=#NK 2;
          end
        endmodule"""

toptest = """
module TOP( input k1, output [2:3] ok2, inout xx1, x1, output reg or1, input wire iw1, output reg [2:1] oreg2);
   input i1;
   parameter N=2,M=1;
   input [2:1] i2;
   output [2:1] o1;
   input clk;
   inout io1,dd021;
   reg d;
   reg [211:1] d1;
   reg signed [3:2] d2;
   reg [2:1] d3,d4;

   always @(posedge clk)
   begin
     d1<=i2;
     d3[2:0]<=i2;
     {d1,d2[1:0],o1}<=i2;
   end

   always
   begin
     d4=i1;
   end

endmodule"""

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
    def formatTop(self,tokens):
        oStr="// file automaticly generated\n"
        for i in tokens:
            oStr+=self.format(i)
        return oStr

    def formatDefault(self,tokens):
        return "default (%s)"%(tokens.getName())

    def formatId(self,tokens):
        oStr=str(tokens[0])
        return oStr

    def _formatIo(self,tokens):
        oStr=""
        label=str(tokens[0])
        spec=self.format(tokens[1])
        ports=tokens[2]
        for port in ports:
            oStr+="%s %s %s;\n"%(label,spec,port)
        return oStr

    def formatInput(self,tokens):
        return self._formatIo(tokens)

    def formatInOut(self,tokens):
        return self._formatIo(tokens)

    def formatOutput(self,tokens):
        return self._formatIo(tokens)

    def formatRegDecl(self,tokens):
        return self._formatIo(tokens)

    def formatRange(self,tokens):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr

    def formatAlways(self,tokens):
        oStr=""
        eventCtrl=self.format(tokens[0])
        stmt=self.format(tokens[1])
        oStr+="always %s\n"%eventCtrl
        oStr+="%s\n"%stmt
        return oStr

    def formatBeginEnd(self,tokens):
        oStr="begin\n"
        for stmt in tokens[0]:
            oStr+=self.format(stmt)
        oStr+="end\n"
        return oStr

    def formatEventCtrl(self,tokens):
        oStr=""
        for el in tokens[0]:
            oStr+=self.format(el)
        return oStr

    def formatDelimitedList(self,tokens):
        oStr=""
        print tokens
        for el in tokens:
            oStr+=self.format(el)
        return oStr
    def formatEventTerm(self,tokens):
        oStr=""
        for el in tokens:
            oStr+=self.format(el)+" "
        return oStr
    def formatIf(self,tokens):
        oStr=""
        return oStr
    def formatIfElse(self,tokens):
        oStr=""
        print tokens
        if len(tokens)==1:
            stm=tokens[0]
        else:
            stm=tokens
        cond=stm[1]
        ifAction=stm[2]
        elseAction=stm[4]
        oStr+="if %s\n"%self.format(cond)
        oStr+="\t%s"%self.format(ifAction)
        oStr+="else\n\t%s"%self.format(elseAction)
# #             prettyPrint(f,ifact, ident+1)
# #             f.write(IS*ident+"else\n")
#             prettyPrint(f,elseact, ident+1)
        return oStr

    def formatModule(self,tokens):
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


    def formatNbAssgnmt(self,tokens):
        tokens=tokens[0]
        lval=self.format(tokens[0])
        delay=self.format(tokens[2])
        expr=self.format(tokens[3])
        oStr="%s <= %s%s;\n"%(lval,delay,expr)

        return oStr

    def formatExpr(self,tokens):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr
    def formatDelay(self,tokens):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr
    def formatCondition(self,tokens):
        oStr=""
        for t in tokens:
            oStr+=self.format(t)
        return oStr

    def __init__(self):
        self.formater["top"]=self.formatTop
        self.formater["default"]=self.formatDefault
        self.formater["module"]=self.formatModule

        self.formater["id"]=self.formatId
        self.formater["input"]=self.formatInput
        self.formater["inout"]=self.formatInOut
        self.formater["output"]=self.formatOutput
        self.formater["regDecl"]=self.formatRegDecl
        self.formater["always"]=self.formatAlways
        self.formater["range"]=self.formatRange
        self.formater["begin-end"]=self.formatBeginEnd
        self.formater["eventCtrl"]=self.formatEventCtrl
        self.formater["delimitedList"]=self.formatDelimitedList
        self.formater["eventTerm"]=self.formatEventTerm
        self.formater["if"]=self.formatIf
        self.formater["if-else"]=self.formatIfElse
        self.formater["nbAssgnmt"]=self.formatNbAssgnmt
        self.formater["expr"]=self.formatExpr
        self.formater["delay"]=self.formatDelay
        self.formater["condition"]=self.formatCondition

    def format(self,tokens):
        if isinstance(tokens, ParseResults):
            name=tokens.getName()
            print "<format %s '%s'>"%(name,str(tokens)[:50])
            if name in self.formater:
                outStr=self.formater[name](tokens)
            else:
                outStr=self.formater["default"](tokens)
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

    if isinstance(tokens, ParseResults):
        name=tokens.getName()
        print "#PP# %-20s %-60s %s %s"%(name, tokens.toVerilog()[:50], hex(id(tokens)),str(tokens.__toverilog))
        if name=="top":
            f.write("// file automaticly generated\n")
            for i in tokens:
                prettyPrint(f,i, 0 )
        elif name in ("output", "input","inout"):
            formInputOutput(f,tokens, ident = ident,label=name)
        elif name=="continuousAssign":
            for t in tokens:
                f.write(IS*(ident)+"assign %s;\n"%resultLine(t))
        elif name=="always":
            if len(tokens)==2:
                eventCtrl=tokens[0]
                eventCtrl_str=resultLine(eventCtrl).rstrip()
                body=tokens[1]
            else:
                eventCtrl_str=""
                body=tokens[0]
            f.write("\n"+IS*ident+"always %s\n"%eventCtrl_str)
            for stmt in body:
                prettyPrint(f,stmt, ident +1)
        elif name=="begin-end":
            f.write(IS*ident+"begin (%d)\n"%(len(tokens)))
            for stmt in tokens:
                prettyPrint(f,stmt, ident +1)
            f.write(IS*ident+"end\n")
        elif name=="assgnmt":
            f.write(IS*ident+resultLine(tokens)+"\n")
        elif name=="nbAssgnmt":
            f.write(IS*ident+resultLine(tokens)+"\n")
        elif name=="stmtBody":
            print "## ",tokens.getName(), tokens
            for token in tokens[0]:
                prettyPrint(f,token, ident)
        elif name=="if":
            if len(tokens)==1:
                stm=tokens[0]
            else:
                stm=tokens
            cond=stm[1]
            f.write(IS*ident+"if %s\n"%(resultLine(cond)))
            ifact=stm[2][0]
            prettyPrint(f,ifact, ident+1)
        elif name=="if-else":
            if len(tokens)==1:
                stm=tokens[0]
            else:
                stm=tokens
#            print tokens
            cond=stm[1]
            f.write(IS*ident+"if %s\n"%(resultLine(cond)))
            ifact=stm[2]
            prettyPrint(f,ifact, ident+1)
            f.write(IS*ident+"else\n")
            elseact=stm[4][0]
            prettyPrint(f,elseact, ident+1)

        else:
            if isinstance(tokens,ParseResults):
                for stmt in tokens:
                    prettyPrint(f,stmt, ident +1)

            else:
                print IS*ident,"#",tokens.getName() ," : %s"%str(tokens)
    else:
        print IS*ident,"$",tokens
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
        def gotExpr(s,l,t):
            #print t
            return t
        def gotModule(s,l,t):
            #print s,l,t
            return t
        def gotContinuousAssign(s,l,t):
            #print s,l,t
            return t
            output=[]
            #for
            #print type(t)
            #print dir(t)
            #return "dupa";

            #self.registers
            #print toks
#            atrs=""
            #for a in toks[0][1:-2]:
#                atrs+=a+" "
#            atrs=atrs.rstrip()
#            for regnames in toks[0][-2]:
#                self.registers[regnames[0]]=atrs

        self.continuousAssign.setParseAction(gotContinuousAssign)
        self.module.setParseAction(gotModule)
        self.expr.setParseAction(gotExpr)
    def triplicate(self):
        tokens=self.verilogbnf.parseString( self.verilog)
        prettyPrint(sys.stdout,tokens)
        #print pprint.PrettyPrinter(2).pprint( tokens.asList() )
        #print "%"*80
        #print prettyPrint(tokens.asList())
        #print dir(tokens)
        #print dir(tokens.top)
def main():
    parser = OptionParser(version="%prog 1.0", usage="%prog [options] fileName")
#    parser.add_option("", "--input-file",         dest="inputFile",   help="Input file name (*.v)", metavar="FILE")
#    parser.add_option("", "--output-file",        dest="outputFile",  help="Output file name (*.v)", metavar="FILE")
#    parser.add_option("-r", "--recursive",       action="store_true", dest="rec", default=True, help="Recurive.")
    parser.add_option("-t", "--triplicate",       action="store_true", dest="tmr", default=False, help="Triplicate.")
    parser.add_option("-p", "--parse",            action="store_true", dest="parse", default=True, help="Parse")
    parser.add_option("-f", "--format",           action="store_true", dest="format", default=True, help="Parse")
    parser.add_option("-i", "--info",             action="store_true", dest="info",  default=False, help="Info")


    try:
        (options, args) = parser.parse_args()
        if len(args)!=1:
            parser.error("You have to specify filename!")

        fname = args[0]
        try:
            print options
            vp=TMR()
            if options.parse or options.tmr or options.format:
                tokens=vp.parseString(readFile(fname))
            if options.info:
                vp.printInfo()
            if options.format:
                #prettyPrint(sys.stdout,tokens)
                vf=VerilogFormater()
                print vf.format(tokens)
            if options.tmr:
                vp.triplicate()

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

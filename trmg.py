#!/usr/bin/env python

from optparse import OptionParser
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
        if name=="top":
            f.write("// file automaticly generated\n")
            for i in tokens:
                prettyPrint(f,i, 0 )
        elif name=="module":
            header=tokens[0]
            modname=header[1][0]
            f.write(IS*ident+"module %s"%modname)
            ports=[]
            if len(header)>2:
                ports=header[2]
                s="(\n"
                for port in ports:
                    s+=IS*(ident+1) +resultLine(port,sep=" ").rstrip()+",\n"
                s=s.rstrip()[:-1]+"\n"+IS*(ident)+")"
                f.write(s)
            f.write(";\n")

            moduleBody=tokens[1]
            for moduleItem in moduleBody:
                prettyPrint(f,moduleItem, ident +1)
            f.write("endmodule\n")
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
            f.write(IS*ident+"begin\n")
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
            stm=tokens[0]
            cond=stm[1]
            f.write(IS*ident+"if %s\n"%(resultLine(cond)))
            ifact=stm[2][0]
            prettyPrint(f,ifact, ident+1)
        elif name=="if-else":
            stm=tokens[0]
            print tokens
            cond=stm[1]
            f.write(IS*ident+"if %s\n"%(resultLine(cond)))
            ifact=stm[2]
            prettyPrint(f,ifact, ident+1)
            f.write(IS*ident+"else %s\n"%(resultLine(cond)))
            elseact=stm[4][0]
            prettyPrint(f,elseact, ident+1)

        else:
            print ident,"#",tokens.getName() ," : %s"%str(tokens)
    else:
        print ident,"$",tokens
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
    parser.add_option("", "--triplicate-inputs",  action="store_true", dest="tInp", default=True, help="Triplicate inputs.")
    parser.add_option("", "--triplicate-outputs", action="store_true", dest="tOut", default=True, help="Triplicate outputs.")
    parser.add_option("", "--triplicate-reg",     action="store_true", dest="tReg", default=True, help="Triplicate registers.")
    parser.add_option("", "--triplicate-comb",    action="store_true", dest="tCom", default=True, help="Triplicate combinatorial logic.")

    parser.add_option("", "--vote-inputs",        action="store_true", dest="vInp", default=True, help="Add majority voters at inputs.")
    parser.add_option("", "--vote-outputs",       action="store_true", dest="vOut", default=True, help="Add majority voters at outputs.")
    parser.add_option("", "--vote-reg",           action="store_true", dest="vReg", default=True, help="Add majority voters at .")
    parser.add_option("", "--vote-comb",          action="store_true", dest="vCom", default=True, help="Add majority voters at .")


    try:
        (options, args) = parser.parse_args()
        if len(args)!=1:
            parser.error("You have to specify filename!")

        fname = args[0]
        vp=TMR()
        vp.parseString(readFile(fname))
        vp.printInfo()
        vp.triplicate()

#            if vp.module_name!="":
#                vp.toHTML(fname+".html")

    except ValueError:
        raise OptionValueError(
            "option %s: invalid complex value: %r" % (opt, value))
#        G.write('simple.dot')
#        G.layout() # layout with default (neato)
#        G.draw('simple.png')

if __name__=="__main__":
    main()

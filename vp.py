#!/usr/bin/env python

# verilogParse.py
#
# an example of using the pyparsing module to be able to process Verilog files
# uses BNF defined at http://www.verilog.com/VerilogBNF.html
#
#    Copyright (c) 2004-2011 Paul T. McGuire.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# If you find this software to be useful, please make a donation to one
# of the following charities:
# - the Red Cross (http://www.redcross.org)
# - Hospice Austin (http://www.hospiceaustin.org)
#
#    DISCLAIMER:
#    THIS SOFTWARE IS PROVIDED BY PAUL T. McGUIRE ``AS IS'' AND ANY EXPRESS OR
#    IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#    MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO
#    EVENT SHALL PAUL T. McGUIRE OR CO-CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
#    INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#    BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OFUSE,
#    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
#    OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
#    EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#    For questions or inquiries regarding this license, or commercial use of
#    this software, contact the author via e-mail: ptmcg@users.sourceforge.net
#
# Todo:
#  - add pre-process pass to implement compilerDirectives (ifdef, include, etc.)
#
# Revision History:
#
#   1.0   - Initial release
#   1.0.1 - Fixed grammar errors:
#           . real declaration was incorrect
#           . tolerant of '=>' for '*>' operator
#           . tolerant of '?' as hex character
#           . proper handling of mintypmax_expr within path delays
#   1.0.2 - Performance tuning (requires pyparsing 1.3)
#   1.0.3 - Performance updates, using Regex (requires pyparsing 1.4)
#   1.0.4 - Performance updates, enable packrat parsing (requires pyparsing 1.4.2)
#   1.0.5 - Converted keyword Literals to Keywords, added more use of Group to
#           group parsed results tokens
#   1.0.6 - Added support for module header with no ports list (thanks, Thomas Dejanovic!)
#   1.0.7 - Fixed erroneous '<<' Forward definition in timCheckCond, omitting ()'s
#   1.0.8 - Re-released under MIT license
#   1.0.9 - Enhanced udpInstance to handle identifiers with leading '\' and subscripting
#   1.0.10 - Fixed change added in 1.0.9 to work for all identifiers, not just those used
#           for udpInstance.
#
import pdb
import time
import pprint
import sys

__version__ = "1.0.10"

import functools

from pyparsing import *
import pyparsing
usePackrat = True
usePsyco = False

import glob


from prettytable import PrettyTable


packratOn = False
psycoOn = False

if usePackrat:
    try:
        ParserElement.enablePackrat()
    except:
        pass
    else:
        packratOn = True

# comment out this section to disable psyco function compilation
if usePsyco:
    try:
        import psyco
        psyco.full()
    except:
        print "failed to import psyco Python optimizer"
    else:
        psycoOn = True


def dumpTokens(s,l,t):
    import pprint
    pprint.pprint( t.asList() )

def delimitedList( expr, delim=",",name="" ):
    """Helper to define a delimited list of expressions - the delimiter defaults to ','.
       By default, the list elements and delimiters can have intervening whitespace, and
       comments, but this can be overridden by passing 'combine=True' in the constructor.
       If combine is set to True, the matching tokens are returned as a single token
       string, with the delimiters included; otherwise, the matching tokens are returned
       as a list of tokens, with the delimiters suppressed.
    """
    return ( (expr) + ZeroOrMore( Suppress(delim) + (expr) ) ).setResultsName("delimitedList")


class VerilogParser:
    def __init__(self):
        sys.setrecursionlimit(2000)
        self.registers={}
        self.inputs={}
        self.outputs={}
        self.inouts={}
        self.parameters={}
        self.portList=[]
        self.parametersList=[]
        self.nba=set()
        self.ba=set()
        self.instances={}
        self.errorOut=False
        self.dnt_from_source=set()
        self.module_name=""
        # compiler directives
        self.compilerDirective = Combine( "`" + \
            oneOf("define undef ifdef else endif default_nettype "
                  "include resetall timescale unconnected_drive "
                  "nounconnected_drive celldefine endcelldefine") + \
            restOfLine ).setName("compilerDirective")

        # primitives
        self.semi = Literal(";")
        self.lpar = Literal("(")
        self.rpar = Literal(")")
        self.equals = Literal("=")

        identLead = alphas+"$_"
        identBody = alphanums+"$_"
        identifier1 = Regex( r"\.?["+identLead+"]["+identBody+"]*(\.["+identLead+"]["+identBody+"]*)*"
                            ).setName("baseIdent")
        identifier2 = Regex(r"\\\S+").setParseAction(lambda t:t[0][1:]).setName("escapedIdent")
        identifier = (identifier1 | identifier2).setResultsName("id")

        hexnums = nums + "abcdefABCDEF" + "_?"
        base = Regex("'[bBoOdDhH]").setName("base")
        basedNumber = Combine( Optional( Word(nums + "_") ) + base + Word(hexnums+"xXzZ"),
                               joinString="", adjacent=False ).setResultsName("basedNumber")
        #~ number = ( basedNumber | Combine( Word( "+-"+spacedNums, spacedNums ) +
                           #~ Optional( "." + Optional( Word( spacedNums ) ) ) +
                           #~ Optional( e + Word( "+-"+spacedNums, spacedNums ) ) ).setName("numeric") )
        number = ( basedNumber | \
                   Regex(r"[+-]?[0-9_]+(\.[0-9_]*)?([Ee][+-]?[0-9_]+)?") \
                  ).setName("numeric")
        #~ decnums = nums + "_"
        #~ octnums = "01234567" + "_"
        self.expr = Forward()

        concat = Group( Suppress("{") + delimitedList( self.expr ) + Suppress("}") ).setResultsName("concat")
        multiConcat = Group("{" + self.expr + concat + "}").setName("multiConcat")
        funcCall = Group(identifier + "(" + Group(Optional( delimitedList( self.expr ) )) + ")").setResultsName("funcCall")

        subscrRef = Group("[" + delimitedList( self.expr, ":" ) + "]")
        subscrIdentifier = Group( identifier + Optional( subscrRef ) ).setResultsName("subscrIdentifier")
        #~ scalarConst = "0" | (( FollowedBy('1') + oneOf("1'b0 1'b1 1'bx 1'bX 1'B0 1'B1 1'Bx 1'BX 1") ))
        scalarConst = Regex("0|1('[Bb][01xX])?")
        mintypmaxExpr = Group( self.expr + ":" + self.expr + ":" + self.expr ).setName("mintypmax")
        primary = (
                  number |
                  ("(" + mintypmaxExpr + ")" ) |
                  ( "(" + Group(self.expr) + ")" ).setName("nestedExpr") | #.setDebug() |
                  multiConcat |
                  concat |
                  dblQuotedString |
                  funcCall |
                  subscrIdentifier
                  )

        unop  = oneOf( "+  -  !  ~  &  ~&  |  ^|  ^  ~^" ).setName("unop")
        binop = oneOf( "+  -  *  /  %  ==  !=  ===  !==  &&  "
                       "||  <  <=  >  >=  &  |  ^  ^~  >>  << ** <<< >>>" ).setName("binop")

        self.expr << (
                ( unop + self.expr ) |  # must be first!
                ( primary + "?" + self.expr + ":" + self.expr ) |
                ( primary + Optional( binop + self.expr ) )
                )
        self.expr=self.expr.setResultsName("expr")
        lvalue = subscrIdentifier | Group(concat)

        # keywords
        if_        = Keyword("if")
        else_      = Keyword("else")
        edge       = Keyword("edge")
        posedge    = Keyword("posedge")
        negedge    = Keyword("negedge")
        specify    = Keyword("specify")
        endspecify = Keyword("endspecify")
        fork       = Keyword("fork")
        join       = Keyword("join")
        begin      = Keyword("begin")
        end        = Keyword("end")
        default    = Keyword("default")
        forever    = Keyword("forever")
        repeat     = Keyword("repeat")
        while_     = Keyword("while")
        for_       = Keyword("for")
        case       = oneOf( "case casez casex" )
        endcase    = Keyword("endcase")
        wait       = Keyword("wait")
        disable    = Keyword("disable")
        deassign   = Keyword("deassign")
        force      = Keyword("force")
        release    = Keyword("release")
        assign     = Keyword("assign").setResultsName("keyword")

        eventExpr = Forward()
        eventTerm = Group (( posedge + self.expr ) | ( negedge + self.expr ) | self.expr | ( "(" + eventExpr + ")" )).setResultsName("eventTerm")
        eventExpr << (
            Group( delimitedList( eventTerm, "or" ).setResultsName("delimitedOrList") )
            )
        eventControl = Group( "@" + ( ( "(" + eventExpr + ")" ) | identifier | "*" ) ).setName("eventCtrl").setResultsName("eventCtrl")

        delayArg = ( number |
                     Word(alphanums+"$_") | #identifier |
                     ( "(" + Group( delimitedList( mintypmaxExpr | self.expr ) ) + ")" )
                   ).setName("delayArg")#.setDebug()
        delay = Group( "#" + delayArg ).setName("delay").setResultsName("delay")#.setDebug()
        delayOrEventControl = delay | eventControl

        assgnmt   = ( lvalue + Suppress("=") + Group(Optional( delayOrEventControl )).setResultsName("delayOrEventControl")
                             + Group(self.expr) ).setName( "assgnmt" ).setResultsName( "assgnmt" )
        def gotAssgnmt(s,loc,toks):
            lhs=toks[0]
#            print toks
            if toks[0].getName()=="subscrIdentifier":
                varid=str(toks[0][0])
                self.ba.add(varid)
#                print ">%s<"%varid
            elif toks[0].getName()=="concat":
#                print "concat", toks[0][0]
                for v in toks[0][0]:
                    varid=v[0]
                    self.ba.add(varid)
#                    print ">%s<"%varid
#            print self.ba
            return toks
        assgnmt.setParseAction(gotAssgnmt)
        self.nbAssgnmt = (( lvalue + "<=" + Group(Optional( delay)).setResultsName("delay") + Group(self.expr) ) |
                     ( lvalue + "<=" + Group(Optional( eventControl)).setResultsName("eventCtrl")
                       + Group(self.expr) )).setResultsName( "nbassgnmt" )
        def gotNbAssgnmt(s,loc,toks):
            lhs=toks[0]
#            print "NBA~~",toks,toks.getName()
            if toks[0].getName()=="subscrIdentifier":
                varid=str(toks[0][0])
                self.nba.add(varid)
#               print "nba>%s<"%varid

            if len(lhs)>=1 and lhs[0]=="{": #concatenation
                for v in lhs[1:-1]:
                    self.nba.add(v[0])
            else:
                self.nba.add(lhs[0])
            return toks

        self.nbAssgnmt.setParseAction(gotNbAssgnmt)

        range = ("[" + self.expr + ":" + self.expr + "]").setResultsName("range")

        def gotParameter(s,loc,toks):
            #for p in toks[1]:
            #    pname=p[0]
            #    pval=" ".join(p[2:])
            #    self.parameters[pname]=pval
            #    self.parametersList.append(pname)
            return toks

        paramAssgnmt = Group( identifier + "=" + self.expr ).setResultsName("paramAssgnmt")


        parameterDecl      = Group( "parameter" + Group(Optional( range )) + Group(delimitedList( paramAssgnmt )) + self.semi).setResultsName("paramDecl")
        parameterDecl.setParseAction(gotParameter)
        localParameterDecl = Group("localparam" + Group( Optional( range )) + Group(delimitedList( paramAssgnmt )) + self.semi).setResultsName("localparamDecl")
        #localParameterDecl.setParseAction(gotParameter)

        def gotIO(resdict,s,loc,toks):
             #print type(toks), dir(toks)
             toks=toks[0]
             #print toks
             start=1
             _type=""
             if toks[start] in ('reg','wire'):
                 _type=toks[start]
                 start+=1
             atrs=""
             for a in toks[1]:
#                 print str(a)
                 atrs+=str(a)+" "
             atrs=atrs.rstrip()
             for regnames in toks[-1]:
                 resdict[regnames]={"atributes":atrs,"tmr":True}
                 self.portList.append(regnames)
                 if type=='reg':
                     self.registers[regnames]={"atributes":atrs,"tmr":True}

#             return toks
        self.inputDecl = Group( "input" + Group(Optional( range )).setResultsName("range") + Group(delimitedList( identifier )) + Suppress(self.semi) ).setResultsName("input")
        self.inputDecl.setParseAction(lambda s,loc,toks : gotIO(self.inputs,s,loc,toks))
        self.outputDecl = Group( "output" + Group(Optional( range )).setResultsName("range") + Group(delimitedList( identifier )) + Suppress(self.semi) ).setResultsName("output")
        self.outputDecl.setParseAction(lambda s,loc,toks : gotIO(self.outputs,s,loc,toks))
        inoutDecl = Group( "inout" + Group(Optional( range )).setResultsName("range") + Group(delimitedList( identifier )) + Suppress(self.semi) ).setResultsName("inout")
        inoutDecl.setParseAction(lambda s,loc,toks : gotIO(self.inouts,s,loc,toks))

        regIdentifier = Group( identifier + Optional( "[" + self.expr + ":" + self.expr + "]" ) )
        self.regDecl = Group( "reg" +
                              Group(Optional("signed") +
                              Optional( range )).setResultsName("range") +
                              Group( delimitedList( regIdentifier )) +
                              Suppress(self.semi)
                            ).setName("regDecl").setResultsName("regDecl")
        def gotReg(s,loc,toks):
            toks=toks[0] #self.registers
            atrs=""
            for a in toks[1]:
                atrs+=str(a)+" "
            atrs=atrs.rstrip()
            for regnames in toks[-1]:
                self.registers[regnames[0]]={"atributes":atrs,"tmr":True} ## co z opcjami ?

#            return toks

        self.regDecl.setParseAction(gotReg)

        timeDecl = Group( "time" + delimitedList( regIdentifier ) + self.semi ).setResultsName("timeDecl")
        integerDecl = Group( "integer" + delimitedList( regIdentifier ) + Suppress(self.semi) ).setResultsName("integerDecl")

        strength0 = oneOf("supply0  strong0  pull0  weak0  highz0")
        strength1 = oneOf("supply1  strong1  pull1  weak1  highz1")
        driveStrength = Group( "(" + ( ( strength0 + "," + strength1 ) |
                                       ( strength1 + "," + strength0 ) ) + ")" ).setName("driveStrength").setResultsName("driveStrength")
        nettype = oneOf("wire  tri  tri1  supply0  wand  triand  tri0  supply1  wor  trior  trireg")
        expandRange = Optional( oneOf("scalared vectored") ) + range
        realDecl = Group( "real" + delimitedList( identifier ) + self.semi )

        eventDecl = Group( "event" + delimitedList( identifier ) + self.semi )

        blockDecl = (
            parameterDecl |
            localParameterDecl |
            self.regDecl |
            integerDecl |
            realDecl |
            timeDecl |
            eventDecl
            )

        self.stmt = Forward().setName("stmt").setResultsName("stmt")#.setDebug()
        stmtOrNull = self.stmt | self.semi
        caseItem = Group( delimitedList( self.expr ) + ":" + stmtOrNull ).setResultsName("caseItem") | \
                   Group( default + Optional(":") + stmtOrNull )
        condition=Group("(" + self.expr + ")").setResultsName("condition")
        self.stmt <<  ( Group( Suppress(begin) +  ZeroOrMore( self.stmt )  + Suppress(end) ).setName("beginend").setResultsName("beginend") | \
            Group( if_ + condition + stmtOrNull +  else_ + stmtOrNull ).setName("ifelse").setResultsName("ifelse") | \
            Group( if_ + condition + stmtOrNull  ).setName("if").setResultsName("if") |\
            Group( delayOrEventControl + stmtOrNull ).setResultsName("delayStm") |\
            Group( case + Suppress("(") + Group(self.expr) + Suppress(")") + Group(OneOrMore( caseItem )) + endcase ).setResultsName("case") |\
            Group( forever + self.stmt ).setResultsName("forever") |\
            Group( repeat + "(" + self.expr + ")" + self.stmt ) |\
            Group( while_ + "(" + self.expr + ")" + self.stmt ) |\
            Group( for_ + "(" + assgnmt + self.semi + Group( self.expr ) + self.semi + assgnmt + ")" + self.stmt ) |\
            Group( fork + ZeroOrMore( self.stmt ) + join ) |\
            Group( fork + ":" + identifier + ZeroOrMore( blockDecl ) + ZeroOrMore( self.stmt ) + end ) |\
            Group( wait + "(" + self.expr + ")" + stmtOrNull ) |\
            Group( "->" + identifier + self.semi ) |\
            Group( disable + identifier + self.semi ) |\
            Group( assign + assgnmt + self.semi ).setResultsName("assign") |\
            Group( deassign + lvalue + self.semi ) |\
            Group( force + assgnmt + self.semi ) |\
            Group( release + lvalue + self.semi ) |\
            Group( begin + ":" + identifier + ZeroOrMore( blockDecl ) + ZeroOrMore( self.stmt ) + end ).setName("begin:label-end").setResultsName("begin:label-end") |\
            Group( Group(assgnmt) + Suppress(self.semi) ).setResultsName("assgnmtStm") |\
            Group( self.nbAssgnmt + Suppress(self.semi) ).setResultsName("nbAssgnmt") |\
            Group( Combine( Optional("$") + identifier ) + Group(Optional( Suppress("(") + delimitedList(self.expr|empty) + Suppress(")") )) + Suppress(self.semi) ).setResultsName("taskEnable") )
            # these  *have* to go at the end of the list!!!

        """
        x::=<blocking_assignment> ;
        x||= <non_blocking_assignment> ;
        x||= if ( <expression> ) <statement_or_null>
        x||= if ( <expression> ) <statement_or_null> else <statement_or_null>
        x||= case ( <expression> ) <case_item>+ endcase
        x||= casez ( <expression> ) <case_item>+ endcase
        x||= casex ( <expression> ) <case_item>+ endcase
        x||= forever <statement>
        x||= repeat ( <expression> ) <statement>
        x||= while ( <expression> ) <statement>
        x||= for ( <assignment> ; <expression> ; <assignment> ) <statement>
        x||= <delay_or_event_control> <statement_or_null>
        x||= wait ( <expression> ) <statement_or_null>
        x||= -> <name_of_event> ;
        x||= <seq_block>
        x||= <par_block>
        x||= <task_enable>
        x||= <system_task_enable>
        x||= disable <name_of_task> ;
        x||= disable <name_of_block> ;
        x||= assign <assignment> ;
        x||= deassign <lvalue> ;
        x||= force <assignment> ;
        x||= release <lvalue> ;
        """
        self.alwaysStmt = Group( Suppress("always") + Group(Optional(eventControl)) + self.stmt ).setName("alwaysStmt").setResultsName("always")
        initialStmt = Group( "initial" + self.stmt ).setName("initialStmt").setResultsName("initialStmt")

        chargeStrength = Group( "(" + oneOf( "small medium large" ) + ")" ).setName("chargeStrength")

        self.continuousAssign = Group(  Suppress(assign)
              + Group(Optional( driveStrength )).setResultsName("driveStrength")
              + Group(Optional( delay )).setResultsName("delay")
              + Group(delimitedList( Group(assgnmt) )) + Suppress(self.semi)
            ).setName("continuousAssign").setResultsName("continuousAssign")#.setDebug()


        tfDecl = (
            parameterDecl |
            localParameterDecl |
            self.inputDecl |
            self.outputDecl |
            inoutDecl |
            self.regDecl |
            timeDecl |
            integerDecl |
            realDecl
            ).setResultsName("tfDecl")

        functionDecl = Group(
            "function" + Optional( range | "integer" | "real" ) + identifier + self.semi +
            Group( OneOrMore( tfDecl ) ) +
            Group( ZeroOrMore( self.stmt ) ) +
            "endfunction"
            ).setResultsName("functionDecl")

        inputOutput = oneOf("input output")

        self.netDecl1 = Group(nettype +
                              Group(Optional( expandRange )).setResultsName("range") +
                              Group(Optional( delay )) +
                              Group( delimitedList( identifier ) ) +
                              Suppress(self.semi)
                             ).setResultsName("netDecl1")
        self.netDecl2 = Group("trireg" +
                              Group(Optional( chargeStrength )) +
                              Group(Optional( expandRange )) +
                              Group(Optional( delay )) +
                              Group( delimitedList(  identifier ) )+
                              Suppress(self.semi)
                              ).setResultsName("netDecl2")

        self.netDecl3 = Group(nettype +
                              Group(Optional( driveStrength )) +
                              Group(Optional( expandRange )).setResultsName("range") +
                              Group(Optional( delay )) +
                              Group( delimitedList( Group(assgnmt) ) ) +
                              Suppress(self.semi)
                             ).setResultsName("netDecl3")

        gateType = oneOf("and  nand  or  nor xor  xnor buf  bufif0 bufif1 "
                         "not  notif0 notif1  pulldown pullup nmos  rnmos "
                         "pmos rpmos cmos rcmos   tran rtran  tranif0  "
                         "rtranif0  tranif1 rtranif1"  )
        gateInstance = Optional( Group( identifier + Optional( range ) ) ) + \
                        "(" + Group( delimitedList( self.expr ) ) + ")"
        gateDecl = Group( gateType +
            Optional( driveStrength ) +
            Optional( delay ) +
            delimitedList( gateInstance) +
            self.semi ).setResultsName("gate")

        udpInstance = Group( Group( identifier + Optional(range | subscrRef) ) +
            "(" + Group( delimitedList( self.expr ) ) + ")" )
        udpInstantiation = Group( identifier -
            Optional( driveStrength ) +
            Optional( delay ) +
            delimitedList( udpInstance ) +
            self.semi ).setName("udpInstantiation")#.setParseAction(dumpTokens).setDebug()

        parameterValueAssignment = Group ( Suppress(Literal("#")) +
                                           Suppress("(") +
                                           Group( delimitedList( self.expr ) ) +
                                           Suppress(")")
                                         ).setResultsName("parameterValueAssignment")

        namedPortConnection = Group( "." + identifier + "(" + self.expr + ")" ).setResultsName("namedPortConnection")
        modulePortConnection = Group(self.expr | empty).setResultsName("modulePortConnection")
        moduleArgs = Group( Suppress("(") +
                            (delimitedList( modulePortConnection ) | delimitedList( namedPortConnection )) +
                            Suppress(")")
                          ).setResultsName("moduleArgs")#.setDebug()

        #parameterValueAssignment = Group( Literal("#") + "(" + Group( delimitedList( self.expr ) ) + ")" ).setResultsName("parameterValueAssignment")
        #namedPortConnection = Group( "." + identifier + "(" + self.expr + ")" ).setResultsName("namedPortConnection")
        #modulePortConnection = namedPortConnection | Group(self.expr).setResultsName("unnamedPortConnection")

        #moduleArgs = Group( "(" + (delimitedList( modulePortConnection ) |
                    #delimitedList( modulePortConnection )) + ")").setName("inst_args").setResultsName("moduleArgs")#.setDebug()

        moduleInstance = Group( Group ( identifier +
                                        Group(Optional(range)).setResultsName("range") ) +
                                moduleArgs
                              ).setResultsName("moduleInstance")

        self.moduleInstantiation = Group( identifier +
                                          Optional( parameterValueAssignment ) +
                                          Group(delimitedList( moduleInstance )).setResultsName("moduleInstantiation") +
                                          Suppress(self.semi)
                                        ).setResultsName("moduleInstantiation")

        def gotModuleInstantiation(s,loc,toks):
            toks=toks[0]
            module=toks[0]
            instname=toks[1][0][0]

            #print modid, modname
            self.instances[instname]={"atributes":module,"tmr":True}
            #self.G.add_edge(self.module_name,module)
            #self.instances.add(modid)
            #pass

        self.moduleInstantiation.setParseAction(gotModuleInstantiation)
        parameterOverride = Group( "defparam" + delimitedList( paramAssgnmt ) + self.semi )
        task = Group( Suppress("task") + identifier + Suppress(self.semi) +
            Group(ZeroOrMore( tfDecl )) +
            stmtOrNull +
            "endtask" ).setResultsName("task")
        def gotTask(s,l,t):
            print "taks"
            return t
        task.setParseAction(gotTask)

        specparamDecl = Group( "specparam" + delimitedList( paramAssgnmt ) + self.semi )

        pathDescr1 = Group( "(" + subscrIdentifier + "=>" + subscrIdentifier + ")" )
        pathDescr2 = Group( "(" + Group( delimitedList( subscrIdentifier ) ) + "*>" +
                                  Group( delimitedList( subscrIdentifier ) ) + ")" )
        pathDescr3 = Group( "(" + Group( delimitedList( subscrIdentifier ) ) + "=>" +
                                  Group( delimitedList( subscrIdentifier ) ) + ")" )
        pathDelayValue = Group( ( "(" + Group( delimitedList( mintypmaxExpr | self.expr ) ) + ")" ) |
                                 mintypmaxExpr |
                                 self.expr )
        pathDecl = Group( ( pathDescr1 | pathDescr2 | pathDescr3 ) + "=" + pathDelayValue + self.semi ).setName("pathDecl")

        portConditionExpr = Forward()
        portConditionTerm = Optional(unop) + subscrIdentifier
        portConditionExpr << portConditionTerm + Optional( binop + portConditionExpr )
        polarityOp = oneOf("+ -")
        levelSensitivePathDecl1 = Group(
            if_ + Group("(" + portConditionExpr + ")") +
            subscrIdentifier + Optional( polarityOp ) + "=>" + subscrIdentifier + "=" +
            pathDelayValue +
            self.semi )
        levelSensitivePathDecl2 = Group(
            if_ + Group("(" + portConditionExpr + ")") +
            self.lpar + Group( delimitedList( subscrIdentifier ) ) + Optional( polarityOp ) + "*>" +
                Group( delimitedList( subscrIdentifier ) ) + self.rpar + "=" +
            pathDelayValue +
            self.semi )
        levelSensitivePathDecl = levelSensitivePathDecl1 | levelSensitivePathDecl2

        edgeIdentifier = posedge | negedge
        edgeSensitivePathDecl1 = Group(
            Optional( if_ + Group("(" + self.expr + ")") ) +
            self.lpar + Optional( edgeIdentifier ) +
            subscrIdentifier + "=>" +
            self.lpar + subscrIdentifier + Optional( polarityOp ) + ":" + self.expr + self.rpar + self.rpar +
            "=" +
            pathDelayValue +
            self.semi )
        edgeSensitivePathDecl2 = Group(
            Optional( if_ + Group("(" + self.expr + ")") ) +
            self.lpar + Optional( edgeIdentifier ) +
            subscrIdentifier + "*>" +
            self.lpar + delimitedList( subscrIdentifier ) + Optional( polarityOp ) + ":" + self.expr + self.rpar + self.rpar +
            "=" +
            pathDelayValue +
            self.semi )
        edgeSensitivePathDecl = edgeSensitivePathDecl1 | edgeSensitivePathDecl2

        edgeDescr = oneOf("01 10 0x x1 1x x0").setName("edgeDescr")

        timCheckEventControl = Group( posedge | negedge | (edge + "[" + delimitedList( edgeDescr ) + "]" ))
        timCheckCond = Forward()
        timCondBinop = oneOf("== === != !==")
        timCheckCondTerm = ( self.expr + timCondBinop + scalarConst ) | ( Optional("~") + self.expr )
        timCheckCond << ( ( "(" + timCheckCond + ")" ) | timCheckCondTerm )
        timCheckEvent = Group( Optional( timCheckEventControl ) +
                                subscrIdentifier +
                                Optional( "&&&" + timCheckCond ) )
        timCheckLimit = self.expr
        controlledTimingCheckEvent = Group( timCheckEventControl + subscrIdentifier +
                                            Optional( "&&&" + timCheckCond ) )
        notifyRegister = identifier

        systemTimingCheck1 = Group( "$setup" +
            self.lpar + timCheckEvent + "," + timCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + self.rpar +
            self.semi )
        systemTimingCheck2 = Group( "$hold" +
            self.lpar + timCheckEvent + "," + timCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + self.rpar +
            self.semi )
        systemTimingCheck3 = Group( "$period" +
            self.lpar + controlledTimingCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + self.rpar +
            self.semi )
        systemTimingCheck4 = Group( "$width" +
            self.lpar + controlledTimingCheckEvent + "," + timCheckLimit +
            Optional( "," + self.expr + "," + notifyRegister ) + self.rpar +
            self.semi )
        systemTimingCheck5 = Group( "$skew" +
            self.lpar + timCheckEvent + "," + timCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + self.rpar +
            self.semi )
        systemTimingCheck6 = Group( "$recovery" +
            self.lpar + controlledTimingCheckEvent + "," + timCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + self.rpar +
            self.semi )
        systemTimingCheck7 = Group( "$setuphold" +
            self.lpar + timCheckEvent + "," + timCheckEvent + "," + timCheckLimit + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + self.rpar +
            self.semi )
        systemTimingCheck = (FollowedBy('$') + ( systemTimingCheck1 | systemTimingCheck2 | systemTimingCheck3 |
            systemTimingCheck4 | systemTimingCheck5 | systemTimingCheck6 | systemTimingCheck7 )).setName("systemTimingCheck")
        sdpd = if_ + Group("(" + self.expr + ")") + \
            ( pathDescr1 | pathDescr2 ) + "=" + pathDelayValue + self.semi

        specifyItem = ~Keyword("endspecify") +(
            specparamDecl |
            pathDecl |
            levelSensitivePathDecl |
            edgeSensitivePathDecl |
            systemTimingCheck |
            sdpd
            )
        """
        x::= <specparam_declaration>
        x||= <path_declaration>
        x||= <level_sensitive_path_declaration>
        x||= <edge_sensitive_path_declaration>
        x||= <system_timing_check>
        x||= <sdpd>
        """
        specifyBlock = Group( "specify" + ZeroOrMore( specifyItem ) + "endspecify" )

        self.moduleItem = ~Keyword("endmodule") + (
            parameterDecl |
            localParameterDecl |
            self.inputDecl |
            self.outputDecl |
            inoutDecl |
            self.regDecl |
            self.netDecl3 |
            self.netDecl1 |
            self.netDecl2 |
            timeDecl |
            integerDecl |
            realDecl |
            eventDecl |
            gateDecl |
            parameterOverride |
            self.continuousAssign |
            specifyBlock |
            initialStmt |
            self.alwaysStmt |
            task |
            functionDecl |
            # these have to be at the end - they start with identifiers
            self.moduleInstantiation
            )
#            udpInstantiation

        """  All possible moduleItems, from Verilog grammar spec
        x::= <parameter_declaration>
        x||= <input_declaration>
        x||= <output_declaration>
        x||= <inout_declaration>
        ?||= <net_declaration>  (spec does not seem consistent for this item)
        x||= <reg_declaration>
        x||= <time_declaration>
        x||= <integer_declaration>
        x||= <real_declaration>
        x||= <event_declaration>
        x||= <gate_declaration>
        x||= <UDP_instantiation>
        x||= <module_instantiation>
        x||= <parameter_override>
        x||= <continuous_assign>
        x||= <specify_block>
        x||= <initial_statement>
        x||= <always_statement>
        x||= <task>
        x||= <function>
        """
        portRef = subscrIdentifier
        portExpr = portRef | Group( "{" + delimitedList( portRef ) + "}" )
        port = (portExpr | Group( ( "." + identifier + "(" + portExpr + ")" ) ) ).setResultsName("port")

        inputOutput = oneOf("input output")
        portIn   = Group( "input"  +  Group(Optional( range )).setResultsName("range") + Group(identifier).setResultsName("names")).setResultsName("inputHdr")
        portOut  = Group( "output" +  Group(Optional( range )).setResultsName("range") + Group(identifier).setResultsName("names")).setResultsName("outputHdr")
        portInOut= Group( "inout"  +  Group(Optional( range )).setResultsName("range") + Group(identifier).setResultsName("names")).setResultsName("inoutHdr")

        portIn.setParseAction(lambda s,loc,toks : gotIO(self.inputs,s,loc,toks))
        portOut.setParseAction(lambda s,loc,toks : gotIO(self.outputs,s,loc,toks))
        portInOut.setParseAction(lambda s,loc,toks : gotIO(self.inouts,s,loc,toks))


        moduleHdr = Group ( oneOf("module macromodule") + Group(identifier).setResultsName("moduleName") +
                            Group(Optional( Suppress("(") +
                                             Optional( delimitedList( portIn | portOut | portInOut | port ) )  +
                                            Suppress(")") )).setResultsName("ports") +
                            Suppress(self.semi) ).setName("moduleHdr").setResultsName("moduleHdr")
        def gotModuleHdr(s,loc,toks):
            self.module_name=toks[0][1]
            return toks
        moduleHdr.addParseAction(gotModuleHdr)


        self.module = Group(  moduleHdr +
                 Group( ZeroOrMore( self.moduleItem ) ).setResultsName("moduleBody") +
                 "endmodule" ).setName("module").setResultsName("module")#.setDebug()


        udpDecl = self.outputDecl | self.inputDecl | self.regDecl
        #~ udpInitVal = oneOf("1'b0 1'b1 1'bx 1'bX 1'B0 1'B1 1'Bx 1'BX 1 0 x X")
        udpInitVal = (Regex("1'[bB][01xX]") | Regex("[01xX]")).setName("udpInitVal")
        udpInitialStmt = Group( "initial" +
            identifier + "=" + udpInitVal + self.semi ).setName("udpInitialStmt")

        levelSymbol = oneOf("0   1   x   X   ?   b   B")
        levelInputList = Group( OneOrMore( levelSymbol ).setName("levelInpList") )
        outputSymbol = oneOf("0   1   x   X")
        combEntry = Group( levelInputList + ":" + outputSymbol + self.semi )
        edgeSymbol = oneOf("r   R   f   F   p   P   n   N   *")
        edge = Group( "(" + levelSymbol + levelSymbol + ")" ) | \
               Group( edgeSymbol )
        edgeInputList = Group( ZeroOrMore( levelSymbol ) + edge + ZeroOrMore( levelSymbol ) )
        inputList = levelInputList | edgeInputList
        seqEntry = Group( inputList + ":" + levelSymbol + ":" + ( outputSymbol | "-" ) + self.semi ).setName("seqEntry")
        udpTableDefn = Group( "table" +
            OneOrMore( combEntry | seqEntry ) +
            "endtable" ).setName("table")

        """
        <UDP>
        ::= primitive <name_of_UDP> ( <name_of_variable> <,<name_of_variable>>* ) ;
                <UDP_declaration>+
                <UDP_initial_statement>?
                <table_definition>
                endprimitive
        """
        udp = Group( "primitive" + identifier +
            "(" + Group( delimitedList( identifier ) ) + ")" + self.semi +
            OneOrMore( udpDecl ) +
            Optional( udpInitialStmt ) +
            udpTableDefn +
            "endprimitive" )

        #verilogbnf = OneOrMore( self.module | udp ) + StringEnd()
        verilogbnf = (( self.module | udp ) + StringEnd()).setName("top").setResultsName("top")

#        specialComment = '//##' + Word(alphanums) + '##' + Word(alphanums+'.') + "::" + Word(nums)
#        def dontMatchSpecialComments(tokens):
#            if tokens[0] == specialComment:
#                raise ParseException("don't match special comments")
#        cppStyleComment.setParseAction(dontMatchSpecialComments)

        self.do_not_triplicate=( Suppress("do_not_triplicate") + identifier)
        def gotComment(s,l,t):
#            print t
            res=self.do_not_triplicate.searchString(t[0])
            for tokens in  res:
#                print tokens
                self.dnt_from_source.add(tokens[0])
            return t
        verilogbnf.ignore( cppStyleComment.setParseAction(gotComment) )
        verilogbnf.ignore( self.compilerDirective )

        self.verilogbnf=verilogbnf
    def applyDntConstrains(self,labels):
        if labels:
            for l in labels:
                if l in self.toTMR:
                    print "Removing %s"%l
                    self.toTMR.remove(l)
                else:
                    print "Unknown %s"%l
    def checkIfContainsParseResult(self,tokens,name):
        def _check(tokens,name):
            if isinstance(tokens, ParseResults):
                if tokens.getName():
                    if tokens.getName().lower() ==name:
                        return True
                for tok in tokens:
                    res=_check(tok,name)
                    if res:return True
                return False
            else:
                return False
        return _check(tokens,name)

    def _isAlwaysSeq(self,tokens):
        return self.checkIfContainsParseResult(tokens,"nbassgnmt")
    def toHTML(self,fname):
        self.tmpl = tempita.Template("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN">
<html>
<head>
<link rel="stylesheet" type="text/css" href="style.css">
</script>
<title>{{title}}</title>
</head>
<body>
<!--
<table class="companion_banner"><tr><td align=center><a class="companion_banner" href="http://www.hdlworks.com">Generated by <b>HDL Companion</b> for <i>willem</i> on Mon May 31 16:49:38 2010</a></td></tr></table>
<br><center><table class="index_tab">
<tr class="index_row">
<td class="index_col">
<a href="index.htm">Object View</a>
</td>
<td class="index_col">
<a href="toc_file.htm">File View</a>
</td>
<td class="index_col">
<a href="toc_top.htm">Top Level View</a>
</td>
<td class="index_col">
<a href="index_hier.htm">Hierarchical View</a>
</td>
<td class="index_col">
<a href="toc.htm">Index</a>
</td>
</tr>
</table>
</center>
-->
<h1>File: {{file}}</h1>
<!-- Scriptum 10.1 Revision 1 Copyright (c) 2010 HDL Works B.V. All rights reserved. -->

<pre class="DefaultText">{{body}}</pre>
</body>
</html>
""")
        verilog=self.verilog
        keywords = Word(alphas, alphanums+"_")
        # or a crude pre-processor (use parse actions to replace matching text)
        def substituteMacro(s,l,t):
            if t[0] in ("if","else","edge","posedge","negedge","wire","input","output","module","wire","reg","endmodule",
                        "specify","endspecify","fork","join","begin","end","default","always", "initial",
                        "forever","repeat", "while","for", "case","casez","casex",
                        "endcase","wait","disable","deassign","force","release","assign"):
                return '<span class="DefaultGroup1">%s</span>'%t[0]
        keywords.setParseAction( substituteMacro )
        keywords.ignore( cppStyleComment )
        verilog=keywords.transformString(verilog)

        def substituteComment(s,l,t):
            s=""
            if t[0].find('\n')>=0:
                for l in t[0].split('\n'):
                    s+='<span class="DefaultComment">%s</span>\n'%l
            else:
                s='<span class="DefaultComment">%s</span>'%t[0]
            return s

        #comment=Regex(r"/(?:\*(?:[^*]*\*+)+?/|/[^\n]*(?:\n[^\n]*)*?(?:(?<!\\)|\Z))").setName("C++ style comment")
        comment=Regex(r"/(?:\*([^*]*\*+)+?/|/[^\n]*(\n[^\n]*)*?((?<!\\)|\Z))").setName("C++ style comment")
        comment.setParseAction( substituteComment )
        verilog=comment.transformString(verilog)

        body=""
        for lno,l in enumerate(verilog.split('\n')):
            body+='<span class="DefaultMargin"> %4d </span><a name="l%d"></a> %s\n'%(lno+1,lno,l)

        vars={"title":self.module_name,"body":body, "file":self.module_name}
        f=open(fname,"w")
        f.write(self.tmpl.substitute(vars))
        f.close()

    def _detectFsm(self):
        print "detect fsm"
        self.fsm=False
        self.fsm_regs=[]
        for r1 in self.registers:
            for r2 in self.registers:
                if r1+"Next"==r2:
                    self.fsm=True
                    self.fsm_regs.append((r1,r2))
                    if self.registers[r1]["atributes"]!=self.registers[r2]["atributes"]:
                        print "Warning! Inconsistent register declaration "
                        print "  %s -> %s"%(r1,self.registers[r1]["atributes"])
                        print "  %s -> %s"%(r2,self.registers[r2]["atributes"])
        if self.fsm:
            self.errorOut=1

    def parseString( self,strng ):
        self.verilog=strng
        self.tokens=self.verilogbnf.parseString( strng )
        self._detectFsm()
        self.toTMR=set()
        for v in self.registers : self.toTMR.add(v)
        for v in self.inputs : self.toTMR.add(v)
        for v in self.outputs : self.toTMR.add(v)
        for v in self.inouts : self.toTMR.add(v)
        for v in self.registers : self.toTMR.add(v)
        for v in self.nba : self.toTMR.add(v)
        for v in self.ba : self.toTMR.add(v)
        for v in self.instances : self.toTMR.add(v)
        self.applyDntConstrains(self.dnt_from_source)
        #print self.toTMR
        return self.tokens

    def printInfo(self):
        def printDict(d,dname=""):
            if len(d)==0: return
            tab = PrettyTable([dname, "type", "tmr"])
            tab.min_width[dname]=50;
            tab.min_width["type"]=20;
            tab.min_width["tmr"]=10;
            tab.align[dname] = "l" # Left align city names

            #print "%-12s:"%dname
            for k in d:
                item=d[k]
                atributes=item["atributes"]
                tmr=item["tmr"]
                tab.add_row([k,atributes, tmr])
            tab.padding_width = 1 # One space between column edges and contents (default)
            print tab

        def printSet(s,sname=""):
            if len(s)==0: return
            tab = PrettyTable([sname])
            tab.align[sname] = "l" # Left align city names
            tab.min_width[sname]=80+6;
            #print s
            for k in s:
                #print k
                tab.add_row([k])
            print tab

        printDict(self.registers, "Registers")
        printDict(self.inputs,    "Inputs")
        printDict(self.outputs,   "Outputs")
        printDict(self.inouts,    "InOuts")
        printDict(self.parameters,"Parameters")
        printSet(self.nba,        "Non Blocking")
        printSet(self.ba,         "Blocking")
        printDict(self.instances, "Instantiations")
        if self.fsm:
            l=[]
            for r1,r2 in self.fsm_regs:
                atrs=""
                if self.registers[r1]["atributes"]!="":
                    atrs="(%s)"%self.registers[r1]["atributes"]
                l.append("%s <- %s %s"%(r1,r2,atrs))
            printSet(l,   "FSM")

    def dtmr(self):
        f=sys.stdout
        def p(s):
            #f.write(s+"\n")
            pass

        mod_tmr=self.module_name+"_dtmr"
        p("module %s"%mod_tmr)
        p("  (")
        TMR_SUFFIX=("A","B","C")
        ports=self.inouts.keys() + self.outputs.keys() + self.inputs.keys()
        plen=len(max(ports, key=len))

        fmr_str="%%-%ds"%(plen+2)
        for pid,port in enumerate(ports):
            for s in TMR_SUFFIX:
                pn=port+s
                if pid!=len(ports)-1: pn+=","
                pn=fmr_str%pn
                p("    %s // %s (%s)"%(pn,port,s))
        p("  );")

        def putIO(type,d,fmr_str="%s"):
            for k in d:
                p("  // -- %s --"%(k))
                for s in TMR_SUFFIX:
                    atr=fmr_str%d[k]
                    p("  %s %s %s%s;"%(type,atr,k,s))

        ports_atr=self.inouts.values() + self.outputs.values() + self.inputs.values()
        vlen=len(max(ports_atr, key=len))

        fmr_str="%%-%ds"%(vlen+2)
        putIO("input ",self.inputs,fmr_str)
        putIO("output",self.outputs,fmr_str)
        putIO("inout ",self.inouts,fmr_str)

        p("  // -- params --")
        for param in self.parameters:
            pv=self.parameters[param];
            p("  %s=%s;"%(param,pv))

        p("  // -- input voters --")
        def busWidth(atr):
            w=1
            range = "[" + self.expr + ":" + self.expr + "]"
            if atr:
                return  "%s - %s + 1"%(range.parseString(atr)[1] ,range.parseString(atr)[3])
            return "1"

        for port in self.inputs:
            pwidth=busWidth(self.inputs[port])
            for s in TMR_SUFFIX:
                p("  wire %s_v%s;"%(port,s))
                p("  voter #(.WIDTH(%s)) %s_v%s "%(pwidth,port,s))
                p("  (")
                for ss in TMR_SUFFIX:
                    p("    .in%s(%s%s),"%(ss,port,ss))
                p("    .out(%s_v%s),"%(port,s))
                p("  );")

        p("  // -- logic --")

        parameters_str=""
        if len(self.parameters):
            parameters_str+="#(\n"
            for pid,param in enumerate(self.parameters):
                comma=""
                if pid!=len(self.parameters)-1: comma+=","
                parameters_str+="    .%s(%s)%s\n"%(param,param,comma)

            parameters_str+="  )"
        for s in TMR_SUFFIX:
            p("  %s %s inst%s"%(self.module_name,parameters_str,s))
            p("  (")
            for pid,port in enumerate(ports):
                comma=""
                if pid!=len(ports)-1: comma+=","
                p("    .%s(%s)%s"%(port,port+s,comma))
            p("  ); ")
        p("  // -- output voters --")

        p("endmodule //%s"%mod_tmr)

if __name__=="__main__":
    print "This module is not ment to be run!"

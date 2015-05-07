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
import logging
import textwrap

from pyparsing import *
import pyparsing

usePackrat = True
usePsyco = False

import glob


from prettytable import PrettyTable
from verilogFormater import VerilogFormater

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

DESIGN={}

class VerilogParser:
    def debugInModule(self,s,type=""):
        if self.current_module:
            self.logger.debug("%s:%-10s:%s"%(self.current_module["name"],type,s))
        else:
            self.logger.warning("No current module in debugInModule")
    def __init__(self):
        sys.setrecursionlimit(2000)
        self.formater=VerilogFormater()
        self.logger = logging.getLogger('VP ')
        self.registers={}
        self.inputs={}
        self.outputs={}
        self.inouts={}
        self.parameters={}
        self.nets={}
        self.portList=[]
        self.parametersList=[]
        self.nba=set()
        self.ba=set()
        self.instances={}
        self.dnt_from_source=set()
        self.tmr_from_source=set()
        self.module_name=""
        self.current_module=None
        # compiler directives
        self.EXT=("A","B","C")
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
        self.constraints = {"triplicate":set(),"do_not_triplicate":set(), "default":True, "tmr_error":False}

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

        subscrRef =      ( Suppress("[") +
                            (delimitedList( self.expr, ":" ) )  +
                           Suppress("]")
                         ).setResultsName("subscrRef")

        subscrIndxRef =      ( Suppress("[") +
                           (self.expr + oneOf("+ -") +  ":" + self.expr) +
                           Suppress("]")
                         ).setResultsName("subscrIndxRef")

        subscrIdentifier = Group( identifier +
                                  Group( Optional( subscrIndxRef | subscrRef ))
                                ).setResultsName("subscrIdentifier")
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
                  ).setResultsName("primary")

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
                             + Group(self.expr) ).setResultsName( "assgnmt" )
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
        self.nbAssgnmt = (( lvalue + Suppress("<=") + Group(Optional( delay)).setResultsName("delay") + Group(self.expr) ) |
                     ( lvalue + Suppress("<=") + Group(Optional( eventControl)).setResultsName("eventCtrl")
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

        def _getLenStr(toks):
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

        self.range = ( Suppress("[") + Group(self.expr) + Suppress(":") + Group(self.expr) + Suppress("]")).setResultsName("range")

        def gotParameter(s,loc,toks):
            #for p in toks[1]:
            #    pname=p[0]
            #    pval=" ".join(p[2:])
            #    self.parameters[pname]=pval
            #    self.parametersList.append(pname)
            return toks

        paramAssgnmt = Group( identifier + "=" + self.expr ).setResultsName("paramAssgnmt")


        parameterDecl      = Group( "parameter" + Group(Optional( self.range )) + Group(delimitedList( paramAssgnmt )) + self.semi).setResultsName("paramDecl")
        parameterDecl.setParseAction(gotParameter)
        localParameterDecl = Group("localparam" + Group( Optional( self.range )) + Group(delimitedList( paramAssgnmt )) + self.semi).setResultsName("localparamDecl")
        #localParameterDecl.setParseAction(gotParameter)

        def gotIO(resdict,s,loc,toks):

             toks=toks[0]
             _dir=toks[0]
             _atrs=""
             _range=self.formater.format(toks[1])
             _len=_getLenStr(toks[1])

             if _len!="1":
                 details="(range:%s len:%s)"%(_range,_len)
             else:
                 details=""


#             start=1
             _type=""
#             if toks[start] in ('reg','wire'):
#                 _type=toks[start]
#                 start+=1
#             atrs=""
#             for a in toks[1]:
#                 print str(a)
#                 atrs+=str(a)+" "
#             atrs=atrs.rstrip()

             for name in toks[-1]:
                 self.debugInModule("gotIO: %s %s"%(name,details),type=_dir)
                 resdict[name]={"atributes":_atrs,"tmr":True,"range":_range, "len":_len }
                 self.portList.append(name)
#                 if type=='reg':
#                     self.registers[name]={"atributes":_atrs,"tmr":True}
                 if not name in  self.current_module["nets"]:
                     self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len }

#             return toks
        self.inputDecl = Group( "input" + Group(Optional( self.range )).setResultsName("range") + Group(delimitedList( identifier )) + Suppress(self.semi) ).setResultsName("input")
        self.inputDecl.setParseAction(lambda s,loc,toks : gotIO(self.inputs,s,loc,toks))
        self.outputDecl = Group( "output" + Group(Optional( self.range )).setResultsName("range") + Group(delimitedList( identifier )) + Suppress(self.semi) ).setResultsName("output")
        self.outputDecl.setParseAction(lambda s,loc,toks : gotIO(self.outputs,s,loc,toks))
        inoutDecl = Group( "inout" + Group(Optional( self.range )).setResultsName("range") + Group(delimitedList( identifier )) + Suppress(self.semi) ).setResultsName("inout")
        inoutDecl.setParseAction(lambda s,loc,toks : gotIO(self.inouts,s,loc,toks))

        regIdentifier = Group( identifier + Optional( "[" + self.expr + ":" + self.expr + "]" ) )
        self.regDecl = Group( "reg" +
                              Group(Optional("signed")) +
                              Group(Optional( self.range)).setResultsName("range") +
                              Group( delimitedList( regIdentifier )) +
                              Suppress(self.semi)
                            ).setName("regDecl").setResultsName("regDecl")
        def gotReg(s,loc,toks):

            toks=toks[0] #self.registers
            _atrs=""
            _range=self.formater.format(toks[1])
            _len=_getLenStr(toks[1])

            if _len!="1":
                details="(range:%s len:%s)"%(_range,_len)
            else:
                details=""
            for reg in toks[-1]:
                 name=reg[0]
                 self.registers[name]={"atributes":_atrs,"range":_range, "len":_len ,"tmr":True}

                 self.debugInModule("gotReg: %s %s" % (name,details), type="regs")
                 if not name in  self.current_module["nets"]:
                     self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len }


        self.regDecl.setParseAction(gotReg)

        timeDecl = Group( "time" + delimitedList( regIdentifier ) + self.semi ).setResultsName("timeDecl")
        integerDecl = Group( "integer" + delimitedList( regIdentifier ) + Suppress(self.semi) ).setResultsName("integerDecl")

        strength0 = oneOf("supply0  strong0  pull0  weak0  highz0")
        strength1 = oneOf("supply1  strong1  pull1  weak1  highz1")
        driveStrength = Group( "(" + ( ( strength0 + "," + strength1 ) |
                                       ( strength1 + "," + strength0 ) ) + ")" ).setName("driveStrength").setResultsName("driveStrength")
        nettype = oneOf("wire  tri  tri1  supply0  wand  triand  tri0  supply1  wor  trior  trireg")
        expandRange = Group(Optional( oneOf("scalared vectored") )) + self.range
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
            ).setResultsName("continuousAssign")#.setDebug()


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
            "function" + Optional( self.range | "integer" | "real" ) + identifier + self.semi +
            Group( OneOrMore( tfDecl ) ) +
            Group( ZeroOrMore( self.stmt ) ) +
            "endfunction"
            ).setResultsName("functionDecl")

        inputOutput = oneOf("input output")

        def gotNet1(toks):
            toks=toks[0]

            _atrs=""
            _range=self.formater.format(toks[1])
            _len=_getLenStr(toks[1])

            for name in toks[3]:
                self.nets[name]={"atributes":_atrs,"range":_range, "len":_len ,"tmr":True}
                if _len!="1":
                    details="(range:%s len:%s)"%(_range,_len)
                else:
                    details=""
                self.debugInModule("gotNet: %s %s" % (name,details), type="nets")
                if not name in  self.current_module["nets"]:
                     self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len}

        self.netDecl1 = Group(nettype +
                              Group(Optional( expandRange )).setResultsName("range") +
                              Group(Optional( delay )) +
                              Group( delimitedList( identifier ) ) +
                              Suppress(self.semi)
                             ).setResultsName("netDecl1")

        self.netDecl1.setParseAction(gotNet1)

        self.netDecl2 = Group("trireg" +
                              Group(Optional( chargeStrength )) +
                              Group(Optional( expandRange )) +
                              Group(Optional( delay )) +
                              Group( delimitedList(  identifier ) )+
                              Suppress(self.semi)
                              ).setResultsName("netDecl2")


        def gotNet3(s,l,toks):
            toks=toks[0]
            _atrs=""
            _range=self.formater.format(toks[2])
            _len=_getLenStr(toks[2])

            for assgmng in toks[4]:
                name=assgmng[0][0]
                self.nets[name]={"atributes":_atrs,"range":_range, "len":_len ,"tmr":True}
                if _len!="1":
                    details="(range:%s len:%s)"%(_range,_len)
                else:
                    details=""
                self.debugInModule("gotNet: %s %s" % (name,details), type="nets")
                if not name in  self.current_module["nets"]:
                     self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len }

        self.netDecl3 = Group(nettype +
                              Group(Optional( driveStrength )) +
                              Group(Optional( expandRange )).setResultsName("range") +
                              Group(Optional( delay )) +
                              Group( delimitedList( Group(assgnmt) ) ) +
                              Suppress(self.semi)
                             ).setResultsName("netDecl3")
        self.netDecl3.setParseAction(gotNet3)

        gateType = oneOf("and  nand  or  nor xor  xnor buf  bufif0 bufif1 "
                         "not  notif0 notif1  pulldown pullup nmos  rnmos "
                         "pmos rpmos cmos rcmos   tran rtran  tranif0  "
                         "rtranif0  tranif1 rtranif1"  )
        gateInstance = Optional( Group( identifier + Optional( self.range ) ) ) + \
                        "(" + Group( delimitedList( self.expr ) ) + ")"
        gateDecl = Group( gateType +
            Optional( driveStrength ) +
            Optional( delay ) +
            delimitedList( gateInstance) +
            self.semi ).setResultsName("gate")

        udpInstance = Group( Group( identifier + Optional(self.range | subscrRef) ) +
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
        self.modulePortConnection = Group(self.expr | empty).setResultsName("modulePortConnection")
        moduleArgs = Group( Suppress("(") +
                            (delimitedList( self.modulePortConnection ) | delimitedList( namedPortConnection )) +
                            Suppress(")")
                          ).setResultsName("moduleArgs")#.setDebug()

        #parameterValueAssignment = Group( Literal("#") + "(" + Group( delimitedList( self.expr ) ) + ")" ).setResultsName("parameterValueAssignment")
        #namedPortConnection = Group( "." + identifier + "(" + self.expr + ")" ).setResultsName("namedPortConnection")
        #modulePortConnection = namedPortConnection | Group(self.expr).setResultsName("unnamedPortConnection")

        #moduleArgs = Group( "(" + (delimitedList( modulePortConnection ) |
                    #delimitedList( modulePortConnection )) + ")").setName("inst_args").setResultsName("moduleArgs")#.setDebug()

        moduleInstance = Group( Group ( identifier +
                                        Group(Optional(self.range)).setResultsName("range") ) +
                                moduleArgs
                              ).setResultsName("moduleInstance")

        self.moduleInstantiation = Group( identifier +
                                          Group(Optional( parameterValueAssignment )) +
                                          Group(delimitedList( moduleInstance )).setResultsName("moduleInstantiation") +
                                          Suppress(self.semi)
                                        ).setResultsName("moduleInstantiation")

        def gotModuleInstantiation(s,loc,toks):
            toks=toks[0]
            identifier=toks[0]
            instance = toks[2][0][0][0]
            self.debugInModule("'%s' (type:%s)"%(instance,identifier),type="instance")
#            print "+",instname, module
            self.instances[instance]={"atributes":identifier,"tmr":True}
            self.current_module["instances"].append({"identifier":identifier, "instance":instance})
            self.current_module["instantiated"]=0
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
            #print "taks"
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
        portIn   = Group( "input"  +  Group(Optional( self.range )).setResultsName("range") + Group(identifier).setResultsName("names")).setResultsName("inputHdr")
        portOut  = Group( "output" +  Group(Optional( self.range )).setResultsName("range") + Group(identifier).setResultsName("names")).setResultsName("outputHdr")
        portInOut= Group( "inout"  +  Group(Optional( self.range )).setResultsName("range") + Group(identifier).setResultsName("names")).setResultsName("inoutHdr")

        portIn.setParseAction(lambda s,loc,toks : gotIO(self.inputs,s,loc,toks))
        portOut.setParseAction(lambda s,loc,toks : gotIO(self.outputs,s,loc,toks))
        portInOut.setParseAction(lambda s,loc,toks : gotIO(self.inouts,s,loc,toks))


        moduleHdr = Group ( oneOf("module macromodule") + Group(identifier).setResultsName("moduleName") +
                            Group(Optional( Suppress("(") +
                                             Optional( delimitedList( portIn | portOut | portInOut | port ) )  +
                                            Suppress(")") )).setResultsName("ports") +
                            Suppress(self.semi) ).setName("moduleHdr").setResultsName("moduleHdr")
        def gotModuleHdr(s,loc,toks):
            self.module_name=toks[0][1][0]

            self.current_module={"instances":[],"nets":{},"name":toks[0][1][0]}

            self.debugInModule("New module found")
#            print ">",self.module_name
            return toks
        moduleHdr.addParseAction(gotModuleHdr)

        def gotEndModule(s,loc,toks):
            if self.current_module:
                self.logger.info("Parsed module %s"%self.current_module["name"])
                DESIGN[self.current_module["name"]]=self.current_module
        self.endmodule=Keyword("endmodule").setResultsName("endModule").addParseAction(gotEndModule)


        self.module = Group(  moduleHdr +
                 Group( ZeroOrMore( self.moduleItem ) ).setResultsName("moduleBody") +
                 self.endmodule ).setName("module").setResultsName("module")#.setDebug()


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
        verilogbnf = (OneOrMore( self.module | udp ) + StringEnd()).setName("top").setResultsName("top")

#        specialComment = '//##' + Word(alphanums) + '##' + Word(alphanums+'.') + "::" + Word(nums)
#        def dontMatchSpecialComments(tokens):
#            if tokens[0] == specialComment:
#                raise ParseException("don't match special comments")
#        cppStyleComment.setParseAction(dontMatchSpecialComments)
        tmrg=Suppress("tmrg")

        self.directive_doNotTriplicate  =( tmrg + Suppress("do_not_triplicate") + OneOrMore(identifier)                ).setResultsName("directive_do_not_triplicate")
        self.directive_triplicate       =( tmrg + Suppress("triplicate")        + OneOrMore(identifier)                ).setResultsName("directive_triplicate")
        self.directive_default          =( tmrg + Suppress("default")           + oneOf("triplicate do_not_triplicate")).setResultsName("directive_default")
        self.directive_tmr_error        =( tmrg + Suppress("tmr_error")         + oneOf("true false")                  ).setResultsName("directive_tmr_error")

        self.directiveItem =  ( self.directive_triplicate |
                                self.directive_doNotTriplicate |
                                self.directive_default |
                                self.directive_tmr_error
                                )


        def gotComment(s,l,t):
            #res=self.directive_do_not_triplicate.searchString(t[0])
            #for tokens in  res:
            #    self.dnt_from_source.add(tokens[0])
            #res=self.directive_triplicate.searchString(t[0])
            #for tokens in  res:
#                print "+",tokens[0]
            #    self.tmr_from_source.add(tokens[0])
            #print s,l,t
            res=self.directiveItem.searchString(t[0])
            for tokens in  res:
                constraint=tokens.getName()[len("directive_"):]
                if constraint in ("triplicate","do_not_triplicate"):
                    for token in tokens:
                        self.constraints[constraint].add(token)
                elif constraint=="default":
                    if tokens[0]=="triplicate":
                        self.constraints["default"]=True
                    else:
                        self.constraints["default"]=False
                elif constraint=="tmr_error":
                    if tokens[0]=="true":
                        self.constraints["tmr_error"]=True
                    else:
                        self.constraints["tmr_error"]=False


#           return t
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
        self.fsm=False
        self.fsm_regs=[]
        for r1 in self.registers:
            for r2 in self.registers:
                if r1+"Next"==r2:
                    self.fsm=True
                    self.fsm_regs.append((r1,r2))
                    if self.registers[r1]["atributes"]!=self.registers[r2]["atributes"]:
                        self.logger.warning( "Warning! Inconsistent register declaration ")
                        self.logger.warning( "  %s -> %s"%(r1,self.registers[r1]["atributes"]))
                        self.logger.warning( "  %s -> %s"%(r2,self.registers[r2]["atributes"]))
        if self.fsm:
            self.errorOut=1

    def _detectPost(self):
        for r1 in self.current_module["nets"].keys():
            for r2 in sorted(self.ba.union(self.nba)):
                for post in self.EXT:
                    if r1+post==r2:
                        print r1,r2
                        if r2 in self.toTMR:
                            self.logger.info("Net %s will not be triplicated"%r2)
                            self.toTMR.remove(r2)

    def _detectVoting(self):
        self.voting_nets=[]
        #for r1 in self.ba.union(self.nba):
        #    for r2 in self.ba.union(self.nba):
        for r1 in self.current_module["nets"].keys():
            for r2 in sorted(self.ba.union(self.nba)):
                if r1+"Voted"==r2:
                    self.voting_nets.append((r1,r2))
        if len(self.voting_nets):
            self.logger.info("Voting present (%d nets)"%(len(self.voting_nets)))
#        if self.fsm:
#            self.errorOut=1

    def applyConstraints(self):
        self.logger.debug("Applying constraints")
        wrapper = textwrap.TextWrapper(width=80)
        self.logger.debug("  Default          : %s"%("triplicate" if self.constraints["default"] else "do_not_triplicate"))
        wrapper.initial_indent   ="  Triplicate       : "
        wrapper.subsequent_indent=" "*4
        map( self.logger.debug,  wrapper.wrap(" ".join(sorted(self.constraints["triplicate"]))))
        wrapper.initial_indent   ="  Do not triplicate: "
        map( self.logger.debug,  wrapper.wrap(" ".join(sorted(self.constraints["do_not_triplicate"]))))

        self.toTMR=set()
        self.ids=set()
        for v in self.registers : self.ids.add(v)
        for v in self.nets : self.ids.add(v)
        for v in self.inputs : self.ids.add(v)
        for v in self.outputs : self.ids.add(v)
        for v in self.inouts : self.ids.add(v)
        for v in self.registers : self.ids.add(v)
        for v in self.nba : self.ids.add(v)
        for v in self.ba : self.ids.add(v)
        for v in self.instances : self.ids.add(v[0])
        #for v in self.tmr_from_source:self.ids.add(v)

        wrapper.initial_indent   ="  IDs found        : "
        map( self.logger.debug,  wrapper.wrap(" ".join(sorted(self.ids))))

        if self.constraints["default"] : #triplicate
            for i in self.ids:
                if i not in self.constraints["do_not_triplicate"]:
                    self.toTMR.add(i)
        else: # do not triplicate by default
            for i in self.constraints["triplicate"]:
                if i in self.ids:
                    self.toTMR.add(i)
                else:
                    self.logger.warning("Unable to apply constrain for '%s' as it has not been found in the design."%i)

        wrapper.initial_indent   ="  IDs to TMR       : "
        map( self.logger.debug,  wrapper.wrap(" ".join(sorted(self.toTMR))))


        self.applyDntConstrains(self.dnt_from_source)


    def parseString( self,strng ):
        self.verilog=strng
        self.tokens=self.verilogbnf.parseString( strng )
        #self._detectFsm()
        self._detectVoting()
        self.applyConstraints()
        self._detectPost()
        return self.tokens

    def printInfo(self):
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
#                print k,item
                range=item["range"]
                tmr=item["tmr"]
                tab.add_row([k,range, tmr])
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
        printDict(self.nets,      "Nets")
        printDict(self.inputs,    "Inputs")
        printDict(self.outputs,   "Outputs")
        printDict(self.inouts,    "InOuts")
        printDict(self.parameters,"Parameters")
        printSet(self.nba,        "Non Blocking")
        printSet(self.ba,         "Blocking")
        printDict(self.instances, "Instantiations")
        if 1:
            print "TMR:"
            for x in  sorted(self.toTMR):
                print x,
            print
            print "NETS:"
            for x in  sorted(self.current_module["nets"]):
                print x,
            print
#        if self.fsm:
#            l=[]
#            for r1,r2 in self.fsm_regs:
#                atrs=""
#                if self.registers[r1]["atributes"]!="":
#                    atrs="(%s)"%self.registers[r1]["atributes"]
#                l.append("%s <- %s %s"%(r1,r2,atrs))
#            printSet(l,   "FSM")


if __name__=="__main__":
    print "This module is not ment to be run!"


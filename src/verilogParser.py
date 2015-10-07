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
import copy

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

class VerilogParser:

    def __init__(self):
        sys.setrecursionlimit(2000)
        self.logger = logging.getLogger('VP')

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
        self.constraints = {"triplicate":set(),"do_not_triplicate":set(), "default":True, "tmr_error":True}

        identLead = alphas+"$_"
        identBody = alphanums+"$_"
        identifier1 = Regex( r"\.?`?["+identLead+"]["+identBody+"]*(\.["+identLead+"]["+identBody+"]*)*").setName("baseIdent")
        identifier2 = Regex(r"\\\S+").setParseAction(lambda t:t[0][1:]).setName("escapedIdent")
        identifier = ( identifier1 | identifier2).setResultsName("id")

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
                            (delimitedList( Group(self.expr), ":" ) )  +
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
                       "||  <  <=  >  >=  &  |  ^  ^~  ~^  >>  << ** <<< >>>" ).setName("binop")
        inlineIfExpr= Group( Group(primary) + Suppress(Literal("?")) + Group(self.expr) + Suppress(Literal(":")) + Group(self.expr) ).setResultsName("inlineIfExpr")

        self.expr << (
                ( unop + self.expr ) |  # must be first!
                inlineIfExpr |
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

        self.assgnmt   = ( lvalue + Suppress("=") + Group(Optional( delayOrEventControl )).setResultsName("delayOrEventControl")
                             + Group(self.expr) ).setResultsName( "assgnmt" )

        self.nbAssgnmt = (( lvalue + Suppress("<=") + Group(Optional( delay)).setResultsName("delay")            + Group(self.expr) ) |
                          ( lvalue + Suppress("<=") + Group(Optional( eventControl)).setResultsName("eventCtrl") + Group(self.expr) )
                         ).setResultsName( "nbassgnmt" )

        self.range = ( Suppress("[") + Group(self.expr) + Suppress(":") + Group(self.expr) + Suppress("]")).setResultsName("range")

        paramAssgnmt = Group( identifier + Suppress("=") + self.expr ).setResultsName("paramAssgnmt")


        parameterDecl      = Group( "parameter" + Group(Optional( self.range )) + Group(delimitedList( paramAssgnmt )) + self.semi).setResultsName("paramDecl")
        localParameterDecl = Group("localparam" + Group(Optional( self.range )) + Group(delimitedList( paramAssgnmt )) + self.semi).setResultsName("localparamDecl")

        self.inputDecl  = Group( "input"  + Group(Optional(oneOf("wire reg"))) +  Group(Optional( self.range )).setResultsName("range") + Group(delimitedList( identifier )) + Suppress(self.semi) ).setResultsName("input")
        self.outputDecl = Group( "output" + Group(Optional(oneOf("wire reg"))) + Group(Optional( self.range )).setResultsName("range") + Group(delimitedList( identifier )) + Suppress(self.semi) ).setResultsName("output")
        inoutDecl = Group( "inout" + Group(Optional( self.range )).setResultsName("range") + Group(delimitedList( identifier )) + Suppress(self.semi) ).setResultsName("inout")

        regIdentifier = Group( identifier + Optional( "[" + self.expr + ":" + self.expr + "]" ) )
        self.regDecl = Group( "reg" +
                              Group(Optional("signed")) +
                              Group(Optional( self.range)).setResultsName("range") +
                              Group( delimitedList( regIdentifier )) +
                              Suppress(self.semi)
                            ).setName("regDecl").setResultsName("regDecl")

        timeDecl = Group( "time" + delimitedList( regIdentifier ) + self.semi ).setResultsName("timeDecl")
        integerDecl = Group( "integer" + Group(delimitedList( regIdentifier )) + Suppress(self.semi) ).setResultsName("integerDecl")

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
        caseItem = Group( Group(delimitedList( self.expr )) + Suppress(":") + stmtOrNull ).setResultsName("caseItem") | \
                   Group( default + Optional(":") + stmtOrNull )
        condition=Group("(" + self.expr + ")").setResultsName("condition")
        self.stmt <<  ( Group( begin +  ZeroOrMore( self.stmt )  + end ).setName("beginend").setResultsName("beginend") | \
            Group( if_ + condition + stmtOrNull +  else_ + stmtOrNull ).setName("ifelse").setResultsName("ifelse") | \
            Group( if_ + condition + stmtOrNull  ).setName("if").setResultsName("if") |\
            Group( delayOrEventControl + stmtOrNull ).setResultsName("delayStm") |\
            Group( case + Suppress("(") + Group(self.expr) + Suppress(")") + Group(OneOrMore( caseItem )) + endcase ).setResultsName("case") |\
            Group( forever + self.stmt ).setResultsName("forever") |\
            Group( repeat + "(" + self.expr + ")" + self.stmt ) |\
            Group( while_ + "(" + self.expr + ")" + self.stmt ) |\
            Group( for_ + Suppress("(") + Group(self.assgnmt) + Suppress(self.semi) + Group( self.expr ) + Suppress(self.semi) + Group(self.assgnmt) + Suppress(")") + self.stmt ).setResultsName("forstmt") |\
            Group( fork + ZeroOrMore( self.stmt ) + join ) |\
            Group( fork + ":" + identifier + ZeroOrMore( blockDecl ) + ZeroOrMore( self.stmt ) + end ) |\
            Group( wait + "(" + self.expr + ")" + stmtOrNull ) |\
            Group( "->" + identifier + self.semi ) |\
            Group( disable + identifier + self.semi ) |\
            Group( assign + self.assgnmt + self.semi ).setResultsName("assign") |\
            Group( deassign + lvalue + self.semi ) |\
            Group( force + self.assgnmt + self.semi ) |\
            Group( release + lvalue + self.semi ) |\
            Group( Suppress(begin) + Suppress(Literal(":")) + identifier + ZeroOrMore( blockDecl ) + ZeroOrMore( self.stmt ) + Suppress(end) ).setResultsName("beginEndLabel") |\
            Group( Group(self.assgnmt) + Suppress(self.semi) ).setResultsName("assgnmtStm") |\
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
        initialStmt = Group( Keyword("initial") + self.stmt ).setName("initialStmt").setResultsName("initialStmt")

        chargeStrength = Group( "(" + oneOf( "small medium large" ) + ")" ).setName("chargeStrength")

        self.continuousAssign = Group(  Suppress(assign)
              + Group(Optional( driveStrength )).setResultsName("driveStrength")
              + Group(Optional( delay )).setResultsName("delay")
              + Group(delimitedList( Group(self.assgnmt) )) + Suppress(self.semi)
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
                              Group( delimitedList( Group(self.assgnmt) ) ) +
                              Suppress(self.semi)
                             ).setResultsName("netDecl3")

        self.genVarDecl = Group(Keyword("genvar") +
                                self.expr +
                                Suppress(self.semi)
                               ).setResultsName("genVarDecl")

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

        parameterOverride = Group( "defparam" + delimitedList( paramAssgnmt ) + self.semi )
        task = Group( Suppress("task") + identifier + Suppress(self.semi) +
            Group(ZeroOrMore( tfDecl )) +
            stmtOrNull +
            "endtask" ).setResultsName("task")

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

        tmrg=Suppress("tmrg")

        self.directive_doNotTriplicate  = Group( tmrg + Suppress("do_not_triplicate") + OneOrMore(identifier)                + Suppress(self.semi)).setResultsName("directive_do_not_triplicate")
        self.directive_triplicate       = Group( tmrg + Suppress("triplicate")        + OneOrMore(identifier)                + Suppress(self.semi)).setResultsName("directive_triplicate")
        self.directive_default          = Group( tmrg + Suppress("default")           + oneOf("triplicate do_not_triplicate")+ Suppress(self.semi)).setResultsName("directive_default")
        self.directive_tmr_error        = Group( tmrg + Suppress("tmr_error")         + oneOf("true false")                  + Suppress(self.semi)).setResultsName("directive_tmr_error")
        self.directive_do_not_touch     = Group( tmrg + ("do_not_touch") + Suppress(self.semi)).setResultsName("directive_do_not_touch")
        self.directive_seu_set          = Group( tmrg + Suppress("seu_set") + identifier + Suppress(self.semi)).setResultsName("directive_seu_set")
        self.directive_seu_reset        = Group( tmrg + Suppress("seu_reset") + identifier +  Suppress(self.semi)).setResultsName("directive_seu_reset")
        self.directive_slicing          = Group( tmrg + ("slicing") + Suppress(self.semi)).setResultsName("directive_slicing")
        self.directive_translate        = Group( tmrg + Suppress("translate")       + oneOf("on off")+ Suppress(self.semi)).setResultsName("directive_translate")

        self.comp_directive = Group(Suppress("__COMP_DIRECTIVE") + CharsNotIn(";") + Suppress(self.semi)).setResultsName("comp_directive")

        synopsys=Keyword("synopsys")
        self.directive_synopsys        = Group( synopsys + oneOf("translate_off translate_on") + Suppress(self.semi)).setResultsName("directive_synopsys")

        """
        x::= <specparam_declaration>
        x||= <path_declaration>
        x||= <level_sensitive_path_declaration>
        x||= <edge_sensitive_path_declaration>
        x||= <system_timing_check>
        x||= <sdpd>
        """
        specifyBlock = Group( "specify" + ZeroOrMore( specifyItem ) + "endspecify" )



        self.moduleOrGenerateItem = ~Keyword("endmodule") + (
            parameterDecl |
            localParameterDecl |
            self.inputDecl |
            self.outputDecl |
            inoutDecl |
            self.regDecl |
            self.netDecl3 |
            self.netDecl1 |
            self.netDecl2 |
            self.genVarDecl |
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
            self.directive_doNotTriplicate |
            self.directive_triplicate |
            self.directive_default |
            self.directive_tmr_error |
            self.directive_do_not_touch |
            self.directive_seu_set |
            self.directive_seu_reset |
            self.comp_directive |
            self.directive_slicing |
            self.directive_translate |
            self.directive_synopsys |
            # these have to be at the end - they start with identifiers
            self.moduleInstantiation
            )

#        generate_module_case_statement =Keyword("case")+  "(" + self.expr + ")" genvar_module_case_item { genvar_module_case_item } Keyword("endcase")

        #genvar_module_case_item ::=
        #constant_expression { , constant_expression } : generate_module_item
        #|	default [ : ] generate_module_item
        #generate_module_item = Forward()
        #generate_module_conditional_statement = Keyword("if") + self.expr + generate_module_item + Group(Optional(Keyword("else") +  generate_module_item ))

        generate_module_named_block = Group(Suppress(Keyword("begin") + ":")  + identifier + OneOrMore(self.moduleOrGenerateItem) +  Suppress(Keyword("end")) + Group(Optional(":" + identifier))).setResultsName("generate_module_named_block")

        genvar_decl_assignment = Group(identifier + "=" +self.expr).setResultsName("genvar_decl_assignment")

        #self.assgnmt   = ( lvalue + Suppress("=") + Group(Optional( delayOrEventControl )).setResultsName("delayOrEventControl")
#                             + Group(self.expr) ).setResultsName( "assgnmt" )

        generate_module_loop_statement = Group( Suppress(Keyword("for")) +
                                                  Suppress("(")  +
                                                  genvar_decl_assignment +
                                                  Suppress(self.semi) +
                                                  Group(self.expr) +
                                                  Suppress(self.semi) +
                                                  Group(self.assgnmt) +
                                                  Suppress(")") +
                                                  generate_module_named_block
                                               ).setResultsName("generate_module_loop_statement")

#genvar_assignment ::=
#genvar_identifier assignment_operator constant_expression
#|	inc_or_dec_operator genvar_identifier
#|	genvar_identifier inc_or_dec_operator
#genvar_decl_assignment ::=
#[ genvar ] genvar_identifier = constant_expression
#generate_module_named_block ::=
#begin : generate_block_identifier { generate_module_item } end [ : generate_block_identifier ]
#|	generate_block_identifier : generate_module_block
#generate_module_block ::=
#begin [ : generate_block_identifier ] { generate_module_item } end [ : generate_block_identifier ]

        generate_body =  generate_module_loop_statement |  self.moduleOrGenerateItem

#                                |	generate_module_case_statement\



        generate = Group( Suppress(Keyword("generate")) + generate_body  + Suppress(Keyword("endgenerate"))).setResultsName("generate")


        self.moduleItem= generate | self.moduleOrGenerateItem

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
        self.port = Group(portExpr | Group( ( "." + identifier + "(" + portExpr + ")" ) ) ).setResultsName("port")

        inputOutput = oneOf("input output")
        self.portIn   = Group( Keyword("input")  + Group(Optional(oneOf("wire reg"))) +  Group(Optional( self.range )).setResultsName("range") + Group(identifier).setResultsName("names")).setResultsName("inputHdr")
        self.portOut  = Group( Keyword("output") + Group(Optional(oneOf("wire reg"))) +  Group(Optional( self.range )).setResultsName("range") + Group(identifier).setResultsName("names")).setResultsName("outputHdr")
        self.portInOut= Group( Keyword("inout")  +  Group(Optional( self.range )).setResultsName("range") + Group(identifier).setResultsName("names")).setResultsName("inoutHdr")



        moduleHdr = Group ( oneOf("module macromodule") + identifier.setResultsName("moduleName") +
                            Group(Optional( Suppress("(") +
                                             Optional( delimitedList( self.portIn | self.portOut | self.portInOut | self.port ) )  +
                                            Suppress(")") )).setResultsName("ports") +
                            Suppress(self.semi) ).setName("moduleHdr").setResultsName("moduleHdr")

        self.endmodule=Keyword("endmodule").setResultsName("endModule")

        self.module = Group(  moduleHdr +
                 Group( ZeroOrMore( self.moduleItem ) ).setResultsName("moduleBody") +
                 self.endmodule ).setName("module").setResultsName("module")


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
        verilogbnf = (OneOrMore( self.module | udp | self.comp_directive ) + StringEnd()).setName("top").setResultsName("top")

#        specialComment = '//##' + Word(alphanums) + '##' + Word(alphanums+'.') + "::" + Word(nums)
#        def dontMatchSpecialComments(tokens):
#            if tokens[0] == specialComment:
#                raise ParseException("don't match special comments")
#        cppStyleComment.setParseAction(dontMatchSpecialComments)

#           return t
        verilogbnf.ignore( cppStyleComment )
        #verilogbnf.ignore( self.compilerDirective )

        self.verilogbnf=verilogbnf

        self.tmrgDirective = (Suppress('//') + "tmrg" + restOfLine).setResultsName("directive")
        def tmrgDirectiveAction(toks):
            return " ".join(toks)+ ";"
        self.tmrgDirective.setParseAction(tmrgDirectiveAction)

        self.synopsysDirective = (Suppress('//') + "synopsys" + restOfLine).setResultsName("synopsysDirective")
        def synopsysDirectiveAction(toks):
            return " ".join(toks)+ ";"
        self.synopsysDirective.setParseAction(synopsysDirectiveAction)

        self.compDirective = (Suppress('`') + oneOf("define undef include elsif else endif timescale ifdef ifndef")+ restOfLine).setResultsName("compDirective")
        def compDirectiveAction(toks):
            return "__COMP_DIRECTIVE "+" ".join(toks)+ ";"
        self.compDirective.setParseAction(compDirectiveAction)

    def parseFile(self,fname):
        self.logger.debug("Parsing file '%s'"%fname)
        self.fname=fname
        f=open(fname,"r")
        body=f.read()
        f.close()
        return self.parseString(body)

    def parseString( self,strng ):
        #self.tmrgDirective = (Suppress('//') + Suppress("tmrg") + OneOrMore(Word(alphanums))).setResultsName("directive")
        preParsedStrng = self.tmrgDirective.transformString( strng )
        preParsedStrng = self.synopsysDirective.transformString( preParsedStrng )
        preParsedStrng = self.compDirective.transformString(preParsedStrng)
        preParsedStrngNew=""
        translate=True
#        self.directive_translate        = Group( tmrg + Suppress("translate")       + oneOf("on off")+ Suppress(self.semi)).setResultsName("directive_translate")

        for line in preParsedStrng.splitlines():
            try:
                parse=self.directive_translate.parseString(line)
            #greeting = greet.parseString( "``DUPA" )
                if parse[0][0].lower()=="off" : translate=False
                else: translate=True
            except:
                pass
            if translate:
                preParsedStrngNew+=line+"\n"
#                print translate, line
        #print preParsedStrng
        self.verilog=preParsedStrngNew
        self.tokens=self.verilogbnf.parseString( preParsedStrngNew )
        return self.tokens

if __name__=="__main__":
    print "This module is not ment to be run!"


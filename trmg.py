#!/usr/bin/env python

from optparse import OptionParser

#
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

from pyparsing import Literal, CaselessLiteral, Keyword, Word, Upcase, OneOrMore, ZeroOrMore, \
        Forward, NotAny, delimitedList, Group, Optional, Combine, alphas, nums, restOfLine, cStyleComment, \
        alphanums, printables, dblQuotedString, empty, ParseException, ParseResults, MatchFirst, oneOf, GoToColumn, \
        ParseResults,StringEnd, FollowedBy, ParserElement, And, Regex, cppStyleComment#,__version__
import pyparsing
usePackrat = True
usePsyco = False

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


class VerilogParser:
    def __init__(self):
        self.registers={}
        self.inputs={}
        self.outputs={}
        self.inouts={}
        self.parameters={}
        self.nba=set()
        self.ba=set()

        # compiler directives
        compilerDirective = Combine( "`" + \
            oneOf("define undef ifdef else endif default_nettype "
                  "include resetall timescale unconnected_drive "
                  "nounconnected_drive celldefine endcelldefine") + \
            restOfLine ).setName("compilerDirective")

        # primitives
        semi = Literal(";")
        lpar = Literal("(")
        rpar = Literal(")")
        equals = Literal("=")

        identLead = alphas+"$_"
        identBody = alphanums+"$_"
        identifier1 = Regex( r"\.?["+identLead+"]["+identBody+"]*(\.["+identLead+"]["+identBody+"]*)*"
                            ).setName("baseIdent")
        identifier2 = Regex(r"\\\S+").setParseAction(lambda t:t[0][1:]).setName("escapedIdent")
        identifier = identifier1 | identifier2
        
        hexnums = nums + "abcdefABCDEF" + "_?"
        base = Regex("'[bBoOdDhH]").setName("base")
        basedNumber = Combine( Optional( Word(nums + "_") ) + base + Word(hexnums+"xXzZ"),
                               joinString=" ", adjacent=False ).setName("basedNumber")
        #~ number = ( basedNumber | Combine( Word( "+-"+spacedNums, spacedNums ) +
                           #~ Optional( "." + Optional( Word( spacedNums ) ) ) +
                           #~ Optional( e + Word( "+-"+spacedNums, spacedNums ) ) ).setName("numeric") )
        number = ( basedNumber | \
                   Regex(r"[+-]?[0-9_]+(\.[0-9_]*)?([Ee][+-]?[0-9_]+)?") \
                  ).setName("numeric")
        #~ decnums = nums + "_"
        #~ octnums = "01234567" + "_"
        self.expr = Forward().setName("expr")
        concat = Group( "{" + delimitedList( self.expr ) + "}" )
        multiConcat = Group("{" + self.expr + concat + "}").setName("multiConcat")
        funcCall = Group(identifier + "(" + Optional( delimitedList( self.expr ) ) + ")").setName("funcCall")

        subscrRef = Group("[" + delimitedList( self.expr, ":" ) + "]")
        subscrIdentifier = Group( identifier + Optional( subscrRef ) )
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

        lvalue = subscrIdentifier | concat

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
        assign     = Keyword("assign")

        eventExpr = Forward()
        eventTerm = ( posedge + self.expr ) | ( negedge + self.expr ) | self.expr | ( "(" + eventExpr + ")" )
        eventExpr << (
            Group( delimitedList( eventTerm, "or" ) )
            )
        eventControl = Group( "@" + ( ( "(" + eventExpr + ")" ) | identifier | "*" ) ).setName("eventCtrl")

        delayArg = ( number |
                     Word(alphanums+"$_") | #identifier |
                     ( "(" + Group( delimitedList( mintypmaxExpr | self.expr ) ) + ")" )
                   ).setName("delayArg")#.setDebug()
        delay = Group( "#" + delayArg ).setName("delay")#.setDebug()
        delayOrEventControl = delay | eventControl

        assgnmt   = ( lvalue + "=" + Optional( delayOrEventControl ) + self.expr ).setName( "assgnmt" )
        def gotAssgnmt(s,loc,toks):
            lhs=toks[0]
            if len(lhs)>=1 and lhs[0]=="{": #concatenation
                for v in lhs[1:-1]:
                    self.ba.add(v[0])
            else:
                self.ba.add(lhs[0])

        assgnmt.setParseAction(gotAssgnmt)
        nbAssgnmt = (( lvalue + "<=" + Optional( delay ) + self.expr ) |
                     ( lvalue + "<=" + Optional( eventControl ) + self.expr )).setName( "nbassgnmt" )
        def gotNbAssgnmt(s,loc,toks):
            lhs=toks[0]
            if len(lhs)>=1 and lhs[0]=="{": #concatenation
                for v in lhs[1:-1]:
                    self.nba.add(v[0])
            else:
                self.nba.add(lhs[0])

        nbAssgnmt.setParseAction(gotNbAssgnmt)
        range = "[" + self.expr + ":" + self.expr + "]"

        def gotParameter(s,loc,toks):
            for p in toks[1]:
                pname=p[0]
                pval=" ".join(p[2:])
                self.parameters[pname]=pval

        paramAssgnmt = Group( identifier + "=" + self.expr ).setName("paramAssgnmt")
        parameterDecl = ( "parameter" + Optional( range ) + Group(delimitedList( paramAssgnmt )) + semi).setName("paramDecl")
        parameterDecl.setParseAction(gotParameter)

        def gotIO(resdict,s,loc,toks):
            atrs=""
            for a in toks[0][1:-2]:
                atrs+=a+" "
            atrs=atrs.rstrip()
            for regnames in toks[0][-2]:
                resdict[regnames]=atrs

        inputDecl = Group( "input" + Optional( range ) + Group(delimitedList( identifier )) + semi )
        inputDecl.setParseAction(lambda s,loc,toks : gotIO(self.inputs,s,loc,toks))
        outputDecl = Group( "output" + Optional( range ) + Group(delimitedList( identifier )) + semi )
        outputDecl.setParseAction(lambda s,loc,toks : gotIO(self.outputs,s,loc,toks))
        inoutDecl = Group( "inout" + Optional( range ) + Group(delimitedList( identifier )) + semi )
        inoutDecl.setParseAction(lambda s,loc,toks : gotIO(self.inouts,s,loc,toks))

        regIdentifier = Group( identifier + Optional( "[" + self.expr + ":" + self.expr + "]" ) )
        regDecl = Group( "reg" + Optional("signed") + Optional( range ) + Group( delimitedList( regIdentifier )) + semi ).setName("regDecl").setResultsName("regDecl")
        def gotReg(s,loc,toks):
            #self.registers
            atrs=""
            for a in toks[0][1:-2]:
                atrs+=a+" "
            atrs=atrs.rstrip()
            for regnames in toks[0][-2]:
                self.registers[regnames[0]]=atrs
        regDecl.setParseAction(gotReg)

        timeDecl = Group( "time" + delimitedList( regIdentifier ) + semi )
        integerDecl = Group( "integer" + delimitedList( regIdentifier ) + semi )

        strength0 = oneOf("supply0  strong0  pull0  weak0  highz0")
        strength1 = oneOf("supply1  strong1  pull1  weak1  highz1")
        driveStrength = Group( "(" + ( ( strength0 + "," + strength1 ) |
                                       ( strength1 + "," + strength0 ) ) + ")" ).setName("driveStrength")
        nettype = oneOf("wire  tri  tri1  supply0  wand  triand  tri0  supply1  wor  trior  trireg")
        expandRange = Optional( oneOf("scalared vectored") ) + range
        realDecl = Group( "real" + delimitedList( identifier ) + semi )

        eventDecl = Group( "event" + delimitedList( identifier ) + semi )

        blockDecl = (
            parameterDecl |
            regDecl |
            integerDecl |
            realDecl |
            timeDecl |
            eventDecl
            )

        stmt = Forward().setName("stmt")#.setDebug()
        stmtOrNull = stmt | semi
        caseItem = ( delimitedList( self.expr ) + ":" + stmtOrNull ) | \
                   ( default + Optional(":") + stmtOrNull )
        stmt << Group(
            ( begin + Group( ZeroOrMore( stmt ) ) + end ).setName("begin-end") |
            ( if_ + Group("(" + self.expr + ")") + stmtOrNull + Optional( else_ + stmtOrNull ) ).setName("if") |
            ( delayOrEventControl + stmtOrNull ) |
            ( case + "(" + self.expr + ")" + OneOrMore( caseItem ) + endcase ) |
            ( forever + stmt ) |
            ( repeat + "(" + self.expr + ")" + stmt ) |
            ( while_ + "(" + self.expr + ")" + stmt ) |
            ( for_ + "(" + assgnmt + semi + Group( self.expr ) + semi + assgnmt + ")" + stmt ) |
            ( fork + ZeroOrMore( stmt ) + join ) |
            ( fork + ":" + identifier + ZeroOrMore( blockDecl ) + ZeroOrMore( stmt ) + end ) |
            ( wait + "(" + self.expr + ")" + stmtOrNull ) |
            ( "->" + identifier + semi ) |
            ( disable + identifier + semi ) |
            ( assign + assgnmt + semi ) |
            ( deassign + lvalue + semi ) |
            ( force + assgnmt + semi ) |
            ( release + lvalue + semi ) |
            ( begin + ":" + identifier + ZeroOrMore( blockDecl ) + ZeroOrMore( stmt ) + end ).setName("begin:label-end") |
            # these  *have* to go at the end of the list!!!
            ( assgnmt + semi ) |
            ( nbAssgnmt + semi ) |
            ( Combine( Optional("$") + identifier ) + Optional( "(" + delimitedList(self.expr|empty) + ")" ) + semi )
            ).setName("stmtBody")
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
        alwaysStmt = Group( "always" + Optional(eventControl) + stmt ).setName("alwaysStmt")
        initialStmt = Group( "initial" + stmt ).setName("initialStmt")

        chargeStrength = Group( "(" + oneOf( "small medium large" ) + ")" ).setName("chargeStrength")

        continuousAssign = Group(
            assign + Optional( driveStrength ) + Optional( delay ) + delimitedList( assgnmt ) + semi
            ).setName("continuousAssign")


        tfDecl = (
            parameterDecl |
            inputDecl |
            outputDecl |
            inoutDecl |
            regDecl |
            timeDecl |
            integerDecl |
            realDecl
            )

        functionDecl = Group(
            "function" + Optional( range | "integer" | "real" ) + identifier + semi +
            Group( OneOrMore( tfDecl ) ) +
            Group( ZeroOrMore( stmt ) ) +
            "endfunction"
            )

        inputOutput = oneOf("input output")
        netDecl1Arg = ( nettype +
            Optional( expandRange ) +
            Optional( delay ) +
            Group( delimitedList( ~inputOutput + identifier ) ) )
        netDecl2Arg = ( "trireg" +
            Optional( chargeStrength ) +
            Optional( expandRange ) +
            Optional( delay ) +
            Group( delimitedList( ~inputOutput + identifier ) ) )
        netDecl3Arg = ( nettype +
            Optional( driveStrength ) +
            Optional( expandRange ) +
            Optional( delay ) +
            Group( delimitedList( assgnmt ) ) )
        netDecl1 = Group(netDecl1Arg + semi)
        netDecl2 = Group(netDecl2Arg + semi)
        netDecl3 = Group(netDecl3Arg + semi)

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
            semi )

        udpInstance = Group( Group( identifier + Optional(range | subscrRef) ) +
            "(" + Group( delimitedList( self.expr ) ) + ")" )
        udpInstantiation = Group( identifier -
            Optional( driveStrength ) +
            Optional( delay ) +
            delimitedList( udpInstance ) +
            semi ).setName("udpInstantiation")#.setParseAction(dumpTokens).setDebug()

        parameterValueAssignment = Group( Literal("#") + "(" + Group( delimitedList( self.expr ) ) + ")" )
        namedPortConnection = Group( "." + identifier + "(" + self.expr + ")" )
        modulePortConnection = self.expr | empty
        #~ moduleInstance = Group( Group ( identifier + Optional(range) ) +
            #~ ( delimitedList( modulePortConnection ) |
              #~ delimitedList( namedPortConnection ) ) )
        inst_args = Group( "(" + (delimitedList( modulePortConnection ) |
                    delimitedList( namedPortConnection )) + ")").setName("inst_args")#.setDebug()
        moduleInstance = Group( Group ( identifier + Optional(range) ) + inst_args )

        moduleInstantiation = Group( identifier +
            Optional( parameterValueAssignment ) +
            delimitedList( moduleInstance ).setName("moduleInstanceList") +
            semi ).setName("moduleInstantiation")

        parameterOverride = Group( "defparam" + delimitedList( paramAssgnmt ) + semi )
        task = Group( "task" + identifier + semi +
            ZeroOrMore( tfDecl ) +
            stmtOrNull +
            "endtask" )

        specparamDecl = Group( "specparam" + delimitedList( paramAssgnmt ) + semi )

        pathDescr1 = Group( "(" + subscrIdentifier + "=>" + subscrIdentifier + ")" )
        pathDescr2 = Group( "(" + Group( delimitedList( subscrIdentifier ) ) + "*>" +
                                  Group( delimitedList( subscrIdentifier ) ) + ")" )
        pathDescr3 = Group( "(" + Group( delimitedList( subscrIdentifier ) ) + "=>" +
                                  Group( delimitedList( subscrIdentifier ) ) + ")" )
        pathDelayValue = Group( ( "(" + Group( delimitedList( mintypmaxExpr | self.expr ) ) + ")" ) |
                                 mintypmaxExpr |
                                 self.expr )
        pathDecl = Group( ( pathDescr1 | pathDescr2 | pathDescr3 ) + "=" + pathDelayValue + semi ).setName("pathDecl")

        portConditionExpr = Forward()
        portConditionTerm = Optional(unop) + subscrIdentifier
        portConditionExpr << portConditionTerm + Optional( binop + portConditionExpr )
        polarityOp = oneOf("+ -")
        levelSensitivePathDecl1 = Group(
            if_ + Group("(" + portConditionExpr + ")") +
            subscrIdentifier + Optional( polarityOp ) + "=>" + subscrIdentifier + "=" +
            pathDelayValue +
            semi )
        levelSensitivePathDecl2 = Group(
            if_ + Group("(" + portConditionExpr + ")") +
            lpar + Group( delimitedList( subscrIdentifier ) ) + Optional( polarityOp ) + "*>" +
                Group( delimitedList( subscrIdentifier ) ) + rpar + "=" +
            pathDelayValue +
            semi )
        levelSensitivePathDecl = levelSensitivePathDecl1 | levelSensitivePathDecl2

        edgeIdentifier = posedge | negedge
        edgeSensitivePathDecl1 = Group(
            Optional( if_ + Group("(" + self.expr + ")") ) +
            lpar + Optional( edgeIdentifier ) +
            subscrIdentifier + "=>" +
            lpar + subscrIdentifier + Optional( polarityOp ) + ":" + self.expr + rpar + rpar +
            "=" +
            pathDelayValue +
            semi )
        edgeSensitivePathDecl2 = Group(
            Optional( if_ + Group("(" + self.expr + ")") ) +
            lpar + Optional( edgeIdentifier ) +
            subscrIdentifier + "*>" +
            lpar + delimitedList( subscrIdentifier ) + Optional( polarityOp ) + ":" + self.expr + rpar + rpar +
            "=" +
            pathDelayValue +
            semi )
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
            lpar + timCheckEvent + "," + timCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + rpar +
            semi )
        systemTimingCheck2 = Group( "$hold" +
            lpar + timCheckEvent + "," + timCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + rpar +
            semi )
        systemTimingCheck3 = Group( "$period" +
            lpar + controlledTimingCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + rpar +
            semi )
        systemTimingCheck4 = Group( "$width" +
            lpar + controlledTimingCheckEvent + "," + timCheckLimit +
            Optional( "," + self.expr + "," + notifyRegister ) + rpar +
            semi )
        systemTimingCheck5 = Group( "$skew" +
            lpar + timCheckEvent + "," + timCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + rpar +
            semi )
        systemTimingCheck6 = Group( "$recovery" +
            lpar + controlledTimingCheckEvent + "," + timCheckEvent + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + rpar +
            semi )
        systemTimingCheck7 = Group( "$setuphold" +
            lpar + timCheckEvent + "," + timCheckEvent + "," + timCheckLimit + "," + timCheckLimit +
            Optional( "," + notifyRegister ) + rpar +
            semi )
        systemTimingCheck = (FollowedBy('$') + ( systemTimingCheck1 | systemTimingCheck2 | systemTimingCheck3 |
            systemTimingCheck4 | systemTimingCheck5 | systemTimingCheck6 | systemTimingCheck7 )).setName("systemTimingCheck")
        sdpd = if_ + Group("(" + self.expr + ")") + \
            ( pathDescr1 | pathDescr2 ) + "=" + pathDelayValue + semi

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

        moduleItem = ~Keyword("endmodule") + (
            parameterDecl |
            inputDecl |
            outputDecl |
            inoutDecl |
            regDecl |
            netDecl3 |
            netDecl1 |
            netDecl2 |
            timeDecl |
            integerDecl |
            realDecl |
            eventDecl |
            gateDecl |
            parameterOverride |
            continuousAssign |
            specifyBlock |
            initialStmt |
            alwaysStmt |
            task |
            functionDecl |
            # these have to be at the end - they start with identifiers
            moduleInstantiation |
            udpInstantiation
            )
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
        port = portExpr | Group( ( "." + identifier + "(" + portExpr + ")" ) )

        moduleHdr = Group ( oneOf("module macromodule") + identifier +
                 Optional( "(" + Group( Optional( delimitedList( 
                                    Group(oneOf("input output") + 
                                            (netDecl1Arg | netDecl2Arg | netDecl3Arg) ) |
                                    port ) ) ) + 
                            ")" ) + semi ).setName("moduleHdr")
        def gotModuleHdr(s,loc,toks):
            self.module_name=toks[0][1]
        moduleHdr.addParseAction(gotModuleHdr)

        module = Group(  moduleHdr +
                 Group( ZeroOrMore( moduleItem ) ) +
                 "endmodule" ).setName("module")#.setDebug()

        udpDecl = outputDecl | inputDecl | regDecl
        #~ udpInitVal = oneOf("1'b0 1'b1 1'bx 1'bX 1'B0 1'B1 1'Bx 1'BX 1 0 x X")
        udpInitVal = (Regex("1'[bB][01xX]") | Regex("[01xX]")).setName("udpInitVal")
        udpInitialStmt = Group( "initial" +
            identifier + "=" + udpInitVal + semi ).setName("udpInitialStmt")

        levelSymbol = oneOf("0   1   x   X   ?   b   B")
        levelInputList = Group( OneOrMore( levelSymbol ).setName("levelInpList") )
        outputSymbol = oneOf("0   1   x   X")
        combEntry = Group( levelInputList + ":" + outputSymbol + semi )
        edgeSymbol = oneOf("r   R   f   F   p   P   n   N   *")
        edge = Group( "(" + levelSymbol + levelSymbol + ")" ) | \
               Group( edgeSymbol )
        edgeInputList = Group( ZeroOrMore( levelSymbol ) + edge + ZeroOrMore( levelSymbol ) )
        inputList = levelInputList | edgeInputList
        seqEntry = Group( inputList + ":" + levelSymbol + ":" + ( outputSymbol | "-" ) + semi ).setName("seqEntry")
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
            "(" + Group( delimitedList( identifier ) ) + ")" + semi +
            OneOrMore( udpDecl ) +
            Optional( udpInitialStmt ) +
            udpTableDefn +
            "endprimitive" )

        #verilogbnf = OneOrMore( module | udp ) + StringEnd()
        verilogbnf = ( module | udp ) + StringEnd()

        verilogbnf.ignore( cppStyleComment )
        verilogbnf.ignore( compilerDirective )

        self.verilogbnf=verilogbnf

    def parseString( self,strng ):
        def show(l,space=""):
            if isinstance(l, str):
                print "%s%s"%(space,l),type(l)
            else:
                print type(l),l
                for x in dir(l):
                    print x,
                print l.__class__
                if 'name' in l: print l.name
                if 'reg' in l: print "~~~~~",l['reg']
                for ll in l:
                    show(ll,space=space+"__")

        tokens = []
        try:
            tokens=self.verilogbnf.parseString( strng )
            #show(tokens)
        except ParseException, err:
            print err.line
            print " "*(err.column-1) + "^"
            print err
        return tokens
    def printInfo(self):
        def printDict(d,dname=""):
            print "%-12s:"%dname,
            for k in d:
                if d[k]!="":
                  print "%s(%s)"%(k,d[k]),
                else:
                  print "%s"%(k),
            print
        def printSet(s,sname=""):
            print "%-12s:"%sname,
            for k in s:
                  print "%s"%(k),
            print

        printDict(self.registers, "Registers")
        printDict(self.inputs,    "Inputs")
        printDict(self.outputs,   "Outputs")
        printDict(self.inouts,    "InOuts")
        printDict(self.parameters,"Parameters")
        printSet(self.nba,        "Non Blocking")
        printSet(self.ba,         "Blocking")
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
module TOP();
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


def main():
    parser = OptionParser(version="%prog 1.0")
    parser.add_option("", "--input-file",   dest="inputFile",   help="Input file name (*.v)", metavar="FILE")
    parser.add_option("", "--output-file",  dest="outputFile",  help="Output file name (*.v)", metavar="FILE")

    parser.add_option("", "--triplicate-inputs",  action="store_true", dest="tInp", default=True, help="Triplicate inputs.")
    parser.add_option("", "--triplicate-outputs", action="store_true", dest="tOut", default=True, help="Triplicate outputs.")
    parser.add_option("", "--triplicate-reg",     action="store_true", dest="tReg", default=True, help="Triplicate registers.")
    parser.add_option("", "--triplicate-comb",    action="store_true", dest="tCom", default=True, help="Triplicate combinatorial logic.")

    parser.add_option("", "--vote-inputs",        action="store_true", dest="vInp", default=True, help="Add majority voters at inputs.")
    parser.add_option("", "--vote-outputs",       action="store_true", dest="vOut", default=True, help="Add majority voters at outputs.")
    parser.add_option("", "--vote-reg",           action="store_true", dest="vReg", default=True, help="Add majority voters at .")
    parser.add_option("", "--vote-comb",          action="store_true", dest="vCom", default=True, help="Add majority voters at .")


    (options, args) = parser.parse_args()

    vp=VerilogParser()
    vp.parseString(toptest)
    print vp.module_name
    vp.printInfo()
    vp.dtmr()

if __name__=="__main__":
    main()
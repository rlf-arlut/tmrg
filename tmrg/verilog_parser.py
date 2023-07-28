#!/usr/bin/env python2

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
#   Szymon Kulis, CERN, 2015-2020
#   Renamed to verilog_parser.py, integreated to TMRG, adjusted to the TMRG needs
#

__version__ = "1.0.10"

import re
import pdb
import time
import pprint
import sys
import functools
import logging
import textwrap
import os

"""
if sys.version_info[0] >= 3:
    from .pyparsing241 import *
    from . import pyparsing241 as pyparsing
else:
    from .pyparsing152 import *
    from . import pyparsing152 as pyparsing
"""
from pyparsing import *
import pyparsing

usePackrat = True
usePsyco = False

import glob
import copy

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
        print("failed to import psyco Python optimizer")
    else:
        psycoOn = True


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
        sys.setrecursionlimit(4000)
        self.include=False
        self.inc_dir=[]

        self.compilerDirective = Combine( "`" + \
            oneOf("define undef ifdef else endif default_nettype "
                  "include resetall timescale unconnected_drive "
                  "nounconnected_drive celldefine endcelldefine") + \
            restOfLine ).setName("compilerDirective")

        # keywords
        if_        = Keyword("if")
        else_      = Keyword("else")
        edge       = Keyword("edge")
        posedge    = Keyword("posedge")
        negedge    = Keyword("negedge")
        or_        = Keyword("or")
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
        unique     = Keyword("unique")
        wire       = Keyword("wire")

        # Keywords
        directions         = MatchFirst(map(Keyword, "input output inout".split()))
        data_2states_types = MatchFirst(map(Keyword, "bit byte shortint int longint".split()))
        data_4states_types = MatchFirst(map(Keyword, "reg logic integer".split()))
        data_nonint_types  = MatchFirst(map(Keyword, "string time real shortreal realtime".split()))
        self.data_types    = data_2states_types | data_4states_types | data_nonint_types
        self.net_types     = MatchFirst(map(Keyword, "wire supply0 supply1 tri triand trior tri0 tri1 wand wor".split()))
        self.gate_types    = MatchFirst(map(Keyword, "and nand or nor xor xnor buf bufif0 bufif1 not notif0 notif1 pulldown pullup nmos rnmos pmos rpmos cmos rcmos tran rtran tranif0 rtranif0 tranif1 rtranif1"))
        modifiers          = MatchFirst(map(Keyword, "unsigned signed vectored scalared const".split()))
        strength           = MatchFirst(map(Keyword, "supply0 supply1 strong strong0 strong1 pull0 pull1 weak weak0 weak1 highz0 highz1 small medium large".split()))
        unsupported_log95  = MatchFirst(map(Keyword, "ifnone".split()))
        unsupported_log21  = MatchFirst(map(Keyword, "incdir pulsestyle_ondetect cell pulsestyle_onevent config instance endconfig liblist showcancelled library use noshowcancelled".split()))
        unsupported_svlog  = MatchFirst(map(Keyword, """
accept_on export ref alias extends restrict extern final s_always first_match s_eventually assert foreach s_nexttime assume forkjoin s_until before globals_until_with bind iff sequence bins ignore_bins binsof illegal_bins implies solve break import inside chandle checker interface class intersect super clocking join_any sync_accept_on join_none sync_reject_on constraint let tagged context local this throughout cover timeprecision covergroup matches timeunit coverpoint modport type cross new dist nexttime union do null unique endchecker package unique0 endclass packed until endclocking priority until_with endgroup program untypted endinterface property var endpackage protected virtual endprogram pure void endproperty rand wait_order endsequence randc enum randcase wildcard eventually randsequence with expect reject_on within 
        """.split()))


        self.forbidden_char = "¤"
        reserved_tmrg = Keyword(self.forbidden_char+"__COMP_DIRECTIVE")

        valid_keywords = directions | self.data_types | self.net_types | modifiers | strength | unsupported_log95 | unsupported_log21 | unsupported_svlog | reserved_tmrg
        custom_type = ~valid_keywords + Word(alphas + '_', alphanums + '_')

        types = Group (
                Group(self.data_types | self.net_types).setResultsName("kind") + 
                Optional(modifiers).setResultsName("attrs")
            ).setResultsName("standard") | Group (
                custom_type.setResultsName("custom_type")
            ).setResultsName("custom")

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
        #identifier = ~valid_keywords + (identifier1 | identifier2)
        identifier = ~(directions | self.data_types | self.net_types) + (identifier1 | identifier2)

        hexnums = nums + "abcdefABCDEF" + "_?"
        base = Regex("[bBoOdDhH]{0,1}").setName("base")
        signed = Regex("'[sS]?").setName("signed")
        basedNumber = Combine( Optional( Word(nums + "_") ) + signed + base + Word(hexnums+"xXzZ"),
                               joinString="", adjacent=False ).setResultsName("basedNumber")
        number = ( basedNumber | \
                   Regex(r"[+-]?[0-9]+(\.[0-9_]*)?([0-9_]*)?([Ee][+-]?[0-9_]+)?") \
                  ).setName("numeric")

        # Expressions
        self.expr = Forward()

        # References to registers or nets
        self.range = Group( Suppress("[") + Group(self.expr).setResultsName("expr@from") + Optional(oneOf(": +: -:")).setResultsName("dir") + Group(self.expr).setResultsName("expr@to") + Suppress("]")).setResultsName("range")
        self.size = Group( Suppress("[") + Group(self.expr) + Suppress("]")).setResultsName("size")
        self.field = Group(Suppress(".") + identifier).setResultsName("field_ref")
        regReference  = Group( Group(identifier).setResultsName("name") + Group(ZeroOrMore(self.range | self.size | self.field)).setResultsName("range_or_field") ).setResultsName("reg_reference")

        # Concatenations
        concat = Optional("'")+Group( Suppress("{") + delimitedList( Group(self.expr) ) + Suppress("}") ).setResultsName("concat")
        multiConcat = Group("{" + self.expr + concat + "}").setName("multiConcat")
        funcCall = Group(identifier + "(" + Group(Optional( Group(delimitedList( Group(self.expr) )) )) + ")").setResultsName("funcCall")

        mintypmaxExpr = Group( self.expr + ":" + self.expr + ":" + self.expr ).setName("mintypmax")
        primary = ( number |
                    ("(" + mintypmaxExpr + ")" ) |
                    ( "(" + Group(self.expr) + ")" ).setName("nestedExpr") |
                    (identifier + "::" + identifier) |
                    multiConcat |
                    concat |
                    dblQuotedString |
                    funcCall |
                    regReference
                  ).setResultsName("primary")

        unop  = oneOf( "+  -  !  ~  &  ~&  |  ^|  ^  ~^" ).setName("unop")
        binop = oneOf( "+  -  *  /  %  ==  !=  ===  !==  &&  "
                       "||  <  <=  >  >=  &  |  ^  ^~  ~^  >>  << ** <<< >>>" ).setName("binop")
        inlineIfExpr= Group( Group(primary) + Suppress(Literal("?")) + Group(self.expr) + Suppress(Literal(":")) + Group(self.expr) ).setResultsName("inlineIfExpr")

        cast = (identifier | "(" + self.expr + ")" | number) + "'" + "(" + self.expr + ")"
        self.expr << (
                      ( unop + self.expr ) |  # must be first!
                      inlineIfExpr | cast |
                      ( primary + Optional( binop + self.expr ) )
                     )

        self.expr=self.expr.setName("expr").setResultsName("expr")

        # Events
        eventExpr = Forward()
        eventTerm = Group ("*" | ( Optional (posedge | negedge) + ( regReference|  "(" + regReference + ")" ))  | ( "(" + eventExpr + ")" )).setResultsName("eventTerm")
        eventExpr << (
            Group( (delimitedList( eventTerm , (or_|",") )).setResultsName("delimitedOrList") )
            )
        eventControl = Group( "@" + eventExpr ).setName("eventCtrl").setResultsName("eventCtrl")

        # Delays
        delayArg = ( 
                     Regex(r"[0-9]+(\.[0-9]+)?(fs|ps|ns|us|ms|s)?") |
                     number |
                     Word(alphanums+"$_") | #identifier ^
                     ( "(" + Group( delimitedList( mintypmaxExpr | self.expr ) ) + ")" )
                   ).setName("delayArg")

        delay = Group( "#" + delayArg ).setName("delay").setResultsName("delay")
        delayOrEventControl = delay | eventControl

        # Assignments
        lvalue = Group(regReference | concat).setResultsName("lvalue")
        self.assignment   = Group( lvalue + oneOf("= += -= |= ^= &= *= /= <<= >>= <<<= >>>= %=").setResultsName("op") + Optional(Group(delayOrEventControl).setResultsName("delayOrEventControl")) + Group(self.expr).setResultsName("expr@rvalue") ).setResultsName( "assignment" )

        self.incr_decr   = Group( regReference + oneOf("++ --")).setResultsName( "incr_decr" )

        self.nbAssgnmt = Group(lvalue + Suppress("<=") + Optional(Group(delayOrEventControl).setResultsName("delayOrEventControl")) + Group(self.expr).setResultsName("expr@rvalue")).setResultsName("nbassignment")

        paramAssgnmt = Group(  identifier + Group(Optional(self.size|self.range)) + Suppress("=") + Group(self.expr) ).setResultsName("paramAssgnmt")

        self.comp_directive = Group(Suppress(self.forbidden_char+"__COMP_DIRECTIVE") + CharsNotIn(";") + Suppress(self.semi)).setResultsName("comp_directive")

        attr_spec = Group(identifier + Optional("=" + self.expr)).setResultsName("attr_spec")

        attribute_instance = Group( "(*" +
                                    Group(delimitedList(attr_spec)) +
                                    "*)"
                                  ).setResultsName("attribute_instance")
        
        regIdentifier = Group( Group(identifier).setResultsName("name") + Group(ZeroOrMore(self.range | self.size)).setResultsName("unpacked_ranges")).setResultsName("identifier")
        
        parameterDecl      = Group( "parameter" +
                                    Group(Optional(modifiers)) +
                                    Group(Optional(self.data_types)) +
                                    Group(Optional(self.range)) +
                                    Group(delimitedList( Group(paramAssgnmt))) +
                                    Suppress(self.semi)
                                  ).setResultsName("paramDecl")

        localParameterDecl = Group("localparam" +
                                   Group(Optional(modifiers)) +
                                   Group(Optional(self.data_types)) +
                                   Group(Optional(self.range)) +
                                   Group(delimitedList(Group(paramAssgnmt))) +
                                   Suppress(self.semi)
                                  ).setResultsName("localparamDecl")

        """
        apaterno: This is not working unfortunately. Had to switch to a more verbose formulation

        port = (
            directions.setResultsName("dir") + (
                Optional(
                    types +
                    Group(ZeroOrMore(self.range)).setResultsName("packed_ranges")
                ) +
                Group( delimitedList( regIdentifier )).setResultsName("identifiers")
            )
        )
        """
        port = (
            directions.setResultsName("dir") + delimitedList(
            Group(
                Group(self.data_types | self.net_types).setResultsName("kind") + 
                Optional(modifiers).setResultsName("attrs") +
                Group(ZeroOrMore(self.range)).setResultsName("packed_ranges") +
                Group( delimitedList( regIdentifier )).setResultsName("identifiers")
            ).setResultsName("standard") | Group(
                custom_type.setResultsName("custom_type") +
                Group(ZeroOrMore(self.range)).setResultsName("packed_ranges") +
                Group( delimitedList( regIdentifier )).setResultsName("identifiers")
            ).setResultsName("custom") |
                Group( delimitedList( regIdentifier )).setResultsName("identifiers")
        ))

        self.portHdr  = Group(port).setName("portHdr").setResultsName("portHdr")
        self.portBody = Group(port + Suppress(self.semi) ).setName("portBody").setResultsName("portBody")

        self.regDecl = Group( (self.net_types | self.data_types).setResultsName("type") +
                              Group(Optional(modifiers)).setResultsName("attributes") +
                              Group(ZeroOrMore(self.range)).setResultsName("packed_ranges") +
                              Group( delimitedList( regIdentifier )).setResultsName("identifiers") +
                              Suppress(self.semi)
                            ).setName("regDecl").setResultsName("regDecl")

        self.netDecl = Group(
                types +
                Group(ZeroOrMore(self.range)).setResultsName("packed_ranges") +
                Group( delimitedList( regIdentifier )).setResultsName("identifiers") +
                Suppress(self.semi)
        ).setResultsName("netDecl")

        self.netDeclWAssignInline = Group(
                types +
                Group(ZeroOrMore(self.range)).setResultsName("packed_ranges") +
                Group(Optional( delay )).setResultsName("delay") +
                Group( delimitedList( self.assignment ) ).setResultsName("assignments")
                ).setResultsName("netDeclWAssign")

        self.netDeclWAssign = Group(
                types +
                Group(ZeroOrMore(self.range)).setResultsName("packed_ranges") +
                Group(Optional( delay )).setResultsName("delay") +
                Group( delimitedList( self.assignment ) ).setResultsName("assignments") +
                Suppress(self.semi)).setResultsName("netDeclWAssign")

        timeDecl = Group( "time" + delimitedList( regIdentifier ) + self.semi ).setResultsName("timeDecl")
        strength0 = oneOf("supply0  strong0  pull0  weak0  highz0")
        strength1 = oneOf("supply1  strong1  pull1  weak1  highz1")
        driveStrength = Group( "(" + ( ( strength0 + "," + strength1 ) |
                                       ( strength1 + "," + strength0 ) ) + ")" ).setName("driveStrength").setResultsName("driveStrength")
        realID = Group(identifier + Group(Optional( "[" + Group(self.expr) + oneOf(": +:") + Group(self.expr) + "]" ) ))

        eventDecl = Group( "event" + delimitedList( identifier ) + self.semi )

        blockDecl = (
            parameterDecl |
            localParameterDecl |
            timeDecl |
            eventDecl |
            self.netDecl
            )

        synopsys=Keyword(self.forbidden_char+"synopsys")
        self.directive_synopsys_translate = Group( synopsys + oneOf("translate_off translate_on") + Suppress(self.semi)).setResultsName("directive_synopsys_translate")
        self.directive_synopsys_ff        = Group( synopsys + oneOf("async_set_reset async_set_reset_local async_set_reset_local_all sync_set_reset sync_set_reset_local sync_set_reset_local_all ") + ((Suppress('"') + Group(OneOrMore(identifier)).setResultsName("identifiers") + Suppress('"')) | (Group(OneOrMore(identifier)).setResultsName("identifiers"))) + Suppress(self.semi)).setResultsName("directive_synopsys_ff")
        self.directive_synopsys_case   = Group( synopsys + OneOrMore( Keyword("full_case") | Keyword("parallel_case") )  + Suppress(self.semi)).setResultsName("directive_synopsys_case")
        self.synopsys_directives = self.directive_synopsys_translate | self.directive_synopsys_ff | self.directive_synopsys_case

        self.stmt = Forward().setName("stmt").setResultsName("stmt")
        stmtOrNull = self.stmt | self.semi
        caseItem = Group( Group(delimitedList( Group(self.expr) )) + Suppress(":") + stmtOrNull ).setResultsName("caseItem") | \
                   Group( default + Optional(":") + stmtOrNull ) | \
                   Group(self.directive_synopsys_case)
        condition=Group("(" + self.expr + ")").setResultsName("condition")
        blockName=identifier.setResultsName("id@blockName")
        self.stmt <<  ( Group( begin  +  ZeroOrMore( self.stmt )  + end ).setName("beginend").setResultsName("beginend") | \
            Group( if_ + condition + stmtOrNull +  else_ + stmtOrNull ).setName("ifelse").setResultsName("ifelse") | \
            Group( if_ + condition + stmtOrNull  ).setName("if").setResultsName("if") |\
            Group( delayOrEventControl + stmtOrNull ).setResultsName("delayStm") |\
            Group( Group(Optional(unique)) + case + Suppress("(") + Group(self.expr) + Suppress(")") +  Group(OneOrMore( caseItem )) + endcase ).setResultsName("case") |\
            Group( forever + self.stmt ).setResultsName("forever") |\
            Group( repeat + "(" + self.expr + ")" + self.stmt ) |\
            Group( while_ + "(" + self.expr + ")" + self.stmt ) |\
            Group( for_ + Suppress("(") + Group(self.assignment|self.netDeclWAssignInline).setResultsName("for1") + Suppress(self.semi) + Group( self.expr ).setResultsName("expr@for2") + Suppress(self.semi) + Group(self.assignment | self.incr_decr).setResultsName("for3") + Suppress(")") + Group(self.stmt).setResultsName("stmt") ).setResultsName("forstmt") |\
            Group( self.incr_decr + self.semi ) |\
            Group( fork + ZeroOrMore( self.stmt ) + join ) |\
            Group( fork + ":" + identifier + ZeroOrMore( blockDecl ) + ZeroOrMore( self.stmt ) + end ) |\
            Group( wait + "(" + self.expr + ")" + stmtOrNull ) |\
            Group( "->" + identifier + self.semi ) |\
            Group( disable + identifier + self.semi ) |\
            Group( assign + self.assignment + self.semi ).setResultsName("assign") |\
            Group( deassign + lvalue + self.semi ) |\
            Group( force + self.assignment + self.semi ).setResultsName("force") |\
            Group( self.directive_synopsys_case )| \
            Group( release + lvalue + self.semi ).setResultsName("release") |\
            Group( Suppress(begin) + Suppress(Literal(":")) + blockName + ZeroOrMore( blockDecl ) + ZeroOrMore( self.stmt ) + Suppress(end) + Optional(Suppress(Literal(":") + blockName))).setResultsName("beginEndLabel") |\
            self.comp_directive |\
            attribute_instance |
            Group( self.assignment + Suppress(self.semi) ).setResultsName("assignmentStm") |\
            Group( self.nbAssgnmt + Suppress(self.semi) ).setResultsName("nbassignmentStm") |\
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
        self.alwaysStmt = Group( oneOf("always always_ff always_comb always_latch").setResultsName("type") + Optional(eventControl) + self.stmt.setResultsName("statement") ).setName("alwaysStmt").setResultsName("always")
        initialStmt = Group( Keyword("initial") + self.stmt ).setName("initialStmt").setResultsName("initialStmt")

        chargeStrength = Group( "(" + oneOf( "small medium large" ) + ")" ).setName("chargeStrength")

        self.continuousAssign = Group(  Suppress(assign)
              + Group(Optional( driveStrength )).setResultsName("driveStrength")
              + Group(Optional( delay )).setResultsName("delay")
              + Group(delimitedList( self.assignment )).setResultsName("assignments") + Suppress(self.semi)
            ).setResultsName("continuousAssign")

        tfDecl = (
            parameterDecl |
            localParameterDecl |
            self.portBody |
            timeDecl |
            self.netDecl
            ).setResultsName("tfDecl")

        lifetime = oneOf("static automatic")
        functionDecl = Group(
            "function" + Group(Optional(lifetime)) + Group(Optional( self.range | "integer" | "real" )) + identifier + self.semi +
            Group( OneOrMore( tfDecl ) ) +
            Group( ZeroOrMore( self.stmt ) ) +
            "endfunction"
            ).setResultsName("functionDecl")

        self.netDecl2 = Group(Keyword("trireg").setResultsName("kind") +
                              Group(ZeroOrMore(modifiers)).setResultsName("attributes") +
                              Group(ZeroOrMore(strength)).setResultsName("strength") +
                              Group(ZeroOrMore(self.range)).setResultsName("packed_ranges") +
                              Group(Optional( delay )).setResultsName("delay") +
                              Group( delimitedList(  identifier ) ).setResultsName("identifiers") +
                              Suppress(self.semi)
                              ).setResultsName("netDecl2")

        self.structDecl = Group(
                "typedef struct packed" +
                Suppress("{") +
                Group(ZeroOrMore( self.netDecl )).setResultsName("fields") +
                Suppress ("}") +
                Group(identifier).setResultsName("id") +
                Suppress(self.semi)
        ).setName("structDecl").setResultsName("structDecl")

        self.genVarDecl = Group(Keyword("genvar") +
                                Group(delimitedList(self.expr)) +
                                Suppress(self.semi)
                               ).setResultsName("genVarDecl")

        # Simple assignment with declaration (in for loops, for instance)
        self.genVarDeclInline = Group(Keyword("genvar") + Group(identifier).setResultsName("name") + Optional(Suppress("=") + Group(self.expr).setResultsName("expr@rvalue"))).setResultsName( "genVarDeclInline" )

        gateType = oneOf("and  nand  or  nor xor  xnor buf  bufif0 bufif1 "
                         "not  notif0 notif1  pulldown pullup nmos  rnmos "
                         "pmos rpmos cmos rcmos   tran rtran  tranif0  "
                         "rtranif0  tranif1 rtranif1"  )
        gateInstance = Group( Optional( Group( identifier + Optional( self.range ) ) ) + \
                        Suppress("(") + Group( delimitedList( self.expr ) ) + Suppress(")"))
        self.gateDecl = Group( gateType +
            Group(Optional(driveStrength)) +
            Group(Optional( delay)) +
            Group(delimitedList( gateInstance)) +
            Suppress(self.semi) ).setResultsName("gateDecl")

        udpInstance = Group( Group( identifier + Optional(self.range | self.size) ) +
            "(" + Group( delimitedList( self.expr ) ) + ")" )
        udpInstantiation = Group( identifier -
            Optional( driveStrength ) +
            Optional( delay ) +
            delimitedList( udpInstance ) +
            self.semi ).setName("udpInstantiation")

        self.namedPortConnection = Group( "." + identifier + "(" + Group(Optional(self.expr)) + ")" ).setResultsName("namedPortConnection")

        parameterValueAssignment = Group ( Suppress(Literal("#")) +
                                           Suppress("(") +
                                           Group( delimitedList(self.namedPortConnection) ) + # expresion is only for compatibility reasons
                                                                                              # if someone tries to TMR expresion (unnamed conenection)
                                                                                              # it will crash ....
                                           Suppress(")")
                                         ).setResultsName("parameterValueAssignment")

        moduleArgs = Group( Suppress("(") +
                            Optional(delimitedList(self.namedPortConnection | Group(self.expr).setResultsName("expr@unnamedPortConnection"))) +
                            Suppress(")")
                          ).setResultsName("moduleArgs")

        moduleInstance = Group( Group ( identifier + Group(Optional(self.range)).setResultsName("range") ) + moduleArgs ).setResultsName("moduleInstance")

        self.moduleInstantiation = Group( Group(identifier).setResultsName("moduleName") +
                                          Group(Optional( parameterValueAssignment )) +
                                          Group(delimitedList( moduleInstance )).setResultsName("moduleInstances") +
                                          Suppress(self.semi)
                                        ).setResultsName("moduleInstantiation")

        parameterOverride = Group( "defparam" + delimitedList( paramAssgnmt ) + self.semi )
        task = Group( Suppress("task") + identifier + Suppress(self.semi) +
            Group(ZeroOrMore( tfDecl )) +
            stmtOrNull +
            "endtask" ).setResultsName("task")

        specparamDecl = Group( "specparam" + delimitedList( paramAssgnmt ) + self.semi )

        pathDescr1 = Group( "(" + regReference + "=>" + regReference + ")" )
        pathDescr2 = Group( "(" + Group( delimitedList( regReference ) ) + "*>" +
                                  Group( delimitedList( regReference ) ) + ")" )
        pathDescr3 = Group( "(" + Group( delimitedList( regReference ) ) + "=>" +
                                  Group( delimitedList( regReference ) ) + ")" )
        pathDelayValue = Group( ( "(" + Group( delimitedList( mintypmaxExpr | self.expr ) ) + ")" ) |
                                 mintypmaxExpr |
                                 self.expr )
        pathDecl = Group( ( pathDescr1 | pathDescr2 | pathDescr3 ) + "=" + pathDelayValue + self.semi ).setName("pathDecl")

        portConditionExpr = Forward()
        portConditionTerm = Optional(unop) + regReference
        portConditionExpr << portConditionTerm + Optional( binop + portConditionExpr )
        polarityOp = oneOf("+ -")
        levelSensitivePathDecl1 = Group(
            if_ + Group("(" + portConditionExpr + ")") +
            regReference + Optional( polarityOp ) + "=>" + regReference + "=" +
            pathDelayValue +
            self.semi )
        levelSensitivePathDecl2 = Group(
            if_ + Group("(" + portConditionExpr + ")") +
            self.lpar + Group( delimitedList( regReference ) ) + Optional( polarityOp ) + "*>" +
                Group( delimitedList( regReference ) ) + self.rpar + "=" +
            pathDelayValue +
            self.semi )
        levelSensitivePathDecl = levelSensitivePathDecl1 | levelSensitivePathDecl2

        edgeIdentifier = posedge | negedge
        edgeSensitivePathDecl1 = Group(
            Optional( if_ + Group("(" + self.expr + ")") ) +
            self.lpar + Optional( edgeIdentifier ) +
            regReference + "=>" +
            self.lpar + regReference + Optional( polarityOp ) + ":" + self.expr + self.rpar + self.rpar +
            "=" +
            pathDelayValue +
            self.semi )
        edgeSensitivePathDecl2 = Group(
            Optional( if_ + Group("(" + self.expr + ")") ) +
            self.lpar + Optional( edgeIdentifier ) +
            regReference + "*>" +
            self.lpar + delimitedList( regReference ) + Optional( polarityOp ) + ":" + self.expr + self.rpar + self.rpar +
            "=" +
            pathDelayValue +
            self.semi )
        edgeSensitivePathDecl = edgeSensitivePathDecl1 | edgeSensitivePathDecl2

        edgeDescr = oneOf("01 10 0x x1 1x x0").setName("edgeDescr")

        scalarConst = Regex("0|1('[Bb][01xX])?")
        timCheckEventControl = Group( posedge | negedge | (edge + "[" + delimitedList( edgeDescr ) + "]" ))
        timCheckCond = Forward()
        timCondBinop = oneOf("== === != !==")
        timCheckCondTerm = ( self.expr + timCondBinop + scalarConst ) | ( Optional("~") + self.expr )
        timCheckCond << ( ( "(" + timCheckCond + ")" ) | timCheckCondTerm )
        timCheckEvent = Group( Optional( timCheckEventControl ) +
                                regReference +
                                Optional( "&&&" + timCheckCond ) )
        timCheckLimit = self.expr
        controlledTimingCheckEvent = Group( timCheckEventControl + regReference +
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

        tmrg=Suppress(self.forbidden_char+"tmrg")

        self.directive_doNotTriplicate  = Group( tmrg + Suppress("do_not_triplicate") + OneOrMore(identifier)                + Suppress(self.semi)).setResultsName("directive_do_not_triplicate")
        self.directive_triplicate       = Group( tmrg + Suppress("triplicate")        + OneOrMore(identifier)                + Suppress(self.semi)).setResultsName("directive_triplicate")
        self.directive_default          = Group( tmrg + Suppress("default")           + oneOf("triplicate do_not_triplicate")+ Suppress(self.semi)).setResultsName("directive_default")
        self.directive_tmr_error        = Group( tmrg + Suppress("tmr_error")         + oneOf("true false")                  + Suppress(self.semi)).setResultsName("directive_tmr_error")
        self.directive_tmr_error_exclude= Group( tmrg + Suppress("tmr_error_exclude") + OneOrMore(identifier)                + Suppress(self.semi)).setResultsName("directive_tmr_error_exclude")
        self.directive_do_not_touch     = Group( tmrg + ("do_not_touch") + ZeroOrMore(identifier) + Suppress(self.semi)).setResultsName("directive_do_not_touch")
        self.directive_seu_set          = Group( tmrg + Suppress("seu_set") + identifier + Suppress(self.semi)).setResultsName("directive_seu_set")
        self.directive_seu_reset        = Group( tmrg + Suppress("seu_reset") + identifier +  Suppress(self.semi)).setResultsName("directive_seu_reset")
        self.directive_slicing          = Group( tmrg + ("slicing") + Suppress(self.semi)).setResultsName("directive_slicing")
        self.directive_translate        = Group( tmrg + Suppress("translate")       + oneOf("on off")+ Suppress(self.semi)).setResultsName("directive_translate")
        self.directive_majority_voter_cell  = Group( tmrg + Suppress("majority_voter_cell")  + OneOrMore(identifier) + Suppress(self.semi)).setResultsName("directive_majority_voter_cell")
        self.directive_fanout_cell      = Group( tmrg + Suppress("fanout_cell")  + OneOrMore(identifier) + Suppress(self.semi)).setResultsName("directive_fanout_cell")


        package_import_item = Group(identifier + "::" + (identifier | "*")).setResultsName("package_import_item")
        package_import_declaration = Group(Keyword("import") + Group(delimitedList(package_import_item)) + Suppress(self.semi)).setResultsName("package_import_declaration")

        """
        x::= <specparam_declaration>
        x||= <path_declaration>
        x||= <level_sensitive_path_declaration>
        x||= <edge_sensitive_path_declaration>
        x||= <system_timing_check>
        x||= <sdpd>
        """
        specifyBlock = Group( "specify" + ZeroOrMore( specifyItem ) + "endspecify" )

        self.moduleOrGenerateItem = Forward()
        generate_module_named_block = Group(Suppress("begin") +
                                            Group(Optional(":" + identifier)) +
                                            ZeroOrMore(self.moduleOrGenerateItem) +
                                            Suppress("end") +
                                            Group(Optional(":" + identifier))
                                            ).setResultsName("generate_module_named_block")

        self.moduleOrGenerateItemOrNamed = self.moduleOrGenerateItem | generate_module_named_block

        generate_if_else_statement =  Group(Suppress(if_) + condition + self.moduleOrGenerateItemOrNamed + Suppress(else_) + self.moduleOrGenerateItemOrNamed).setResultsName("generate_if_else_statement")
        generate_if_statement =     Group(Suppress(if_) + condition + self.moduleOrGenerateItemOrNamed).setResultsName("generate_if_statement")

        generate_module_loop_statement = Group( Suppress(for_) +
            Suppress("(")  +
            Group(Optional(self.assignment|self.netDeclWAssignInline|self.genVarDeclInline)).setResultsName("for1") +
            Suppress(self.semi) +
            Group(self.expr).setResultsName("expr@for2") +
            Suppress(self.semi) +
            Group(Optional(self.assignment | self.incr_decr)).setResultsName("for3") +
            Suppress(")") +
            generate_module_named_block
        ).setResultsName("generate_module_loop_statement")

        self.moduleOrGenerateItem << (
            parameterDecl |
            self.synopsys_directives |
            localParameterDecl |
            self.portBody |
            self.continuousAssign |
            self.netDecl2 |
            self.genVarDecl |
            package_import_declaration |
            timeDecl |
            eventDecl |
            self.structDecl |
            self.gateDecl |
            parameterOverride |
            specifyBlock |
            initialStmt |
            self.alwaysStmt |
            task |
            functionDecl |
            self.netDecl |
            self.netDeclWAssign |
            self.directive_doNotTriplicate |
            self.directive_triplicate |
            self.directive_default |
            self.directive_tmr_error |
            self.directive_tmr_error_exclude |
            self.directive_do_not_touch |
            self.directive_seu_set |
            self.directive_seu_reset |
            self.comp_directive |
            self.directive_slicing |
            self.directive_translate |
            self.directive_majority_voter_cell  |
            self.directive_fanout_cell  |
            self.moduleInstantiation |
            generate_module_loop_statement |
            generate_if_else_statement |
            generate_if_statement
        )

        generate_body =  OneOrMore(self.moduleOrGenerateItem)# |generate_module_loop_statement

        self.generate = Group( Suppress(Keyword("generate")) + generate_body  + Suppress(Keyword("endgenerate"))).setResultsName("generate")

        self.moduleItem = self.generate | self.moduleOrGenerateItem

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
        portRef = regReference
        portExpr = portRef | Group( "{" + delimitedList( portRef ) + "}" )
        self.port = Group(portExpr | Group( ( "." + identifier + "(" + portExpr + ")" ) ).setResultsName("explicitConn") ).setResultsName("port")

        portlist = Group(Optional(
            Suppress("(") +
            Optional(
                delimitedList(self.portHdr) | # ANSI
                delimitedList(self.port)      # Non-ANSI
            ) +
            Suppress(")")
        )).setResultsName("ports")

        moduleHdr = Group ( oneOf("module macromodule") + 
            identifier.setResultsName("id@moduleName") +
            Group(Optional(
                Suppress("#")+
                Suppress("(") +
                delimitedList(
                    Group(
                        Optional(Suppress("parameter")) + 
                        Group(Optional( self.range )) +
                        paramAssgnmt
                    )
                ) + 
                Suppress(")")
            )) +
            portlist +
            Suppress(self.semi) ).setName("moduleHdr").setResultsName("moduleHdr")

        self.endmodule = Keyword("endmodule").setResultsName("endModule")

        self.module = Group( moduleHdr +
                 Group( ZeroOrMore( self.moduleItem ) ).setResultsName("moduleBody") +
                 self.endmodule +
                 Group(Optional(":" + identifier)) ).setName("module").setResultsName("module")

        udpDecl = self.portBody | self.regDecl
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

        verilogbnf = (OneOrMore( self.module | udp | self.comp_directive | self.structDecl) + StringEnd()).setName("top").setResultsName("top")

        verilogbnf.ignore( cppStyleComment )

        self.verilogbnf=verilogbnf

        self.tmrgDirective = (Suppress('//') + "tmrg" + restOfLine).setResultsName("directive")
        def tmrgDirectiveAction(toks):
            toks=map(str.strip,toks)
            return self.forbidden_char+" ".join(toks)+ ";"
        self.tmrgDirective.setParseAction(tmrgDirectiveAction)

        self.synopsysDirective = (Suppress('//') + "synopsys" + restOfLine).setResultsName("synopsysDirective")
        def synopsysDirectiveAction(toks):
            toks=map(str.strip,toks)
            return self.forbidden_char+" ".join(toks)+ ";"
        self.synopsysDirective.setParseAction(synopsysDirectiveAction)

        self.compDirective = (Suppress('`') + oneOf("define undef include elsif else endif timescale ifdef ifndef resetall celldefine endcelldefine default_nettype")+ restOfLine).setResultsName("compDirective")
        def compDirectiveAction(toks):
            # Remove single line comments behind directives to make
            # sure we don't create an error if toks[1] contains a single
            # line comment which would obviously obfuscate the semicolon
            toks[1]=re.sub("\/\/.*", "", toks[1])

            if toks[0]=="include":
                if self.include:
                    fname=toks[1].replace('"','').strip()
                    logging.info("Including '%s'"% fname)
                    found = False
                    for d in self.inc_dir:
                        fullname=os.path.join(d,fname)
                        if os.path.isfile(fullname):
                            logging.info("File '%s' found in '%s'"%(fname,fullname))
                            fin=open(fullname)
                            fcontent=fin.read()
                            fin.close()
                            return fcontent
                            found=True
                    if not found:
                        logging.warning("File '%s' not found" % (fname))
            return self.forbidden_char+"__COMP_DIRECTIVE "+" ".join(toks)+ ";"
        self.compDirective.setParseAction(compDirectiveAction)


    def parseFile(self,fname):
        logging.debug("Parsing file '%s'"%fname)
        self.fname=fname
        f=open(fname,"r")
        body=f.read()
        f.close()
        return self.parseString(body)

    def parseString( self,strng ):
        preParsedStrng = strng
        preParsedStrng = self.compDirective.transformString(preParsedStrng)
        preParsedStrng = self.tmrgDirective.transformString( preParsedStrng )
        preParsedStrng = self.synopsysDirective.transformString( preParsedStrng )
        preParsedStrng = cppStyleComment.suppress().transformString(preParsedStrng)
        preParsedStrng = self.compDirective.transformString(preParsedStrng) # do it twice in case there are defines in included files
        preParsedStrngNew=""
        translate=True

        for line in preParsedStrng.splitlines():
            try:
                parse=self.directive_translate.parseString(line)
                if parse[0][0].lower()=="off" : translate=False
                else: translate=True
            except:
                pass
            if translate:
                preParsedStrngNew+=line+"\n"
        self.verilog=preParsedStrngNew
        try:
            self.tokens = self.verilogbnf.parseString(preParsedStrngNew)
        except:
            for i,l in enumerate(preParsedStrngNew.split("\n")):
                logging.debug("[%d] %s"%(i,l))
            raise

        return self.tokens

if __name__=="__main__":
    print("This module is not ment to be run!")

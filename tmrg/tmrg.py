#!/usr/bin/env python3

# Copyright (c) CERN and the TMRG authors.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import traceback
import pprint
import os
import glob
import filecmp
import copy
import time
import subprocess
import getpass
import socket
import time
import datetime
import hashlib
import zipfile
import logging
from optparse import *
from .verilog_elaborator import *
from .toolset import *


def tmr_reg_list(tokens):
    newtokens = ParseResults([], name=tokens.getName())
    for element in tokens:
        if element[0] in self.toTMR:
            for post in self.EXT:
                newtokens2 = element.deepcopy()
                newtokens2[0] = element[0]+post
                newtokens.append(newtokens2)
        else:
            newtokens.append(element)
    return newtokens


class CmdConstrainParser:
    def __init__(self):
        self.semi = Literal(";")
        self.lpar = Literal("(")
        self.rpar = Literal(")")
        self.equals = Literal("=")
        self.constraints = {"triplicate": set(), "do_not_triplicate": set(), "default": True, "tmr_error": False}

        identLead = alphas+"$_"
        identBody = alphanums+"$_"
        identifier1 = Regex(r"\.?["+identLead+"]["+identBody+"]*(\.["+identLead+"]["+identBody+"]*)*"
                            ).setName("baseIdent")
        identifier2 = Regex(r"\\\S+").setParseAction(lambda t: t[0][1:]).setName("escapedIdent")
        identifier = (identifier1 | identifier2).setResultsName("id")

        self.directive_doNotTriplicate = (Suppress("do_not_triplicate") +
                                          OneOrMore(identifier)).setResultsName("directive_do_not_triplicate")
        self.directive_triplicate = (Suppress("triplicate") + OneOrMore(identifier)
                                     ).setResultsName("directive_triplicate")
        self.directive_default = (Suppress("default") + oneOf("triplicate do_not_triplicate") +
                                  Group(Optional(identifier))).setResultsName("directive_default")
        self.directive_tmr_error = (Suppress("tmr_error") + oneOf("true false") +
                                    Group(Optional(identifier))).setResultsName("directive_tmr_error")
        self.directive_do_not_touch = (Suppress("do_not_touch") + OneOrMore(identifier)
                                       ).setResultsName("directive_do_not_touch")

        self.directiveItem = (self.directive_triplicate |
                              self.directive_doNotTriplicate |
                              self.directive_default |
                              self.directive_tmr_error |
                              self.directive_do_not_touch
                              )

    def parse(self, s):
        try:
            return self.directiveItem.parseString(s)
        except:
            raise ErrorMessage("Error during parsing command line provided constrains (%s)" % s)


class TMR(VerilogElaborator):
    def __init__(self, options, args):
        VerilogElaborator.__init__(self, options, args, cnfgName="tmrg")
        self.EXT = ('A', 'B', 'C')
        self.__voterPresent = False
        self.__fanoutPresent = False
        self.__init_tripclicate_callbacks()

        # command line specified config files
        for fname in self.options.config:
            if os.path.exists(fname):
                logging.debug("Loading command line specified config file from %s" % fname)
                self.config.read(fname)
                if self.options.generateBugReport:
                    bn = os.path.basename(fname)
                    fcopy = os.path.join(self.options.bugReportDir, "cmd_%s.cfg" % bn)
                    logging.debug("Coping  command line specified config file from '%s' to '%s'" % (fname, fcopy))
                    shutil.copyfile(fname, fcopy)
            else:
                raise ErrorMessage("Command line specified config file does not exists at %s" % fname)
        if "tmr_dir" in dir(self.options) and self.options.tmr_dir:
            logging.debug("Setting tmr_dir to %s" % self.options.tmr_dir)
            self.config.set("tmrg", "tmr_dir", self.options.tmr_dir)

        if "rtl_dir" in dir(self.options) and self.options.rtl_dir:
            logging.debug("Setting rtl_dir to %s" % self.options.rtl_dir)
            self.config.set("tmrg", "rtl_dir", self.options.rtl_dir)

        if "tmr_suffix" in dir(self.options) and self.options.tmr_suffix:
            logging.debug("Setting tmr_suffix to %s" % self.options.tmr_suffix)
            self.config.set("tmrg", "tmr_suffix", self.options.tmr_suffix)

        if self.config.has_option('tmrg', 'files'):
            files = self.config.get("tmrg", "files").split()
            for file in files:
                file = file.strip()
                logging.debug("Adding file from config file %s" % file)
                self.args.append(file)

        if self.config.has_option('tmrg', 'libs'):
            files = self.config.get("tmrg", "libs").split()

            for file in files:
                if len(file) == 0:
                    continue
                file = file.strip()
                logging.debug("Adding lib file from config file : %s" % file)
                self.libFiles.append(file)

        # parse command line constrains
        ccp = CmdConstrainParser()
        self.cmdLineConstrains = {}
        for c in self.options.constrain:
            tokens = ccp.parse(c)
            name = tokens.getName()
            if name == "directive_triplicate" or name == "directive_do_not_triplicate":
                tmrVal = False
                if name == "directive_triplicate":
                    tmrVal = True
                for _id in tokens:
                    if _id.find(".") >= 0:
                        module, net = _id.split(".")
                        logging.info("Command line constrain '%s' for net '%s' in module '%s'" %
                                         (name, net, module))
                        if not module in self.cmdLineConstrains:
                            self.cmdLineConstrains[module] = {}
                        self.cmdLineConstrains[module][net] = tmrVal
                    else:
                        logging.info("Command line constrain '%s' for net '%s'" % (name, net))
                        net = _id
                        if not "global" in self.cmdLineConstrains:
                            self.cmdLineConstrains["global"] = {}
                        self.cmdLineConstrains["global"][net] = tmrVal
            elif name == "directive_default":
                tmrVal = False
                if tokens[0].lower() == "triplicate":
                    tmrVal = True
                if len(tokens[1]) > 0:
                    for module in tokens[1]:
                        logging.info("Command line constrain '%s' for module '%s' (value:%s)" %
                                         (name, module, str(tmrVal)))
                        if not module in self.cmdLineConstrains:
                            self.cmdLineConstrains[module] = {}
                        self.cmdLineConstrains[module]["default"] = tmrVal
                else:
                    if not "global" in self.cmdLineConstrains:
                        self.cmdLineConstrains["global"] = {}
                    self.cmdLineConstrains["global"]["default"] = tmrVal
            elif name == "directive_tmr_error":
                tmrErr = False
                if tokens[0].lower() == "true":
                    tmrErr = True
                if len(tokens[1]) > 0:
                    for module in tokens[1]:
                        logging.info("Command line constrain '%s' for module '%s' (value:%s)" %
                                         (name, module, str(tmrErr)))
                        if not module in self.cmdLineConstrains:
                            self.cmdLineConstrains[module] = {}
                        self.cmdLineConstrains[module]["tmr_error"] = tmrErr
                else:
                    if not "global" in self.cmdLineConstrains:
                        self.cmdLineConstrains["global"] = {}
                    self.cmdLineConstrains["global"]["default"] = tmrErr
            elif name == "directive_do_not_touch":
                for module in tokens:
                    if not module in self.cmdLineConstrains:
                        self.cmdLineConstrains[module] = {}
                    if not "constraints" in self.cmdLineConstrains[module]:
                        self.cmdLineConstrains[module]["constraints"] = {}
                    self.cmdLineConstrains[module]["constraints"]["dnt"] = True
                    logging.info("Command line constrain '%s' for module '%s')" % (name, module))

            else:
                logging.warning("Unknown constrain '%s'" % name)
        if len(self.args) == 0:
            rtl_dir = self.config.get("tmrg", "rtl_dir")
            logging.debug("No input arguments specified. All files from rtl_dir (%s) will be parsed." % rtl_dir)
            self.args = [rtl_dir]

    def __init_tripclicate_callbacks(self):
        # scan class looking for triplicator functions
        self.triplicator = {}
        for member in dir(self):
            if member.find("_TMR__triplicate_") == 0:
                token = member[len("_TMR__triplicate_"):].lower()
                self.triplicator[token] = getattr(self, member)
                logging.debug("Found triplicator for %s" % token)

    def __triplicate_directive_default(self, tokens):
        return []

    def __triplicate_directive_triplicate(self, tokens):
        return []

    def __triplicate_directive_do_not_triplicate(self, tokens):
        return []

    def __triplicate_directive_do_not_touch(self, tokens):
        return []

    def __triplicate_directive_tmr_error(self, tokens):
        return []

    def __triplicate(self, tokens, i=""):
        debug = 0
        if debug:
            print(i, "_(1 in )_ >", tokens.getName(), str(tokens)[:100])
        i += "    "
        if isinstance(tokens, ParseResults):
            name = str(tokens.getName()).lower()
            offset = name.find("@")
            if offset != -1:
                name = name[0:offset]
            if len(tokens) == 0:
                return tokens
            if name in self.triplicator:
                logging.debug("Found triplicator for %s" % name)
                if debug:
                    print(i, "_(2 tmr)_>", str(tokens)[:100])
                tokens = self.triplicator[name](tokens)
            else:
                logging.debug("No triplicator for %s : %s" % (name, tokens))
                newTokens = ParseResults([], name=tokens.getName())
                if debug:
                    print(i, "_(3 lis)_ >", str(tokens)[:100])
                i += "    "
                for j in range(len(tokens)):
                    if isinstance(tokens[j], ParseResults):
                        tmrToks = self.__triplicate(tokens[j], i+"    ")
                        if isinstance(tmrToks, list):
                            for idx, otokens in enumerate(tmrToks):
                                newTokens.append(otokens)
                                if debug:
                                    print(i, "_(4 out)_>", str(otokens)[:100])
                        else:
                            newTokens.append(tmrToks)
                            tid = id(tokens[j])
                            for kname in tokens.keys():
                                if id(tokens[kname]) == tid:
                                    newTokens[kname] = tmrToks
                            if debug:
                                print(i, "_(4 out)_>", str(tmrToks)[:100])
                    else:
                        newTokens.append(tokens[j])
                        tid = id(tokens[j])
                        for kname in tokens.keys():
                            if id(tokens[kname]) == tid:
                                newTokens[kname] = tokens[j]
                        if debug:
                            print(i, "_(4 out)_>", str(tokens[j])[:100])
                if debug:
                    print(i, "_(new)_>", newTokens.getName(), str(newTokens)[:100])
                return newTokens
        else:
            # we have a string!
            if debug:
                print(i, "_(str2)_>", str(tokens[j])[:100])
        if debug:
            print(i, "_(ret)_>", str(tokens)[:100])
        return tokens

    @staticmethod
    def _append_tmr(net, letter):
        pointpos = net.find(".")

        if pointpos == -1:
            return net + letter

        return net[0:pointpos] + letter + net[pointpos:]

    def __triplicate_Always(self, tokens):
        result = []
        # check if the module needs triplication
        ids = self.getLeftRightHandSide(tokens)
        tmr = self.shouldTriplicate(ids)

        logging.debug("[Always block]")
        logging.debug("      Left :"+" ".join(sorted(ids["left"])))
        logging.debug("      Right:"+" ".join(sorted(ids["right"])))
        logging.debug("      TMR  :"+str(tmr))
        if not tmr:
            self._addVotersIfTmr(ids["right"], addWires="output")
            return tokens

        self._addFanoutsIfTmr(ids["right"], addWires="output")

        for i in self.EXT:
            cpy = tokens.deepcopy()
            self.smartreplace(cpy, i)
            """
            for name in list(ids["right"])+list(ids["left"]):
                _to_name = self._append_tmr(name, i)
                self.replace(cpy, name, _to_name)
            """
            self.appendToBlockName(cpy, i)
            result.append(cpy)
        return result

    def __triplicate_initialStmt(self, tokens):
        result = []
        ids = self.getLeftRightHandSide(tokens)
        tmr = self.shouldTriplicate(ids)

        logging.debug("[Initial block]")
        logging.debug("      Left :"+" ".join(sorted(ids["left"])))
        logging.debug("      Right:"+" ".join(sorted(ids["right"])))
        logging.debug("      TMR  :"+str(tmr))

        if not tmr:
            return tokens
        for i in self.EXT:
            cpy = tokens.deepcopy()
            """
            for name in list(ids["right"])+list(ids["left"]):
                _to_name = self._append_tmr(name, i)
                self.replace(cpy, name, _to_name)
            """
            self.smartreplace(cpy, i)
            self.appendToBlockName(cpy, i)
            result.append(cpy)
        return result

    def __triplicate_continuousassign(self, tokens):
        # check if the module needs triplication
        ids = self.getLeftRightHandSide(tokens)
        tmr = self.shouldTriplicate(ids)

        logging.debug("[Continuous Assign block]")
        logging.debug("      Left :"+" ".join(sorted(ids["left"])))
        logging.debug("      Right:"+" ".join(sorted(ids["right"])))
        logging.debug("      TMR  :"+str(tmr))

        if not tmr:
            logging.info("Adding voters, if needed, for signals: " + " ".join(ids["right"]))
            self._addVotersIfTmr(ids["right"], group="", addWires="output")
            return tokens

        logging.info("Adding fanouts, if needed, for signals: " + " ".join(ids["right"]))
        self._addFanoutsIfTmr(ids["right"], addWires="output")
        result = []
        for i in self.EXT:
            cpy = tokens.deepcopy()
            """
            for name in list(ids["right"]) + list(ids["left"]):
                _to_name = self._append_tmr(name, i)
                self.replace(cpy, name, _to_name)
            """
            self.smartreplace(cpy, i)
            result.append(cpy)

        return result

    def __triplicate_NetDecl1(self, tokens):
        ids = self.getLeftRightHandSide(tokens)
        tmr = self.shouldTriplicate(ids)

        logging.debug("[net1decl]")
        logging.debug("      Left :"+" ".join(sorted(ids["left"])))
        logging.debug("      Right:"+" ".join(sorted(ids["right"])))
        logging.debug("      TMR  :"+str(tmr))
        if not tmr:
            return tokens

        result = []
        for i in self.EXT:
            cpy = tokens.deepcopy()
            for name in list(ids["right"])+list(ids["left"]):
                _to_name = self._append_tmr(name, i)
                self.replace(cpy, name, _to_name)
            result.append(cpy)

        return result

    def __triplicate_integerDecl(self, tokens):
        #        print tokens
        logging.debug("[integer dec]")
        logging.debug("      left : "+str(tokens[-1]))
        toTMR = set()
        for _id in tokens[-1]:
            name = _id[0]
            TMR = False
            if name in self.current_module["nets"]:
                if self.current_module["nets"][name]["tmr"]:
                    TMR = True
            else:
                if len(name) and name[0] == '`':
                    logging.warning("Define %s" % name)
                else:
                    logging.warning("Unknown net '%s' (TMR may malfunction)" % name)
            if TMR:
                toTMR.add(name)
        result = []
        if len(toTMR):
            for i in self.EXT:
                cpy = tokens.deepcopy()
                for name in toTMR:
                    _to_name = self._append_tmr(name, i)
                    self.replace(cpy, name, _to_name)
                result.append(cpy)
            return result
        else:
            return tokens

    def __triplicate_fields(self, tokens):
        # Don't triplicate
        # If not present, will try to triplicate members!
        return tokens

    def __triplicate_customDecl(self, tokens):
        logging.debug("[custom decl]")
        logging.debug("      left : "+str(tokens.get("identifiers")))

        toTMR = set()
        for name in tokens.get("identifiers"):
            name = name[0]
            TMR = False
            if name in self.current_module["nets"]:
                if self.current_module["nets"][name]["tmr"]:
                    TMR = True
            else:
                if len(name) and name[0] == '`':
                    logging.warning("Define %s" % name)
                else:
                    logging.warning("Unknown net '%s' (TMR may malfunction)" % name)
            if TMR:
                toTMR.add(name)
        result = []
        if len(toTMR):
            for i in self.EXT:
                cpy = tokens.deepcopy()
                for name in toTMR:
                    _to_name = self._append_tmr(name, i)
                    self.replace(cpy, name, _to_name)
                result.append(cpy)
            return result
        else:
            return tokens

    def __triplicate_netdecl(self, tokens):
        logging.debug("[net decl]")
        logging.debug("      left : "+str(tokens.get("identifiers")))

        toTMR = set()
        for identifier in tokens.get("identifiers"):
            name = identifier.get("name")[0]
            TMR = False
            if name in self.current_module["nets"]:
                if self.current_module["nets"][name]["tmr"]:
                    TMR = True
            else:
                if len(name) and name[0] == '`':
                    logging.warning("Define %s" % name)
                else:
                    logging.warning("Unknown net '%s' (TMR may malfunction)" % name)
            if TMR:
                toTMR.add(name)

        result = []
        if len(toTMR):
            for i in self.EXT:
                cpy = tokens.deepcopy()
                """
                for name in toTMR:
                    _to_name = self._append_tmr(name, i)
                    self.replace(cpy, name, _to_name)
                """
                self.smartreplace(cpy, i)
                result.append(cpy)
            return result
        else:
            return tokens

    def __triplicate_netDeclWAssign(self, tokens):
        ids = self.getLeftRightHandSide(tokens)
        tmr = self.shouldTriplicate(ids)

        logging.debug("[net declaration with assigment]")
        logging.debug("      Left :"+" ".join(sorted(ids["left"])))
        logging.debug("      Right:"+" ".join(sorted(ids["right"])))
        logging.debug("      TMR  :"+str(tmr))

        logging.debug("DETECTED %s" % tokens.asDict())

        # A simple assignment is A = B
        left = tokens.get("assignments")[0].get("lvalue")[0]
        right = tokens.get("assignments")[0].get("expr@rvalue")

        logging.debug("DETECTED LEFT (%s) %s" % (left.getName(), left.asDict()))
        logging.debug("DETECTED RIGHT (%s) %s" % (right.getName(), right.asDict()))

        left_reg = False
        right_reg = False

        if left.getName() == "reg_reference":
            left = left.get("name")[0]
            left_reg = True

            if len(right) == 1 and isinstance(right[0], ParseResults) and right[0].getName() == "reg_reference":
                right = right[0].get("name")[0]

                right_reg = True

        # Process simple assignments to look for voters, fanins, fanouts
        if left_reg and right_reg:
            # check if this is explicit fanout
            if left.endswith(self.EXT) and left[:-1] == right:
                logging.info("Removing declaration of '%s' (it comes from a fanout of %s)" % (left, right))
                return ParseResults([], name=tokens.getName())

            # check fanin
            if right.endswith(self.EXT) and right[:-1] == left:
                logging.info("Removing declaration of '%s' (it was declared for fanin)" % (left))
                return ParseResults([], name=tokens.getName())

            if len(self.voting_nets) and (right, left) in self.voting_nets:
                bits = " ".join([i["len"] for i in self.current_module["nets"][right]["packed_ranges"]])
                logging.info("TMR voting %s -> %s (bits: %s)" % (right, left, bits))
                newtokens = ParseResults([], name=tokens.getName())

                a = right+self.EXT[0]
                b = right+self.EXT[1]
                c = right+self.EXT[2]
                for ext in self.EXT:
                    voterInstName = "%sVoter%s" % (right, ext)
                    name_voted = "%s%s" % (left, ext)
                    netErrorName = "%sTmrError%s" % (right, ext)
                    self._addVoterExtended(voterInstName=voterInstName,
                                           inA=a,
                                           inB=b,
                                           inC=c,
                                           out=name_voted,
                                           tmrError=netErrorName,
                                           type=self.current_module["nets"][right]["type"],
                                           is_custom_type=self.current_module["nets"][right]["is_custom_type"],
                                           attributes=self.current_module["nets"][right]["attributes"],
                                           packed_ranges=self.current_module["nets"][right]["packed_ranges"],
                                           unpacked_ranges=self.current_module["nets"][right]["unpacked_ranges"],
                                           group=ext,
                                           addWires="output")

                return newtokens

        elif left_reg:
            # check if this is part of explicit voter
            if left.endswith(self.EXT):
                if left[:-1] in self.current_module["nets"]:
                    logging.info("Explicit fanin '%s' part of '%s' (group %s)" % (left, left[:-1], left[-1]))
                    for name in list(ids["right"]):
                        self._addVoter(name, "", addWires="output")
                    return tokens

        # FIX ME !!!!!!!!!! quick and dirty !!!!!!
        # commented to allow access to specific tmrerror signals ! # and "tmrError" in self.current_module["nets"]:
        if left.lower().find("tmrerror") >= 0:
            if left == "tmrError":
                logging.info("Removing declaration of '%s' (%s)" % (left, str(tokens)))
                return []

            for net in self.current_module["nets"]:
                netTmrErr = net+"TmrError"
                if left == netTmrErr:
                    logging.info("Removing declaration of %s" % (left))
                    return []

            for net in self.current_module["instances"]:
                netTmrErr = net+"tmrError"
                if left == netTmrErr:
                    logging.info("Removing declaration of %s" % (left))
                    return []

        # in any other case, triplicate right hand side
        result = []
        if not tmr:
            logging.info("Adding voters, if needed, for signals: " + " ".join(ids["right"]))
            self._addVotersIfTmr(ids["right"], group="", addWires="output")
            return tokens

        logging.info("Adding fanouts, if needed, for signals: " + " ".join(ids["right"]))
        self._addFanoutsIfTmr(ids["right"], addWires="output")

        for i in self.EXT:
            cpy = tokens.deepcopy()
            """
            for name in list(ids["right"])+list(ids["left"]):
                _to_name = self._append_tmr(name, i)
                self.replace(cpy, name, _to_name)
            """
            self.smartreplace(cpy, i)
            result.append(cpy)
        return result

    def ___triplicate_untouchable_module_instantiation(self, tokens):
        identifier = tokens.get("moduleName")[0]
        instances = tokens.get("moduleInstances")

        new_instances = ParseResults([], name=instances.getName())

        for instance in instances:
            iname = instance[0][0]
            itmr = self.current_module["instances"][iname]["tmr"]

            # If the instance is to be triplicated, triplicate it as a whole
            if itmr:

                # Instantiate it 3 times with appropriate signal names in the connectivity
                for post in self.EXT:
                    instCpy = instance.deepcopy()

                    instCpy[0][0] += post ;# Append suffix to instance name
                    for port in instCpy[1]:
                        # Can't support implicit connections
                        if len(port) == 1:
                            raise ErrorMessage("Implicit connections in module instantiation are not supported\nProblematic instance: `%s` (module: `%s`)" % (iname, identifier))

                        # Disconnected port: nothing to be done
                        if len(port[3]) == 0:
                            continue

                        # Change signal references in connectivity
                        self.smartreplace(port[3], post, check=False)
                        """
                        ids = self.getLeftRightHandSide(port[3])
                        for rid in ids["right"]:
                            self.replace(port[3], rid, rid+post)
                        """
                    new_instances.append(instCpy)

            # If the instance is not to be triplicated
            else:
                new_instances.append(instance)

            # Add voters and/or fanouts for the signals in the connectivity
            for port in instance[1]:
                dname = port[1]

                # Non-existent port for module
                if not dname in self.modules[identifier]["io"]:
                    raise ErrorMessage("Module '%s' does not have port '%s'" % (identifier, dname))

                # Unconnected port: skip
                if len(port[3]) == 0:
                    continue

                # Ahm don't know what this is for.
                if isinstance(port[3][0], str):
                    continue

                dtype = self.modules[identifier]["io"][dname]['type']
                ids = self.getLeftRightHandSide(port[3])
                # Iterate over signals on the right hand side
                for sname in ids["right"]:
                    if sname not in self.current_module["nets"]:
                        logging.debug("Wire '%s' does not exist in the net database" % sname)
                        logging.debug("The connection will not be changed.")
                        continue

                    stmr = self.current_module["nets"][sname]["tmr"]
                    logging.debug("      %s (%s) -> %s (tmr:%s)" % (dname, dtype, sname, str(stmr)))

                    # Instance is triplicated but the signal is not.
                    if itmr and not stmr:
                        # If port is input, must fanout the non-triplicated signal to the triplicated port
                        if dtype == "input":
                            self._addFanout(sname, addWires="output")

                        # If port is input, must vote the triplicated port to the non-triplicated signal
                        else:
                            self._addVoter(sname, addWires="input")

                    # Instance is not triplicated but the signal is.
                    elif not itmr and stmr:
                        # If port is input, must vote the triplicated signal to the non-triplicated port
                        if dtype == "input":
                            self._addVoter(sname, addWires="output")

                        # If port is output, must fanout the non-triplicated port to the triplicated signal
                        else:
                            self._addFanout(sname, addWires="input")

        # Update instance list
        tokens["moduleInstances"] = new_instances
        return tokens

    def ___triplicate_touchable_module_instantiation(self, tokens):
        identifier = tokens.get("moduleName")[0]
        instances = tokens.get("moduleInstances")

        identifierTMR = identifier+"TMR"

        # Update module name
        tokens["moduleName"][0] = identifierTMR

        # New instances
        tokensIns = ParseResults([], name=instances.getName())

        for instance in instances:
            iname = instance[0][0]

            # Can we touch the instance?
            if "dntinst" in self.current_module["constraints"] and iname in self.current_module["constraints"]["dntinst"]:
                logging.debug("Instance '%s' has property do_not_touch." % iname)
                tokensIns.append(instance)
                continue

            ports = instance[1]
            instCpy = instance.deepcopy()
            newPorts = ParseResults([], name=ports.getName())

            for port in ports:
                if port.getName() != "namedPortConnection":
                    raise ErrorMessage("Cannot support unnamed port connections in triplicated instance: %s." % iname)

                dport = port[1]  # skip dot
                sport = port[3]

                if dport is not None and not dport in self.modules[identifier]["nets"]:
                    raise ErrorMessage("Module '%s' does not have port '%s'" % (identifier, dport))

                dportTmr = self.modules[identifier]["nets"][dport]["tmr"]
                logging.debug("      %s (tmr:%s) -> %s" % (dport, dportTmr, self.vf.format(sport)))

                # Port is NOT to be triplicated!
                if not dportTmr:
                    # Just copy it as it is
                    newPorts.append(port)

                # Port is to be triplicated
                elif dportTmr:
                    for post in self.EXT:
                        portCpy = port.deepcopy()
                        portCpy[1] = portCpy[1]+post
                        self.smartreplace(portCpy[3], post, check=False)
                        newPorts.append(portCpy)

                # Add voters or fanouts
                ids = self.getLeftRightHandSide(sport)
                for sname in ids['right']:
                    stmr = self.current_module["nets"][sname]["tmr"]
                    dtype = self.modules[identifier]["io"][dport]["type"]

                    # Instance is triplicated but the signal is not.
                    if dportTmr and not stmr:
                        # If port is input, must fanout the non-triplicated signal to the triplicated port
                        if dtype == "input":
                            self._addFanout(sname, addWires="output")

                        # If port is input, must vote the triplicated port to the non-triplicated signal
                        else:
                            self._addVoter(sname, addWires="input")

                    # Instance is not triplicated but the signal is.
                    elif not dportTmr and stmr:
                        # If port is input, must vote the triplicated signal to the non-triplicated port
                        if dtype == "input":
                            self._addVoter(sname, addWires="output")

                        # If port is output, must fanout the non-triplicated port to the triplicated signal
                        else:
                            self._addFanout(sname, addWires="input")

            # TODO ADD TMR ERROR !!!!!!!!!!!!
            # "tmrError" in self.modules[identifier]["nets"]:
            if self.modules[identifier]["constraints"]["tmrErrorOut"]:
                for post in self.EXT:
                    netName = "%stmrError%s" % (iname, post)
                    logging.debug("Adding net '%s' for module '%s'" % (netName, identifier))
                    tmrErrOut = self.vp.namedPortConnection.parseString(".tmrError%s(%s)" % (post, netName))[0]
                    self._addTmrErrorWire(post, netName)
                    newPorts.append(tmrErrOut)

            instCpy[1] = newPorts
            tokensIns.append(instCpy)

        tokens["moduleInstances"] = tokensIns
        return tokens

    def __triplicate_ModuleInstantiation(self, tokens):
        identifier = tokens.get("moduleName")[0]
        instances = [i[0][0] for i in tokens.get("moduleInstances")]
        logging.debug("[module instances]")
        logging.debug("      Module name    :"+identifier)
        logging.debug("      Instance names :" + ", ".join(instances))

        # Do we know the module? If not, raise an error.
        if not identifier in self.modules:
            logging.error("")
            logging.error("      Module %s is unknown" % identifier)
            raise ErrorMessage("      Module %s is unknown" % identifier)

        # If we cannot touch the module...
        if "dnt" in self.modules[identifier]["constraints"] and self.modules[identifier]["constraints"]["dnt"]:
            logging.debug("      Module '%s' will not be touched (id:%s)" % (identifier, instances))

            return self.___triplicate_untouchable_module_instantiation(tokens)

        # If the instance can be touched
        else:
            return self.___triplicate_touchable_module_instantiation(tokens)

    def __triplicate_gateDecl(self, tokens):
        logging.warning("Verilog gate level modeling is generally not supported.")
        logging.warning("Please carefully review the generated code.")
        gate = tokens[0]
        instance = tokens[3][0][0][0]
        logging.debug("[gate instances]")
        logging.debug("      gate: %s", gate)
        logging.debug("      ins : %s", instance)

        logging.debug("      Gate '%s' will not be touched (%s)" % (gate, instance))

        nets_tmr = set()
        for port in tokens[3][0][1]:
            ids = self.getLeftRightHandSide(port)
            for rid in ids["right"]:
                net_tmr = self.current_module["nets"][rid]["tmr"]
                nets_tmr.add(net_tmr)

        if len(nets_tmr)!=1:
            raise ErrorMessage("Gate '%s' connects to triplicated and not triplicated wires!" % (instance))
        tmr = next(iter(nets_tmr))
        if tmr:
                ret = []
                # triplicate instances
                for post in self.EXT:
                    instCpy = tokens.deepcopy()
                    for inst in range(len(instCpy[3])):  # iterate over all instances
                        instCpy[3][inst][0][0] = instCpy[3][inst][0][0]+post  # change instance name
                        for port in instCpy[3][inst][1]:
                            ids = self.getLeftRightHandSide(port)
                            for rid in ids["right"]:
                                net_tmr = self.current_module["nets"][rid]["tmr"]
                                self.replace(port, rid, rid+post)
                    ret.append(instCpy)

                return ret
        else:
            ret = tokens
        return tokens

    def __slice_module(self, tokens):
        result = []
        header = tokens[0]
        moduleName = header[1]

        # generate slice
        slice = tokens.deepcopy()
        slice[0][1] = str(moduleName)+"_slice"
        wrapperWires = []
        portsToAdd = []
        portsToAddVoted = []

        if len(self.voting_nets):
            newModuleItems = ParseResults([], name=tokens[1].getName())
            for moduleItem in slice[1]:
                ids = self.getLeftRightHandSide(moduleItem)
                vote = False
                if moduleItem.getName() == "moduleInstantiation":
                    modName = moduleItem[0]
                    if not "dnt" in self.modules[modName]["constraints"] and self.modules[modName]["constraints"]["dnt"]:
                        raise ErrorMessage(
                            "Error during slicing. Module '%s' should have directive 'do_not_touch'" % modName)

                if moduleItem.getName() == "netDecl3":
                    if len(ids["right"]) == 1 and len(ids["left"]) == 1:
                        for net, netVoted in self.voting_nets:
                            if netVoted in ids["left"] and net in ids["right"]:
                                vote = True
                                voteNet = net
                if not vote:
                    newModuleItems.append(moduleItem)
                else:
                    inst = voteNet+"Voter"
                    logging.info("Instantiating voter %s" % inst)
                    net = self.modules[moduleName]["nets"][voteNet]

                    _range = " ".join([i["range"] for i in net["packed_ranges"]])
                    _len = " + ".join([i["len"] for i in net["packed_ranges"]]) if _range else "1"

                    _o = voteNet+"Voted"
                    _err = voteNet+"TmrError"
                    _a = voteNet+"A"
                    _b = voteNet+"B"
                    _c = voteNet+"C"
                    newModuleItems.insert(0, self.vp.portBody.parseString("input %s %s;" % (_range, _a))[0])
                    newModuleItems.insert(0, self.vp.portBody.parseString("input %s %s;" % (_range, _b))[0])
                    newModuleItems.insert(0, self.vp.portBody.parseString("input %s %s;" % (_range, _c))[0])
                    newModuleItems.insert(0, self.vp.portBody.parseString("output %s %s;" % (_range, voteNet))[0])
                    newModuleItems.insert(0, self.vp.netDecl.parseString("wire %s %s;" % (_range, _o))[0])
                    wrapperWires.insert  (0, self.vp.netDecl.parseString("wire %s %s;" % (_range, _a))[0])
                    wrapperWires.insert  (0, self.vp.netDecl.parseString("wire %s %s;" % (_range, _b))[0])
                    wrapperWires.insert  (0, self.vp.netDecl.parseString("wire %s %s;" % (_range, _c))[0])

                    portsToAddVoted.append(_a)
                    portsToAddVoted.append(_b)
                    portsToAddVoted.append(_c)
                    portsToAdd.append(voteNet)
                    width = ""
                    if _len != "1":
                        width += "#(.WIDTH(%s)) " % _len
                    majorityVoterCell = "majorityVoter"+self.options.common_cells_postfix
                    if "majority_voter_cell" in self.modules[moduleName]["constraints"]:
                        majorityVoterCell = self.modules[moduleName]["constraints"]["majority_voter_cell"]
                    newModuleItems.append(self.vp.moduleInstantiation.parseString(majorityVoterCell+" %s%s (.inA(%s), .inB(%s), .inC(%s), .out(%s));" %
                                                                                  (width, inst, _a, _b, _c, _o))[0])
                    self.__voterPresent = True
            slice[1] = newModuleItems
            for port in portsToAdd + portsToAddVoted:
                slice[0][3].append(self.vp.port.parseString(port)[0])

        # generate wrapper
        wrapper = tokens.deepcopy()

        portList = []
        # triplicate module header | add tmr signals
        if len(wrapper[0]) > 2:
            #print "w",wrapper
            ports = wrapper[0][3]
            #print ports
            newports = ParseResults([], name=ports.getName())
            for port in ports:
                port = port[0]
                if port.getName() == "reg_reference":
                    portName = port.get("name")[0]
                    portList.append(portName)
                    if not portName in self.current_module["nets"]:
                        logging.warning("Net '%s' unknown." % portName)
                        continue
                    doTmr = self.current_module["nets"][portName]["tmr"]
                    portstr = "Port %s -> " % (portName)

                    if doTmr:
                        sep = ""
                        for post in self.EXT:
                            newport = portName+post
                            newports.append(newport)
                            portstr += sep+newport
                            sep = ", "
                    else:
                        newports.append(port)
                    logging.debug(portstr)
                else:
                    portName = port[4][0]
                    portList.append(portName)
                    if not portName in self.current_module["nets"]:
                        logging.warning("Net '%s' unknown." % portName)
                        continue
                    doTmr = self.current_module["nets"][portName]["tmr"]
                    portstr = "Port %s -> " % (portName)
                    if doTmr:
                        sep = ""
                        for post in self.EXT:
                            portCpy = port.deepcopy()
                            newPortName = portName+post
                            self.replace(portCpy, portName, newPortName)
                            newports.append(portCpy)
                            portstr += sep+newPortName
                            sep = ", "
                    else:
                        newports.append(port)

                    logging.debug(portstr)

            if "tmrError" in self.current_module["nets"]:
                groups = set(self.current_module["voters"].keys()) | set(self.current_module["tmrErrNets"].keys())
                for group in sorted(groups):
                    newport = "tmrError%s" % group
                    newports.append(newport)
                    logging.debug("Port %s" % (newport))
            wrapper[0][3] = newports

        newModuleItems = ParseResults([], name=tokens[1].getName())
        for moduleItem in wrapper[1]:
            if moduleItem.getName() in ("input", "output"):
                newModuleItems.append(self.__triplicate(moduleItem))
            pass
        for wire in wrapperWires:
            newModuleItems.append(wire)
        for ext in self.EXT:
            instName = wrapper[0][1]+ext
            modName = slice[0][1]
            portStr = ""
            sep = ""
            for port in portList + portsToAdd:
                portStr += sep+".%s(%s%s)" % (port, port, ext)
                sep = ","
            for port in portsToAddVoted:
                portStr += sep+".%s(%s)" % (port, port)
            newModuleItems.append(self.vp.moduleInstantiation.parseString(
                "%s %s(%s);" % (modName, instName, portStr))[0])
        wrapper[1] = newModuleItems

        result.append(slice)
        result.append(wrapper)
        return result

    def __triplicate_module(self, tokens):
        header = tokens[0]

        moduleName = header[1]
        self.current_module = self.modules[moduleName]
        if "dnt" in self.modules[moduleName]["constraints"] and self.modules[moduleName]["constraints"]["dnt"]:
            logging.info("Module '%s' is not to be touched" % moduleName)
            return tokens
        if "slicing" in self.modules[moduleName]["constraints"]:
            logging.info("Module '%s' is to be sliced" % moduleName)
            return self.__slice_module(tokens)
        header[1] = str(moduleName)+"TMR"
        logging.debug("")
        logging.debug("= "*50)
        logging.debug("Module %s -> %s" % (moduleName, header[1]))
        logging.debug("= "*50)

        logging.debug("- module body "+"- "*43)

        moduleBody = tokens[1]
        moduleBody = self.__triplicate(moduleBody)
        tokens[1] = moduleBody

        logging.debug("- module header "+"- "*42)
        # triplicate module header | add tmr signals
        if len(header) > 3:
            ports = header[3]
            newports = ParseResults([], name=ports.getName())
            for port in ports:
                if port.getName() == "port":
                    portName = port[0][0]
                    if not portName in self.current_module["nets"]:
                        logging.warning("Net '%s' unknown." % portName)
                        continue
                    doTmr = self.current_module["nets"][portName]["tmr"]
                    portstr = "Port (%s - %s) %s -> " % (port.getName(), doTmr, portName)

                    if doTmr:
                        sep = ""
                        for post in self.EXT:
                            newport = portName+post
                            newports.append(newport)
                            portstr += sep+newport
                            sep = ", "
                    else:
                        newports.append(portName)
                        portstr += portName
                    logging.debug(portstr)
                else:
                    _identifiers = None
                    if "standard" in port:
                        _identifiers = port.get("standard").get("identifiers")
                    elif "custom" in port:
                        _identifiers = port.get("custom").get("identifiers")
                    else:
                        _identifiers = port.get("identifiers")

                    for identifier in _identifiers:
                        portName = identifier.get("name")[0]
                        if not portName in self.current_module["nets"]:
                            logging.warning("Net '%s' unknown." % portName)
                            continue
                        doTmr = self.current_module["nets"][portName]["tmr"]
                        portstr = "Port (%s - %s) %s -> " % (port.getName(), doTmr, portName)
                        if doTmr:
                            sep = ""
                            for post in self.EXT:
                                portCpy = port.deepcopy()
                                newPortName = portName+post
                                self.replace(portCpy, portName, newPortName)
                                newports.append(portCpy)
                                portstr += sep+newPortName
                                sep = ", "
                        else:
                            newports.append(port)
                            portstr += portName

                        logging.debug(portstr)

            if self.current_module["constraints"]["tmrErrorOut"]:
                groups = set(self.current_module["voters"].keys()) | set(self.current_module["tmrErrNets"].keys())
                for group in sorted(groups):
                    newport = "tmrError%s" % group
                    if self.current_module["portMode"] == "ANSI":
                        newport = self.vp.portOut.parseString("output %s" % newport)[0]
                        newports.append(newport)
                    else:
                        newports.append(newport)
                    logging.debug("Port %s" % (newport))
            header[3] = newports

        logging.debug("- voters & fanouts  "+"- "*40)
        groups = set(self.current_module["voters"].keys()) | set(self.current_module["tmrErrNets"].keys())
        for group in sorted(groups):
            errSignals = set()
            if group in sorted(self.current_module["voters"]):
                for voter_name in sorted(self.current_module["voters"][group]):
                    voter = self.current_module["voters"][group][voter_name]
                    _o = voter["out"]
                    _err = voter["err"]
                    _a = voter["inA"]
                    _b = voter["inB"]
                    _c = voter["inC"]

                    _type = "wire" if voter["is_custom_type"] else voter["type"]
                    __range_start = 1 if voter["is_custom_type"] else 0
                    _range = " ".join([i["range"] for i in voter["packed_ranges"][__range_start:]])
                    _len = "(" + " * ".join(["(" + i["len"] + ")" for i in voter["packed_ranges"]]) + ")" if _range else "1"
                    _arange = " ".join([i["range"] for i in voter["unpacked_ranges"]])

                    if _range:
                        _range += " "

                    if _arange:
                        _arange = " "+_arange

                    attributes = voter["attributes"]
                    addWires = voter["addWires"]
                    logging.info("Instantiating voter %s of type %s (addWires:%s)" % (voter_name, _type, addWires))

                    if addWires == "output":
                        logging.debug("Adding output %s %s" % (_type, _o))
                        moduleBody.insert(0, self.vp.netDecl.parseString("%s %s%s%s;" % (_type, _range, _o, _arange))[0])
                        logging.debug("Added output %s %s" % (_type, _o))

                    elif addWires == "input":
                        logging.debug("Adding input %s %s, %s , %s" % (_type, _a, _b, _c))
                        moduleBody.insert(0, self.vp.netDecl.parseString("%s %s%s%s;" % (_type, _range, _a, _arange))[0])
                        moduleBody.insert(0, self.vp.netDecl.parseString("%s %s%s%s;" % (_type, _range, _b, _arange))[0])
                        moduleBody.insert(0, self.vp.netDecl.parseString("%s %s%s%s;" % (_type, _range, _c, _arange))[0])

                    width = ""
                    if _len != "1":
                        width += "#(.WIDTH(%s)) " % _len

                    majorityVoterCell = "majorityVoter"+self.options.common_cells_postfix
                    if "majority_voter_cell" in self.current_module["constraints"]:
                        majorityVoterCell = self.current_module["constraints"]["majority_voter_cell"]

                    if "tmrError" in self.current_module["nets"]:
                        errSignals.add(_err)
                    else:
                        moduleBody.insert(0, self.vp.netDecl.parseString("wor %s;" % _err)[0])

                    logging.debug("Instantiating voter...")
                    if voter["unpacked_ranges"]:
                        logging.debug("Iterating over unpacked ranges...")
                        genstr = "genstr\n"

                        for i, unpacked_range in enumerate(voter["unpacked_ranges"]):
                            varname = "gen_%s%d" % (voter_name, i)
                            genstr = "genvar %s;" % varname

                            moduleBody.append(self.vp.genVarDecl.parseString(genstr)[0])

                            _start = "((%s>%s) ? %s : %s )" % (unpacked_range["from"], unpacked_range["to"], unpacked_range["to"], unpacked_range["from"])
                            _stop  = "((%s>%s) ? %s : %s )" % (unpacked_range["from"], unpacked_range["to"], unpacked_range["from"], unpacked_range["to"])
                            _for   = "for(%s=%s;%s<=%s;%s=%s+1) begin : %s_fanout" % (varname, _start, varname, _stop, varname, varname, varname)

                            genstr += _for + "\n"

                        genstr += majorityVoterCell + " %s%s (.inA(%s[%s]), .inB(%s[%s]), .inC(%s[%s]), .out(%s[%s]), .tmrErr(%s));" % \
                            (width, voter_name, _a, varname, _b, varname, _c, varname, _o, varname, _err)

                        for i in range(len(voter["unpacked_ranges"])):
                            genstr += "end\n"

                        genstr += "endgenerate"

                        moduleBody.append(self.vp.generate.parseString(genstr)[0])
                        logging.debug("... done")
                    else:  # normal voter
                        moduleBody.append(self.vp.moduleInstantiation.parseString(
                            majorityVoterCell + " %s%s (.inA(%s), .inB(%s), .inC(%s), .out(%s), .tmrErr(%s));" %
                            (width, voter_name, _a, _b, _c, _o, _err))[0])

                    logging.debug("... done")

            if group in sorted(self.current_module["tmrErrNets"]):
                errSignals = errSignals | self.current_module["tmrErrNets"][group]

            # add wires for all error signals
            if len(errSignals):
                for signal in sorted(errSignals):
                    moduleBody.insert(0, self.vp.netDecl.parseString("wor %s;" % signal)[0])

            # after all voters are added, we can create an "OR" of all them
            if "tmrError" in self.current_module["nets"]:

                if self.current_module["constraints"]["tmrErrorOut"]:
                    if self.current_module["portMode"] == "non-ANSI":
                        moduleBody.insert(0, self.vp.outputDecl.parseString("output tmrError%s;" % group)[0])
                else:
                    if not self.current_module["constraints"]["tmrErrorOut"]:
                        moduleBody.insert(0, self.vp.netDecl.parseString("wire tmrError%s;" % group)[0])
                        logging.debug("Adding wire tmrError%s;" % group)
                sep = ""
                asgnStr = "assign tmrError%s=" % group
                if len(errSignals):
                    for signal in sorted(errSignals):
                        signalRaw = signal[:-len("TmrError"+group)]
                        if "tmr_error_exclude" in self.current_module["constraints"] and signalRaw in self.current_module["constraints"]["tmr_error_exclude"]:
                            logging.debug("Removing signal '%s' from tmrError", signal)
                            continue
                        asgnStr += sep+signal
                        sep = "|"
                else:
                    asgnStr += "1'b0"
                asgnStr += ";"
                moduleBody.append(self.vp.continuousAssign.parseString(asgnStr)[0])

        for fanout_name in sorted(self.current_module["fanouts"]):
            fanout = self.current_module["fanouts"][fanout_name]
            logging.info("Instantiating fanout %s" % fanout_name)
            _in = fanout["in"]
            _a = fanout["outA"]
            _b = fanout["outB"]
            _c = fanout["outC"]

            _type = "wire" if fanout["is_custom_type"] else fanout["type"]
            __range_start = 1 if fanout["is_custom_type"] else 0
            _range = " ".join([i["range"] for i in fanout["packed_ranges"][__range_start:]])
            _array_range = " ".join([i["range"] for i in fanout["unpacked_ranges"]])
            _len = "(" + " * ".join(["(" + i["len"] + ")" for i in fanout["packed_ranges"]]) + ")" if _range else "1"

            addWires = fanout["addWires"]
            attributes = fanout["attributes"]
            if addWires == "output":
                logging.debug("Adding output %s %s, %s , %s" % (_type, _a, _b, _c))
                moduleBody.insert(0, self.vp.netDecl.parseString("%s %s %s %s %s;" %
                                                                  (_type, attributes, _range, _a, _array_range))[0])
                moduleBody.insert(0, self.vp.netDecl.parseString("%s %s %s %s %s;" %
                                                                  (_type, attributes, _range, _b, _array_range))[0])
                moduleBody.insert(0, self.vp.netDecl.parseString("%s %s %s %s %s;" %
                                                                  (_type, attributes, _range, _c, _array_range))[0])
                logging.debug("Added output wires %s, %s , %s" % (_a, _b, _c))
            elif addWires == "input":
                logging.debug("Adding input %s %s" % (_type, _in))
                moduleBody.insert(0, self.vp.netDecl.parseString("%s %s %s %s %s;" %
                                                                  (_type, attributes, _range, _in, _array_range))[0])

            width = ""
            if _len != "1":
                width += "#(.WIDTH(%s)) " % _len

            fanoutCell = "fanout"+self.options.common_cells_postfix
            if "fanout_cell" in self.current_module["constraints"]:
                fanoutCell = self.current_module["constraints"]["fanout_cell"]

            if fanout["unpacked_ranges"]:
                genstr = "genstr\n"

                for i, unpacked_range in enumerate(fanout["unpacked_ranges"]):
                    varname = "gen_%s%d" % (fanout_name, i)
                    genstr = "genvar %s;" % varname

                    moduleBody.append(self.vp.genVarDecl.parseString(genstr)[0])

                    _start = "((%s>%s) ? %s : %s )" % (unpacked_range["from"], unpacked_range["to"], unpacked_range["to"], unpacked_range["from"])
                    _stop  = "((%s>%s) ? %s : %s )" % (unpacked_range["from"], unpacked_range["to"], unpacked_range["from"], unpacked_range["to"])
                    _for   = "for(%s=%s;%s<=%s;%s=%s+1) begin : %s_fanout" % (varname, _start, varname, _stop, varname, varname, varname)

                    genstr += _for + "\n"

                genstr += fanoutCell + " %s%s (.inA(%s[%s]), .inB(%s[%s]), .inC(%s[%s]), .out(%s[%s]), .tmrErr(%s));" % \
                    (width, fanout_name, _a, varname, _b, varname, _c, varname, _o, varname, _err)

                for i in range(len(fanout["unpacked_ranges"])):
                    genstr += "end\n"

                genstr += "endgenerate"

                moduleBody.append(self.vp.generate.parseString(genstr)[0])
            else:  # normal fanout
                moduleBody.append(self.vp.moduleInstantiation.parseString(fanoutCell+" %s%s (.in(%s), .outA(%s), .outB(%s), .outC(%s));" %
                                                                          (width, fanout_name, _in, _a, _b, _c))[0])

        # detect if user created constrains which could generate invalid code
        vouter_outputs = []
        for group in sorted(groups):
            if group in sorted(self.current_module["voters"]):
                for voter in sorted(self.current_module["voters"][group]):
                    vouter_outputs.append(self.current_module["voters"][group][voter]["out"])
        for fanout in sorted(self.current_module["fanouts"]):
            _in = self.current_module["fanouts"][fanout]["in"]
            if _in in vouter_outputs:
                logging.warning("Signal '%s' is connected to fanout input and voter output." % (_in))
                logging.warning("Probably the resulting code does not reflect the design intent.")
                logging.warning("Please consider upgrading tmrg directives.")


        paramPos = 0
        for i, item in enumerate(moduleBody):
            if item.getName() == "paramDecl":
                logging.debug("Moving declaration to the front '%s'" % (str(item)))
                moduleBody.insert(paramPos, item)
                paramPos += 1
                del moduleBody[i+1]
            if item.getName() == "localparamDecl":
                logging.debug("Moving declaration to the front '%s'" % (str(item)))
                moduleBody.insert(paramPos, item)
                paramPos += 1
                del moduleBody[i+1]
            if item.getName() == "package_import_declaration":
                logging.debug("Moving import to the front '%s'" % (str(item)))
                moduleBody.insert(paramPos, item)
                paramPos += 1
                del moduleBody[i+1]
        return [tokens]

    def __triplicate_portbody(self, tokens):
        before = str(tokens.get("identifiers"))
        tokens["identifiers"] = self._tmr_list(tokens.get("identifiers"))
        after = str(tokens.get("identifiers"))
        logging.debug("%s %s -> %s" % (tokens.get("dir"), before, after))
        return tokens

    def __triplicate_porthdr(self, tokens):
        return self.__triplicate_portbody(tokens)

    def checkIfContains(self, tokens, label):
        def _check(tokens, label):
            if isinstance(tokens, ParseResults):
                for tok in tokens:
                    res = _check(tok, label)
                    if res:
                        return True
                return False
            else:
                return label == tokens
        return _check(tokens, label)

    def replace(self, tokens, _from, _to):
        def _replace(tokens, _from, _to):
            if isinstance(tokens, ParseResults):
                """
                for i, d in enumerate(tokens):
                    if isinstance(d, ParseResults):
                        _replace(d, _from, _to)
                    else:
                        check_and_replace(_from, tokens, i, _to)
                """

                for k, v in tokens.items():
                    if not isinstance(v, ParseResults):
                        #check_and_replace(_from, tokens, k, _to)
                        continue

                    if v.getName() == "name":
                        """
                        netname, netfield = self.split_name(v[0])
                        print("DEADBEEF %s (%s) is %s -> %s" % (netname, v[0], _from, _to))
                        if netname not in self.current_module["nets"]:
                            continue

                        if self.current_module["nets"][netname]["type"] in self.current_module["structs"]:
                            if _from == netname:
                                if netfield:
                                    tokens[k][0] = _to + "." + netfield
                                else:
                                    tokens[k][0] = _to

                        elif netfield:
                            raise ValueError("Trying to access field %s of %s, which is not a struct" % (netfield, netname))

                        elif _from == netname:
                            tokens[k][0] = _to
                        """
                        if _from == v[0]:
                            tokens[k][0] = _to
                    else:
                        _replace(v, _from, _to)

        return _replace(tokens, _from, _to)

    def smartreplace(self, tokens, ext, done=None, check=True):
        # Not a ParseResults, probably text, just ignore
        if not isinstance(tokens, ParseResults):
            return

        if done is None:
            done = []

        keys = list(tokens.keys())
        keys.extend(list(range(len(tokens))))
        for k in keys:
            v = tokens[k]

            if id(tokens[k]) in done:
                continue
            else:
                done.append(id(tokens[k]))

            # Not a ParseResults, probably text, just ignore
            if not isinstance(v, ParseResults):
                continue

            # Only replace "name" results. Otherwise, probe.
            if v.getName() != "name":
                self.smartreplace(v, ext, done, check)
                continue

            netname, netfield = self.split_name(v[0])
            #print("DEADBEEF %s (%s) is %s -> %s" % (netname, v[0], _from, _to))

            # Net not known. Ignore.
            if netname not in self.current_module["nets"]:
                continue

            # Net not to be triplicated. Ignore.
            if check and not self.current_module["nets"][netname]["tmr"]:
                continue

            # If a struct, treat it accordingly.
            if self.current_module["nets"][netname]["type"] in self.current_module["structs"]:
                if netfield:
                    tokens[k][0] = netname + ext + "." + netfield
                else:
                    tokens[k][0] = netname + ext

                continue

            # Looks like a struct, but it's not. Throw error.
            elif netfield:
                raise ValueError("Trying to access field %s of %s, which is not a struct" % (netfield, netname))

            # Not a struct field reference.
            tokens[k][0] = netname + ext

    def appendToBlockName(self, tokens, postfix):
        def _appendToBlockName(tokens, postfix):
            if isinstance(tokens, ParseResults):
                for i in range(len(tokens)):
                    if isinstance(tokens[i], ParseResults):
                        if tokens[i].getName() == "blockName":
                            tokens[i][0] += postfix
                        else:
                            res = _appendToBlockName(tokens[i], postfix)

        return _appendToBlockName(tokens, postfix)

    def replaceDot(self, tokens, post):
        def _replace(tokens, post):
            if isinstance(tokens, ParseResults):
                for i in range(len(tokens)):
                    if isinstance(tokens[i], ParseResults):
                        res = _replace(tokens[i], post)
                    else:
                        if tokens[i][0] == '.':
                            tokens[i] += post
        return _replace(tokens, post)

    def replaceAll(self, tokens, post, dot=1):
        for var in self.toTMR:
            self.replace(tokens, var, var+post)
        if dot:
            self.replaceDot(tokens, post)
        return tokens

    def shouldTriplicate(self, ids):
        leftTMR = False
        leftNoTMR = False
        logging.debug("SHOULDTRIPLICATE Will check nets: %s" % (ids["left"]))
        for net in ids["left"]:
            # Check if struct
            netname, netfield = self.split_name(net)

            if netname not in self.current_module["nets"]:
                if net in self.current_module["params"]:
                    logging.debug("SHOULDTRIPLICATE Found parameter %s. Ignoring." % net)

                elif netname[0] == '`':
                    logging.debug("SHOULDTRIPLICATE Found macro %s. Ignoring." % net)

                elif netname in self.current_module["instances"]:
                    # TODO: This could - in principle - be triplicateable.
                    logging.debug("SHOULDTRIPLICATE Found instance name %s. Assuming %s is a hierarchical reference. Ignoring." % (netname, net))

                else:
                    logging.warning("%s cannot be recognized as neither parameter, macro, or hierarchical reference. Leaving it untouched." % net)

            else:
                if self.current_module["nets"][netname]["tmr"]:
                    logging.debug("SHOULDTRIPLICATE Found net %s. Triplicate: %s" % (netname, "True"))
                    leftTMR = True

                if not self.current_module["nets"][netname]["tmr"]:
                    logging.debug("SHOULDTRIPLICATE Found net %s. Triplicate: %s" % (netname, "False"))
                    leftNoTMR = True

                logging.debug("SHOULDTRIPLICATE Found net %s. Triplicate: %s" % (netname, "Default"))

        if leftTMR and leftNoTMR:
            logging.error("Block contains both type of elements (should and should not be triplicated!) in one expression.")
            logging.error("This request will not be properly processed!")
            logging.error("Elements: %s" % (" ".join(sorted(ids["left"]))))
            return False

        return leftTMR

    def tmrNbAssgnmt(self, t):
        # cpy=t.deepcopy()
        # for v in self.toTMR:
        # #if self.checkIfContains(cpy,"rst"):
        #     print "shot!"
        #     self.replace(cpy,v,v+"A")
        return t

    def _tmr_list(self, tokens):
        newtokens = ParseResults([], name=tokens.getName())
        for identifier in tokens:
            name = identifier.get("name")[0]
            if name in self.current_module["nets"]:
                if self.current_module["nets"][name]["tmr"]:
                    for post in self.EXT:
                        nt = identifier.deepcopy()
                        nt["name"] = [name+post]
                        nt[0] = [name+post]
                        newtokens.append(nt)
                else:
                    nt = identifier.deepcopy()
                    newtokens.append(nt)
            else:
                logging.warning("Net %s unknown!" % name)
                newtokens.append(name)
        return newtokens

    def hasAnythingToTMR(self, tokens):
        toTMR = 0
        for varToTMR in self.toTMR:
            if self.checkIfContains(tokens, varToTMR):
                toTMR = 1
                break
        return toTMR

    def _addVoterExtended(self, voterInstName, inA, inB, inC, out, tmrError, type, is_custom_type, packed_ranges, unpacked_ranges, group, attributes, addWires=""):
        if not group in self.current_module["voters"]:
            self.current_module["voters"][group] = {}
            logging.info("Creating TMR error group %s" % group)
        if not voterInstName in self.current_module["voters"][group]:
            logging.debug("Adding voter '%s' to group '%s' (extended)" % (voterInstName, group))
            logging.debug("    %s %s %s -> %s & %s" % (inA, inB, inC, out, tmrError))
            self.current_module["voters"][group][voterInstName] = {
                "inA": inA,
                "inB": inB,
                "inC": inC,
                "out": out,
                "err": tmrError,
                "attributes": attributes,
                "type": type,
                "is_custom_type": is_custom_type,
                "packed_ranges": packed_ranges,
                "unpacked_ranges": unpacked_ranges,
                "group": group,
                "addWires": addWires}
            self.__voterPresent = True

    def _addVoter(self, netID, group="", addWires=""):
        if not group in self.current_module["voters"]:
            self.current_module["voters"][group] = {}
            logging.info("Creating TMR error group %s" % group)

        voterInstName = "%sVoter" % (netID)
        if not voterInstName in self.current_module["voters"][group]:

            nameVoted = "%s" % (netID)
            netErrorName = "%sTmrError" % (netID)
            inA = netID+self.EXT[0]
            inB = netID+self.EXT[1]
            inC = netID+self.EXT[2]
            logging.debug("Adding voter '%s' to group '%s' (simple)" % (voterInstName, group))
            logging.debug("    %s %s %s -> %s & %s" % (inA, inB, inC, nameVoted, netErrorName))

            packed_ranges = self.current_module["nets"][netID]["packed_ranges"]
            unpacked_ranges = self.current_module["nets"][netID]["unpacked_ranges"]
            attributes = self.current_module["nets"][netID]["attributes"]
            nettype = self.current_module["nets"][netID]["type"]
            nettype_is_custom = self.current_module["nets"][netID]["is_custom_type"]
            self.current_module["voters"][group][voterInstName] = {
                "inA": inA,
                "inB": inB,
                "inC": inC,
                "out": nameVoted,
                "err": netErrorName,
                "packed_ranges": packed_ranges,
                "unpacked_ranges": unpacked_ranges,
                "attributes": attributes,
                "type": nettype,
                "is_custom_type": nettype_is_custom,
                "group": group,
                "addWires": addWires}
            self.__voterPresent = True

    def _addVotersIfTmr(self, idList, group="", addWires="output"):
        for netID in idList:
            if self.current_module["nets"][netID]["tmr"]:
                self._addVoter(netID, group=group, addWires=addWires)

    def _addFanout(self, netID, addWires=""):
        inst = netID+"Fanout"
        if not netID in self.current_module["nets"]:
            logging.warning("Net %s unknown in addFanout!" % netID)
            return

        if not inst in self.current_module["fanouts"]:
            _in = netID
            outA = netID+self.EXT[0]
            outB = netID+self.EXT[1]
            outC = netID+self.EXT[2]
            packed_ranges = self.current_module["nets"][netID]["packed_ranges"]
            unpacked_ranges = self.current_module["nets"][netID]["unpacked_ranges"]
            attributes = self.current_module["nets"][netID]["attributes"]
            type = self.current_module["nets"][netID]["type"]
            is_custom_type = self.current_module["nets"][netID]["is_custom_type"]
            logging.debug("Adding fanout %s" % inst)
            logging.debug("    %s -> %s %s %s packed %s unpacked %s" % (_in, outA, outB, outC, packed_ranges, unpacked_ranges))
            self.current_module["fanouts"][inst] = {
                "in": _in,
                "outA": outA,
                "outB": outB,
                "outC": outC,
                "packed_ranges": packed_ranges,
                "unpacked_ranges": unpacked_ranges,
                "attributes": attributes,
                "type": type,
                "is_custom_type": is_custom_type,
                "addWires": addWires
            }
            self.__fanoutPresent = True

    def _addFanouts(self, idList, addWires=""):
        for netId in idList:
            netname, netfields = self.split_name(netId)
            self._addFanout(netname, addWires=addWires)

    def _addFanoutsIfTmr(self, idList, addWires=""):
        for netId in idList:
            netname, netfields = self.split_name(netId)
            if not self.current_module["nets"][netname]["tmr"]:
                self._addFanout(netname, addWires=addWires)

    def _addTmrErrorWire(self, post, netName):
        if not post in self.current_module["tmrErrNets"]:
            self.current_module["tmrErrNets"][post] = set()
        self.current_module["tmrErrNets"][post].add(netName)

    def exc(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("")
        logging.error("TMR exception:")
        for l in traceback.format_exception(exc_type, exc_value,
                                            exc_traceback):
            for ll in l.split("\n"):
                logging.error(ll)
        logging.error(ll)

    def __getLenStr(self, toks):
        rangeLen = "1"
        if len(toks) < 2:
            return rangeLen
        left = toks[-2]
        right = toks[-1]
        rangeLen = "%s - %s + 1" % (self.vf.format(left), self.vf.format(right))
        try:
            rangeInt = eval(rangeLen)
            rangeLen = "%d" % rangeInt
        except:
            pass
        return rangeLen

    def elaborate(self, allowMissingModules=False):
        """ Elaborate the design
        :return:
        """
        # allowMissingModules = False # FIXME shoudl not be here like that (added for wrappers)
        VerilogElaborator.elaborate(self, allowMissingModules=allowMissingModules)
        # apply constrains
        logging.info("")
        logging.info("Applying constrains")
        for module in sorted(self.modules):
            logging.info("Module %s" % module)

            # tmr error output
            # global settings
            tmrErrOut = self.config.getboolean("global", "tmr_error")
            s = "configGlobal:%s" % (str(tmrErrOut))
            # from source code
            if "tmr_error" in self.modules[module]["constraints"]:
                tmrErrOut = self.modules[module]["constraints"]["tmr_error"]
                s += " -> srcModule:%s" % (str(tmrErrOut))
            # from module configuration
            if self.config.has_section(module) and self.config.has_option(module, "tmr_error"):
                tmrErrOut = self.config.getboolean(module, "tmr_error")
                s += " -> configModule:%s" % (str(tmrErrOut))
            # from command line arguments
            if module in self.cmdLineConstrains and "tmr_error" in self.cmdLineConstrains[module]:
                tmrErrOut = self.cmdLineConstrains[module]["tmr_error"]
                s += " -> cmdModule:%s" % (str(tmrErrOut))
            logging.info(" | tmrErrOut : %s (%s)" % (str(tmrErrOut), s))
            if tmrErrOut:
                self.modules[module]["nets"]["tmrError"] = {
                    "tmr": True,
                    "attributes" : "",
                    "packed_ranges": [], 
                    "unpacked_ranges": []
                }
            self.modules[module]["constraints"]["tmrErrorOut"] = tmrErrOut

            s = "false"
            do_not_touch = False
            if self.modules[module]["constraints"]["dnt"]:
                do_not_touch = self.modules[module]["constraints"]["dnt"]
                s += " -> srcModule:%s" % (str(do_not_touch))

            if self.config.has_section(module) and self.config.has_option(module, "do_not_touch"):
                do_not_touch = self.config.getboolean(module, "do_not_touch")
                s += " -> configModule:%s" % (str(do_not_touch))
            if module in self.cmdLineConstrains and "constraints" in self.cmdLineConstrains[module] and "dnt" in self.cmdLineConstrains[module]["constraints"]:
                do_not_touch = True
                s += " -> cmdModule:%s" % (str(do_not_touch))
            self.modules[module]["constraints"]["dnt"] = do_not_touch
            logging.info(" | do_not_touch : %s (%s)" % (str(tmrErrOut), s))

            for net in self.modules[module]["nets"]:
                tmr = False
                # default from global configuration
                globalTmr = self.config.get("global", "default")
                if globalTmr.lower() == "triplicate":
                    tmr = True
                s = "configGlobalDefault:%s" % (str(tmr))
                # default from source code
                if "default" in self.modules[module]["constraints"]:
                    tmr = self.modules[module]["constraints"]["default"]
                    s += " -> srcModuleDefault:%s" % (str(tmr))

                # default from module configuration
                if self.config.has_section(module) and self.config.has_option(module, "default"):
                    modDefault = self.config.get(module, "default")
                    if modDefault.lower() == "triplicate":
                        tmr = True
                    else:
                        tmr = False
                    s += " -> configModuleDefault:%s" % (str(tmr))

                # default from command line arguments
                if module in self.cmdLineConstrains and "default" in self.cmdLineConstrains[module]:
                    tmr = self.cmdLineConstrains[module]["default"]
                    s += " -> cmdModuleDefault:%s" % (str(tmr))

                # net specific from source code
                if net in self.modules[module]["constraints"]:
                    tmr = self.modules[module]["constraints"][net]
                    s += " -> src:%s" % (str(tmr))

                # net specific from configuration
                if self.config.has_section(module) and self.config.has_option(module, net):
                    conf = self.config.get(module, net)
                    if conf.lower() == "triplicate":
                        tmr = True
                    else:
                        tmr = False
                    s += " -> config:%s" % (str(tmr))

                # net specific from command line
                if module in self.cmdLineConstrains and net in self.cmdLineConstrains[module]:
                    tmr = self.cmdLineConstrains[module][net]
                    s += " -> cmd:%s" % (str(tmr))

                if "slicing" in self.modules[module]["constraints"]:
                    tmr = True
                    s += " -> slicing:%s" % (str(tmr))

                if "dnt" in self.modules[module]["constraints"] and self.modules[module]["constraints"]["dnt"]:
                    tmr = False
                    s += " -> do_not_touch:%s" % (str(tmr))

                logging.info(" | module %s net %s : %s (%s)" % (module, net, str(tmr), s))
                self.modules[module]["nets"][net]["tmr"] = tmr

            for inst in self.modules[module]["instances"]:
                tmr = False
                # default from global configuration
                globalTmr = self.config.get("global", "default")
                if globalTmr.lower() == "triplicate":
                    tmr = True
                s = "configGlobalDefault:%s" % (str(tmr))
                # default from module configuration
                if self.config.has_section(module) and self.config.has_option(module, "default"):
                    modDefault = self.config.get(module, "default")
                    if modDefault.lower() == "triplicate":
                        tmr = True
                    else:
                        tmr = False
                    s += " -> configModuleDefault:%s" % (str(tmr))
                # default from source code
                if "default" in self.modules[module]["constraints"]:
                    tmr = self.modules[module]["constraints"]["default"]
                    s += " -> srcModuleDefault:%s" % (str(tmr))

                # default from command line arguments
                if module in self.cmdLineConstrains and "default" in self.cmdLineConstrains[module]:
                    tmr = self.cmdLineConstrains[module]["default"]
                    s += " -> cmdModuleDefault:%s" % (str(tmr))
                # inst specific from configuration
                if self.config.has_section(module) and self.config.has_option(module, inst):
                    conf = self.config.get(module, inst)
                    if conf.lower() == "triplicate":
                        tmr = True
                    else:
                        tmr = False
                    s += " -> config:%s" % (str(tmr))
                # inst specific from source code
                if inst in self.modules[module]["constraints"]:
                    tmr = self.modules[module]["constraints"][inst]
                    s += " -> src:%s" % (str(tmr))
                # inst specific from command line
                if module in self.cmdLineConstrains and inst in self.cmdLineConstrains[module]:
                    tmr = self.cmdLineConstrains[module][inst]
                    s += " -> cmd:%s" % (str(tmr))

                logging.info(" | inst %s : %s (%s)" % (inst, str(tmr), s))
                self.modules[module]["instances"][inst]["tmr"] = tmr

        # apply special constrains by name conventions
        logging.info("")
        logging.info("Applying constrains by name")
        self.voting_nets = []
        for module in sorted(self.modules):
            logging.info("Module %s" % module)
            for net1 in self.modules[module]["nets"]:
                # Look for voting nets...
                net2 = net1+"Voted"
                if not net2 in self.modules[module]["nets"]:
                    continue

                self.voting_nets.append((net1, net2))
                logging.info("Full voting detected for nets %s -> %s" % (net1, net2))
                if not self.modules[module]["nets"][net1]["tmr"] or not self.modules[module]["nets"][net2]["tmr"]:
                    logging.warning("Nets for full voting should be triplicated! (%s:%s, %s:%s)" % (
                        net1, self.modules[module]["nets"][net1]["tmr"], net2, self.modules[module]["nets"][net2]["tmr"]))

        if len(self.voting_nets):
            logging.info("Voting present (%d nets)" % (len(self.voting_nets)))

    def _addCommonModules(self, fname, voter=False, fanout=False):
        if not self.__fanoutPresent and not self.__voterPresent:
            return
        if not self.config.getboolean("tmrg", "add_common_definitions"):
            return
        if self.options.no_common_definitions:
            return
        logging.info("Declarations of voters and fanouts are being added to %s" % fname)
        f = open(fname, "a")

        if self.__voterPresent:
            vfile = os.path.join(self.scriptDir,  self.config.get("tmrg", "voter_definition"))
            logging.info("Taking voter declaration from %s" % vfile)
            f.write("\n\n// %s\n" % vfile)
            fileContent = readFile(vfile)
            fileContent = fileContent.replace("majorityVoter", "majorityVoter"+self.options.common_cells_postfix)
            f.write(fileContent)

        if self.__fanoutPresent:
            ffile = os.path.join(self.scriptDir,  self.config.get("tmrg", "fanout_definition"))
            logging.info("Taking fanout declaration from %s" % ffile)
            f.write("\n\n// %s\n" % ffile)
            fileContent = readFile(ffile)
            fileContent = fileContent.replace("fanout", "fanout"+self.options.common_cells_postfix)
            f.write(fileContent)
        f.close()

    def getHeader(self, fname, fout):
        HLEN = 100
        header = "/"+("*"*HLEN)+"\n"

        def getRevInfo(fname):
            git_version, errors = runCommand('git rev-parse HEAD')
            if git_version:
                oStr = "Git SHA           : %s" % git_version.rstrip().decode("utf-8")
                git_status, errors = runCommand('git status --short %s'%fname)
                git_status = git_status.rstrip().decode("utf-8")
                if git_status:
                    oStr += " (%s)\n" % git_status
                else:
                    oStr += "\n"
            else:
                oStr = "Git SHA           : File not in git repository!\n"

            t = os.path.getmtime(fname)
            oStr += "Modification time : %s\n" % datetime.datetime.fromtimestamp(t)
            oStr += "File Size         : %s\n" % os.path.getsize(fname)
            oStr += "MD5 hash          : %s" % hashlib.md5(open(fname, 'rb').read()).hexdigest()

            return oStr

        def addLine(header, s, align="left"):
            if align == "left":
                line = s+" "*(HLEN-4-len(s))
                header += " * %s *\n" % line
            if align == "center":
                slen = HLEN-4-len(s)
                sleft = int(slen/2)
                sright = slen-sleft
                line = (" "*sleft) + s + (" "*sright)
                header += " * %s *\n" % line
            return header

        def getTmrgRev():
            ver = tmrg_version()
            if ver == "trunk":
                out, err = runCommand("svnversion %s" % sys.argv[0])
                ver += " (svnversion: %s)" % out.rstrip()
            return ver
        header = addLine(header, "! THIS FILE WAS AUTO-GENERATED BY TMRG TOOL !", align="center")
        header = addLine(header, "! DO NOT EDIT IT MANUALLY !", align="center")
        header = addLine(header, "")
        header = addLine(header, "file    : %s" % (fout))
        header = addLine(header, "")
        header = addLine(header, "user    : %s" % (getpass.getuser()))
        header = addLine(header, "host    : %s" % (socket.gethostname()))
        header = addLine(header, "date    : %s" % (time.strftime("%d/%m/%Y %H:%M:%S")))
        header = addLine(header, "")
        header = addLine(header, "workdir : %s" % os.getcwd())
        for l in textwrap.wrap("cmd     : %s" % (" ".join(sys.argv)), 100, subsequent_indent="          "):
            header = addLine(header, l)

        header = addLine(header, "tmrg rev: %s" % (getTmrgRev()))

        header = addLine(header, "")
        header = addLine(header, "src file: %s" % fname)
        for l in getRevInfo(fname).split("\n"):
            header = addLine(header, "          "+l)
        header = addLine(header, "")
        header += " "+("*"*HLEN)+"/\n\n"
        return header

    def triplicate(self):
        """ Triplicate the design
        :return:
        """
        tmrSuffix = "TMR"
        spaces = self.config.getint("tmrg", "spaces")

        logging.debug("")
        logging.info("Triplication starts here")
        tmr_start_time = time.time()
        self.tmrLinesTotal = 0
        self.statsLogs = []
        if not os.path.isdir(self.config.get("tmrg", "tmr_dir")):
            raise ErrorMessage("Specified output directory does not exists (%s)" % self.config.get("tmrg", "tmr_dir"))

        for fname in sorted(self.files):
            file, ext = os.path.splitext(os.path.basename(fname))
            logging.info("")
            logging.debug("#"*100)
            logging.info("Triplicating file %s" % (fname))
            logging.debug("#"*100)
            tokens = self.files[fname]
            tmrTokens = self.__triplicate(tokens)

            fout = os.path.join(self.config.get("tmrg", "tmr_dir"), file+tmrSuffix+ext)
            foutnew = fout+'.new'
            logging.debug("Saving result of triplication to %s" % foutnew)

            f = open(foutnew, "w")
            if self.options.header and self.config.getboolean("tmrg", "add_header"):
                header = self.getHeader(fname, fout)
                f.write(header)
            f.write(self.vf.format(tmrTokens).replace("\t", " "*self.config.getint("tmrg", "spaces")))
            f.close()

            if self.options.stats:
                lines = self.lineCount(foutnew)
                self.statsLogs.append("File '%s' has %d lines " % (foutnew, lines))
                self.tmrLinesTotal += lines

        topFile, ext = os.path.splitext(os.path.basename(self.topFile))
        ftop = os.path.join(self.config.get("tmrg", "tmr_dir"), topFile+tmrSuffix+ext+'.new')
        self._addCommonModules(ftop)

        if self.options.simplify_verilog:
            try:
                from pyosys import libyosys as ys
                mode = "-o"
                for fname in sorted(self.files):
                    file, ext = os.path.splitext(os.path.basename(fname))
                    fout = os.path.join(self.config.get("tmrg", "tmr_dir"), file+tmrSuffix+ext)+'.new'
                    design = ys.Design()
                    ys.run_pass("tee -q %s yosys.log read_verilog %s" % (mode, fout) , design)
                    ys.run_pass("tee -q -a yosys.log proc", design)
                    ys.run_pass("tee -q -a yosys.log write_verilog  %s" % fout, design)
                    mode = "-a"
                    del design
            except ModuleNotFoundError:
                raise ErrorMessage("Option '--simplify-verilog' requires pyosys.")

        for fname in sorted(self.files):
            file, ext = os.path.splitext(os.path.basename(fname))
            fout = os.path.join(self.config.get("tmrg", "tmr_dir"), file+tmrSuffix+ext)
            foutnew = fout+'.new'

            if self.options.generateBugReport:
                bn = file+tmrSuffix+ext
                fcopy = os.path.join(self.options.bugReportDir, bn)
                logging.debug("Coping output file from '%s' to '%s'" % (foutnew, fcopy))
                shutil.copyfile(foutnew, fcopy)

            if os.path.exists(fout):
                if filecmp.cmp(fout, foutnew):
                    logging.info("File '%s' exists. Its content is up to date." % fout)
                    logging.debug("Removing temporary file %s." % foutnew)
                    os.remove(foutnew)
                else:
                    if self.config.getboolean("tmrg", "overwrite_files"):
                        logging.debug("Overwriting %s by %s" % (fout, foutnew))
                        os.rename(foutnew, fout)
                    else:
                        logging.warning("File '%s' exists. Saving output to '%s'" % (fout, foutnew))
            else:
                logging.info("Saving output to '%s'" % (fout))
                logging.debug("Rename %s to %s" % (foutnew, fout))
                os.rename(foutnew, fout)
        self.genSDC()
        if self.options.stats:
            tmr_time = time.time()-tmr_start_time
            for line in self.statsLogs:
                print(line)
            print("Total number of triplicated lines: %d " % self.tmrLinesTotal)
            print("Triplication time : %.3f s " % tmr_time)
            print("-"*80)

    def genSDC(self):
        tmrSuffix = "TMR"

        def _findVotersAndFanouts(module, i="", ret=[]):
            for fanoutInst in self.modules[module]["fanouts"]:
                fanout = self.modules[module]["fanouts"][fanoutInst]
                postfix = ""
                if len(fanout["unpacked_ranges"] + fanout["packed_ranges"]) > 0:
                    postfix = "[*]"
                ret.append(i+fanout["outA"]+postfix)
                ret.append(i+fanout["outB"]+postfix)
                ret.append(i+fanout["outC"]+postfix)
                ret.append(i+fanout["in"]+postfix)

            for group in self.modules[module]["voters"]:
                for voterInst in self.modules[module]["voters"][group]:
                    voter = self.modules[module]["voters"][group][voterInst]
                    postfix = ""
                    if len(voter["unpacked_ranges"] + voter["packed_ranges"]) > 0:
                        postfix = "[*]"
                    ret.append(i+voter["inA"]+postfix)
                    ret.append(i+voter["inB"]+postfix)
                    ret.append(i+voter["inC"]+postfix)
                    ret.append(i+voter["out"]+postfix)

            for instName in self.modules[module]["instances"]:
                ni = i+"%s/" % instName
                inst = self.modules[module]["instances"][instName]["instance"]
                if inst in self.modules:
                    _findVotersAndFanouts(inst, ni, ret)
                else:
                    pass
            return ret

        if self.config.getboolean("tmrg", "sdc_generate") or self.options.sdc_generate:
            topFile, ext = os.path.splitext(os.path.basename(self.topFile))
            if self.options.sdc_fileName != "":
                fsdc = self.options.sdc_fileName
            elif self.config.get("tmrg", "sdc_file_name") != "":
                fsdc = self.config.get("tmrg", "sdc_file_name")
            else:
                fsdc = os.path.join(self.config.get("tmrg", "tmr_dir"), topFile+tmrSuffix+".sdc")
            logging.info("Generating SDC constraints file %s" % fsdc)

            header = ""
            if self.config.getboolean("tmrg", "sdc_headers") or self.options.sdc_headers:
                header = "set sdc_version 1.3\n"
            # generate sdf file
            ret = _findVotersAndFanouts(self.topModule, i="/")
            f = open(fsdc, "w")
            f.write(header)
            f.write("""
set tmrgSucces 0
set tmrgFailed 0
proc constrainNet netName {
  global tmrgSucces
  global tmrgFailed
  # find nets matching netName pattern
  set nets [dc::get_net $netName]
  if {[llength $nets] != 0} {
    set_dont_touch $nets
    incr tmrgSucces
  } else {
    puts "\[TMRG\] Warning! Net(s) '$netName' not found"
    incr tmrgFailed
  }
}

""")
            if self.__voterPresent:
                # f.write("set_dont_touch majorityVoter\n")
                pass
            if self.__fanoutPresent:
                # f.write("set_dont_touch fanout\n")
                pass
            retset = set(ret)  # we can have some duplicates because of voters
            for l in sorted(retset):
                f.write("constrainNet %s\n" % l)

            f.write('\n\n    puts "TMRG successful  $tmrgSucces failed $tmrgFailed"\n')

            f.close()

            if self.options.generateBugReport:
                fcopy = os.path.join(self.options.bugReportDir, os.path.basename(fsdc))
                logging.debug("Coping output file from '%s' to '%s'" % (fsdc, fcopy))
                shutil.copyfile(fsdc, fcopy)



def main():
    OptionParser.format_epilog = lambda self, formatter: self.epilog
    parser = OptionParser(version="TMRG %s" % tmrg_version(),
                          usage="%prog [options] fileName [fileName2 fileName3]", epilog=epilog)

    parser.add_option("-v",  "--verbose",          dest="verbose",      action="count",
                      default=0, help="More verbose output (use: -v, -vv, -vvv..)")
    parser.add_option("",  "--doc",               dest="doc",  action="store_true",
                      default=False, help="Open documentation in web browser")

    actionGroup = OptionGroup(parser, "Actions")
    actionGroup.add_option("-p", "--parse-only",        action="store_true",
                           dest="parse",     default=False, help="Parse")
    actionGroup.add_option("-e", "--elaborate",         action="store_true",
                           dest="elaborate", default=False, help="Elaborate")
    actionGroup.add_option("", "--log",                 dest="log",
                           default="",             help="Store detailed log to file")
    parser.add_option_group(actionGroup)

    dirGroup = OptionGroup(parser, "Directories")
    dirGroup.add_option("",   "--rtl-dir",           dest="rtl_dir",      action="store", default="",
                        help="All files from this directory are taken as input files (only if no input files are specified as arguments)")
    dirGroup.add_option("",   "--inc-dir",           dest="inc_dir",      action="append", default=[],
                        help="Directory where to look for include files (use option --include to actualy include the files during preprocessing)")
    dirGroup.add_option("",   "--tmr-dir",           dest="tmr_dir",      action="store", default="",
                        help="Directory for output files (where all the *TMR.v files are placed)")
    dirGroup.add_option("-l",  "--lib",              dest="libs",       action="append",    default=[],
                        help="Verilog file to be included as a library (modules from this file are not triplicated)")
    parser.add_option_group(dirGroup)

    tmrGroup = OptionGroup(parser, "Triplication")
    tmrGroup.add_option("",    "--tmr-suffix",       dest="tmr_suffix",   action="store", default="")
    tmrGroup.add_option("-c",  "--config",           dest="config",
                        action="append",   default=[], help="Load config file")
    tmrGroup.add_option("-w",  "--constrain",        dest="constrain",
                        action="append",   default=[], help="Load config file")
    tmrGroup.add_option("", "--no-common-definitions", dest="no_common_definitions", action="store_true",
                        default=False, help="Do not add definitions of common modules (majorityVoter and fanout)")
    tmrGroup.add_option("", "--common-cells-postfix",  dest="common_cells_postfix",  action="store",
                        default="",    help="String to be appended to common cell names")
    tmrGroup.add_option("",  "--no-header",          dest="header",       action="store_false",
                        default=True, help="Do not append  information header to triplicated file.")
    tmrGroup.add_option("",  "--sdc-generate",       dest="sdc_generate",   action="store_true",
                        default=False, help="Generate SDC file for Design Compiler")
    tmrGroup.add_option("",  "--sdc-headers",        dest="sdc_headers",
                        action="store_true",   default=False, help="Append SDC headers")
    tmrGroup.add_option("",  "--sdc-file-name",      dest="sdc_fileName",    default="",   help="Specify SDC filename")
    tmrGroup.add_option("",  "--generate-report",    dest="generateBugReport",
                        action="store_true",   default=False, help="Generate bug report")
    tmrGroup.add_option("",  "--stats",              dest="stats",    action="store_true",   help="Print statistics")
    tmrGroup.add_option("",  "--include",            dest="include",    action="store_true",
                        default=False,   help="Include include files")
    dirGroup.add_option("",   "--top-module",        dest="top_module",
                        action="store", default="",  help="Specify top module name")
    dirGroup.add_option("",   "--simplify-verilog",   dest="simplify_verilog",
                        action="store_true", default=False,  help="Simplifies generated verilog code to enable SET injection (requires pyosys)")
    parser.add_option_group(tmrGroup)
    logFormatter = logging.Formatter('[%(levelname)-7s] %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    exit_code = 0
    try:
        (options, args) = parser.parse_args()


        if options.verbose == 0:
            consoleHandler.setLevel(logging.WARNING)
        if options.verbose == 1:
            consoleHandler.setLevel(logging.INFO)
        elif options.verbose == 2:
            consoleHandler.setLevel(logging.DEBUG)

        if options.log != "":
            logging.debug("Creating log file '%s'" % options.log)
            fileHandler = logging.FileHandler(options.log, mode='w')
            fileHandler.setFormatter(logFormatter)
            fileHandler.setLevel(logging.DEBUG)
            rootLogger.addHandler(fileHandler)

        if options.generateBugReport:
            bugReportDir = "bugReport_%s_%s" % (getpass.getuser(), time.strftime("%d%m%Y_%H%M%S"))
            options.bugReportDir = bugReportDir
            makeSureDirExists(bugReportDir)
            fileHandlerBug = logging.FileHandler(os.path.join(bugReportDir, "log.txt"))
            fileHandlerBug.setFormatter(logFormatter)
            fileHandlerBug.setLevel(logging.DEBUG)
            rootLogger.addHandler(fileHandlerBug)
            logging.info("Creating debug report in location '%s'" % bugReportDir)
            logging.debug("Creating log file '%s'" % options.log)
            logging.debug("Run cmd '%s'" % " ".join(sys.argv))

        tmrg = TMR(options, args)

        if options.doc:
            startDocumentation()
            return

        tmrg.parse()
        if options.parse:
            return

        tmrg.elaborate()
        tmrg.showSummary()
        if options.elaborate:
            return

        tmrg.triplicate()

        if options.generateBugReport:
            options.bugReportDir = bugReportDir
            zipFile = options.bugReportDir+".zip"

            def zipdir(path, zipf):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        zipf.write(os.path.join(root, file))
            fileHandlerBug.close()
            zipf = zipfile.ZipFile(zipFile, 'w')
            zipdir(options.bugReportDir, zipf)
            zipf.close()
            consoleHandler.setLevel(logging.INFO)
            logging.info("Creating zip archive with bug report '%s'" % zipFile)
            try:
                shutil.rmtree(options.bugReportDir)
                os.rmdir(options.bugReportDir)
            except:
                pass
    except ErrorMessage as e:
        for line in str(e).split("\n"):
            logging.error(line)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.debug("The exception was raised from:")
        for l in traceback.format_tb(exc_traceback):
            for ll in l.split("\n"):
                logging.debug(ll)
        logging.debug(ll)
        rootLogger.handlers = []
        exit_code = 1

    rootLogger.handlers = []

    with open("trace.log", "w") as f:
        f.write(tracefunc.log)
        f.write("\n\n")

        s = dict(sorted(tracefunc.stats.items(), key= lambda item: item[1]))

        for k in s:
            f.write("%s : %s\n" % (datetime.timedelta(seconds=s[k]), k))

    sys.exit(exit_code)

import sys
import time
import datetime
def tracefunc(frame, event, arg, indent=[0]):
    try:
        elapsed = str(datetime.timedelta(seconds=(time.time() - tracefunc.starttime)))

        if event == "call":
            #indent[0] += 2
            #tracefunc.log += elapsed + " " + "-" * indent[0] + "> call function " + frame.f_code.co_name + "\n"

            if frame.f_code.co_name in tracefunc.last:
                return

            tracefunc.last[frame.f_code.co_name] = time.time()

        elif event == "return":
            #tracefunc.log += elapsed + " " + "<" + "-" * indent[0] + " exit function " + frame.f_code.co_name + "\n"
            #indent[0] -= 2

            if frame.f_code.co_name not in tracefunc.last:
                return

            if frame.f_code.co_name not in tracefunc.stats:
                tracefunc.stats[frame.f_code.co_name] = 0

            tracefunc.stats[frame.f_code.co_name] += int(time.time() - tracefunc.last[frame.f_code.co_name])
            del tracefunc.last[frame.f_code.co_name]

        return tracefunc
    except:
        pass

tracefunc.starttime = time.time()
tracefunc.log = ""
tracefunc.stats = {}
tracefunc.last = {}

#sys.setprofile(tracefunc)

if __name__ == "__main__":
    tracefunc.starttime = time.time()
    main()

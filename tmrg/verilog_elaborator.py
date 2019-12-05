#!/usr/bin/env python2

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

import logging
import traceback
import pprint
import os
import glob
import logging
import filecmp
import copy
import shutil
import zipfile
import mmap
import time
try:
    import ConfigParser as cp
except:
    import configparser as cp
from optparse import *
from .verilog_parser import *
from .verilog_formatter import VerilogFormatter


class ErrorMessage(BaseException):
    def __init__(self, s):
        BaseException.__init__(self, s)


def readFile(fname):
    if os.path.isfile(fname):
        f = open(fname, "r")
        body = f.read()
        f.close()
        return body
    else:
        logging.error("File '%s' does not exists" % fname)
        return ""


def resultLine(tokens, sep=""):
    s = ""
    if isinstance(tokens, ParseResults):
        for i in tokens:
            s += resultLine(i)+sep
    else:
        s += tokens
    return s


class VerilogElaborator():
    def __init__(self, options, args, cnfgName):
        self.options = options
        self.args = args
        self.vp = VerilogParser()
        self.statsLogs = []
        self.statsFilesParsed = 0
        self.vp.include = options.include
        self.vp.inc_dir = options.inc_dir

        self.vf = VerilogFormatter()
        self.logger = logging.getLogger('TMR')
        self.libFiles = []

        if self.options.verbose == 0:
            self.logger.setLevel(logging.WARNING)
        if self.options.verbose == 1:
            self.logger.setLevel(logging.INFO)
        elif self.options.verbose >= 2:
            self.logger.setLevel(logging.DEBUG)
        self.files = {}
        self.libs = {}
        self.__init_elaborate_callbacks()

        self.trace = True

        self.config = cp.ConfigParser()
        self.scriptDir = os.path.abspath(os.path.dirname(__file__))
        self.logger.debug("Script path : %s" % self.scriptDir)

        # master clonfig file
        masterCnfg = os.path.join(self.scriptDir, "../etc/%s.cfg" % cnfgName)
        if os.path.exists(masterCnfg):
            self.logger.debug("Loading master config file from %s" % masterCnfg)
            self.config.read(masterCnfg)
            if self.options.generateBugReport:
                fcopy = os.path.join(self.options.bugReportDir, "master.cfg")
                self.logger.debug("Coping master config file from '%s' to '%s'" % (masterCnfg, fcopy))
                shutil.copyfile(masterCnfg, fcopy)

        else:
            self.logger.warning("Master config file does not exists at '%s'" % masterCnfg)

        # user config file
        userCnfg = os.path.expanduser('~/.%s.cfg' % cnfgName)
        if os.path.exists(userCnfg):
            self.logger.debug("Loading user config file from %s" % userCnfg)
            self.config.read(userCnfg)
            if self.options.generateBugReport:
                fcopy = os.path.join(self.options.bugReportDir, "user.cfg")
                self.logger.debug("Coping user config file from '%s' to '%s'" % (userCnfg, fcopy))
                shutil.copyfile(userCnfg, fcopy)
        else:
            self.logger.info("User config file does not exists at '%s'" % userCnfg)
        self.translate = True
        self.linesTotal = 0

    def __init_elaborate_callbacks(self):
        # scan class looking for elaborator functions
        self.elaborator = {}
        for member in dir(self):
            if member.find("_elaborate_") == 0:
                token = member[len("_elaborate_"):].lower()
                self.elaborator[token] = getattr(self, member)
                self.logger.debug("Found elaborator for %s" % token)

    def getLeftRightHandSide(self, t, res=None):
        if res == None:
            res = {"left": set(), "right": set()}

        def _extractID(t, res=None):
            if res == None:
                res = set()
            if isinstance(t, ParseResults):
                name = str(t.getName()).lower()
                if name == "subscridentifier":
                    if not t[0] in self.current_module["nets"]:
                        if not t[0] in self.current_module["params"] and t[0][0] != '`':
                            pass
                        return res
                    if not "dnt" in self.current_module["nets"][t[0]]:
                        res.add(t[0])
                    _extractID(t[1], res=res)

                else:
                    for i in range(len(t)):
                        res = _extractID(t[i], res=res)
            return res

        if isinstance(t, ParseResults):
            name = str(t.getName()).lower()
            if len(t) == 0:
                return res
            if name in ("assgnmt", "nbassgnmt"):
                if t[0].getName() == "subscrIdentifier":
                    left_id = t[0][0]
                    res["left"].add(left_id)
                    res["right"].update(_extractID(t[0][1]))
                else:
                    logging.error("Unsupported syntax : concatenation on left hand side of the assignment (%s). " %
                                  str(self.vf.format(t)))
                    logging.error("Output may be incorrect.")
                res["right"].update(_extractID(t[2]))
            elif name in ("regdecl"):
                for tt in t[3]:
                    left_id = tt[0]
                    res["left"].add(left_id)
            elif name in ("netdecl1"):
                for tt in t[4]:
                    left_id = tt[0]
                    res["left"].add(left_id)
            elif name == "subscridentifier":
                if t[0] in self.current_module["nets"]:
                    res["right"].add(t[0])
                    res = self.getLeftRightHandSide(t[1], res=res)
                else:
                    pass
            else:
                for i in range(len(t)):
                    res = self.getLeftRightHandSide(t[i], res=res)

        return res

    def _elaborate_integerDecl(self, tokens):
        _atrs = ""
        _range = ""
        _len = "1"

        details = ""

        for reg in tokens[-1]:
            name = reg[0]
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {"atributes": _atrs, "range": _range, "len": _len,  "type": "int"}

    def _elaborate_regdecl(self, tokens):
        _atrs = self.vf.format(tokens[1])
        _range = self.vf.format(tokens[2])
        _len = self.__getLenStr(tokens[2])
        _from = self.__getFromStr(tokens[2])
        _to = self.__getToStr(tokens[2])

        if _len != "1":
            details = "(range:%s len:%s)" % (_range, _len)
        else:
            details = ""

        for reg in tokens[-1]:
            name = reg[0]
            _array_range = ""
            _array_len = ""
            _array_from = ""
            _array_to = ""
            if len(reg) > 1:
                arrayDec = reg[1]
                _array_range = self.vf.format(arrayDec)
                _array_len = self.__getArrayLenStr(arrayDec)
                _array_from = self.__getArrayFrom(arrayDec)
                _array_to = self.__getArrayTo(arrayDec)
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {"atributes": _atrs,
                                                     "range": _range,
                                                     "len": _len,
                                                     "from": _from,
                                                     "to": _to,
                                                     "type": "reg",
                                                     "array_range": _array_range,
                                                     "array_len": _array_len,
                                                     "array_from": _array_from,
                                                     "array_to": _array_to
                                                     }

    def _elaborate_moduleinstantiation(self, tokens):
        identifier = tokens[0]
        instance = tokens[2][0][0][0]
        _range = ""
        _len = "1"
        self.current_module["instances"][instance] = {"instance": identifier, "range": _range, "len": _len}

    def _elaborate_always(self, tokens):
        self._elaborate(tokens[1])

    def _elaborate_input(self, tokens):
        _dir = tokens[0]
        _atrs = self.vf.format(tokens[2])
        _range = self.vf.format(tokens[3])
        _len = self.__getLenStr(tokens[3])

        if _len != "1":
            details = "(range:%s len:%s)" % (_range, _len)
        else:
            details = ""

        for name in tokens[-1]:
            self.lastANSIPort = {}
            self.lastANSIPort["io"] = {"atributes": _atrs, "range": _range, "len": _len, "type": "input"}
            self.lastANSIPort["net"] = {"atributes": _atrs,
                                        "range": _range,
                                        "len": _len,
                                        "type": "wire",
                                        "array_len": "",
                                        "array_range": "",
                                        "array_from": "",
                                        "array_to": ""
                                        }

            if not name in self.current_module["nets"]:
                self.current_module["io"][name] = {"atributes": _atrs, "range": _range, "len": _len, "type": "input"}
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {"atributes": _atrs,
                                                     "range": _range,
                                                     "len": _len,
                                                     "type": "wire",
                                                     "array_len": "",
                                                     "array_range": "",
                                                     "array_from": "",
                                                     "array_to": ""
                                                     }  # TODO add better array support ?

    def _elaborate_inout(self, tokens):
        # ! TODO ! Fixme ! quick fix, copied from _elaborate_input without rethinkign all the problems it created!
        # tokens=tokens[0]
        _dir = tokens[0]
        _atrs = self.vf.format(tokens[2])
        _range = self.vf.format(tokens[3])
        _len = self.__getLenStr(tokens[3])
        if _len != "1":
            details = "(range:%s len:%s)" % (_range, _len)
        else:
            details = ""

        for name in tokens[-1]:
            self.lastANSIPort = {}
            self.lastANSIPort["io"] = {"atributes": _atrs, "range": _range, "len": _len, "type": "input"}
            self.lastANSIPort["net"] = {"atributes": _atrs,
                                        "range": _range,
                                        "len": _len,
                                        "type": "wire",
                                        "array_len": "",
                                        "array_range": "",
                                        "array_from": "",
                                        "array_to": ""}

            if not name in self.current_module["nets"]:
                self.current_module["io"][name] = {"atributes": _atrs, "range": _range, "len": _len, "type": "inout"}
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {"atributes": _atrs,
                                                     "range": _range,
                                                     "len": _len,
                                                     "type": "wire",
                                                     "array_len": "",
                                                     "array_range": "",
                                                     "array_from": "",
                                                     "array_to": ""}

    def _elaborate_inputhdr(self, tokens):
        if self.current_module["portMode"] == "non-ANSI":
            self.current_module["portMode"] = "ANSI"
            self.logger.info("Port mode : ANSI")
        self._elaborate_input(tokens)

    def _elaborate_inouthdr(self, tokens):
        if self.current_module["portMode"] == "non-ANSI":
            self.current_module["portMode"] = "ANSI"
            self.logger.info("Port mode : ANSI")

        self._elaborate_inout(tokens)

    def _elaborate_port(self, tokens):
        if self.current_module["portMode"] == "ANSI":
            name = tokens[0][0]
            if not name in self.current_module["nets"]:
                self.current_module["io"][name] = copy.deepcopy(self.lastANSIPort["io"])
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = copy.deepcopy(self.lastANSIPort["net"])

    def _elaborate_output(self, tokens):
        _dir = tokens[0]
        _atrs = self.vf.format(tokens[2])
        _range = self.vf.format(tokens[3])
        _len = self.__getLenStr(tokens[3])
        if _len != "1":
            details = "(range:%s len:%s)" % (_range, _len)
        else:
            details = ""

        for name in tokens[-1]:
            self.lastANSIPort = {}
            self.lastANSIPort["io"] = {"atributes": _atrs, "range": _range, "len": _len, "type": "output"}
            self.lastANSIPort["net"] = {"atributes": _atrs,
                                        "range": _range,
                                        "len": _len,
                                        "type": "wire",
                                        "array_len": "",
                                        "array_range": "",
                                        "array_from": "",
                                        "array_to": ""}

            if not name in self.current_module["nets"]:
                self.current_module["io"][name] = {"atributes": _atrs, "range": _range, "len": _len, "type": "output"}
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {"atributes": _atrs,
                                                     "range": _range,
                                                     "len": _len, "type": "wire",
                                                     "array_len": "",
                                                     "array_range": "",
                                                     "array_from": "",
                                                     "array_to": ""}
            # if not name in  self.current_module["nets"]:
            #    self.current_module["nets"][name]={"atributes":_atrs,"range":_range, "len":_len,"type":"wire"}

    def _elaborate_outputhdr(self, tokens):
        if self.current_module["portMode"] == "non-ANSI":
            self.current_module["portMode"] = "ANSI"
            self.logger.info("Port mode : ANSI")

        self._elaborate_output(tokens)

    def _elaborate_netdecl1(self, tokens):
        _atrs = self.vf.format(tokens[1])
        _range = self.vf.format(tokens[2])
        _len = self.__getLenStr(tokens[2])
        _from = self.__getFromStr(tokens[2])
        _to = self.__getToStr(tokens[2])
        type = tokens[0]
        for net in tokens[4]:
            name = net[0]
            _array_range = ""
            _array_len = ""
            _array_from = ""
            _array_to = ""
            if len(net) > 1:
                arrayDec = net[1]
                _array_range = self.vf.format(arrayDec)
                _array_len = self.__getArrayLenStr(arrayDec)
                _array_from = self.__getArrayFrom(arrayDec)
                _array_to = self.__getArrayTo(arrayDec)
            self.current_module["nets"][name] = {"atributes": _atrs,
                                                 "range": _range,
                                                 "len": _len,
                                                 "from": _from,
                                                 "to": _to,
                                                 "type": type,
                                                 "array_range": _array_range,
                                                 "array_len": _array_len,
                                                 "array_from": _array_from,
                                                 "array_to": _array_to}
            if _len != "1":
                details = "(range:%s len:%s)" % (_range, _len)
            else:
                details = ""

    def _elaborate_localparamdecl(self, tokens):
        _range = self.vf.format(tokens[1])
        _len = self.__getLenStr(tokens[1])
        _from = self.__getFromStr(tokens[1])
        _to = self.__getToStr(tokens[1])

        for param in tokens[2]:
            pname = param[0][0]
            pval = self.vf.format(param[0][1:])

            self.logger.debug("Parameter %s = %s" % (pname, pval))
            self.current_module["params"][pname] = {"value": pval, "range": _range, "len": _len, "type": "localparam"}

    def _elaborate_paramdecl(self, tokens):
        _range = self.vf.format(tokens[1])
        _len = self.__getLenStr(tokens[1])
        for param in tokens[2]:
            pname = param[0][0]
            pval = self.vf.format(param[0][1:])
            self.logger.debug("Parameter %s = %s" % (pname, pval))
            self.current_module["params"][pname] = {"value": pval, "range": _range, "len": _len, "type": "param"}

    def _elaborate_netdecl3(self, tokens):
        _atrs = self.vf.format(tokens[1])
        _range = self.vf.format(tokens[3])
        _len = self.__getLenStr(tokens[3])
        _from = self.__getFromStr(tokens[3])
        _to = self.__getToStr(tokens[3])

        for assgmng in tokens[5]:
            ids = self.getLeftRightHandSide(assgmng)
            name = assgmng[0][0]
            dnt = False
            if len(ids["right"]) != 0:
                idRight = ids["right"].pop()
                for ex in self.EXT:
                    if name == idRight+ex:
                        dnt = True
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {"atributes": _atrs,
                                                     "range": _range,
                                                     "len": _len,
                                                     "from": _from,
                                                     "to": _to,
                                                     'type': 'wire',
                                                     "array_range": "",
                                                     "array_len": "",
                                                     "array_from": "",
                                                     "array_to": ""
                                                     }
                if dnt:
                    self.current_module["nets"][name]["dnt"] = True
                    self.logger.debug("Net %s will not be touched!" % name)

    def _elaborate_directive_default(self, tokens):
        tmr = False
        if tokens[0].lower() == 'triplicate':
            tmr = True
        self.current_module["constraints"]["default"] = tmr

    def _elaborate_directive_do_not_triplicate(self, tokens):
        for net in tokens:
            self.current_module["constraints"][net] = False

    def _elaborate_directive_triplicate(self, tokens):
        for net in tokens:
            self.current_module["constraints"][net] = True

    def _elaborate_directive_do_not_touch(self, tokens):
        if len(tokens) == 1:
            self.current_module["constraints"]["dnt"] = True
        else:
            self.current_module["constraints"]["dntinst"] = tokens[1:]

    def _elaborate_directive_slicing(self, tokens):
        self.current_module["constraints"]["slicing"] = True

    def _elaborate_directive_translate(self, tokens):
        # this function is not really used now, this happens at the preprocesor stage
        if tokens[0].lower() == "off":
            self.translate = False
        elif tokens[0].lower() == "on":
            self.translate = True
        else:
            self.logger.error("Unknown parameter for tmrg translate directive '%s'" % tokens[0])

    def _elaborate_directive_tmr_error(self, tokens):
        en = False
        if tokens[0].lower() in ('true', 'enable'):
            en = True
        self.current_module["constraints"]["tmr_error"] = en

    def _elaborate_directive_tmr_error_exclude(self, tokens):
        if not "tmr_error_exclude" in self.current_module["constraints"]:
            self.current_module["constraints"]["tmr_error_exclude"] = []
        self.current_module["constraints"]["tmr_error_exclude"].append(tokens[0])

    def _elaborate_directive_seu_set(self, tokens):
        self.current_module["constraints"]["seu_set"] = tokens[0]

    def _elaborate_directive_seu_reset(self, tokens):
        self.current_module["constraints"]["seu_reset"] = tokens[0]

    def _elaborate_directive_majority_voter_cell(self, tokens):
        self.current_module["constraints"]["majority_voter_cell"] = tokens[0]

    def _elaborate_directive_fanout_cell(self, tokens):
        self.current_module["constraints"]["fanout_cell"] = tokens[0]

    def _elaborate(self, tokens):
        """ Elaborates tokens
        :param tokens: tokens to be parsed
        :return:
        """
        if isinstance(tokens, ParseResults):
            name = str(tokens.getName()).lower()
            if len(tokens) == 0:
                return
            self.logger.debug("[%-20s] len:%2d  str:'%s' >" % (name, len(tokens), str(tokens)[:80]))
            if name in self.elaborator:
                self.elaborator[name](tokens)
            else:
                self.logger.debug("No elaborator for %s" % name)
                if len(tokens):
                    for t in tokens:
                        self._elaborate(t)

    def exc(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.logger.error("")
        self.logger.error("TMR exception:")
        for l in traceback.format_exception(exc_type, exc_value,
                                            exc_traceback):
            for ll in l.split("\n"):
                self.logger.error(ll)
        self.logger.error(ll)

    def lineCount(self, fname):
        f = open(fname)
        lines = 0
        buf_size = 1024 * 1024
        read_f = f.read  # loop optimization

        buf = read_f(buf_size)
        while buf:
            lines += buf.count('\n')
            buf = read_f(buf_size)
        return lines

    def addFile(self, fname):
        if self.options.generateBugReport:
            bn = os.path.basename(fname)
            fcopy = os.path.join(self.options.bugReportDir, bn)
            self.logger.debug("Coping source file from '%s' to '%s'" % (fname, fcopy))
            shutil.copyfile(fname, fcopy)
        tokens = self.vp.parseFile(fname)
        if self.options.stats:
            lines = self.lineCount(fname)
            self.statsLogs.append("File '%s' has %d lines " % (fname, lines))
            self.statsFilesParsed += 1
            self.linesTotal += lines
        self.files[fname] = tokens

    def addLibFile(self, fname):
        if self.options.generateBugReport:
            bn = os.path.basename(fname)
            fcopy = os.path.join(self.options.bugReportDir, bn)
            self.logger.debug("Coping library file from '%s' to '%s'" % (fname, fcopy))
            shutil.copyfile(fname, fcopy)
        tokens = self.vp.parseFile(fname)
        if self.options.stats:
            lines = self.lineCount(fname)
            self.statsLogs.append("File '%s' has %d lines " % (fname, lines))
            self.linesTotal += lines
            self.statsFilesParsed += 1
        self.libs[fname] = tokens

    def __getLenStr(self, toks):
        rangeLen = "1"
        if len(toks) < 2:
            return rangeLen
        left = self.vf.format(toks[-2])
        right = self.vf.format(toks[-1])
        onlyInt = "abs((%s) - (%s))" % (left, right)
        try:
            onlyIntEval = eval(onlyInt)
            return "%d" % (onlyIntEval+1)
        except:
            pass
        rangeLen = "((%s) > (%s)) ? ((%s) - (%s) + 1) : ((%s) - (%s) + 1) " % (left, right, left, right, right, left)
        try:
            rangeInt = eval(rangeLen)
            rangeLen = "%d" % rangeInt
        except:
            pass
        return rangeLen

    def __getFromStr(self, toks):
        fromStr = ""
        if len(toks) < 2:
            return fromStr
        fromStr = "%s" % (self.vf.format(toks[-2]))
        try:
            fromInt = eval(fromStr)
            fromStr = "%d" % fromInt
        except:
            pass
        return fromStr

    def __getToStr(self, toks):
        toStr = ""
        if len(toks) < 2:
            return toStr
        toStr = "%s" % (self.vf.format(toks[-1]))
        try:
            toInt = eval(toStr)
            toStr = "%d" % toInt
        except:
            pass
        return toStr

    def __getArrayLenStr(self, toks):
        rangeLen = "%s - %s + 1" % (self.vf.format(toks[3]), self.vf.format(toks[1]))
        try:
            rangeInt = eval(rangeLen)
            rangeLen = "%d" % rangeInt
        except:
            pass
        return rangeLen

    def __getArrayFrom(self, toks):
        return "%s" % (self.vf.format(toks[3]))

    def __getArrayTo(self, toks):
        return "%s" % (self.vf.format(toks[1]))

    def moduleSummary(self, module):
        def printDict(d, dname=""):
            if len(d) == 0:
                return

            tab = PrettyTable([dname,  "tmr", "range", "atributes", "array"])
            tab.min_width[dname] = 50
            tab.min_width["range"] = 20
            tab.min_width["array"] = 20
            tab.min_width["atributes"] = 20
            tab.min_width["tmr"] = 10
            tab.align[dname] = "l"  # Left align city names

            for k in d:
                item = d[k]
                range = item["range"]
                if "array_range" in item:
                    array_range = item["array_range"]
                else:
                    array_range = ""
                if "atributes" in item:
                    atributes = item["atributes"]
                else:
                    atributes = "dupa"
                if "tmr" in item:
                    tmr = item["tmr"]
                else:
                    tmr = "-"
                if "dnt" in item:
                    tmr = "DNT"
                tab.add_row([k, tmr, range, atributes, array_range])
            tab.padding_width = 1  # One space between column edges and contents (default)
            for l in str(tab).split("\n"):
                self.logger.info(l)

        self.logger.info("")
        self.logger.info("Module:%s (dnt:%s)" % (module["name"], module["constraints"]["dnt"]))
        printDict(module["nets"],    "Nets")
        printDict(module["instances"], "Instantiations")
        if "params" in module:
            printDict(module["params"], "Params")

    def parse(self):
        """ Parse files
        :return:
        """
        def args2files(args):
            files = []
            for name in args:
                if len(name) == 0:
                    continue
                if os.path.isfile(name):
                    files.append(name)
                elif os.path.isdir(name):
                    for fname in glob.glob("%s/*.v" % name):
                        files.append(fname)
                else:
                    self.logger.error("File or directory does not exists '%s'" % name)

            return files
        parse_start_time = time.time()
        for fname in args2files(self.args):
            try:
                logging.info("Loading file '%s'" % fname)
                self.addFile(fname)
            except ParseException as err:
                logging.error("Error in file '%s' around line '%d'." % (fname, err.lineno))
                if err.line.find("tmrg ") == 0:
                    logging.error("")
                    logging.error("  Wrong tmrg directive")
                    logging.error("  //%s" % err.line[:-1])
                    logging.error("")
                else:
                    logging.error("")
                    logging.error(err.line)
                    logging.error(" "*(err.column-1) + "^")
                    logging.error(err)
                for l in traceback.format_exc().split("\n"):
                    logging.debug(l)
                raise ErrorMessage("Error during parsing")

        for fname in self.options.libs:
            self.libFiles.append(fname)

        for fname in self.libFiles:
            try:
                logging.info("Loading lib file '%s'" % fname)
                self.addLibFile(fname)
            except ParseException as err:
                logging.error("")
                logging.error(err.line)
                logging.error(" "*(err.column-1) + "^")
                logging.error(err)
                for l in traceback.format_exc().split("\n"):
                    logging.error(l)
                raise ErrorMessage("Error during parsing")
        if self.options.stats:
            parse_time = time.time()-parse_start_time
            print("-"*80)
            for line in self.statsLogs:
                print(line)
            print("-"*80)
            print("Total number of files parsed: %d " % self.statsFilesParsed)
            print("Total number of lines parsed: %d " % self.linesTotal)
            print("Total parse time: %.3f s " % parse_time)
            print("-"*80)

    def elaborate(self, allowMissingModules=False):
        """ Elaborate the design
        :return:
        """
        elaborate_start_time = time.time()

        self.modules = {}
        # elaborate all modules
        for fname in sorted(self.files):
            self.logger.info("")
            self.logger.info("Elaborating %s" % (fname))
            tokens = self.files[fname]
            for module in tokens:
                if module.getName() != "module":
                    continue

                moduleHdr = module[0]
                moduleName = moduleHdr[1]
                moduleParams = moduleHdr[2]
                modulePorts = moduleHdr[3]
                self.logger.debug("")
                self.logger.debug("= "*50)
                self.logger.info("Module %s (%s)" % (moduleName, fname))
                self.logger.debug("= "*50)
                self.current_module = {"instances": {}, "nets": {}, "name": moduleName, "io": {}, "constraints": {"dnt": False},
                                       "instantiated": 0, 'file': fname, "fanouts": {}, "voters": {}, "params": {}, "portMode": "non-ANSI",
                                       "tmrErrNets": {}}
                for param in moduleParams:
                    pname = param[1][0]
                    pval = self.vf.format(param[1][1])
                    self.logger.debug("Parameter %s = %s" % (pname, pval))
                    self.current_module["params"][pname] = {"value": pval, "range": "", "len": "", "type": "param"}

                for port in modulePorts:
                    self._elaborate(port)

                for moduleItem in module[1]:
                    self._elaborate(moduleItem)

                def pdict(d, i="", title=""):
                    for e in d:
                        if isinstance(d[e], dict):
                            pdict(d[e], i+"  ", title=e)
                        else:
                            pass

                self.modules[moduleName] = copy.deepcopy(self.current_module)

        for fname in sorted(self.libs):
            self.logger.info("")
            self.logger.info("Elaborating library %s" % (fname))
            tokens = self.libs[fname]
            for module in tokens:
                if module.getName() != "module":
                    continue
                moduleHdr = module[0]
                moduleName = moduleHdr[1]
                moduleParams = moduleHdr[2]
                modulePorts = moduleHdr[3]

                self.logger.debug("")
                self.logger.debug("= "*50)
                self.logger.info("Module %s (%s)" % (moduleName, fname))
                self.logger.debug("= "*50)
                self.current_module = {"instances": {}, "nets": {}, "name": moduleName, "io": {}, "constraints": {}, "instantiated": 0,
                                       'file': fname, "fanouts": {}, "voters": {}, "lib": fname, "portMode": "non-ANSI"}

                for param in moduleParams:
                    pname = param[0]
                    pval = self.vf.format(param[1])
                    self.logger.debug("Parameter %s = %s" % (pname, pval))
                    self.current_module["params"][pname] = {"value": pval, "range": "", "len": "", "type": "param"}

                for port in modulePorts:
                    self._elaborate(port)

                for moduleItem in module[1]:
                    self._elaborate(moduleItem)
                self.current_module["constraints"]["dnt"] = True
                self.modules[moduleName] = copy.deepcopy(self.current_module)

        # display summary
        if len(self.modules) > 1:
            self.logger.info("")
            self.logger.info("Modules found %d" % len(self.modules))
            libDetails = {}
            for module in sorted(self.modules):
                if "lib" not in self.modules[module]:
                    self.logger.info(" - %s (%s)" % (module, self.modules[module]["file"]))
                else:
                    lib = self.modules[module]["lib"]
                    if not lib in libDetails:
                        libDetails[lib] = []
                    libDetails[lib].append(module)
            for lib in libDetails:
                s = "Lib %s : " % lib
                infoed = 0
                for m in libDetails[lib]:
                    s += m+" "
                    if len(s) > 100:
                        if infoed < 5:
                            self.logger.info(s)
                        else:
                            self.logger.debug(s)
                        s = ""
                        infoed += 1
                if infoed < 5:
                    self.logger.info(s)
                else:
                    self.logger.debug(s)

        # check if all modules are known
        self.logger.info("")
        self.logger.info("Checking the design hierarchy")
        elaborationError = False
        for module in self.modules:
            for instName in self.modules[module]["instances"]:
                instance = self.modules[module]["instances"][instName]["instance"]
                if instance in self.modules:
                    self.modules[instance]["instantiated"] += 1
                else:
                    if "dnt" in self.modules[module]["constraints"] and self.modules[module]["constraints"]["dnt"]:
                        self.logger.warning("Unknown module instantiation! In module '%s', instance name '%s' instance type '%s'." % (
                            module, instName, instance))
                    else:
                        self.logger.error("Unknown module instantiation! In module '%s', instance name '%s' instance type '%s'." % (
                            module, instName, instance))
                        elaborationError = True

        tops = 0
        self.topFile = ""
        self.topModule = ""
        if len(self.modules) == 0:
            raise ErrorMessage(
                "No modules found. Please refer to the documentation using 'tmrg --help' or 'tmrg --doc'")

        for module in self.modules:
            if "lib" in self.modules[module]:
                continue
            if self.modules[module]["instantiated"] == 0:
                self._printHierary(module)
                self.topModule = module
                self.topFile = self.modules[module]["file"]
                tops += 1

        top_module = self.config.get("global", "top_module")
        if self.options.top_module:
            top_module = self.options.top_module
        if top_module:
            if not top_module in self.modules:
                self.logger.error("Specified top module (%s) not found.", self.options.top_module)
                elaborationError = True
            else:
                self.topModule = top_module
                self.logger.info("Top module found (%s)!", self.topModule)
        elif tops != 1:
            self.logger.warning("The design has multiple top cells! Output may not be correct!")

        if not allowMissingModules and elaborationError:
            raise ErrorMessage("Serious error during elaboration.")

        if self.options.stats:
            elaborate_time = time.time()-elaborate_start_time
            print("Elaboration time : %.3f s " % elaborate_time)
            print("-"*80)

    def _printHierary(self, topModule):
        def _printH(module, i=""):
            i += "  |"
            for instName in self.modules[module]["instances"]:
                inst = self.modules[module]["instances"][instName]["instance"]
                if inst in self.modules:
                    self.logger.info(i+"- "+instName+":"+inst)
                    _printH(inst, i)
                else:
                    self.logger.info(i+"- [!] "+instName+":"+inst)

        self.logger.info("[%s]" % topModule)
        _printH(topModule)

    def showSummary(self):
        for module in sorted(self.modules):
            self.moduleSummary(self.modules[module])

    def getAllInsttances(self, module, prefix=""):
        res = []
        # we want store instances from the bottom of the hierarhy
        if len(self.modules[module]["instances"]) == 0:
            res.append((prefix, module))
        else:
            # in other case we loop over hierarchy
            for instId in self.modules[module]["instances"]:
                inst = self.modules[module]["instances"][instId]['instance']
                if "[" in instId:
                    instId = "\\"+instId+" "
                if inst in self.modules:
                    res += self.getAllInsttances(inst, prefix=prefix+"/"+instId)
        return res

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
from .prettytable import PrettyTable

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
        self.libFiles = []

        self.files = {}
        self.libs = {}
        self.__init_elaborate_callbacks()

        self.trace = True

        self.structs = {}

        self.config = cp.ConfigParser()
        self.scriptDir = os.path.abspath(os.path.dirname(__file__))
        logging.debug("Script path : %s" % self.scriptDir)

        # master clonfig file
        masterCnfg = os.path.join(self.scriptDir, "../etc/%s.cfg" % cnfgName)
        if os.path.exists(masterCnfg):
            logging.debug("Loading master config file from %s" % masterCnfg)
            self.config.read(masterCnfg)
            if self.options.generateBugReport:
                fcopy = os.path.join(self.options.bugReportDir, "master.cfg")
                logging.debug("Coping master config file from '%s' to '%s'" % (masterCnfg, fcopy))
                shutil.copyfile(masterCnfg, fcopy)

        else:
            logging.warning("Master config file does not exists at '%s'" % masterCnfg)

        # user config file
        userCnfg = os.path.expanduser('~/.%s.cfg' % cnfgName)
        if os.path.exists(userCnfg):
            logging.debug("Loading user config file from %s" % userCnfg)
            self.config.read(userCnfg)
            if self.options.generateBugReport:
                fcopy = os.path.join(self.options.bugReportDir, "user.cfg")
                logging.debug("Coping user config file from '%s' to '%s'" % (userCnfg, fcopy))
                shutil.copyfile(userCnfg, fcopy)
        else:
            logging.info("User config file does not exists at '%s'" % userCnfg)
        self.translate = True
        self.linesTotal = 0

    def __init_elaborate_callbacks(self):
        # scan class looking for elaborator functions
        self.elaborator = {}
        for member in dir(self):
            if member.find("_elaborate_") == 0:
                token = member[len("_elaborate_"):].lower()
                self.elaborator[token] = getattr(self, member)
                logging.debug("Found elaborator for %s" % token)

    def getLeftRightHandSide(self, t, res=None):
        def _extractID(t, res=None):
            if res == None:
                res = set()
            if isinstance(t, ParseResults):
                if t.getName() == "reg_reference":
                    netname, netfield = self.split_name(t.get("name")[0])

                    if not netname in self.current_module["nets"]:
                        if not t[0] in self.current_module["params"] and netname[0] != '`':
                            logging.warning("%s is neither a parameter nor a net. Leaving it as it is" % t[0])
                        return res

                    if not "dnt" in self.current_module["nets"][netname]:
                        res.add(netname)
                    _extractID(t[1], res=res)

                else:
                    for i in range(len(t)):
                        res = _extractID(t[i], res=res)
            return res

        # Initialize if needed
        if res == None:
            res = {"left": set(), "right": set()}

        # Return empty results if not a ParseResults instance
        if not isinstance(t, ParseResults):
            return res

        # Return empty results if there are no tokens
        if len(t) == 0:
            return res

        name = str(t.getName()).lower()

        # Assignments
        if name in ("assignment", "nbassignment"):
            print("Looking inside assignment/nb")
            print(t.asDict())
            lvalue = t.get("lvalue")[0]
            if lvalue.getName() == "reg_reference":
                print(lvalue.asDict())
                res["left"].add(lvalue.get("name")[0])
                res["right"].update(_extractID(t.get("expr@rvalue")))
            else:
                logging.error("Unsupported syntax : %s on left hand side of the assignment (%s). " % (lvalue.getName(), str(self.vf.format(t))))
                logging.error("Output may be incorrect.")

        # Register declaration with assignment
        elif name in ("netdecl"):
            for tt in t.get("identifiers"):
                res["left"].add(tt.get("name")[0])

        # Net declaration
        elif name in ("netdecl1"):
            for tt in t[4]:
                res["left"].add(tt[0])

        # Register reference
        elif name == "reg_reference":
            if t.get("name")[0] in self.current_module["nets"]:
                res["right"].add(t.get("name")[0])
                res = self.getLeftRightHandSide(t.get("range_or_field"), res=res)
            else:
                pass

        # All else
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
                self.current_module["nets"][name] = {"attributes": _atrs, "packed_ranges": [], "unpacked_ranges": [],  "type": "int", "is_custom_type" : False}
                logging.debug("integerDecl: Adding net: %s" % self.current_module["nets"][name])

    def __structdecl(self, tokens):
        fields = tokens.get("fields")

        res = {}

        res["fields"] = {}
        total_size = []
        for field in fields:
            packed_ranges = self.__elaborate_packed(field.get("packed_ranges"))
            size = " + ".join([i["len"] for i in packed_ranges])
            size = "(" + size + ")" if size else "1"

            for reg in field.get("identifiers"):
                res["fields"][reg.get("name")[0]] = {
                    "atrs": "",
                    "type": field[0],
                    "packed_ranges" : packed_ranges,
                    "unpacked_ranges" : self.__elaborate_unpacked(reg.get("unpacked_ranges")),
                    "size" : size
                }
                total_size.append(size)

        res["total_size"] = "(" + " + ".join(total_size) + ")"
        return res

    def _elaborate_structdecl(self, tokens):
        self.current_module["structs"][tokens.get("name")] = self.__structdecl(tokens)

    def backup_elaborate_regdecl(self, tokens):
        _atrs = self.vf.format(tokens[1])
        
        packed_ranges = self.__elaborate_packed(tokens.get("packed_ranges"))

        for reg in tokens.get("identifiers"):
            name = reg.get("name")[0]

            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {
                    "attributes": _atrs,
                    "type": "wire",
                    "packed_ranges" : packed_ranges,
                    "unpacked_ranges": self.__elaborate_unpacked(reg.get("unpacked_ranges"))
                }
                logging.debug("regdecl: Adding net: %s" % self.current_module["nets"][name])

    def backup_elaborate_customdecl(self, tokens):
        if tokens[0] not in self.current_module["structs"]:
            raise ValueError("Error while elaborating %s: %s is not a defined struct" % (tokens[1], tokens[0]))

        _atrs = ""
        _type = tokens.get("custom_type")[0]
        _len = self.current_module["structs"][_type]["total_size"]
        _range = "["+_len+" -1 :0]"

        for name in tokens.get("identifiers"):
            name = name[0]
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {
                    "attributes": _atrs,
                    "type": str(_type),
                    "packed_ranges" : [{
                        "range" : _range,
                        "len"   : _len,
                        "from"  : "(" + _len + "-1)",
                        "to"    : 0
                    }],
                    "unpacked_ranges" : []
                }
                logging.debug("customdecl: Adding net: %s" % self.current_module["nets"][name])

    def _elaborate_netdecl(self, tokens):
        _atrs = None
        _type = None
        packed_ranges = []

        custom = False
        if "standard" in tokens:
            _atrs = tokens.get("standard").get("attrs") if "attrs" in tokens else ""
            _type = tokens.get("standard").get("kind")[0]
            packed_ranges = self.__elaborate_packed(tokens.get("packed_ranges"))
        else:
            _atrs = ""
            _type = tokens.get("custom")[0]
            _len = self.current_module["structs"][_type]["total_size"]
            packed_ranges = [{
                "range" : "["+_len+" -1 :0]",
                "len"   : _len,
                "from"  : "(" + _len + "-1)",
                "to"    : 0
            }] + self.__elaborate_packed(tokens.get("packed_ranges"))
            custom = True

        for identifier in tokens.get("identifiers"):
            name = identifier.get("name")[0]
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {
                    "attributes": _atrs,
                    "type": str(_type),
                    "packed_ranges" : packed_ranges,
                    "unpacked_ranges" : self.__elaborate_unpacked(identifier.get("unpacked_ranges")),
                    "is_custom_type" : custom
                }
                logging.debug("netdecl: Adding net %s: %s" % (name, self.current_module["nets"][name]))

    def _elaborate_moduleinstantiation(self, tokens):
        identifier = tokens.get("moduleName")[0]
        instances = [i[0][0] for i in tokens.get("moduleInstances")]
        _range = ""
        _len = "1"

        for inst in instances:
            self.current_module["instances"][inst] = {"instance": identifier, "range": _range, "len": _len}

    def _elaborate_reg_reference(self, tokens):
        print("ELABORATING " + "%s" % tokens)
        # Check for errors
        netname = tokens.get("name")[0]
        if netname not in self.current_module["nets"]:
            return

        field_parsed = False
        for field in tokens.get("range_or_field"):
            # We're only checking that fields exist here
            if field.getName() != "field":
                continue

            if field_parsed:
                raise ValueError("Nested fields are not supported yet.")

            field_parsed = True

            if self.current_module["nets"][netname]["type"] not in self.current_module["structs"]:
                raise ValueError("Trying to access field %s of %s, which is not a struct" % (netfield, netname))

            fields = self.current_module["structs"][self.current_module["nets"][netname]["type"]]["fields"]

            if field not in fields:
                raise ValueError("Field %s is not a field of struct %s. Available fields are: %s" % (netfield, netname, fields))


    def _elaborate_always(self, tokens):
        for t in tokens[1:]:
            self._elaborate(t)

    def __elaborate_packed(self, tokens):
        packed_ranges = []

        if not tokens:
            return []

        for r in tokens:
            _dir  = r.get("dir")[0] ;# First character out of ": -: +:" is ": - +"
            _from = self.vf.format(r.get("expr@from"))
            _to   = self.vf.format(r.get("expr@to"))

            if _dir != ":":
                _len = "(%s + 1)" % (_to)
                _range = "[ %s %s %s ]" % (_from, _dir, _to)
            else:
                _len = "($abs(%s-%s) + 1)" % (_from, _to)
                _range = "[ %s : %s ]" % (_from, _to)

            packed_ranges.append({
                "range" : _range,
                "len"   : _len,
                "from"  : _from,
                "to"    : _to
            })

        return packed_ranges

    def __elaborate_unpacked(self, tokens):
        unpacked_ranges = []

        if not tokens:
            return []

        for r in tokens:
            # this part decodes declarations using size: name [M]
            if r.getName() == "size":
                _array_len = self.vf.format(r[0])
                _array_from = 0
                _array_to = "%s -1" % (_array_len)
                _array_range = "[%s : %s]" % (_array_from, _array_to)

                unpacked_ranges.append({
                    "range" : _array_range,
                    "len"   : _array_len,
                    "from"  : _array_from,
                    "to"    : _array_to
                })

            # this part decodes declarations using range: name [N:M]
            elif r.getName() == "range":
                print("range:" + "%s" % r.asDict())
                _dir  = r.get("dir")[0] ;# First character out of ": -: +:" is ": - +"
                _from = self.vf.format(r.get("expr@from"))
                _to   = self.vf.format(r.get("expr@to"))

                if _dir != ":":
                    _len = "(%s + 1)" % (_to)
                    _range = "[ %s %s %s ]" % (_from, _dir, _to)
                else:
                    _len = "($abs(%s-%s) + 1)" % (_from, _to)
                    _range = "[ %s : %s ]" % (_from, _to)

                unpacked_ranges.append({
                    "range" : _range,
                    "len"   : _len,
                    "from"  : _from,
                    "to"    : _to
                })
            else:
                raise TypeError("Unsupported unpacked range type: %s" % r.getName())

        return unpacked_ranges

    def _get_port_type(self, tokens):
        _type = "wire"
        custom = False

        if "custom" in tokens.keys():
            _type = tokens.get("custom").get("custom_type")[0]
            custom = True
        elif "standard" in tokens.keys():
            _s = tokens.get("standard")
            _type = _s.get("kind")[0] if "kind" in _s else "wire"

        return custom, _type

    def __elaborate_generic_port(self, tokens):
        _atrs = ""
        if "standard" in tokens.keys():
            standard = tokens.get("standard")
            _atrs  = self.vf.format(standard.get("attrs")) if "attrs" in standard.keys() else ""
        else:
            _atrs = ""

        packed_ranges = self.__elaborate_packed(tokens.get("packed_ranges")) if "packed_ranges" in tokens.keys() else []
        details = ""

        for identifier in tokens.get("identifiers"):
            name = identifier.get("name")[0]
            is_custom, type = self._get_port_type(tokens)
            self.lastANSIPort = {
                "io" : {
                    "attributes": _atrs,
                    "packed_ranges" : packed_ranges,
                    "unpacked_ranges" : self.__elaborate_unpacked(identifier.get("unpacked_ranges")),
                    "type": tokens.get("dir")
                },
                "net" : {
                    "attributes": _atrs,
                    "type": type,
                    "is_custom_type": is_custom,
                    "packed_ranges" : packed_ranges,
                    "unpacked_ranges" : self.__elaborate_unpacked(identifier.get("unpacked_ranges"))
                }
            }

            if not name in self.current_module["io"]:
                self.current_module["io"][name] = self.lastANSIPort["io"]

            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = self.lastANSIPort["net"]
                logging.debug("generic_port: Adding net %s: %s" % (name, self.current_module["nets"][name]))


    def _elaborate_porthdr(self, tokens):
        if self.current_module["portMode"] == "non-ANSI":
            self.current_module["portMode"] = "ANSI"
            logging.info("Port mode : ANSI")

        self.__elaborate_generic_port(tokens)

    def _elaborate_portbody(self, tokens):
        self.__elaborate_generic_port(tokens)

    def _elaborate_port(self, tokens):
        if self.current_module["portMode"] == "ANSI":
            name = tokens[0][0]
            if not name in self.current_module["nets"]:
                self.current_module["io"][name] = copy.deepcopy(self.lastANSIPort["io"])
            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = copy.deepcopy(self.lastANSIPort["net"])
                logging.debug("port: Adding net: %s" % self.current_module["nets"][name])

    def _elaborate_netdecl1(self, tokens):
        _atrs = self.vf.format(tokens.get("attributes"))
        packed = self.__elaborate_packed(tokens.get("packed_ranges"))
        type = tokens.get("kind")[0]
        for net in tokens.get("identifiers"):
            name = net.get("name")[0]
            self.current_module["nets"][name] = {
                "attributes": _atrs,
                "type": "wire",
                "packed_ranges": packed,
                "unpacked_ranges": self.__elaborate_unpacked(net.get("unpacked_ranges"))
            }
            logging.debug("netdecl1: Adding net: %s" % self.current_module["nets"][name])
            if _len != "1":
                details = "(range:%s len:%s)" % (_range, _len)
            else:
                details = ""

    def _elaborate_assignment_with_declaration(self, tokens):
        type = tokens.get("type") if "type" in tokens.keys() else "wire"
        if type != "genvar":
            name = self.vf.format(tokens.get("name")[0])
            self.current_module["nets"][name] = {
                "attributes": "",
                "type": type,
                "packed_ranges": [],
                "unpacked_ranges": []
            }
            logging.debug("assignment_with_declaration: Adding net: %s" % self.current_module["nets"][name])

    def _elaborate_localparamdecl(self, tokens):
        _range = self.vf.format(tokens[1])
        _len = self.__getLenStr(tokens[1])
        _from = self.__getFromStr(tokens[1])
        _to = self.__getToStr(tokens[1])
        for param in tokens[4]:
            pname = param[0][0]
            pval = self.vf.format(param[0][1:])
            logging.debug("Parameter %s = %s" % (pname, pval))
            self.current_module["params"][pname] = {"value": pval, "range": _range, "len": _len, "type": "localparam"}

    def _elaborate_paramdecl(self, tokens):
        _range = self.vf.format(tokens[1])
        _len = self.__getLenStr(tokens[1])
        for param in tokens[4]:
            pname = param[0][0]
            pval = self.vf.format(param[0][1:])
            logging.debug("Parameter %s = %s" % (pname, pval))
            self.current_module["params"][pname] = {"value": pval, "range": _range, "len": _len, "type": "param"}

    def _elaborate_netdecl3(self, tokens):
        _atrs = self.vf.format(tokens.get("attributes"))
        _type = tokens.get("kind")[0]
        packed = self.__elaborate_packed(tokens.get("packed_ranges"))

        for assignment in tokens.get("assignments"):
            ids = self.getLeftRightHandSide(assignment)
            name = self.vf.format(assignment.get("lvalue")[0])
            dnt = False
            if len(ids["right"]) != 0:
                idRight = ids["right"].pop()
                for ex in self.EXT:
                    if name == idRight+ex:
                        dnt = True

            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {
                    "attributes": _atrs,
                    "type": _type,
                    "packed_ranges" : packed,
                    "unpacked_ranges" : []
                }
                logging.debug("netdecl3: Adding net: %s" % self.current_module["nets"][name])

                if dnt:
                    self.current_module["nets"][name]["dnt"] = True
                    logging.debug("Net %s will not be touched!" % name)

    def _elaborate_customDeclwAssign(self, tokens):
        if tokens[0] not in self.current_module["structs"]:
            raise ValueError("Error while elaborating %s: %s is not a defined struct" % (tokens[1], tokens[0]))

        _atrs = ""
        _len = self.current_module["structs"][tokens[0]]["total_size"]
        _range = "["+_len+" -1 :0]"

        for assignment in tokens.get("assignments"):
            ids = self.getLeftRightHandSide(assignment)
            name = self.vf.format(assignment.get("lvalue")[0])
            dnt = False
            if len(ids["right"]) != 0:
                idRight = ids["right"].pop()
                for ex in self.EXT:
                    if name == idRight+ex:
                        dnt = True

            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {
                        "attributes": _atrs,
                        "packed_ranges" : [{
                            "range": _range,
                            "len": _len,
                            "from": "(" + _len + "-1)",
                            "to": "0"
                        }],
                        "type": str(tokens[0]),
                        "unpacked_ranges" : []
                    }

            if dnt:
                self.current_module["nets"][name]["dnt"] = True
                logging.debug("Net %s will not be touched!" % name)

    def _elaborate_netDeclWAssign(self, tokens):
        _atrs = None
        _type = None
        packed_ranges = []

        custom = False
        if "standard" in tokens:
            _atrs = tokens.get("standard").get("attrs") if "attrs" in tokens else ""
            _type = tokens.get("standard").get("kind")[0]
            packed_ranges = self.__elaborate_packed(tokens.get("packed_ranges"))
        else:
            _atrs = ""
            _type = tokens.get("custom")[0]
            _len = self.current_module["structs"][_type]["total_size"]
            packed_ranges = [{
                "range" : "["+_len+" -1 :0]",
                "len"   : _len,
                "from"  : "(" + _len + "-1)",
                "to"    : 0
            }] + self.__elaborate_unpacked(tokens.get("packed_ranges"))
            custom = True

        for assignment in tokens.get("assignments"):
            ids = self.getLeftRightHandSide(assignment)
            name = self.vf.format(assignment.get("lvalue")[0])
            unpacked = []
            if assignment.get("lvalue")[0].getName() == "reg_reference":
                range_or_field = assignment.get("lvalue")[0].get("range_or_field")
                if range_or_field:
                    logging.warning("Unpacked net declaration with assignment is not supported. TMR may malfunction.")

            dnt = False
            if len(ids["right"]) != 0:
                idRight = ids["right"].pop()
                for ex in self.EXT:
                    if name == idRight+ex:
                        dnt = True

            if not name in self.current_module["nets"]:
                self.current_module["nets"][name] = {
                        "attributes": _atrs,
                        "packed_ranges" : packed_ranges,
                        "type": _type,
                        "unpacked_ranges" : unpacked,
                        "is_custom_type" : custom
                    }

            if dnt:
                self.current_module["nets"][name]["dnt"] = True
                logging.debug("Net %s will not be touched!" % name)

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
            logging.error("Unknown parameter for tmrg translate directive '%s'" % tokens[0])

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
            if len(tokens) == 0:
                return

            name = str(tokens.getName()).lower()
            offset = name.find("@")
            if offset != -1:
                name = name[0:offset]

            logging.debug("[%-20s] len:%2d  str:'%s' >" % (name, len(tokens), str(tokens)[:80]))
            if name in self.elaborator:
                self.elaborator[name](tokens)
            else:
                logging.debug("No elaborator for %s" % name)
                if len(tokens):
                    for t in tokens:
                        self._elaborate(t)

    def exc(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("")
        logging.error("TMR exception:")
        for l in traceback.format_exception(exc_type, exc_value,
                                            exc_traceback):
            for ll in l.split("\n"):
                logging.error(ll)
        logging.error(ll)

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
            logging.debug("Copying source file from '%s' to '%s'" % (fname, fcopy))
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
            logging.debug("Copying library file from '%s' to '%s'" % (fname, fcopy))
            shutil.copyfile(fname, fcopy)
        tokens = self.vp.parseFile(fname)
        if self.options.stats:
            lines = self.lineCount(fname)
            self.statsLogs.append("File '%s' has %d lines " % (fname, lines))
            self.linesTotal += lines
            self.statsFilesParsed += 1
        self.libs[fname] = tokens

    def __getLenStr(self, toks):
        if not toks or len(toks) < 2:
            return "1"

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

            tab = PrettyTable([dname,  "type", "attributes", "packed range", "unpacked_range", "tmr"])
            tab.min_width[dname] = 30
            tab.min_width["type"] = 10
            tab.min_width["packed range"] = 20
            tab.min_width["unpacked range"] = 20
            tab.min_width["attributes"] = 10
            tab.min_width["tmr"] = 10
            tab.align[dname] = "l"  # Left align city names

            for k in d:
                item = d[k]

                packed_ranges = " ".join([i["range"] for i in item["packed_ranges"]]) if "packed_ranges" in item else ""
                unpacked_ranges = " ".join([i["range"] for i in item["unpacked_ranges"]]) if "unpacked_ranges" in item else ""
                type = item["type"] if "type" in item else ""

                if "attributes" in item:
                    attributes = item["attributes"]
                else:
                    attributes = ""

                if "tmr" in item:
                    tmr = item["tmr"]
                else:
                    tmr = "-"

                if "dnt" in item:
                    tmr = "DNT"

                tab.add_row([k, type, attributes, packed_ranges, unpacked_ranges, tmr])
            tab.padding_width = 1  # One space between column edges and contents (default)
            for l in str(tab).split("\n"):
                logging.info(l)

        logging.info("")
        logging.info("Module:%s (dnt:%s)" % (module["name"], module["constraints"]["dnt"]))
        logging.info("Constraints:")
        for k in module["constraints"]:
            logging.info("    %s: %s" % (k, module["constraints"][k]))
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
                    logging.error("File or directory does not exists '%s'" % name)

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
                logging.error("Error in file '%s' around line '%d'." % (fname, err.lineno))
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
            logging.info("")
            logging.info("Elaborating %s" % (fname))
            tokens = self.files[fname]
            for item in tokens:
                if item.getName() == "structDecl":
                    name = item.get("id")[0]
                    self.structs[name] = self.__structdecl(item)

                if item.getName() == "module":
                    moduleHdr = item[0]
                    moduleName = moduleHdr[1]
                    moduleParams = moduleHdr[2]
                    modulePorts = moduleHdr[3]
                    logging.debug("")
                    logging.debug("= "*50)
                    logging.info("Module %s (%s)" % (moduleName, fname))
                    logging.debug("= "*50)
                    self.current_module = {"instances": {}, "nets": {}, "name": moduleName, "io": {}, "constraints": {"dnt": False},
                                           "instantiated": 0, "file": fname, "fanouts": {}, "voters": {}, "params": {}, "portMode": "non-ANSI",
                                           "tmrErrNets": {}, "structs" : self.structs}
                    for param in moduleParams:
                        pname = param[1][0]
                        pval = self.vf.format(param[1][1])
                        logging.debug("Parameter %s = %s" % (pname, pval))
                        self.current_module["params"][pname] = {"value": pval, "range": "", "len": "", "type": "param"}

                    for port in modulePorts:
                        self._elaborate(port)

                    for moduleItem in item[1]:
                        self._elaborate(moduleItem)

                    def pdict(d, i="", title=""):
                        for e in d:
                            if isinstance(d[e], dict):
                                pdict(d[e], i+"  ", title=e)
                            else:
                                pass

                    self.modules[moduleName] = copy.deepcopy(self.current_module)

        for fname in sorted(self.libs):
            logging.info("")
            logging.info("Elaborating library %s" % (fname))
            tokens = self.libs[fname]
            for module in tokens:
                if module.getName() != "module":
                    continue
                moduleHdr = module[0]
                moduleName = moduleHdr[1]
                moduleParams = moduleHdr[2]
                modulePorts = moduleHdr[3]
                auto_inferred = False

                if moduleName.endswith("TMR"):
                    logging.info("Module %s has been already triplicated (%s)" % (moduleName, fname))
                    moduleName = moduleName[:-len("TMR")]
                    logging.info("Infering non triplicated version: %s" % moduleName)
                    auto_inferred = True

                logging.debug("")
                logging.debug("= "*50)
                logging.info("Module %s (%s)" % (moduleName, fname))
                logging.debug("= "*50)
                self.current_module = {"instances": {}, "nets": {}, "name": moduleName, "io": {}, "constraints": {}, "instantiated": 0, "file": fname, "fanouts": {}, "voters": {}, "lib": fname, "portMode": "non-ANSI", "params": {}, "structs" : self.structs}

                for param in moduleParams:
                    pname = param[0]
                    pval = self.vf.format(param[1])
                    logging.debug("Parameter %s = %s" % (pname, pval))
                    self.current_module["params"][pname] = {"value": pval, "range": "", "len": "", "type": "param"}

                for port in modulePorts:
                    self._elaborate(port)

                for moduleItem in module[1]:
                    self._elaborate(moduleItem)

                if auto_inferred:
                    for io in list(self.current_module["io"]):
                        # look for all pins ending with A,B,C and replace with a single pin
                        # and set proper constraints
                        if io.endswith("A"):
                            port = io[:-1]
                            bport = io[:-1] + "B"
                            cport = io[:-1] + "C"
                            if bport in self.current_module["io"] and cport in self.current_module["io"]:
                                logging.info("Port %s is triplicated" % (port))
                                # create new port and net
                                self.current_module["io"][port] = self.current_module["io"][io]
                                self.current_module["nets"][port] = self.current_module["nets"][io]

                                # remove triplicated ports and nets
                                del self.current_module["io"][bport]
                                del self.current_module["nets"][bport]

                                del self.current_module["io"][cport]
                                del self.current_module["nets"][cport]

                                del self.current_module["io"][io] # A
                                del self.current_module["nets"][io]

                                # add constraints
                                self.current_module["constraints"][port] = True

                if "tmrError" in self.current_module["io"]:
                    self.current_module["constraints"]["tmr_error"] = True
                    del self.current_module["io"]["tmrError"]

                self.current_module["constraints"]["dnt"] = True
                if auto_inferred:
                    self.current_module["constraints"]["dnt"] = False
                    self.current_module["constraints"]["default"] = False

                self.modules[moduleName] = copy.deepcopy(self.current_module)

        # display summary
        if len(self.modules) > 1:
            logging.info("")
            logging.info("Modules found %d" % len(self.modules))
            libDetails = {}
            for module in sorted(self.modules):
                if "lib" not in self.modules[module]:
                    logging.info(" - %s (%s)" % (module, self.modules[module]["file"]))
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
                            logging.info(s)
                        else:
                            logging.debug(s)
                        s = ""
                        infoed += 1
                if infoed < 5:
                    logging.info(s)
                else:
                    logging.debug(s)

        # check if all modules are known
        logging.info("")
        logging.info("Checking the design hierarchy")
        elaborationError = False
        for module in self.modules:
            for instName in self.modules[module]["instances"]:
                instance = self.modules[module]["instances"][instName]["instance"]
                if instance in self.modules:
                    self.modules[instance]["instantiated"] += 1
                else:
                    if "dnt" in self.modules[module]["constraints"] and self.modules[module]["constraints"]["dnt"]:
                        logging.warning("Unknown module instantiation! In module '%s', instance name '%s' instance type '%s'." % (
                            module, instName, instance))
                    else:
                        logging.error("Unknown module instantiation! In module '%s', instance name '%s' instance type '%s'." % (
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
                logging.error("Specified top module (%s) not found.", self.options.top_module)
                elaborationError = True
            else:
                self.topModule = top_module
                logging.info("Top module found (%s)!", self.topModule)
        elif tops != 1:
            logging.warning("The design has multiple top cells! Output may not be correct!")

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
                    logging.info(i+"- "+instName+":"+inst)
                    _printH(inst, i)
                else:
                    logging.info(i+"- [!] "+instName+":"+inst)

        logging.info("[%s]" % topModule)
        _printH(topModule)

    @staticmethod
    def split_name(name):
        if not isinstance(name, str):
            raise TypeError("%s is not a string!" % name)

        splitted = name.split(".")
        
        if len(splitted) > 2:
            raise ValueError("Cannot elaborate %s: going further than 1st hierarchy for structs is not yet supported" % name)

        return (splitted[0], splitted[1] if len(splitted) > 1 else None)

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

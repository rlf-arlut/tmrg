import sys
if sys.version_info[0] >= 3:
    from .pyparsing241 import *
else:
    from .pyparsing152 import *


class VerilogFormatter:
    formater = {}

    def setTrace(self, t):
        self.trace = t

    def _format_Top(self, tokens, i=""):
        oStr = ""
        for i in tokens:
            oStr += self.format(i)
        return oStr

    def _format_lineComment(self, tokens, i=""):
        return i+"// %s\n" % tokens[0]

    def _format_Default(self, tokens, i=""):
        return "default (%s : %s)\n" % (tokens.getName(), tokens)

    def _format_Id(self, tokens, i=""):
        oStr = str(tokens[0])
        return oStr

    def _format_None(self, tokens, i=""):
        oStr = ""
        for t in tokens:
            oStr += self.format(t)+" "
        return oStr

    def _format_assign(self, tokens, i=""):
        oStr = tokens[0]
        oStr += " %s" % self.format(tokens[1])
        oStr += "="
        for t in tokens[2:]:
            oStr += self.format(t)+" "
        return oStr

    def _formatIo(self, tokens, i=""):
        oStr = ""
        label = str(tokens[0])
        spec = self.format(tokens[1])
        if spec != "":
            spec += " "
        spec += self.format(tokens[2])
        if spec != "":
            spec += " "
        spec += self.format(tokens[3])
        if spec != "":
            spec += " "
        ports = tokens[4]
        for port in ports:
            oStr += "%s %s%s;\n" % (label, spec, port)
        return oStr

    def _format_enum_identifier_with_package_name(self, tokens, i=""):
        return "".join(tokens[0])

    def _format_Input(self, tokens, i=""):
        return self._formatIo(tokens)

    def _format_InOut(self, tokens, i=""):
        return self._formatIo(tokens)

    def _format_Output(self, tokens, i=""):
        return self._formatIo(tokens)

    def _formatIoHdr(self, tokens, i=""):
        oStr = ""
        label = str(tokens[0])
        spec = self.format(tokens[1])
        spec += self.format(tokens[2])
        spec += self.format(tokens[3])
        ports = tokens[4]
        for port in ports:
            oStr += "%s %s %s" % (label, spec, port)
        return oStr

    def _format_inputhdr(self, tokens, i=""):
        return self._formatIoHdr(tokens)

    def _format_outputhdr(self, tokens, i=""):
        return self._formatIoHdr(tokens)

    def _format_inouthdr(self, tokens, i=""):
        return self._formatIoHdr(tokens)

    def _format_port(self, tokens, i=""):
        return tokens[0][0]

    def _format_RegDecl(self, tokens, i=""):
        oStr = ""
        label = str("".join(tokens[0]))
        attributes = self.format(tokens[1])

        spec = self.format(tokens[2])
        if spec != "":
            spec += " "
        for port in tokens[3]:
            r = ""
            if len(port) > 1:
                r = " "+self.format(port[1:])
            oStr += "%s %s %s%s%s;\n" % (label, attributes, spec, port[0], r)
        return oStr

    def _format_force(self, tokens, i=""):
        force = str(tokens[0])
        assgnmt = self._format_assgnmt(tokens[1])
        return "%s%s %s;\n" % (i, force, assgnmt)

    def _format_release(self, tokens, i=""):
        release = str(tokens[0])
        return "%s%s %s;\n" % (i, release, self.format(tokens[1]))

    def _format_netDecl3(self, tokens, i=""):
        oStr = ""
        label = str(tokens[0])
        sign = self.format(tokens[1])
        drives = self.format(tokens[2])
        spec = self.format(tokens[3])
        delay = self.format(tokens[4])
        if drives != "":
            drives += " "
        if spec != "":
            spec += " "
        if delay != "":
            delay += " "
        ports = tokens[5]
        for port in ports:
            port_str = self.format(port)
            oStr += "%s %s%s%s%s%s;\n" % (label, sign, drives, spec, delay, port_str)
        return oStr

    def _format_realDecl(self, tokens, i=""):
        oStr = ""
        real = str(tokens[0])
        ports = tokens[1:]
        for port in ports:
            port_name = port[0]
            port_str = self.format(port[1:])
            if port_str != "":
                port_str = " "+port_str
            oStr += "%s %s%s;\n" % (real, port_name, port_str)
        return oStr

    def _format_netDecl1(self, tokens, i=""):
        oStr = ""
        nettype = str(tokens[0])
        sign = self.format(tokens[1])
        range = self.format(tokens[2])
        delay = self.format(tokens[3])
        if sign != "":
            sign += " "
        if range != "":
            range += " "
        if delay != "":
            delay += " "
        ports = tokens[4]
        for port in ports:
            r = ""
            if len(port) > 1:
                r = " " + self.format(port[1:])
            port_str = self.format(port)
            oStr += "%s %s%s%s%s%s;\n" % (nettype, sign, range, delay, port_str, r)
        return oStr

    def _format_genVarDecl(self, tokens, i=""):
        oStr = ""
        genvar = str(tokens[0])
        expr = self.format(tokens[1:])
        oStr = genvar+" "+expr+";\n"
        return oStr

    def _format_namedPortConnection(self, tokens, i=""):
        oStr = ""
        for i in tokens:
            oStr += self.format(i)
        return oStr

    def _format_generate_module_named_block(self, tokens, i=""):
        oStr = i+"begin %s\n" % self.format(tokens[0])
        for stmt in tokens[1:]:
            oStr += self.format(stmt, i+"\t")
        oStr += i+"end\n"
        return oStr

    def _format_generate_module_loop_statement(self, tokens, i=""):
        genvar_decl_assignment = self.format(tokens[0])
        genvar_cond = self.format(tokens[1])
        genvar_assignment = self.format(tokens[2])
        oStr = i+"for(%s;%s;%s)\n" % (genvar_decl_assignment, genvar_cond, genvar_assignment)
        oStr += self.format(tokens[3], i=i+"\t")
        return oStr

    def _format_generate_if_statement(self, tokens, i=""):
        genvar_cond = self.format(tokens[0])
        body = self.format(tokens[1], i=i+"\t")
        oStr = i + "if %s" % genvar_cond + \
               body
        return oStr


    def _format_generate_if_else_statement(self, tokens, i=""):
        genvar_cond = self.format(tokens[0])
        bodyIf = self.format(tokens[1], i=i+"\t")
        bodyElse = self.format(tokens[2], i=i+"\t")
        oStr = i + "if %s" % genvar_cond + \
               bodyIf +  \
               i + "else" +\
               bodyElse
        return oStr
        
    def _format_generate(self, tokens, i=""):
        oStr = ""
        oStr = "\n"+i

        oStr += "generate\n"
        for sub_tokens in tokens:
            oStr += self.format(sub_tokens, i+"\t")+"\n"
        oStr += i+"endgenerate\n"
        return oStr

    def _format_Range(self, tokens, i=""):
        oStr = "["
        oStr += self.format(tokens[-2])
        oStr += ":"
        oStr += self.format(tokens[-1])
        oStr += "]"
        return oStr

    def _format_Always(self, tokens, i=""):
        oStr = "\n"+i + "%s %s\n" % (self.format(tokens[0]), self.format(tokens[1]))
        oStr += i+"\t%s\n" % self.format(tokens[2], i+"\t")
        return oStr

    def _format_subscrRef(self, tokens, i=""):
        if len(tokens) == 0:
            return ""
        oStr = "["
        sep = ""
        for t in tokens:
            oStr += sep+self.format(t, i)
            sep += ":"
        oStr += "]"
        return oStr

    def _format_subscrIndxRef(self, tokens, i=""):
        if len(tokens) == 0:
            return ""
        oStr = "["
        for t in tokens:
            oStr += self.format(t, i)
        oStr += "]"
        return oStr

    def _format_subscrIdentifier(self, tokens, i=""):

        oStr = ""
        for sid in tokens:
            oStr += self.format(sid)
        return oStr

    def _format_BeginEnd(self, tokens, i=""):
        oStr = "begin\n"
        for stmt in tokens[1:-1]:
            oStr += i+"\t"+self.format(stmt, i+"\t")+"\n"
        oStr += i+"end"
        return oStr

    def _format_beginEndLabel(self, tokens, i=""):
        oStr = "begin : %s\n" % (self.format(tokens[0]))
        for stmt in tokens[1:]:
            oStr += i+"\t"+self.format(stmt, i+"\t")+"\n"
        oStr += i+"end"
        return oStr

    def _format_taskEnable(self, tokens, i=""):
        oStr = ""
        id = tokens[0]
        oStr = "%s" % id
        if len(tokens[1]):
            oStr += "("
            sep = ""
            for v in tokens[1]:
                oStr += sep+self.format(v, i)
                sep = ", "
            oStr += ")"
        oStr += ";"
        return oStr

    def _format_delayStm(self, tokens, i=""):
        oStr = ""
        delay = self.format(tokens[0])
        stm = self.format(tokens[1])
        oStr += "%s%s %s" % (i, delay, stm)
        return oStr

    def _format_task(self, tokens, i=""):
        tid = self.format(tokens[0])
        oStr = "task %s;\n" % tid
        for tfDecl in tokens[1]:
            oStr += "\t"+self.format(tfDecl, i+"\t")
        stmt = tokens[2]
        oStr += "\t"+self.format(stmt, i+"\t")+"\n"
        oStr += "endtask\n"
        return oStr

    def _format_EventCtrl(self, tokens, i=""):
        oStr = ""
        for el in tokens:
            oStr += self.format(el)
        return oStr

    def _format_DelimitedList(self, tokens, i=""):
        oStr = ""
        sep = ""
        for el in tokens:
            oStr += sep+self.format(el)
            sep = ", "
        return oStr

    def _format_DelimitedOrList(self, tokens, i=""):
        oStr = ""
        sep = ""
        for el in tokens:
            oStr += sep+self.format(el)
            sep = " or "
        return oStr

    def _format_EventTerm(self, tokens, i=""):
        oStr = ""
        sep = ""
        for el in tokens:
            oStr += sep+self.format(el)
            sep = " "
        return oStr

    def _format_if(self, tokens, i=""):
        oStr = ""
        if len(tokens) == 1:
            stm = tokens[0]
        else:
            stm = tokens
        cond = stm[1]
        ifAction = stm[2]
        oStr += "if %s\n" % self.format(cond)
        oStr += i+"\t%s" % self.format(ifAction, i+"\t")
        return oStr

    def _format_concat(self, tokens, i=""):
        oStr = "{"
        sep = ""
        for t in tokens:
            oStr += sep+self.format(t)
            sep = ","
        oStr += "}"
        return oStr

    def _format_caseItem(self, tokens, i=""):
        expr = self.format(tokens[0])
        stm = self.format(tokens[1], i+"\t")
        if stm.find("\n") >= 0:
            stm = "\n%s%s" % (i+"\t", stm)
        oStr = "%s : %s" % (expr, stm)
        return oStr

    def _format_case(self, tokens, i=""):

        label = tokens[1]
        cond = self.format(tokens[2])
        oStr = "%s%s (%s)\n" % (self.format(tokens[0]), label, cond)
        for t in tokens[3]:
            oStr += i+"\t"+self.format(t, i+"\t")+"\n"
        oStr += i+tokens[4]
        return oStr

    def _format_funcCall(self, tokens, i=""):
        identifier = tokens[0]
        oStr = "%s(" % identifier
        for expr in tokens[2]:
            oStr += self.format(expr, i=i)
        oStr += ")"
        return oStr

    def _format_IfElse(self, tokens, i=""):
        oStr = ""
        if len(tokens) == 1:
            stm = tokens[0]
        else:
            stm = tokens
        cond = stm[1]
        ifAction = stm[2]
        elseAction = stm[4]
        oStr += "if %s\n" % self.format(cond)
        oStr += i+"\t%s\n" % self.format(ifAction, i+"\t")
        oStr += i+"else\n"
        oStr += i+"\t%s" % self.format(elseAction, i+"\t")
        return oStr

    def _format_parameterValueAssignment(self, tokens, i=""):
        if len(tokens[0]) > 1:
            oStr = "#(\n"+i
            sep = ""
            for param in tokens[0]:
                oStr += sep+self.format(param)
                sep = ",\n"+i
            oStr += "\n)\n"
            return oStr
        else:
            oStr = "#("
            oStr += self.format(tokens[0][0])
            oStr += ") "
            return oStr

    def _format_primary(self, tokens, i=""):
        oStr = ""
        for t in tokens:
            oStr += self.format(t, i="")
        return oStr

    def _format_moduleInstance(self, tokens, i=""):
        id = self.format(tokens[0][0])
        range = self.format(tokens[0][1])
        args = self.format(tokens[1], i=i)
        return "%s %s%s" % (id, range, args)

    def _format_moduleArgs(self, tokens, i=""):
        i += "\t"
        oStr = "(\n"+i
        sep = ""
        for t in tokens:
            oStr += sep+self.format(t, i)
            sep = ",\n"+i
        oStr += "\n"+i+")"
        return oStr

    def _format_modulePortConnection(self, tokens, i=""):

        return self.format(tokens[0], i)

    def _format_moduleInstantiation(self, tokens, i=""):
        ostr = ""
        identifier = self.format(tokens[0])
        if len(tokens) > 2:
            parameterValueAssignment = self.format(tokens[1], i=i+"\t")
            modulesList = tokens[2]
        else:
            parameterValueAssignment = ""
            modulesList = tokens[1]

        for modIns in modulesList:
            modInsStr = self.format(modIns, i=i+"\t")
            ostr += "\n%s%s %s%s;\n" % (i, identifier, parameterValueAssignment, modInsStr)

        return ostr

    def _format_functionDecl(self, tokens, i=""):
        oStr = "%s%s %s %s%s\n" % (i, tokens[0], self.format(tokens[1]), tokens[2], tokens[3])
        for item in tokens[4]:
            oStr += i + "\t" + self.format(item)
        for item in tokens[5]:
            oStr += i + "\t" + self.format(item)
        oStr += "\n%s%s\n" % (i, tokens[6])
        return oStr

    def _format_Module(self, tokens, i=""):
        header = tokens[0]
        modname = header[1]
        oStr = "module %s" % modname
        if len(header[2]) > 0:
            oStr += " #(\n  "
            sep = ""
            for p in header[2]:
                _range = self.format(p[0])
                if _range != "":
                    _range += " "
                oStr += "%sparameter %s%s=%s" % (sep, _range, p[1][0], self.format(p[1][1]))
                sep = ",\n  "
            oStr += "\n)"
        sep = ""
        if len(header) > 3:
            ports = header[3]
            oStr += "(\n"
            for port in ports:
                oStr += sep+"\t"+self.format(port)
                sep = ",\n"
            oStr += "\n)"
        oStr += ";\n"

        moduleBody = tokens[1]
        for moduleItem in moduleBody:
            oStr += self.format(moduleItem)

        endmodule_label = ""
        if len(tokens[3]):
            endmodule_label = " : %s" % modname
        oStr += "endmodule%s\n\n" % (endmodule_label)
        return oStr

    def _format_NbAssgnmt(self, tokens, i=""):
        lval = self.format(tokens[0])
        delay = self.format(tokens[1])
        if delay != "":
            delay += " "
        expr = self.format(tokens[2])
        oStr = "%s <= %s%s;" % (lval, delay, expr)

        return oStr

    def _format_inlineIfExpr(self, tokens, i=""):
        if len(tokens) == 1:
            return self.format(tokens[0])
        primary = self.format(tokens[0])
        expr1 = self.format(tokens[1])
        expr2 = self.format(tokens[2])

        return "%s ? %s : %s" % (primary, expr1, expr2)

    def _format_Expr(self, tokens, i=""):
        oStr = ""
        for t in tokens:
            oStr += self.format(t)
        return oStr

    def _format_Delay(self, tokens, i=""):
        oStr = ""
        for t in tokens:
            oStr += self.format(t)
        return oStr

    def _format_Condition(self, tokens, i=""):
        oStr = ""
        for t in tokens:
            oStr += self.format(t)
        return oStr

    def _format_paramAssgnmt(self, tokens, i=""):
        id = self.format(tokens[0])
        val = self.format(tokens[1])
        oStr = "%s=%s" % (id, val)
        return oStr.rstrip()

    def _format_paramdecl(self, tokens, i=""):
        oStr = ""
        signed = self.format(tokens[1])
        range = self.format(tokens[2])
        if len(range) >= 0:
            range = " "+range
        for p in tokens[3]:
            pname = p[0][0]
            oStr += tokens[0]+" %s %s %s=" % (signed, range, pname)
            oStr += self.format(p[0][1:])+";\n"
        return oStr

    def _format_localparamdecl(self, tokens, i=""):
        return self._format_paramdecl(tokens)

    def _format_delayOrEventControl(self, tokens, i=""):
        oStr = ""
        return oStr

    def _format_blockName(self, tokens, i=""):
        oStr = tokens[0]
        return oStr

    def _format_integerDecl(self, tokens, i=""):
        oStr = ""
        label = tokens[0]
        for var in tokens[1]:
            oStr += "%s %s;\n" % (label, self.format(var))
        return oStr

    def _format_integerDeclAssgn(self, tokens, i=""):
        oStr = ""
        for assigment in tokens[1]:
            label = tokens[0]
            oStr += "%s %s = %s;\n" % (label, self.format(assigment[0]), self.format(assigment[-1]))
        return oStr

    def _format_assgnmtStm(self, tokens, i=""):
        oStr = self.format(tokens[0])+";"
        return oStr

    def _format_assgnmt(self, tokens, i=""):
        oStr = ""
        lvalue = self.format(tokens[0])
        assign = tokens[1]
        delayOrEventControl = self.format(tokens[2])+" "
        expr = self.format(tokens[3])

        oStr = "%s = %s%s" % (lvalue, delayOrEventControl, expr)
        return oStr

    def _format_assgnmt_with_declaration(self, tokens, i=""):
        return tokens[0] + " " + self._format_assgnmt(tokens[1:])

    def _format_incr_decr(self, tokens, i=""):
        return self.format(tokens[0]) + " " + tokens[1]

    def _format_forstmt(self, tokens, i=""):
        e1 = self.format(tokens[1])
        e2 = self.format(tokens[2])
        e3 = self.format(tokens[3])
        s = self.format(tokens[4], i=i+"\t")
        oStr = "for(%s;%s;%s)\n%s\t%s" % (e1, e2, e3, i, s)
        return oStr

    def _format_driveStrength(self, tokens, i=""):
        oStr = ""
        for t in tokens:
            oStr += self.format(t)
        return oStr

    def _format_continuousAssign(self, tokens, i=""):
        oStr = i
        driveStrength = self.format(tokens[0])
        if driveStrength:
            driveStrength += " "
        delay = self.format(tokens[1])
        if delay:
            delay += " "
        for asg in tokens[2]:
            asg_str = self.format(asg)
            oStr += "assign %s%s%s;\n" % (driveStrength, delay, asg_str)
        return oStr

    def _format_net3(self, tokens, i=""):
        oStr = ""
        return oStr

    def _format_initialStmt(self, tokens, i=""):
        oStr = "initial\n\t%s\n" % self.format(tokens[1], i+"\t")
        return oStr

    def _format_directive_synopsys(self, tokens, i=""):
        return "// "+" ".join(tokens)+"\n"

    def _format_directive_synopsys_case(self, tokens, i=""):
        return "// "+" ".join(tokens[0])+"\n"

    def _format_comp_directive(self, tokens, i=""):
        return "`"+tokens[0].lstrip()+"\n"

    def _format_default(self, tokens, i=""):
        return ""

    def _format_directive_default(self, tokens, i=""):
        return ""

    def _format_directive_do_not_touch(self, tokens, i=""):
        return ""

    def _format_directive_majority_voter_cell(self, tokens, i=""):
        return ""

    def _format_directive_fanout_cell(self, tokens, i=""):
        return ""

    def _format_directive_tmr_error_exclude(self, tokens, i=""):
        return ""

    def _format_directive_do_not_triplicate(self, tokens, i=""):
        return ""

    def _format_directive_slicing(self, tokens, i=""):
        return ""

    def _format_directive_translate(self, tokens, i=""):
        return ""

    def _format_gate(self, tokens, i=""):
        oStr = ""
        return oStr

    def _format_package_import_item(self, tokens, i=""):
        return "".join(tokens)

    def _format_package_import_declaration(self, tokens, i=""):
        oStr = i + tokens[0] + " " + self.format(tokens[1]) + ";\n"
        return oStr

    def __init__(self):
        for member in dir(self):
            if member.find("_format_") == 0:
                token = member[len("_format_"):].lower()
                self.formater[token] = getattr(self, member)
        self.trace = False

    def format(self, tokens, i=""):
        self.trace = 0
        outStr = ""
        if tokens == None:
            return ""
        if isinstance(tokens, ParseResults):
            name = str(tokens.getName()).lower()
            if self.trace:
                print("[%-20s] len:%2d  str:'%s' >" % (name, len(tokens), str(tokens)[:80]))
            if name != "moduleargs" and len(tokens) == 0:
                return ""
            if name in self.formater:
                outStr = self.formater[name](tokens, i)
            else:
                outStr = self.formater["default"](tokens, i)
        elif isinstance(tokens, list):
            outStr = "".join(map(self.format, tokens))
        else:
            outStr = tokens
        return outStr

    def __call__(self, tokens, i=""):
        return self.format(tokens, i)


def prettyPrint(f, tokens, ident=0):
    IS = "  "

    def formInputOutput(f, tokens, ident=0, label="input"):
        spec = ""
        if len(tokens) > 2:
            spec = resultLine(tokens[1]).rstrip()
            ports = tokens[2]
        else:
            ports = tokens[1]
        for port in ports:
            f.write(IS*ident+"%s %s %s;\n" % (label, spec, port))

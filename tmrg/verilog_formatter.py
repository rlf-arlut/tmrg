import sys
if sys.version_info[0] >= 3:
    from .pyparsing241 import *
else:
    from .pyparsing152 import *
"""
from pyparsing import *
"""

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

    def _format_array_size(self, tokens, i=""):
        return "[%s]" % self.format(tokens[0])

    def _formatIo(self, tokens, i=""):
        return str(tokens[0]) + self._format_RegDecl(tokens)

    def _format_Input(self, tokens, i=""):
        return self._formatIo(tokens)

    def _format_InOut(self, tokens, i=""):
        return self._formatIo(tokens)

    def _format_Output(self, tokens, i=""):
        return self._formatIo(tokens)

    def _formatIoHdr(self, tokens, i="", end=""):
        oStr = ""
        spec = []
        dir = str(tokens.get("dir"))

        if "standard" in tokens.keys():
            _standard = tokens.get("standard")
            if "kind" in _standard.keys():
                spec.append(_standard.get("kind")[0])
            if "attrs" in _standard.keys():
                spec.append(self.format(tokens.get("standard").get("attrs")))
            for r in tokens.get("packed_ranges"):
                spec.append(self.format(r))
        elif "custom" in tokens:
            spec = [self.format(tokens.get("custom").get("custom_type")[0])]

        spec = " ".join(spec)

        ports = tokens.get("identifiers")
        for port in ports:
            name = port.get("name")[0]
            array = ""
            for r in port.get("unpacked_ranges"):
                array += " "+self.format(r)

            oStr += "%s %s %s%s%s" % (dir, spec, name, array, end)
        return oStr

    def _format_porthdr(self, tokens, i=""):
        return self._formatIoHdr(tokens)

    def _format_portbody(self, tokens, i=""):
        return self._formatIoHdr(tokens, end=";\n")

    def _format_port(self, tokens, i=""):
        return tokens[0][0]

    def _format_force(self, tokens, i=""):
        force = str(tokens[0])
        assignment = self._format_assignment(tokens[1])
        return "%s%s %s;\n" % (i, force, assignment)

    def _format_release(self, tokens, i=""):
        release = str(tokens[0])
        return "%s%s %s;\n" % (i, release, self.format(tokens[1]))

    def _format_netDecl3(self, tokens, i=""):
        oStr = i
        type = str(tokens.get("kind"))
        attributes = self.format(tokens.get("attributes"))

        packed = " "
        for r in tokens.get("packed_ranges"):
            packed += self.format(r) + " "

        delay = self.format(tokens.get("delay"))
        ports = tokens.get("assignments")

        for port in ports:
            port_str = self.format(port)
            oStr += "%s %s %s%s%s;\n" % (type, attributes, packed, delay, port_str)
        return oStr

    def _format_netdeclwassign(self, tokens, i="", ending=";\n"):
        oStr = ""
        label = ""
        if "standard" in tokens.keys():
            label = tokens.get("standard").get("kind")[0]
            if "attrs" in tokens.get("standard"):
                label += " " + tokens.get("standard").get("attrs")

            for r in tokens.get("packed_ranges"):
                label += " " + self.format(r)
        else:
            label = tokens.get("custom").get("custom_type")[0]

        for assignment in tokens.get("assignments"):
            assignment_str = self._format_assignment(assignment)
            oStr += "%s %s%s" % (label, assignment_str, ending)
        return oStr

    def _format_customDeclwAssign(self, tokens, i=""):
        oStr = i
        label = str(tokens.get("custom_type")[0])
        for assignment in tokens.get("assignments"):
            assignment_str = self._format_assignment(assignment)
            oStr += "%s %s;\n" % (label, assignment_str)
        return oStr

    def _format_realDecl(self, tokens, i=""):
        oStr = i
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
        oStr = i
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
        oStr = i
        genvar = str(tokens[0])
        expr = self.format(tokens[1:])
        oStr = genvar+" "+expr+";\n"
        return oStr

    def _format_genVarDeclInline(self, tokens, i=""):
        oStr = i+"genvar "+tokens.get("name")[0]

        if "expr@rvalue" in tokens.keys():
            oStr += " = " + self.format(tokens.get("expr@rvalue"))

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
        genvar_decl_assignment = self.format(tokens.get("for1")[0]).replace("\n", " ")
        genvar_cond = self.format(tokens.get("expr@for2"))
        genvar_assignment = self.format(tokens.get("for3")[0])
        oStr = i+"for(%s;%s;%s)\n" % (genvar_decl_assignment, genvar_cond, genvar_assignment)
        oStr += self.format(tokens.get("generate_module_named_block"), i=i+"\t")
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
        oStr += self.format(tokens[0])
        oStr += tokens[1]
        oStr += self.format(tokens[2])
        oStr += "]"
        return oStr

    def _format_Size(self, tokens, i=""):
        oStr = "["
        oStr += self.format(tokens[0])
        oStr += "]"
        return oStr

    def _format_Field(self, tokens, i=""):
        return "." + tokens[0]

    def _format_Always(self, tokens, i=""):
        print("Formatting always: %s" % tokens.asDict())

        oStr = "\n"+i + "%s" % self.format(tokens.get("type"))
        if "eventCtrl" in tokens:
            oStr += " %s" % self.format(tokens.get("eventCtrl"))

        oStr += "\n" + i + "\t%s\n" % self.format(tokens.get("statement"), i+"\t")

        return oStr

    def _format_reg_reference(self, tokens, i=""):
        oStr = tokens.get("name")[0]

        for sid in tokens[1]:
            oStr += self.format(sid)

        return oStr

    def _format_field_ref(self, tokens, i=""):
        return "."+tokens[0]

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
        identifier = tokens.get("moduleName")[0]
        if len(tokens) > 2:
            parameterValueAssignment = self.format(tokens[1], i=i+"\t")
        else:
            parameterValueAssignment = ""

        modulesList = tokens.get("moduleInstances")

        for modIns in modulesList:
            modInsStr = self.format(modIns, i=i+"\t")
            ostr += "\n%s%s %s%s;\n" % (i, identifier, parameterValueAssignment, modInsStr)

        return ostr

    def _format_functionDecl(self, tokens, i=""):
        
        oStr = "%s%s %s %s %s%s\n" % (i, tokens[0], self.format(tokens[1]), self.format(tokens[2]), tokens[3], tokens[4])
        for item in tokens[5]:
            oStr += i + "\t" + self.format(item)
        for item in tokens[6]:
            oStr += i + "\t" + self.format(item)
        oStr += "\n%s%s\n" % (i, tokens[7])
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
                oStr += "%sparameter %s %s" % (sep, _range, self.format(p[1]))
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

    def _format_nbassignment(self, tokens, i=""):
        lval = self.format(tokens.get("lvalue")[0])
        doec = ""
        if "delayOrEventControl" in tokens:
            doec = " " + self.format(tokens.get("delayOrEventControl")[0])
            print("ZZZ " + doec)

        expr = self.format(tokens.get("expr@rvalue"))
        oStr = "%s <= %s%s;" % (lval, doec, expr)

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
        size = self.format(tokens[1])
        val = self.format(tokens[2])
        oStr = "%s %s = %s" % (id, size, val)
        return oStr.rstrip()

    def _format_paramdecl(self, tokens, i=""):
        oStr = ""
        signed = self.format(tokens[1])
        type_ = self.format(tokens[2])
        range = self.format(tokens[3])
        for p in tokens[4]:
            pname = p[0][0]
            size = self.format(p[0][1])
            oStr += tokens[0]+" %s %s %s %s %s=" % (signed, type_, range, pname, size)
            oStr += self.format(p[0][2:])+";\n"
        while "  " in oStr:
            oStr = oStr.replace("  "," ")
        return oStr

    def _format_localparamdecl(self, tokens, i=""):
        return self._format_paramdecl(tokens)

    def _format_blockName(self, tokens, i=""):
        oStr = tokens[0]
        return oStr

    def _format_integerDecl(self, tokens, i=""):
        oStr = ""
        label = tokens[0]
        for var in tokens[1]:
            oStr += "%s %s;\n" % (label, self.format(var))
        return oStr

    def _format_from(self, tokens, i=""):
        return self._format_Expr(tokens)

    def _format_to(self, tokens, i=""):
        return self._format_Expr(tokens)

    def _format_RegDecl(self, tokens, i=""):
        oStr = ""
        label = str(tokens.get("type"))
        attributes = self.format(tokens.get("attributes"))

        packed = " "
        for r in tokens.get("packed_ranges"):
            packed += self.format(r) + " "

        for port in tokens.get("identifiers"):
            unpacked = ""
            for r in port.get("unpacked_ranges"):
                unpacked += self.format(r)

            oStr += "%s %s %s%s%s;\n" % (label, attributes, packed, port.get("name")[0], unpacked)
        return oStr

    def _format_customDecl(self, tokens, i=""):
        oStr = ""
        label = tokens.get("custom_type")[0]
        for var in tokens.get("identifiers"):
            oStr += "%s %s;\n" % (label, self.format(var[0]))
        return oStr

    def _format_netdecl(self, tokens, i=""):
        label = ""
        if "standard" in tokens.keys():
            label = tokens.get("standard").get("kind")[0]
            if "attrs" in tokens.get("standard"):
                label += " " + tokens.get("standard").get("attrs")
        else:
            label = tokens.get("custom").get("custom_type")[0]

        for r in tokens.get("packed_ranges"):
            label += " " + self.format(r)

        label += " "

        oStr = ""
        for port in tokens.get("identifiers"):
            unpacked = ""
            for r in port.get("unpacked_ranges"):
                unpacked += " " + self.format(r)

            oStr += "%s%s%s;\n" % (label, port.get("name")[0], unpacked)
        return oStr

    def _format_structDecl(self, tokens, i=""):
        oStr = tokens[0] + " { \n"

        for field in tokens[1]:
            label = str(field.get("type"))
            attributes = self.format(field.get("attributes"))

            spec = " "
            for r in field.get("packed_ranges"):
                spec += self.format(r) + " "

            for port in field.get("identifiers"):
                r = self.format(port.get("name")[0])
                if "unpacked_ranges" in port.keys():
                    r += self.format(port.get("unpacked_ranges"))

                oStr += "    %s %s %s %s;\n" % (label, attributes, spec, r)

        oStr += "} " + tokens.get("id")[0] + ";\n"

        return oStr

    def _format_integerDeclAssgn(self, tokens, i=""):
        oStr = ""
        for assigment in tokens[1]:
            label = tokens[0]
            oStr += "%s %s = %s;\n" % (label, self.format(assigment[0]), self.format(assigment[-1]))
        return oStr

    def _format_assignmentStm(self, tokens, i=""):
        oStr = self.format(tokens[0])+";"
        return oStr

    def _format_nbassignmentStm(self, tokens, i=""):
        return self.format(tokens[0])

    def _format_assignment(self, tokens, i=""):
        lvalue = self.format(tokens.get("lvalue")[0])
        assign = tokens.get("op")

        doec = ""
        if "delayOrEventControl" in tokens:
            doec = " " + self.format(tokens.get("delayOrEventControl")[0])

        expr = self.format(tokens.get("expr@rvalue"))
        oStr = "%s %s%s %s" % (lvalue, assign, doec, expr)
        return oStr

    def _format_assignment_with_declaration(self, tokens, i=""):
        return tokens.get("type") + " " + tokens.get("name")[0] + " = " + self.format(tokens.get("expr@rvalue"))

    def _format_incr_decr(self, tokens, i=""):
        return self.format(tokens[0]) + tokens[1]

    def _format_forstmt(self, tokens, i=""):
        for1 = tokens.get("for1")[0]

        # If netDeclWAssign, remove newline and ;
        if for1.getName() == "netDeclWAssign":
            decl_assignment = self._format_netdeclwassign(for1, ending="")
        else:
            decl_assignment = self.format(for1)

        cond = self.format(tokens.get("expr@for2"))
        assignment = self.format(tokens.get("for3")[0])
        stmt = tokens.get("stmt")[0]

        oStr = "for(%s; %s; %s)\n" % (decl_assignment, cond, assignment)
        if stmt.getName().startswith("beginend"):
            oStr += i+self.format(stmt, i)
        else:
            oStr += i+"\t"+self.format(stmt, i=i+"\t")
        return oStr

    def _format_driveStrength(self, tokens, i=""):
        oStr = ""
        for t in tokens:
            oStr += self.format(t)
        return oStr

    def _format_attr_spec(self, tokens, i=""):
        return " ".join(tokens)

    def _format_attribute_instance(self, tokens, i=""):
        oStr = tokens[0] + " "
        attr_list = []
        for attr in tokens[1]:
          attr_list.append(self.format(attr))
        oStr += ", ".join(attr_list)
        oStr += " " + tokens[2]
        return oStr

    def _format_continuousAssign(self, tokens, i=""):
        oStr = i
        driveStrength = self.format(tokens.get("driveStrength"))
        if driveStrength:
            driveStrength += " "
        delay = self.format(tokens.get("delay"))
        if delay:
            delay += " "

        for asg in tokens.get("assignments"):
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

    def _format_gateDecl(self, tokens, i=""):
        ostr = ""
        gate = self.format(tokens[0])
        for gate_inst, ports in tokens[3]:
            gate_inst_str = self.format(gate_inst)
            ports_str = self.format(ports)
            ostr += "\n%s%s %s (%s);\n" % (i, gate, gate_inst_str, ports_str)
        return ostr

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
        self.trace = 1
        outStr = ""
        if tokens == None:
            return ""
        if isinstance(tokens, ParseResults):
            name = str(tokens.getName()).lower()
            offset = name.find("@")
            if offset != -1:
                name = name[0:offset]
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

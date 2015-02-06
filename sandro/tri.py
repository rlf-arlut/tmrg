#!/usr/bin/python

###########################################################################
#
# Triple Module Redundant state machnine generator script
#
# Sandro Bonacini, 2008
#
# Modified 30/09/2010, added warning messages.
#
###########################################################################
#
# Notes: 
# 	- code must be in "old" Verilog	style (v2001 is not supported yet...)
#	- sequential logic regs must be assigned only with <=
#	- combinatorial logic regs must be assigned only with =
#	- functions, tasks and module instantiations are not supported yet
#	- the script might have problems with long/complex expressions
#
###########################################################################


import re
import sys

orig=sys.stdin.read()
regs_raw=re.findall("(\w+)\s*<=",orig);
regs=[];

for r in regs_raw:
	if not r in regs:
		regs.append(r);

regs_raw=[];

print >>sys.stderr, "Found registers: ", regs, "\n";

#
# split multiple declarations into single line declarations
#
orig_new="";
while (orig!=orig_new):
	if (orig_new): orig=orig_new;
	orig_new=re.sub("(\s+)(input|output|reg)(\s+)(\w+\s*),(\s*\w+\s*)","\\1\\2\\3\\4;\n\\1\\2\\3\\5",orig);
	orig_new=re.sub("(\s+)(input|output|reg)(\s*\[[^\[\]]*\]\s*)(\w+\s*),(\s*\w+\s*)","\\1\\2\\3\\4;\n\\1\\2\\3\\5",orig_new);

orig=orig_new;

#print >>sys.stderr, orig;

#
# change module name
#		
iostate=re.sub("(module\s*\w+)", "\\1_iostate", orig);

for r in regs:
	# change left-hand assigments (_o)
	iostate=re.sub("(" + r + ")(\s*(\[[^\[\];]+\])?\s*<=)", "\\1_o\\2", iostate);
	# change right-hand assigments (_i)
	iostate=re.sub("(?s)(<=[^;]*?\W" + r + ")(;|\W[^;]*?;)", "\\1_i\\2", iostate);
	iostate=re.sub("(?s)(<=[^;]*?\W" + r + ")(;|\W[^;]*?;)", "\\1_i\\2", iostate);
	iostate=re.sub("(\[[^\[\]]*?\W|\[)(" + r + ")(\W[^\[\]]*?\]|\])", "\\1\\2_i\\3", iostate);
	# change if statements (_i)
	iostate=re.sub("(?s)(if\s*[^;]*?\W" + r + ")(\W[^;]*?)(\w+\[?\d*\]?\s*<?=|begin)", "\\1_i\\2\\3", iostate);
	iostate=re.sub("(?s)(if\s*[^;]*?\W" + r + ")(\W[^;]*?)(\w+\[?\d*\]?\s*<?=|begin)", "\\1_i\\2\\3", iostate);
	# change combinatorial logic expressions (_i)
	iostate=re.sub("(?s)([^<>=]=[^;]*?" + r + ")(;|\W[^;]*?;)", "\\1_i\\2", iostate);
	iostate=re.sub("(?s)([^<>=]=[^;]*?" + r + ")(;|\W[^;]*?;)", "\\1_i\\2", iostate);
	# change case statements (_i)
	iostate=re.sub("(case\s*\([^();]*?\W" + r + ")(\W[^();]*?)(\)\s*)", "\\1_i\\2\\3", iostate);
	# change port declarations (_i, _o)
	if (re.findall("(?s)module[^;]*?\W" + r + "\W[^;]*?;",iostate)!=[]):
		iostate=re.sub("(?s)(module[^;]*?\W" + r + ")(\W[^;]*?;)", "\\1_i, " + r + "_o\\2", iostate);
	else:
		iostate=re.sub("(?s)(module[^;]*?)(\)\s*;)", "\\1, " + r + "_i, " + r + "_o\\2", iostate);
	# change reg declarations (_i, _o)
	iostate=re.sub("(reg\s*(\[[^\[\];]+\])?\s*\W" + r + ")(\s*;)", "\\1_o\\3", iostate);
	# add/change I/O declarations (_i, _o)
	if (re.findall("(output\s*(\[[^\[\];]+\])?\s*\W" + r + ")(\s*;)",iostate)!=[]):
		iostate=re.sub("(output)(\s*(\[[^\[\];]+\])?\s*\W" + r + ")(\s*;)", "\\1\\2_o\\4\n\tinput\\2_i\\4", iostate);
	else:
		iostate=re.sub("(reg)(\s*(\[[^\[\];]+\])?\s*\W" + r + ")_o(\s*;)", "\\1\\2_o\\4\n\toutput\\2_o\\4\n\tinput\\2_i\\4", iostate);
	iostate=re.sub("(?s)(input[^;]*?;\s*)(.*)(input[^;]*?;\s*)", "\\1\\3\\2", iostate);
	iostate=re.sub("(?s)(output[^;]*?;\s*)(.*)(output[^;]*?;\s*)", "\\1\\3\\2", iostate);
	if (re.findall(r + "_o\s*<=\s*(#\s*\d+)?\s*" + r + "_i\s*;", iostate)==[]):
		print >>sys.stderr, "You are missing an assigment like:" 
		print >>sys.stderr, r + " <=#1 " + r + ";"
		print >>sys.stderr, "If this is not a deliberate choice, please put it in your original code and re-run this script!\n" 
		iostate="// missing: " + r + "_o <=#1 " + r + "_i;\n" + iostate;

print iostate;

#
# make stub of iostate module
#
stub = iostate;
stub_new="";
while (stub_new!=stub):
	if (stub_new): stub=stub_new;
	stub_new=re.sub("(?s)\W(always|initial|reg|wire|tri|assign)\W.*?(\W(endmodule|input|output|inout)\W)","\\2",stub);

stub_iostate=re.sub("//.*\n","",stub_new);

#
# from iostate module stub, make wire definitions
#

#wires=re.sub("(?s)module[^;]*?;(.*)endmodule","\\1",stub_iostate);
#wires=re.sub("input.*\n","",wires);
#wires=re.sub("(?s)parameter[^;]*;","",wires);
#wires=re.sub("`timescale.*\n","",wires);
#wires=re.sub("\s*output","\n\twire",wires);
#wires=re.sub("_o;",";",wires);

wires="";
for r in regs:
	brackets_raw=re.findall("\s*output\s*(\[[^\[\];]+\])\s*"+r,stub_iostate);
	if (brackets_raw):
		wires = wires + "\twire " + brackets_raw[0] + " " + r + ";\n";
	else:
		wires = wires + "\twire " + r + ";\n";
#
# from iostate module stub take parameters
#
#print >>sys.stderr, "Stub: ", stub_iostate, "\n";
parameters=re.sub("(?s)module[^;]*?;(.*)endmodule","\\1",stub_iostate);
parameters=re.sub("input.*\n","",parameters);
parameters=re.sub("output.*\n","",parameters);
parameters=re.sub("`timescale.*\n","",parameters);
parameters=re.sub("`include.*\n","",parameters);
parameters=re.sub("`undef.*\n","",parameters);
localparams=re.findall("localparam.*\n",parameters);
parameters=re.sub("localparam.*\n","",parameters);
#print >>sys.stderr, "Found parameters: ", parameters, "\n";

#
# from iostate module stub, make module instantiation
#
inst=re.sub("(?s)module\s+(\w+)([^;]*?);.*endmodule","\t\\1 \\2;",stub_iostate);
inst=re.sub("(?s)parameter[^;]*;","",inst);
inst=re.sub("`timescale.*\n","",inst);
inst=re.sub("`include.*\n","",inst);
inst=re.sub("`undef.*\n","",inst);
inst1=re.sub("(?s)(\w+)([^;]*?);","\\1 \\1_1 \\2;", inst);
inst1=re.sub("(\w+)\s*([,)])",".\\1(\\1_1)\\2",inst1);
inst1=re.sub("(\.\w+_o\()(\w+)_o_1\)","\\1\\2_2)",inst1);
inst1=re.sub("(\.\w+_i\()(\w+)_i_1\)","\\1\\2_1)",inst1);
inst2=re.sub("(?s)(\w+)([^;]*?);","\\1 \\1_2 \\2;", inst);
inst2=re.sub("(\w+)\s*([,)])",".\\1(\\1_2)\\2",inst2);
inst2=re.sub("(\.\w+_o\()(\w+)_o_2\)","\\1\\2_3)",inst2);
inst2=re.sub("(\.\w+_i\()(\w+)_i_2\)","\\1\\2_2)",inst2);
inst3=re.sub("(?s)(\w+)([^;]*?);","\\1 \\1_3 \\2;", inst);
inst3=re.sub("(\w+)\s*([,)])",".\\1(\\1_3)\\2",inst3);
inst3=re.sub("(\.\w+_o\()(\w+)_o_3\)","\\1\\2)",inst3);
inst3=re.sub("(\.\w+_i\()(\w+)_i_3\)","\\1\\2_3)",inst3);
inst=inst1 + inst2 + inst3;
addparam=re.sub("\s*parameter\s*\[?\d*:?\d*\]?\s*(\w+)\s*.*?\n",".\\1(\\1) ",parameters);
addparam=re.sub("\) \.","), .",addparam);
addparam=re.sub("\s+"," ",addparam);
if (addparam!=" "): inst=re.sub("(\w+)\s+(\w+)\s*\(","\\1 #("+addparam+") \\2 (",inst);

#
# calculate majority voter width from wire definitions
#
wires_raw=re.findall("wire",wires);
brackets_raw=re.findall("wire\s*\[([^\[\]:]*):([^\[\]:]*)\]",wires);
width=0;
strwidth="";

for w in wires_raw:
	width = width + 1;

for w in brackets_raw:
	try: width = width + int(w[0]);
	except: strwidth = strwidth + "+" + w[0];
	try: width = width - int(w[1]);
	except: strwidth = strwidth + "-" + w[1];

#
# from wire definitions make majority voter instantiation
#
mv=re.sub("\s*wire\s*(\[[^\[\]]*?\])?\s*(\w+)\s*;\s*","\\2, ",wires);
mv1=".in1({" + re.sub("(\w+),","\\1_2,",mv) + "}),";
mv2=".in2({" + re.sub("(\w+),","\\1_3,",mv) + "}),";
mv3=".in3({" + re.sub("(\w+),","\\1,",mv) + "}),";
mv=".out({" + re.sub("(\w+),","\\1_1,",mv) + "}),";
mv = "\tmajority_voter #(.WIDTH(" + str(width) + strwidth + ")) mv (\n\t\t" + mv1 + "\n\t\t"+ mv2 + "\n\t\t"+ mv3 + "\n\t\t" + mv + "\n\t\t.err()\n\t);"
mv=re.sub(", }","}",mv);

#
# make stub for tri module and finalize it
#
stub=orig;
stub_new="";
while (stub_new!=stub):
	if (stub_new): stub=stub_new;
	stub_new=re.sub("(?s)\W(always|initial|reg|wire|tri|assign)\W.*?(\W(endmodule|input|output|inout)\W)","\\2",stub);

#print stub_new;
#print stub_iostate;

tri=re.sub("(?s)parameter[^;]*;","",stub);
tri=re.sub("(?s)localparam[^;]*;","",tri);
tri=re.sub("(module\s*\w+)", "\\1_tri", tri);
tri=re.sub("endmodule",wires + "endmodule",tri);

tri=re.sub("(\w+)(\s*[,);])", "\\1_1, \\1_2, \\1_3\\2", tri);
#tri=re.sub("(wire|input|output)(\s*\[?\d*:?\d*\]?\s*)(\w+)(\s*[,);])", "\\1\\2\\3_1, \\3_2, \\3_3\\4", tri);
tri=re.sub("endmodule",wires + inst + "\n" + mv + "\n" + "endmodule",tri);
localparamstr = ''.join(localparams)
tri=re.sub("(?s)(module[^;]*;)","\\1\n" + parameters + localparamstr,tri);
tri=re.sub("(?s)\n\s+\n+","\n\n",tri);

print tri;

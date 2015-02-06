#!/usr/bin/python

###########################################################################
#
# Triple Module Redundant netlist generator script
#
# Sandro Bonacini, 2013
#
###########################################################################
#
# Notes: 
#	-Verilog 2005 declaration style
#	-arguments in the command line are module names that are not triplicated
#	-only for netlists (no "always" or "initial" statements)
#	-assign is allowed
#	-no expressions in instances
#	- instance parameters on a single line
###########################################################################


import re
import sys
#import str

orig=sys.stdin.read()

timescale=re.findall("`timescale .*",orig)
if (timescale!=[]): print timescale[0]

modulehead=re.findall("module\s+(\w+)\s*(#\([^)]+\))?", orig);
print "module " + str(modulehead[0][0])+"_tri " 
if (len(modulehead[0])>1): 
	print str(modulehead[0][1])
	parameters = re.findall("(\w+)\s*=",modulehead[0][1])
print " ("


orig=re.sub("(input|output)","\n\\1",orig)
inouts=re.findall("(?s)((?:input|output).+?)\n",orig);
for i in inouts:
	decl=re.findall("^(input|output)",i)[0]
	ins=re.sub("(input|output)","",i)
	bus=re.findall("\[[^\[\]]+\]",ins)
	#print bus
	busstr=""
	if (bus!=[]): 
		ins=ins.replace(bus[0],"")
		busstr=bus[0];
	out=decl + " "+busstr+re.sub("(\w+)","\\1_1",ins)
	out=out+"\n"+ decl +" "+busstr+re.sub("(\w+)","\\1_2",ins)
	out=out+"\n"+ decl +" "+busstr+re.sub("(\w+)","\\1_3",ins)
	out=re.sub("(\w+)\s*\n\s*(\w+)","\\1,\n\\2",out);#add comma where necessary
	print out

print ");"

wires=re.findall("\s+wire\s+[^;]+;",orig);
for i in wires:
	ins=re.sub("^\s+wire","",i)
	bus=re.findall("\[[^\[\]]+\]",ins)
	#print bus
	busstr=""
	if (bus!=[]): 
		ins=ins.replace(bus[0],"")
		busstr=bus[0];
	out="wire "+busstr+re.sub("(\w+)","\\1_1",ins)
	out=out+"\nwire "+busstr+re.sub("(\w+)","\\1_2",ins)
	out=out+"\nwire "+busstr+re.sub("(\w+)","\\1_3",ins)
	print out



instances = re.findall("(?s)(\w+\s+(#\([^#;]*?\))?\s*\w+\s+\([^;]*);",orig);
for i in instances:
	ins=i[0]
	header=re.findall("^(\w+\s*(#\(.*?\))?\s*\w+\s*\()",i[0]);
	name=re.findall("^\w+",header[0][0])[0]
	ins=ins.replace(str(header[0][0]),""); #delete header
	if (name in sys.argv): #not a _tri cell
		out=re.sub("(\w+)\s*\($","\\1_1 (",header[0][0])
		out=out+re.sub("\.(\w+)\s*\((\w+)(\[?\d*\:?\d*\]?\))",".\\1(\\2_1\\3",ins)
		out=out+";\n"+re.sub("(\w+)\s*\($","\\1_2 (",header[0][0])
		out=out+re.sub("\.(\w+)\s*\((\w+)(\[?\d*\:?\d*\]?\))",".\\1(\\2_2\\3",ins)
		out=out+";\n"+re.sub("(\w+)\s*\($","\\1_3 (",header[0][0])
		out=out+re.sub("\.(\w+)\s*\((\w+)(\[?\d*\:?\d*\]?\))",".\\1(\\2_3\\3",ins)
		out=out+";"
	else: #it's a _tri cell
		#print header[0]
		ins=re.sub("\s*\)\s*$","",ins); #delete trailing parenthesis
		out=re.sub("^(\w+)","\\1_tri",header[0][0])
		out=out+re.sub("\.(\w+)\s*\((\w+)(\[?\d*\:?\d*\]?\))",".\\1_1(\\2_1\\3",ins)
		out=out+re.sub("\.(\w+)\s*\((\w+)(\[?\d*\:?\d*\]?\))",".\\1_2(\\2_2\\3",ins)
		out=out+re.sub("\.(\w+)\s*\((\w+)(\[?\d*\:?\d*\]?\))",".\\1_3(\\2_3\\3",ins)
		out=re.sub("(?s)(\.\w+\([^);,]*\))\s+(\.\w+\([^);,]*\))","\\1,\n\t\t\\2",out)
		out=out+"\n\t);"
	print "\n"+out+"\n"

assigns = re.findall("(assign\s+\w+[^;]*;)",orig);
for i in assigns: 
	#print i
	i=re.sub("assign","",i);
	out="\nassign" + re.sub("([^'A-Za-z_0-9])([A-Za-z_]\w*)","\\1\\2_1",i);
	out=out + "\nassign" + re.sub("([^'A-Za-z_0-9])([A-Za-z_]\w*)","\\1\\2_2",i);
	out=out + "\nassign" + re.sub("([^'A-Za-z_0-9])([A-Za-z_]\w*)","\\1\\2_3",i);
	for p in parameters: out=re.sub("(\W)"+p+"_[123](\W)","\\1"+p+"\\2",out);
	print out


print "endmodule"


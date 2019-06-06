#!/usr/bin/env python2

from optparse import *
from vp import *
import glob
import os

import fnmatch
import os


import re
import sys

def fgrep(fname,str):
    file = open(fname, "r")
    for line in file:
        if re.search(str, line):
              return 1
    return 0



class VerilogParserInstance(VerilogParser):
    def __init__(self):
        VerilogParser.__init__(self)

    def instance(self,indentLen=2,sort=0, group=1,tmr=0, show_parameters=0):
        o=self.module_name+" "

        if show_parameters and self.parameters:
            o+="(\n"
            if sorted:
                parameters=sorted(self.parametersList)
            else:
                parameters=self.parametersList

            for parameter in parameters:
                comma=","
                if parameter==parameters[-1]: comma=""
                o+=".%s(%s)%s\n"%(parameter,self.parameters[parameter],comma)
            o+=")\n"
        def tmrName(name):
            return (name+"A", name+"B", name+"C")
        def addGroup(portList, comment=""):
            outStr=""
            if comment and len(portList):
                outStr+="// %s\n"%comment
            for port in portList:
                outStr+=".%s(%s),\n"%(port,port)
            return outStr

        o+="%s1 (\n"%(self.module_name.upper())

        if group:
            inputs= [port for port in self.portList if port in self.inputs]
            outputs=[port for port in self.portList if port in self.outputs]
            inouts= [port for port in self.portList if port in self.inouts]

            if sort:
                inputs=sorted(inputs)
                outputs=sorted(outputs)
                inouts=sorted(inouts)
            if tmr:
                inputs =  [p for port in inputs for p in tmrName(port)]
                outputs = [p for port in outputs for p in tmrName(port)]
                inouts =  [p for port in inouts for p in tmrName(port)]

            o+=addGroup(inputs,"inputs")
            o+=addGroup(outputs,"outputs")
            o+=addGroup(inouts,"inouts")
        else:
            # no grouping, use portList
            portList=self.portList
            if sort:
                portList=sorted(self.portList)
            if tmr:
                portList =  [p for port in portList for p in tmrName(port)]
            o+=addGroup(portList)
        o=o.rstrip() # remove last carriage return
        if o[-1:]==",":
            o=o[:-1]
            o+="\n"
        o+=");\n"

        outStr=""
        indentChr=" "
        indentStr = indentChr * indentLen
        outStr=indentStr + ('\n'+indentStr).join(o.split('\n'))
        #add additional indent

        indentStr2 = indentChr * (indentLen+2)
        outStr=outStr.replace(indentStr+".",indentStr2+".")
        outStr=outStr.replace(indentStr+"//",indentStr2+"//")
        print outStr
def insensitive_glob(pattern):
    def either(c):
        return '[%s%s]'%(c.lower(),c.upper()) if c.isalpha() else c
    return glob.glob(''.join(map(either,pattern)))

def readFile(fname):
    f=open(fname,"r")
    body=f.read()
    f.close()
    return body
def main():
    parser = OptionParser(version="%prog 1.0", usage="%prog [options] module")
    parser.add_option("", "--search-path",  dest="searchPath",   help="Search path (*.v)", default=".")
    parser.add_option("-s", "--sort",       dest="sort",       action="store_true", help="Sort port names", default=False)
    parser.add_option("-g", "--group",      dest="group",      action="store_true", help="Group port types together (input, outputs, inouts)", default=False)
    parser.add_option("-t", "--tmr",        dest="tmr",        action="store_true", help="Triplicate ports", default=False)
    parser.add_option("-p", "--parameters", dest="parameters", action="store_true", help="Add parameters", default=False)

    try:
      (options, args) = parser.parse_args()
      if len(args)!=1:
         parser.error("You have to specify module name!")

      module = args[0]
      pattern="*%s.v"%(module)

      for root, dirnames, filenames in os.walk(options.searchPath):
         for filename in fnmatch.filter(filenames, '*.v'):
           fn=(os.path.join(root, filename))
           m=fgrep(fn,module)
           if m:
               print "// %s"%fn
               vp=VerilogParserInstance()
               vp.parseString(readFile(fn))
               vp.instance(sort=options.sort, group=options.group, tmr=options.tmr, show_parameters=options.parameters)
    except ValueError:
        raise OptionValueError(
            "option %s: invalid complex value: %r" % (opt, value))
if __name__=="__main__":
    main()

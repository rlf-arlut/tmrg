#!/usr/bin/env python

from optparse import OptionParser
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
    def instance(self,indent=2):
        o=self.module_name+" "
        if self.parameters:
            o+="(\n"
            for p in self.parameters:
                o+=".%s(%s)\n"%(p,self.parameters[p])
            o+=")\n"
        o+="%s1 ("%(self.module_name.upper())
        def add_io(o,dict):
            for d in dict:
                o+=".%s(%s),\n"%(d,d)
            return o
        added=0
        o=add_io( o,self.inputs)
        o=add_io( o,self.outputs)
        o=add_io( o,self.inouts)

        o+=")\n"


        print o
def insensitive_glob(pattern):
    def either(c):
        return '[%s%s]'%(c.lower(),c.upper()) if c.isalpha() else c
    return glob.glob(''.join(map(either,pattern)))

def main():
    parser = OptionParser(version="%prog 1.0")
    parser.add_option("", "--search-path",   dest="searchPath",   help="Search path (*.v)", default=".")
    (options, args) = parser.parse_args()
    if len(args)!=1:
        print "Module name is missing!"
        return

    module = args[0]
    pattern="*%s.v"%(module)

    for root, dirnames, filenames in os.walk(options.searchPath):
       for filename in fnmatch.filter(filenames, '*.v'):
            fn=(os.path.join(root, filename))
            m=fgrep(fn,module)
            if m:
                print "// %s"%fn
                vp=VerilogParserInstance()
                f=open(fn,"r")
                body=f.read()
                f.close()
                print body
                vp.parseString(body)
                vp.instance()

if __name__=="__main__":
    main()
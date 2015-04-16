#!/usr/bin/env python
import sys
from optparse import OptionParser
import pdb
import time
import pprint
import sys
import functools
from pyparsing import *
import pyparsing


def main():
    if len(sys.argv)<2:
        print './prog filename'
        return
    f=open(sys.argv[1])
    mod=0
    for l in f.readlines():
        if l.find("module")==0:
            name=l.split()[1]
            mod=1
            if name.find("(")>0:
                name=name[:name.find("(")]
            f=open("source/%s.v"%name,"w")
        if mod:
            f.write(l)

        if l.find("endmodule")==0:
            mod=0
            f.close()
    f.close()

if __name__=="__main__":
    main()

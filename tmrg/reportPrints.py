#!/usr/bin/env python
import glob

def main():
    for fname in "tbg.py tmrg.py verilogParser.py verilogElaborator.py".split():
        f=open(fname,"r")
        for l in f.readlines():
            if l.find(" print ")>=0:
                if l.find("#")>=0 and (l.find("#")<l.find("print")): continue
                print(fname,l.rstrip())
        f.close()
if __name__=="__main__":
    main()

#!/usr/bin/env python

def loadLEF(fname):
  f=open(fname,"r")
  cells={}
  macro=0
  name=""
  for l in f.readlines():
    l=l.lstrip()
    ll=l.split()
    if len(ll)<1: continue
    key=ll[0]
    if key=="MACRO":
      name=l.split()[1]
      macro={}
    elif key=="SIZE":
      print(name,float(ll[1])*float(ll[3]))
    if l.find("MACRO %s"%name)>=0:
      macro=None
  f.close()
  return cells
if __name__=="__main__":
  lef=loadLEF("CORELIB.lef")
  print(len(lef))

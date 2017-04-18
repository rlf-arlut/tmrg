#!/usr/bin/env python
import os
import sys
os.system("git log --all --stat > /tmp/log.txt")
f=open("/tmp/log.txt")
IDLE,COMMIT,DATE,STATS=range(4)
state=IDLE
history={}

m2int={
"Apr": 4,
"Aug": 8,
"Dec": 12,
"Feb": 2,
"Jan": 1,
"Jul": 7,
"Jun": 6,
"Mar": 3,
"May": 5,
"Oct": 10,
"Nov": 11,
"Sep": 9
}
month=0
year=0
for l in f.readlines():
    if l.find("commit")>=0:
        pass
    elif l.find("Date")>=0:
        ll= l.split()
        year=int(ll[5])
        month=m2int[ll[2]]
        if not year in history:
            history[year]={}
        if not month in history[year]:
            history[year][month]={"events":0,"lines":0,"files":0}
        history[year][month]["events"]+=1
    elif l.find("files changed")>=0:
        try:
            ll=l.split()
            #print ll
            files=int(ll[0])
            lines=int(ll[3])
        #    if len(ll)>5:
        #        lines+=int(ll[5])
        except:
            pass #print l
        finally:
            #print files,lines
            history[year][month]["files"]+=files
            history[year][month]["lines"]+=lines
f.close()

f=open("history.dat","w")
for year in sorted(history):
    for month in range(1,13):
        v="0 0 0"
        if month in  history[year]:
            v="%d %d %d"%(history[year][month]["events"],history[year][month]["files"],history[year][month]["lines"])
        f.write("%4d %2d %s\n"%(year, month, v))
f.close()

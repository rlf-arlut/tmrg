#!/usr/bin/env python
import logging
from toolset import tmrg_version
import os

def replaceStrInFile(fname,fromStr,toStr):
    f=open(fname,"r")
    logging.info("%s %s->%s"%(fname,fromStr,toStr))
    body=""
    for l in f.readlines():
        nl=l.replace(fromStr,toStr)
        body+=nl
    f.close()

    f=open(fname,"w")
    f.write(body)
    f.close()

def main():
    version=tmrg_version()
    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)
    logging.info("Version : %s"%version)
    fname="tmrg.tgz"#%version

    logging.info("Replace")
    #replaceStrInFile("../tags/%s/doc/source/conf.py"%tag,"[trunk]","[%s]"%tag)
    replaceStrInFile("./tmake/toolset.py",'tmrg_version.str=""','tmrg_version.str="%s"'%version)

    logging.info("make html")
    os.system("cd doc ; make html")
    logging.info("make pdf")
    os.system("cd doc ; make latexpdf")
    logging.info("copy html")
    os.system("mv doc/build/html doc/")
    os.system("mkdir doc/pdf")
    os.system("mv doc/build/latex/tmrg.pdf doc/pdf")
    logging.info("tar")
    cmd="""cd .. ; tar --exclude='activity.py' --exclude='fastLefParser.py' --exclude='top.py' --exclude='*.pyc' --exclude='*~' \
          --exclude='reportPrints.py' --exclude='scanExamples.py'  --exclude='sdf.py' --exclude='spliter.py' --exclude="rc" \
          --exclude="examples/doc"  --exclude="examples/*.py" --exclude="examples/*.cnf" \
          -cvzf  %s tmrg/doc/html tmrg/doc/pdf tmrg/src tmrg/etc tmrg/common tmrg/bin tmrg/examples  tmrg/README.md tmrg/LICENSE && mv %s tmrg"""%(fname,fname)
#    print cmd
    os.system(cmd)
    logging.info("File %s"%(fname))
    logging.info("File size :%.1f kB"%(float(os.path.getsize(fname))/(1024)))
    return


if __name__=="__main__":
    main()

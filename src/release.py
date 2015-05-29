#!/usr/bin/env python
import pysvn
import logging




def svnStatusGood(client):
    changes = client.status('.')

    res=1
    toBeAdded = [f.path for f in changes if f.text_status == pysvn.wc_status_kind.added]
    if len(toBeAdded):
        logging.error( 'Files to be added: '+" ".join(toBeAdded))
        res=0

    toBeRemoved = [f.path for f in changes if f.text_status == pysvn.wc_status_kind.deleted]
    if len(toBeRemoved):
        logging.error( 'Files to be removed: '+" ".join(toBeRemoved))
        res=0

    modified = [f.path for f in changes if f.text_status == pysvn.wc_status_kind.modified]
    if len(modified):
        logging.error( 'Files that have changed: '+" ".join(modified))
        res=0

    conflicts = [f.path for f in changes if f.text_status == pysvn.wc_status_kind.conflicted]
    if len(conflicts):
        logging.error( 'Files with merge conflicts: '+" ".join(conflicts))
        res=0
    unversioned =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.unversioned]
    if len(unversioned):
      logging.warning( 'unversioned files: '+" ".join(unversioned))
    return res

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

def main2():
    tag="0.1.1"
    client = pysvn.Client()

    logging.basicConfig(format='[%(levelname)-7s] %(message)s', level=logging.INFO)
    logging.info("TAG : %s"%tag)
    logging.info("SVN: check status")
    if not svnStatusGood(client):
        print "exit"
        return
    log_message = "[tag] Tag %s created"%(tag)
    def get_log_message():
       return True, log_message
    client.callback_get_log_message = get_log_message

    _from='svn+ssh://skulis@svn.cern.ch/reps/tmrg/trunk'
    _to='svn+ssh://skulis@svn.cern.ch/reps/tmrg/tags/%s' % tag
    logging.info("SVN: copy %s %s"%(_from,_to))
    client.copy( _from, _to )

    logging.info("SVN: update ../tags")
    client.update('../tags')

    for dir in ("img","tests"):
        client.remove('../tags/%s/%s'%(tag,dir))

    logging.info("Replace")
    replaceStrInFile("../tags/%s/doc/source/conf.py"%tag,"[trunk]","[%s]"%tag)
    replaceStrInFile("../tags/%s/src/toolset.py"%tag,'return "trunk"','return "%s"'%tag)
    logging.info("SVN: commit ./tags")
    client.checkin(["../tags/%s"%tag], '[tag] tuning for tag %s'%tag)

    _from='../tags/%s'%tag
    _to='../rel/tmrg-%s'%tag
    logging.info("SVN: export %s %s"%(_from,_to))
    client.export(_from, _to)

    logging.info("make html")
    os.system("cd ../tags/%s/doc ; make html"%tag)
    logging.info("copy html")
    os.system("cp -r ../tags/%s/doc/build/html ../rel/tmrg-%s/doc/build"%(tag,tag))
    logging.info("tar")
    os.system("cd ../rel/ ; tar -cvzf tmrg-%s.tgz tmrg-%s"%(tag,tag))

    logging.info("File tmrg-%s.tgz"%(tag))
    logging.info("File size :%.1f"%(float(os.path.getsize('../rel/tmrg-%s.tgz'%(tag)))/(1024*1024)))
    f=open("tmrg.pass","r")
    sshpassword=f.read()
    f.close()

    os.system("sshpass -p '%s' ssh tmrg@lxplus mkdir ./www/releases/%s"%(sshpassword,tag))
    os.system("sshpass -p '%s' scp -r ../rel/tmrg-%s/doc/build/html/* tmrg@lxplus:./www/releases/%s"%(sshpassword,tag,tag))
    os.system("sshpass -p '%s' scp -r ~/work/tmrg/rel/tmrg-%s.tgz tmrg@lxplus:./www/releases/"%(sshpassword,tag))

if __name__=="__main__":
    main()




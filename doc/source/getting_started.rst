Getting started
###############

Installation
============

From the SVN repository
-----------------------

The TMRG project is stored in CERN SVN. 


#. Fetch the repository::

    svn checkout svn+ssh://USER@svn.cern.ch/reps/tmrg/trunk tmrg


#. Enter the directory::

    cd tmrg


#. Try to run an example::

    ./tmrg.py -t examples/fsm02.v


#. You may also want to change you enviroment::

    export PATH=/path/to/tmrg:$PATH

MIC cluster
-----------

If you are using mic cluster @CERN, you can use an instalation from 

/homedir/skulis/tmrg/trunk


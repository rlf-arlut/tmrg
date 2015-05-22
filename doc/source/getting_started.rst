Getting started
###############

Installation
============

The TMRG tool set does not really require installation. It is a set of python scripts.
It is enough to download it, extract and set a system PATH to point on the bin directory.

Getting source code from the SVN repository
-------------------------------------------

The source of TMRG project is stored in CERN SVN. To fetch the source code from the SVN repository one has to:

.. code-block:: bash

    $ svn checkout svn+ssh://USER@svn.cern.ch/reps/tmrg/trunk tmrg

To start using TMRG it is enough to source the environment file

.. code-block:: bash

    $ source etc/tmrg.sh

MIC cluster
-----------

If you are using mic cluster @CERN, you can use an installation from  ``/homedir/skulis/tmrg/trunk`` by sourcing:

.. code-block:: bash

    $ source /homedir/skulis/tmrg/trunk/etc/tmrg.sh

Triplicating first design
=========================

There are many examples distributed with the source code in ``examples`` directory.
You may copy one of them. For the purpose of this tutorial, you may create a file ``dff.v`` which should contain

.. code-block:: verilog
   :linenos:

   module dff(d,c,q);
     // tmrg default triplicate
     input d,c;
     output q;
     reg q;
     wire dVoted=d;
     always @(posedge c)
       q<=dVoted;
   endmodule

This file models a simple ``D`` flipflop active on a rising edge of signal ``c``.
Do not worry if you do not understand everythin in the code above, you will find a detailed explanation of possible syntax in section :ref:`constraining_the_design`.
To triplicate the code it is enough to call 

.. code-block:: bash

    $ tmrg dff.v

You should see nothing, which means that script finished successfully without any errors.
As a result of script operation a file ``dffTMR.v`` should be created in a current directory. 
The file contains  (please review it!) fully triplicated, synthesizable module.

Synthesizing the design
=======================

Place and route the design
==========================

Simulation
==========

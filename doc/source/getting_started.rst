Getting started
###############

.. _installation:

Installation
============

The TMRG toolset does not really require installation. It is a set of python scripts.
It is sufficient to download it, extract it, and set a system PATH to point to the bin directory.

Getting source code from the GIT repository
-------------------------------------------

The TMRG project source is stored in CERN GIT repository. To fetch the source code from the repository one has to use the command:

.. code-block:: bash

    $ git clone https://:@gitlab.cern.ch:8443/skulis/tmrg.git

    $ git clone https://skulis@gitlab.cern.ch/skulis/tmrg.git

    $ git clone ssh://git@gitlab.cern.ch:7999/skulis/tmrg.git

for ``kerberos``, ``https``, or ``ssh`` authorization method respectively.

To start using the TMRG it is enough to source the environment file:

.. code-block:: bash

    $ source etc/tmrg.sh

MIC cluster
-----------

If you are using mic cluster @CERN, you can use an installation from  ``/homedir/skulis/tmrg/``.
Bash users should source:

.. code-block:: bash

    $ source /homedir/skulis/tmrg/etc/tmrg.sh

while, tcsh users should source:

.. code-block:: bash

    $ source /homedir/skulis/tmrg/etc/tmrg.csh

Getting help
=============

If you want to see how to use the TMRG you can run:

.. code-block:: bash

    $ tmrg -h

which will show a summary of available options. If you want to read the user manual you can run:

.. code-block:: bash

    $ tmrg --doc

which should open the manual in the web browser.

Triplicating first design
=========================

There are many examples distributed with the source code in ``examples`` directory.
You can copy one of them. For the purpose of this tutorial, you should create a file ``dff.v`` which should contain:

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
Do not worry if you do not understand everything in the code above, you will find a detailed explanation of possible syntax in the section :ref:`constraining_the_design`.
To triplicate the code it is enough to call:

.. code-block:: bash

    $ tmrg dff.v

You should see nothing, which means that the script finished successfully without any errors.
As a result of the script operation a file ``dffTMR.v`` should be created in the current directory. 
The file contains  (please review it!) a fully triplicated, synthesizable module.


In the next step you should implement and verify the design. The TMRG tool assists with this steps as well.
For more details please refer :ref:`implementation` and  :ref:`verification` sections.


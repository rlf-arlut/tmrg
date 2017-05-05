Triple Modular Redundancy Generator
###################################

This website describes the **Triple Modular Redundancy Generator** tool.
The TMRG toolset assists in the process of creating digital designs immune 
to single event upsets. The immunity is provided by means of triple modular 
redundancy. 

.. note:: Before you start reading further, you should understand the purpose of 
   the tool. The TMRG tool **IS NOT** a single button solution which will make
   your CHIP / FPGA design safe from single event upsets. You, as a designer, have to know which
   parts of your circuits should (have to) be protected. The TMRG tool will save
   you the time needed for copy-pasting your code and will minimize probability
   that you will forget to change some postfix in your triplicated variable
   names. It will also simplify the physical implementation and verification
   process by providing some routines. 

.. note:: The TMRG tool is open source, however, it **CAN NOT**  be made publicly available. 
   By downloading the code, you become **RESPONSIBLE** for protecting it.
   For more details please refer :ref:`licesing`.

.. note:: 
   `TMRG introduction presentation <http://cern.ch/tmrg/html/tmrg_introduction.pdf>`_ [PDF] Presented on 12 June 2015.


Content:


.. toctree::
   :maxdepth: 2

   flow
   getting_started
   triplication
   implementation
   verification
   faq
   license

Quick links:
  * gitlab page: https://gitlab.cern.ch/skulis/tmrg
  * ``git clone https://:@gitlab.cern.ch:8443/skulis/tmrg.git``

..   general_assumptions
..   synthesis_tests
..   examples


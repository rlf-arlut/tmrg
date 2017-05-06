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

**Content**:

.. toctree::
   :maxdepth: 2

   flow
   getting_started
   triplication
   implementation
   verification
   faq
   license


**Other resources**:

  * `Single Event Upsets mitigation techniques [PDF] <https://indico.cern.ch/event/465343/>`_, EPE-ESE seminar Tuesday 12 Apr 2016
  * `Single Event Effects mitigation with TMRG tool <http://iopscience.iop.org/article/10.1088/1748-0221/12/01/C01082/meta>`_, Journal of Instrumentation, Volume 12, January 2017 


**Quick links**:

  * gitlab page: https://gitlab.cern.ch/skulis/tmrg
  * ``git clone https://:@gitlab.cern.ch:8443/skulis/tmrg.git``
  * `PDF version of this document  <https://tmrg.web.cern.ch/tmrg/html/tmrg.pdf>`_
  * `TMRG toolset  <https://tmrg.web.cern.ch/tmrg/html/tmrg.tgz>`_ (soruce, doc, examples)

..   general_assumptions
..   synthesis_tests
..   examples


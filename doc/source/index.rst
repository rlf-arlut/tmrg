Triple Modular Redundancy Generator
###################################

This website describes the **Triple Modular Redundancy Generator** tool.

.. note:: Before you start reading further, you should understand the purpose of the tool. 
   The TMRG tool **is not** a single button solution which will make you CHIP / FPGA design SEU proof.
   You, as a designer, have to know which parts of your circuits should (have to) be protected. 
   The TMRG tool will save you some time needed for copy-pasting your code and will minimize probability that you will forget to change some postfix in your triplicated variable names. 
   It will also simplify verification process by providing some routines. 


Content:

.. toctree::
   :maxdepth: 2

   general_assumptions
   installation
   getting_started
   triplication
   implementation
   verification

..   synthesis_tests
..   examples


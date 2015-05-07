General Assumptions
*******************

.. warning:: Before you start reading further, you should understand the purpose of the tool. 
   The TMRG tool **is not** a single button solution which will make you CHIP / FPGA design SEU proof.
   You, as a designer, have to know which parts of your circuits should (have to) be protected. 
   The TMRG tool will save you some time needed for copy-pasting your code and will minimize probability that you will forget to change some postfix in your triplicated variable names. 
   It will also simplify verification process by providing some routines. 



Specification
-------------

  1) tool should be able to transform the whole project (e.g. macro cell like i2cSlave) (Not single modules only). 
     The input project files should be normal verilog which can be simulated and synthesized.
  2) triplication should be done on RTL level
  3) tool should generate one output module for each input module. This requirement has some consequences: imagine that you have a module, like a simple added, which you are using in various places across your design. If you want to obtain various levels of protection in various places (e.g. full triplication in FSM, no protection on a data path) you have to create two identical modules (with different names) in the source project.
  4) triplication should be possible only for given signals/instances (while leaving others not touched)
      - specification of these should be done via pragmas in the source code or in the configuration file (similarly to RTL compiler)
      - "conversion" between triplicated and non triplicated signals should be handled automatically by means of fanout and voters
      - it should be possible to add voter anywhere (also on combinatorial signals)
      - designer should be able to access individual signals of the triplicated net (power on reset, clock gating)
  4) error output from majority voters should be available for the designer. This output can be used for a clock gating, error counting, or others.

..  4) (too some extend) understand the circuit (detect whether logic is combinatorial or sequential)
..      - the goal is not to write synthesizer which understand all possible cases
..      - simple approach: use blocking assignments for combinatorial logic and non blocking assignments for sequential logic
..      - defining common coding standard for FSM is not strictly necessary, but function to recognize and transform each type of coding has to be added and tested. 

Using this approach is more power full that triplicating the output netlist. 
It is much easier to guide the tool which wires/instances should be triplicated and which should be not. More over this approach allows to access to error output and to modify the circuit operation accordingly (which is very difficult at the nestlist level). 

.. FSM implementation
.. ^^^^^^^^^^^^^^^^^^

.. As it has been disused in section :ref:`sec-fsm-triplication`, triplication at
.. the output and triplication at the output of the register is possible. 
.. To keep implementation similar for FSM and data path, the triplication at 
.. the register input is chosen. 

.. Recommendation for FSM coding style:

.. .. code-block:: verilog
.. 
..    module fsm(in1, in2, out1, clk, rst);
..      input in1,in2,clk,rst;
..      output out1;
..      reg out1,out1next;
..      
..      always 
..        if (in1)
..          out1next= ~in2;
..        else
..          out1next=in1 ^ out1;
..      
..      always @(posedge clk or posedge rst)
..      begin
..        if (rst)
..          out1<=1'b0;
..        else
..          out1<= out1next;
..      end
..    endmodule

.. Other remarks
.. ^^^^^^^^^^^^^

..   1) keep verilog code clean and simple. e.g. DO NOT introduce unnecessary temporary variables, like::

..        module moduleOut(in1, in2, out1);
..          input in1,in2;
..          output out1;
..          reg out1,out1next;
..          wire tmp;
..          assign tmp=in1;
..          moduleIn instIn( .in1(tmp), .in2(in2), .out1(out));
..        endmodule
   
..      Tool will not crash because of that, however propagation of properties (like do not triplicate) may not work properly (as stated above, the goal of the project is not writing full blown synthesizer). 
   
Proposed approach
-----------------
The process of triplicating verilog code can be divided in following steps:
  1) parsing input files
       **input:** verilog code

       **output:** list of tokens
  2) analysis of the tokens (within the proper context)
       **input:** tokens

       **output:** list of module inputs, outputs, registers, instances, always blocks, ...
  3) application of constrains from the verilog code and configuration file (like do_not_triplicate directive)
  4) triplication
       **input:** tokens

       **output:** tokens
  5) generation verilog code
       **input:** tokens

       **output:** verilog code

Advantages of proposed approach
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  1) at the each processing step we have information about the context of the expression. 

     For example, expression ``input [7:0] bus;`` can be used in module declaration as well as in the task header. In the second case, it should not be triplicated.
  2) indication of invalid/confusing syntax which may lead to undesired results
  3) not sensitive to variable names, any name convention can be applied without risk of misunderstanding the design

.. How triplication is implemented
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. For each functional block we have a callback. 
.. The naive implementation of triplication may look like:

.. .. code-block:: verilog

..    def tmrModule(tokens):         <- tokens from the source code
..      return tokens+tokens+tokens  <- tokens for output code

Side benefits
^^^^^^^^^^^^^

By implementing this strategy, one can (relatively easy) get two other tools:
  1) executing steps 1) and 5) one can obtain "formatter" of the verilog code (uniformity of the code across the project). See :ref:`exaple_verilog_formatting`.
  2) easy to generate HTML documentation (with clickable references to modules and variables). 



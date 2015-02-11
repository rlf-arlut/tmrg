General Assumptions
*******************

Specification
-------------
The tool/flow should:
  1) be able to transform the whole project (e.g. macro cell like ePortRx)
  2) allow to not triplicate given signals / components 
      - specification of these should be done by command line parameters of pragmas in source code
      - information about non triplicated nets should be propagated across the hierarchy
  3) generate one output file(module) for each input file(module) (ePortRx -> ePortRxTMR)
  4) (too some extend) understand the circuit (detect whether logic is combinatorial or sequential)
      - the goal is not to write synthesizer which understand all possible cases
      - simple approach: use blocking assignments for combinatorial logic and non blocking assignments for sequential logic
      - defining common coding standard for FSM is not strictly necessary, but function to recognize and transform each type of coding has to be added and tested. 
  


FSM implementation
^^^^^^^^^^^^^^^^^^

As it has been disused in section :ref:`sec-fsm-triplication`, triplication at
the output and triplication at the output of the register is possible. 
To keep implementation similar for FSM and data path, the triplication at 
the register input is chosen. 


Recommendation for FSM coding style:

.. code-block:: verilog

   module fsm(in1, in2, out1, clk, rst);
     input in1,in2,clk,rst;
     output out1;
     reg out1,out1next;
     
     always 
       if (in1)
         out1next= ~in2;
       else
         out1next=in1 ^ out1;
     
     always @(posedge clk or posedge rst)
     begin
       if (rst)
         out1<=1'b0;
       else
         out1<= out1next;
     end
   endmodule


Proposed approach
-----------------
Flow steps:
  1) parsing input files
       **input:** verilog code
       **output:** list of tokens
  2) analysis of the tokens (within the proper context)
       **input:** tokens
       **output:** list of module inputs, outputs, registers, instances, always blocks, ...
  3) application of constrains (like do_not_triplicate directive)
  4) triplication
       **input:** tokens
       **output:** tokens
  5) generation verilog code
       **input:** tokens
       **output:** verilog code

Advantages of proposed approach
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  1) at each processing step we have information about the context of the expression. 
      For example, expression ``input [7:0] bus;`` can be used in module declaration or in the task header. In the second case, it should not be triplicated.
  2) indication of invalid/confusing syntax


How triplication is implemented
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For each functional block we have a callback. 
The naive implementation of triplication may look like:

.. code-block:: verilog

   def tmrModule(tokens):         <- tokens from the source code
     return tokens+tokens+tokens  <- tokens for output code



Side benefits
-------------
By implementing this strategy, one can (relatively easy) get two other tools:
  1) executing steps 1) and 5) one can obtain "formatter" of the verilog code (uniformity of the code across the project)
  2) easy to generate HTML documentation (with clicable references to modules and variables). 

Examples
********

Input file
----------

.. code-block:: verilog

   module tmr(in1, in2, out1, clk, rst);  input in1,in2,clk,
   rst; output out1; reg out1; always @(posedge clk or 
   posedge rst) begin if (   rst)       out1<=1'b0; else out1
   <= in1 & (in2 ^ out1);  end endmodule
   
Analysis
--------

.. code-block:: verilog

   ##########################################################################################
   # Inputs                                             |         type         |    tmr     #
   ##########################################################################################
   | rst                                                |                      |     0      |
   | in1                                                |                      |     0      |
   | in2                                                |                      |     0      |
   | clk                                                |                      |     0      |
   ##########################################################################################
   # Outputs                                            |         type         |    tmr     #
   ##########################################################################################
   | out1                                               |                      |     0      |
   ##########################################################################################
   # Registers                                          |         type         |    tmr     #
   ##########################################################################################
   | out1                                               |                      |     0      |
   ##########################################################################################
   # Non Blocking                                                                           #
   ##########################################################################################
   | out1                                                                                   |
   +----------------------------------------------------------------------------------------+

Output file (non triplicated)
-----------------------------

.. code-block:: verilog

   // file automaticly generated
   module tmr(
     in1,
     in2,
     out1,
     clk,
     rst
   );
   input in1;
   input in2;
   input clk;
   input rst;
   output out1;
   reg out1;

   always @(posedge clk or osedge rst )
     begin
       if (rst)
         out1 <= 1'b0;
       else
         out1 <= in1&(in2^out1);
     end
   endmodule



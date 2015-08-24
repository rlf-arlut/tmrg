`define XXX 1'b1
`include "x.v"
module test;
  reg x;
  always @*
    x= `XXX;
endmodule

module mlogic (I,ZN);
  // tmrg default triplicate
  input  I;
  output ZN;
  assign ZN=~I;
endmodule

`timescale s10n/s10p
`include "dsad.v"
module inst03 (in,out);
  // tmrg default triplicate
  input in;
  output out;
  // tmrg do_not_triplicate in2s
  reg in2;
`ifdef FIRST
  reg in3;
`endif
  mlogic logic01(.I((in|in2)&in3|1'b1),.ZN(out));
endmodule

`timescale 10 ns /10 ps 
// `include "mux.v" does not work for automatic testing because of paths

module mlogic (I,ZN);
  // tmrg default triplicate
  input  I;
  output ZN;
  assign ZN=~I;
endmodule


module inst03 (in,out);
  // tmrg default triplicate
  input in;
  output out;
  // tmrg do_not_triplicate in2s
  reg in2;
`ifdef FIRST
  reg in3;
`endif
  mlogic logic01(.I(1'b1),.ZN(out));
endmodule

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
  reg in3;
  mlogic logic01(.I((in|in2)&in3|1'b1),.ZN(out));
endmodule

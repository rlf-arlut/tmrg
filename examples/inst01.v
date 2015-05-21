module logic(I,ZN);
  // tmrg do_not_touch
  input I;
  output ZN;
  assign ZN=~I;
endmodule

module inst01 (in,out);
  // tmrg default triplicate
  input in;
  output out;
  logic logic01(.I(in),.ZN(out));
endmodule

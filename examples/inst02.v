module mlogic(I,ZN);
  // tmrg do_not_touch
  input I;
  output ZN;
  assign ZN=~I;
endmodule

module inst02 (in,out);
  // tmrg default triplicate
  // tmrg do_not_triplicate logic01
  input in;
  output out;
  mlogic logic01(.I(in),.ZN(out));
endmodule

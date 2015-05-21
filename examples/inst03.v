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
  mlogic logic01(.I(in),.ZN(out));
endmodule

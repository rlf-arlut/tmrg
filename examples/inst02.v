module inv(I,ZN);
  // tmrg default do_not_triplicate
  input I;
  output ZN;
  assign ZN=~I;
endmodule

module inst02 (in,out);
  // tmrg default triplicate
  input in;
  output out;
  inv inv01(.I(in),.ZN(out));
endmodule

module inv(I,ZN);
  // tmrg default triplicate
  input I;
  output ZN;
  assign ZN=~I;
endmodule

module inst01 (in,out);
  // tmrg default triplicate
  input in;
  output out;
  inv inv01(.I(in),.ZN(out));
endmodule

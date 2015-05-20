
module inst03 (in,out);
  // tmrg default triplicate
  input in;
  output out;
  inv inv01(.I(in),.ZN(out));
endmodule

module inv (I,ZN);
  // tmrg do_not_touch
  input  I;
  output ZN;
endmodule

module inst04 (in,out);
  // tmrg default triplicate
  // tmrg do_not_triplicate inv01
  input in;
  output out;
  inv inv01(.I(in),.ZN(out));
endmodule

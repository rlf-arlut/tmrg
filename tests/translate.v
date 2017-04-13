module translate_test(
  input i1,
  input [1:0] i2,i3,
  output x);
  // tmrg translate off
  assign x=|i1 & ^i3;
  // tmrg translate on
endmodule


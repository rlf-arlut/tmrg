module submodule (
  input i,
  output z
);
  // tmrg tmr_error true
  wire i_voted = i;
  assign z = i_voted;
endmodule

module topmodule (
  input i,
  output z
);
  submodule submodule_inst (.i(i), .z(z));
endmodule



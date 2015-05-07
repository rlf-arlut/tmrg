module comb05 (in,out);
  // tmrg default triplicate
  // tmrg do_not_triplicate combLogic
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

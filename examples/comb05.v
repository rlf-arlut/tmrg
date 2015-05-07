module comb05 (in,out);
  // tmrg default do_not_triplicate
  // tmrg triplicate combLogic
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

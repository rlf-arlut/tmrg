module comb03 (in,out);
  // tmrg default triplicate
  // tmrg do_not_triplicate in
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

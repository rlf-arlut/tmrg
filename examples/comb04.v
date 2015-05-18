module comb04 (in,out);
  // tmrg default triplicate
  // tmrg do_not_triplicate out
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

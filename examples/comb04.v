module comb04 (in1,in2,out1,out2);
  // tmrg default triplicate
  // tmrg do_not_triplicate out
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

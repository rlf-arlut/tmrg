module comb02 (in,out);
  // tmrg default triplicate
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

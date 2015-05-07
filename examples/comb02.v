module comb02 (in1,in2,out1,out2);
  // tmrg default triplicate
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

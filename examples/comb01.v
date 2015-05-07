module comb01 (in,out);
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in1;
  assign out = combLogic;
endmodule

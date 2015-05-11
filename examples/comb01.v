module comb01 (in,out);
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

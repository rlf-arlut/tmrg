module comb03 (in,out);
  // tmrg default triplicate
  // tmrg do_not_triplicate in
  input [7:0] in;
  output out;
  reg combLogic;
  always @(in)
    if (in)
      combLogic = 1'b0;
    else
      combLogic = 1'b1;
  assign out = combLogic;
endmodule

module test(input clk, input [1:0] din);
  // tmrg default do_not_triplicate
  reg r1,r2;
  always @(clk)
    {r1,r2}=din;
endmodule

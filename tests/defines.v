`define XXX 1'b1

module test;
  reg x;
  wire y;
  always @*
    x = y+ `XXX;
endmodule

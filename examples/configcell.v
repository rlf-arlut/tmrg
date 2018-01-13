module configCell(
  input [7:0]  din,
  input        clk,
  input        load,
  output [7:0] q
);
  // tmrg default triplicate
  wire tmrError=1'b0;

  reg [7:0]  mem;
  reg [7:0]  memNext;
  wire [7:0] memNextVoted=memNext;

  wire clkInt=clk|tmrError;

  always @(load or d or q)
    if (load)
      memNext=din;
    else
      memNext=mem;

  always @(posedge clkInt)
    mem <= memNextVoted;

  assign q=mem;
endmodule

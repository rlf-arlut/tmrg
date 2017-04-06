module al(input clk,input d, output reg q);
always @(posedge clk, d)
  q<=d;

always @(clk, posedge clk)
  q<=d;

always @*
  q=d;

endmodule

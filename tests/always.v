module al(input clk,input d, output reg q);
always @(posedge clk)
  q<=d;

always @(clk)
  q<=d;

always @*
  q=d;

endmodule

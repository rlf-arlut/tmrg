module al(input clk,input d, output reg q, input rst);
always @(posedge clk, d)
  q<=d;

always @(clk , posedge clk)
  q<=d;

always @(posedge clk , negedge rst)
  q<=d;

always @*
  q=d;

always @(*)
  q=d;

endmodule

module al(input clk,input d, output reg q, input rst);
always @(posedge clk or negedge rst)
  q<=d;

always @(clk or negedge d)
  q<=d;

always @(clk)
  q<=d;

always @(clk or d)
  q<=d;

always @*
  q=d;

always @(*)
  q=d;

endmodule

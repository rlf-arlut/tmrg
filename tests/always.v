module al(input clk,input d, output q);
always @(posedge clk)
  d<=q;

always @(clk)
  d<=q;

always @*
  d<=q;

endmodule

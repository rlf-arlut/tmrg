module assigment(input clk);
 reg [7:0] x;
 reg [6:0] y;
 
 always @(clk)
   y[2:1]<=x[3:2];

 always @(clk)
   y[4+:2]<=x[5+:2];

 always @(clk)
   y[2:1] = #1 x[3:2];

 localparam DEL=2;
 always @*
   y[4+:2] = #(DEL) x[5+:2];

 always @(clk)
  begin
   @(posedge clk);
   y =  x;
  end
endmodule

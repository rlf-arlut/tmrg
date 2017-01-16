module x;
 reg [7:0] x;
 reg [6:0] y;
 always @(x)
   y[1:2]<=x[0];
endmodule

module x;
 reg [3:0] x;
 reg [1:0] y;
 reg z;
 
 always @*
   if (x[y])
     z=1'b1;
 
endmodule

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

  wire z1;
  assign (supply0,weak1) #1 z1=x;

  // tmrg triplicate z2
  wire z2;
  assign (supply0,strong1) #1 z2=~x;

  // tmrg triplicate z2
  wor z3=z1^z2;

endmodule

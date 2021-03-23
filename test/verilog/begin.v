module test;
 reg y;
 integer i;
initial 
  begin: x
     y=1'b1;
  end

initial 
  begin
     y=1'b1;
  end
always @(y)
  for (i=0;i<9;i=i+1)
    begin
    end

always @(y)
  for (i=0;i<9;i=i+1)
    begin : x2
    end

endmodule

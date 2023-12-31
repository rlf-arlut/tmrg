
module anotherModule2 (
  input in1,
  output result
    );
assign result = ~in1;
endmodule


module anotherModule (
  input in1,
  input [7:0] in2,
  output result
    );
assign result = in1 | in2[2];
endmodule

module tmr2(in1, in2, out1, clk, rst);
  input in1,clk,rst;
  input [7:0] in2;
  output [7:0] out1;
  reg [7:0] out1;
  reg [7:0] out1next; // do_not_triplicate out1next 

 
  always @*
    begin
      if (in1)
        out1next = in2 ^ result2;
      else
        out1next = in2 ^ out1;
    end
    
  always @(posedge clk or posedge rst)
  begin
    if (rst)
      out1<=8'b0;
    else
      out1<= out1next;
  end
  
  wire result1,result2;
  
  anotherModule moduleInst(
    .in1(in1),
    .in2(in2),
    .result(result1)
    );

  anotherModule2 moduleInst2(
    .in1(result1),
    .result(result2)
    );

endmodule


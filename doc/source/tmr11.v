module tmr1(in1, in2, out1, clk, rst);
  input in1,in2,clk,rst;
  output reg out1;

  always @(posedge clk or posedge rst)
  begin
    if (rst)
      out1<=1'b0;
    else
      out1<= in1 & in2;
  end
endmodule


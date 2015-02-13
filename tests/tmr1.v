module tmr(in1, in2, out1, clk, rst);
  input in1,in2,clk,rst;
  output out1;
  reg [1:0] out1;
  reg out1next;

  always 
      out1next = in1 & (in2 ^ out1);
  
  always @(posedge clk or posedge rst)
  begin
    if (rst)
      out1 <= 1'b0;
    else
      out1 <= out1next;
  end
  //x
  
  //fds
endmodule


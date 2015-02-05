// comment
module test01( in, out );
  input [7:0] in;
  reg d;
  output [5:0] out; //comment
  parameter N=2;
  
  always @(posedge clk)
    begin
      x<=#NK 2;
    end
endmodule

// comment
module test01( in, out );
  input [7:0] in;
  reg d;
  output [5:0] out; //comment
  COUNT_BITS8 count_bits( .IN( in ), .C( out ) );
  always @(posedge clk)
    begin
      x<=#NK 2;
    end
endmodule

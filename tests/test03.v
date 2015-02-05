// comment
module test03( 
  input [7:0] in, 
  output out,
  inout [3:1] io
  );
  COUNT_BITS8 count_bits( .IN( in ), .C( out ) );
  reg [1:0] x;
  always @(posedge clk)
    begin
      x<=#NK 2;
    end
endmodule

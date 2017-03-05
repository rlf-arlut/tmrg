// comment
module COUNT_BITS8 #(parameter N=8)  ( input IN, output reg [N-1:0] C);
  always @(posedge IN)
    C<= #1 C+1;
endmodule

module test03( 
  input [7:0] in, 
  input [7:0] in2, 
  output [7:0] out,
  inout [3:1] io
  );
  // tmrg do_not_triplicate clk
  wire clk=|in;

  // tmrg do_not_triplicate clk2
  wire clk2;
  assign clk2=|in2;

  COUNT_BITS8 count_bits( .IN( clk ), .C( out ) );
  reg [1:0] x;
  localparam NK = 1;
  always @(posedge clk)
    begin
      x<=#NK 2;
    end
endmodule

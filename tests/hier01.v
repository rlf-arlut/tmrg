// comment
module hier01( 
  input  [7:0] in, 
  output [7:0] out
  );
  wire [7:0] tmp;
  comb00 c00( .in1( in ), .C( tmp ) );
  comb01 c01( .in2( tmp ), .C( out ) );
endmodule

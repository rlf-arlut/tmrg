//-----------------------------------------------------
// Design Name : decoder_using_assign
// File Name   : decoder_using_assign.sv
// Function    : decoder using assign
// Coder       : Deepak Kumar Tala
//-----------------------------------------------------
module decoder_using_assign (
input  wire [3:0]  binary_in   , //  4 bit binary input
output wire [15:0] decoder_out , //  16-bit out 
input  wire        enable        //  Enable for the decoder
);
//--------------Code Starts Here----------------------- 
assign decoder_out = (enable) ? (1 << binary_in) : 16'b0 ;

endmodule

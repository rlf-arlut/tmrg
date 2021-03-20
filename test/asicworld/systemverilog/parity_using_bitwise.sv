//-----------------------------------------------------
// Design Name : parity_using_bitwise
// File Name   : parity_using_bitwise.sv
// Function    : Parity using bitwise xor
// Coder      : Deepak Kumar Tala
//-----------------------------------------------------
module parity_using_bitwise (
input   wire [7:0] data_in    , //  8 bit data in
output  wire       parity_out   //  1 bit parity out
);
//--------------Code Starts Here----------------------- 
assign parity_out = ^data_in; 

endmodule

//-----------------------------------------------------
// Design Name : mux_using_case
// File Name   : mux_using_case.sv
// Function    : 2:1 Mux using Case
// Coder      : Deepak Kumar Tala
//-----------------------------------------------------
module  mux_using_case(
input  wire  din_0      , // Mux first input
input  wire  din_1      , // Mux Second input
input  wire  sel        , // Select input
output reg   mux_out      // Mux output
);
//-------------Code Starts Here---------
always @ (*)
MUX : begin
 case (sel) 
    1'b0 : mux_out = din_0;
    1'b1 : mux_out = din_1;
 endcase 
end 

endmodule //End Of Module mux

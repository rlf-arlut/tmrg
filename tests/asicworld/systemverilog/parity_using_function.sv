//-----------------------------------------------------
// Design Name : parity_using_function
// File Name   : parity_using_function.sv
// Function    : Parity using function
// Coder      : Deepak Kumar Tala
//-----------------------------------------------------
module parity_using_function (
input   wire [7:0] data_in    , //  8 bit data in
output  wire       parity_out   //  1 bit parity out
);
//--------------Code Starts Here----------------------- 
function  parity;
  input [31:0] data; 
  begin
    parity =  (data_in[0] ^ data_in[1]) ^  
              (data_in[2] ^ data_in[3]) ^ 
              (data_in[4] ^ data_in[5]) ^  
              (data_in[6] ^ data_in[7]);
  end 
endfunction 
 
assign parity_out = parity(data_in);

endmodule

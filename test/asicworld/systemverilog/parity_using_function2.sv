//-----------------------------------------------------
// Design Name : parity_using_function2
// File Name   : parity_using_function2.v
// Function    : Parity using function
// Coder       : Deepak Kumar Tala
//-----------------------------------------------------
module parity_using_function2 (
input   wire [31:0] data_in    , //  8 bit data in
output  reg         parity_out   //  1 bit parity out
);
//--------------Code Starts Here----------------------- 
function parity;
  input [31:0] data; 
  integer i; 
  begin 
    parity = 0; 
    for (i = 0; i < 32; i = i + 1) begin  
      parity = parity ^ data[i]; 
    end 
  end 
endfunction 

always_comb
begin
  parity_out = parity(data_in);
end

endmodule

//-----------------------------------------------------
// Design Name : pri_encoder_using_if
// File Name   : pri_encoder_using_if.sv
// Function    : Pri Encoder using If
// Coder      : Deepak Kumar Tala
//-----------------------------------------------------
module pri_encoder_using_if (
output reg  [3:0]  binary_out , //  4 bit binary output
input  wire [15:0] encoder_in , //  16-bit input 
input  wire        enable       //  Enable for the encoder
);
//--------------Code Starts Here----------------------- 
always_comb
begin
  binary_out = 0;
  if (enable) begin
   priority if (encoder_in == {{14{1'bx}},1'b1,{1{1'b0}}}) begin
    binary_out = 1; 
   end else if (encoder_in == {{13{1'bx}},1'b1,{2{1'b0}}}) begin 
    binary_out = 2; 
   end else if (encoder_in == {{12{1'bx}},1'b1,{3{1'b0}}}) begin 
    binary_out = 3; 
   end else if (encoder_in == {{11{1'bx}},1'b1,{4{1'b0}}}) begin 
    binary_out = 4; 
   end else if (encoder_in == {{10{1'bx}},1'b1,{5{1'b0}}}) begin 
    binary_out = 5; 
   end else if (encoder_in == {{9{1'bx}},1'b1,{6{1'b0}}}) begin 
    binary_out = 6; 
   end else if (encoder_in == {{8{1'bx}},1'b1,{7{1'b0}}}) begin 
    binary_out = 7; 
   end else if (encoder_in == {{7{1'bx}},1'b1,{8{1'b0}}}) begin 
    binary_out = 8; 
   end else if (encoder_in == {{6{1'bx}},1'b1,{9{1'b0}}}) begin 
    binary_out = 9; 
   end else if (encoder_in == {{5{1'bx}},1'b1,{10{1'b0}}}) begin 
    binary_out = 10; 
   end else if (encoder_in == {{4{1'bx}},1'b1,{11{1'b0}}}) begin 
    binary_out = 11; 
   end else if (encoder_in == {{3{1'bx}},1'b1,{12{1'b0}}}) begin 
    binary_out = 12; 
   end else if (encoder_in == {{2{1'bx}},1'b1,{13{1'b0}}}) begin 
    binary_out = 13; 
   end else if (encoder_in == {{1{1'bx}},1'b1,{14{1'b0}}}) begin 
    binary_out = 14; 
   end else if (encoder_in == {1'b1,{15{1'b0}}}) begin 
    binary_out = 15; 
   end
  end
end

endmodule  

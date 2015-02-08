//-----------------------------------------------------
// Design Name : mux_using_if
// File Name   : mux_using_if.sv
// Function    : 2:1 Mux using If
// Coder      : Deepak Kumar Tala
//-----------------------------------------------------
module  mux_using_if(
input  wire  din_0      , // Mux first input
input  wire  din_1      , // Mux Second input
input  wire  sel        , // Select input
output reg   mux_out      // Mux output
);
//-------------Code Starts Here---------
always_comb
begin : MUX
  if (sel == 1'b0) begin
      mux_out = din_0;
  end else begin
      mux_out = din_1 ;
  end
end

endmodule //End Of Module mux

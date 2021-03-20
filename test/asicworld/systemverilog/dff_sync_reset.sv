//-----------------------------------------------------
// Design Name : dff_sync_reset
// File Name   : dff_sync_reset.sv
// Function    : D flip-flop sync reset
// Coder      : Deepak Kumar Tala
//-----------------------------------------------------
module dff_sync_reset (
input  wire data  , // Data Input
input  wire clk   , // Clock Input
input  wire reset , // Reset input 
output reg  q       // Q output
);
//-------------Code Starts Here---------
always_ff @ ( posedge clk)
if (~reset) begin
  q <= 1'b0;
end  else begin
  q <= data;
end

endmodule //End Of Module dff_sync_reset

//-----------------------------------------------------
// Design Name : tff_sync_reset
// File Name   : tff_sync_reset.sv
// Function    : T flip-flop sync reset
// Coder       : Deepak Kumar Tala
//-----------------------------------------------------
module tff_sync_reset (
input  wire data  , // Data Input
input  wire clk   , // Clock Input
input  wire reset , // Reset input
output reg  q       // Q output
);
//-------------Code Starts Here---------
always_ff @ ( posedge clk)
if (~reset) begin
  q <= 1'b0;
end else if (data) begin
  q <= !q;
end

endmodule //End Of Module tff_async_reset

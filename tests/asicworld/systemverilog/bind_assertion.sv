//+++++++++++++++++++++++++++++++++++++++++++++++++
//   DUT With assertions
//+++++++++++++++++++++++++++++++++++++++++++++++++
module bind_assertion(
  input wire clk,req,reset, 
  output reg gnt);
//=================================================
// Actual DUT RTL
//=================================================
always @ (posedge clk)
  gnt <= req;

endmodule

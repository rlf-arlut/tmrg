
module top #(parameter REG_WIDTH=8)(
  input [REG_WIDTH-1:0]  dataIn,
  output [REG_WIDTH-1:0] dataOut, 
  input clk
);
// tmrg default triplicate 
reg [REG_WIDTH-1:0] mem;
wire [REG_WIDTH-1:0] memVoted=mem;
assign dataOut=mem;
wire memTmrError=1'b0;
wire tmpTmrError=memTmrError;

always @(posedge clk)
  if (tmpTmrError)
    mem <= memVoted;
  else
    mem <= dataIn;
endmodule

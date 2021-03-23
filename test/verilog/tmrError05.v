
module top #(parameter REG_WIDTH=8)(
  input [REG_WIDTH-1:0]  dataIn,
  output [REG_WIDTH-1:0] dataOut, 
  input clk
);
// tmrg default do_not_triplicate
// tmrg triplicate mem 
reg [REG_WIDTH-1:0] mem;
assign dataOut=mem;
wire memTmrError=1'b0;
wire tmpTmrError=memTmrError;

always @(posedge clk)
  if (tmpTmrError)
    mem <= dataOut;
  else
    mem <= dataIn;
assign dataOut=mem;
endmodule

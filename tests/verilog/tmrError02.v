
module top #(parameter REG_WIDTH=8)(input [REG_WIDTH-1:0]  dataIn,output dataOut, input clk);
// tmrg do_not_triplicate dataIn dataOut
wire tmrError = 1'b0;
//wire memTmrError = 1'b0;
reg [REG_WIDTH-1:0] mem;
assign dataOut=mem;

always @(posedge clk)
  if (memTmrError)
    mem <= dataOut;
  else
  mem <= dataIn;

endmodule

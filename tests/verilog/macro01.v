`define INIT_DELAY 2
`define TEST_VAL 1'b1
`define DELAY (2+2)
`define INIT2 1'b0

module DFF(data, clk, out, outConst);
	parameter INIT = 0;
	parameter WIDTH = 4;

	input [WIDTH-1:0] data;
	input clk;
	output reg [WIDTH-1:0] out, outConst;

	initial out <= #`INIT_DELAY INIT;

	initial out <= # `INIT_DELAY (`INIT2 ^ 1'b1);

	always @(posedge clk)
		out <= #`DELAY (data == `TEST_VAL);
endmodule

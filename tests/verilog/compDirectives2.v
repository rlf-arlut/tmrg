`define BLOCKING

module DFF(data, clk, out);
	parameter WIDTH = 4;

	input [WIDTH-1:0] data;
	input clk;
	output reg [WIDTH-1:0] out;

	always @(posedge clk)
	begin
`ifdef BLOCKING
		out = data;
`else
		out <= data;
`endif
	end
endmodule


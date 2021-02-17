`define INIT_DELAY 2

module DFF(data, clk, out, outConst);
	parameter INIT = 0;
	parameter WIDTH = 4;
	
	input [WIDTH-1:0] data;
	input clk;
	output reg [WIDTH-1:0] out, outConst;

	// synopsys translate_off
	//This gives an error
	initial data <= #`INIT_DELAY INIT;
	//This works
	//initial data <= #2 INIT;
	// synopsys translate_on

	always @(posedge clk)
	begin
		out <= data;
	end
endmodule


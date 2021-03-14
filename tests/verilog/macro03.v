//if RESET_EDGE=posedge => set RESET_VAL=1
//if RESET_EDGE=negedge => set RESET_VAL=0
`define RESET_EDGE posedge
`define RESET_VAL 1

module macro03_reset_edge(data, clk, rst, out);
	parameter WIDTH = 4;

	input [WIDTH-1:0] data;
	input clk, rst;
	output reg [WIDTH-1:0] out;

	always @(posedge clk or `RESET_EDGE rst)
	begin
		if(rst == `RESET_VAL) out <= 0; 
		else out <= data;
	end
endmodule

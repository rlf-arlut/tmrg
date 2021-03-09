`define INIT_DELAY_NUM 2
`define INIT_DELAY #2
`define CONST_VAL 0

module macro02(data, clk, out);
	parameter INIT = 0;
	parameter WIDTH = 4;
	
	input [WIDTH-1:0] data;
	input clk;
	output reg [WIDTH-1:0] out;

	initial data <= #`INIT_DELAY_NUM INIT;
	initial data <= # `INIT_DELAY_NUM INIT;
	initial data <= #`INIT_DELAY_NUM 2'b10;
	initial data = #`INIT_DELAY_NUM INIT;
	initial data = # `INIT_DELAY_NUM INIT;
	initial data = #`INIT_DELAY_NUM 2'b10;

	initial data <= `INIT_DELAY INIT;
	initial data <= `INIT_DELAY 2'b10;
	initial data = `INIT_DELAY INIT;
	initial data = `INIT_DELAY 2'b10;
	
	initial data <= `CONST_VAL;
	initial data = `CONST_VAL;
	
	always @(posedge clk)
	begin
		out <= data;
	end
endmodule

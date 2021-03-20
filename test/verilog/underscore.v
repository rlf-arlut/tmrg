
module underscore(in1, in2, out);
	input in1, in2;
	output wire out;

	wire _xor, my_xor;
	assign _xor = in1 ^ in2;
	assign my_xor = in1 ^ in2;

	assign out = my_xor;
	assign out = _xor;
	assign out = 1'b0_0;
	assign out = 0_0;
	assign out = 0_0______1;
endmodule

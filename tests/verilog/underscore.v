
module underscore(in1, in2, out);
	input in1, in2;
	output wire out;

	wire _xor, my_xor;
	assign _xor = in1 ^ in2;
	assign my_xor = in1 ^ in2;

	// This works.
	assign out = my_xor;
	// This fails because the first _ is recognized as a number.
	// However, a _ is not allowed as the first character of a number.
	assign out = _xor;
	// To verify, this still works with the patch.
	assign out = 1'b0_0;
	// Both notations below are also valid but don't work without the patch.
	assign out = 0_0;
	assign out = 0_0______1;
endmodule

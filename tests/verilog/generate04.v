module pseudo_counter #(parameter WIDTH=10) (
	input clk,
	input rst_n,
	input enable,
	output wire [WIDTH-1:0] value
);
// tmrg default do_not_triplicate
// tmrg triplicate value_tmr
	reg [WIDTH-1:0] value_tmr;
	assign value=value_tmr;

	wire ornot, xorornot;
	wire feed_back_0; 

	assign ornot = |value[WIDTH-2:0];
	assign xorornot = value[WIDTH-1] ^ ~ornot;

	generate if ( WIDTH==10 ) begin: cnt10
			assign feed_back_0 = xorornot^value[1];
		end else if ( WIDTH==8 ) begin: cnt8
			assign feed_back_0 = xorornot^value[3]^value[5]^value[2];
		end else if ( WIDTH==6 ) begin: cnt6
			assign feed_back_0 = xorornot^value[4];
		end  else begin: cntX
			assign feed_back_0 = 1'bx;
		end
	endgenerate

	always @(posedge clk or negedge rst_n)
		if (!rst_n)
			value_tmr <= 0;
		else
			if (enable) begin
				value_tmr <= {value[WIDTH-2:0], feed_back_0};
			end
endmodule

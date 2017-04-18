module tests();

parameter WIDTH = 5;

wire [WIDTH:0] bus1 = 'b0;
wire [WIDTH-1:0] bus2;
reg [WIDTH-1:0] bus3;
wire [WIDTH:0] bus4;

assign bus2 = bus1[WIDTH-1:0];

always @ (bus2) begin
	bus3 <= bus1[WIDTH-1:0];
end

assign bus4 = bus1[WIDTH:0];

/*****************************/

reg[3:0] shift;
wire shift_in = 'b0;
reg clk160_i;

integer i;
always @(posedge clk160_i) begin
	for(i = 1; i < 4; i = i + 1) begin
		shift[i] <=  shift[i-1];
	end
	shift[0] <=  shift_in; 
end

endmodule
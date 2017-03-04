module test;
parameter P=16;
// tmrg default triplicate
// tmrg do_not_triplicate signal0
reg    [13:0] signal0 [0:P-1];
wire   [13:0] signal1;
assign signal1=signal0[0];


// tmrg do_not_triplicate signal3
reg    [13:0] signal2 [0:P-1];
wire   [13:0] signal3;
assign signal3=signal2[0];

reg           signal4 [0:P-1];
reg    [13:0] signal5;

wire          signal6 [0:P-1];
wire   [13:0] signal7;


reg           signal8 [0:10];
wire          signal9 [0:10];

endmodule


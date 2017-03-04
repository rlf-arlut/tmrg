module test;
// tmrg default triplicate
// tmrg do_not_triplicate signal0
reg    [13:0] signal0 [0:CLUST-1];
wire   [13:0] signal1;
assign signal1=signal0[0];


// tmrg do_not_triplicate signal3
reg    [13:0] signal2 [0:CLUST-1];
wire   [13:0] signal3;
assign signal2=signal2[0];

reg           signal4 [0:CLUST-1];
reg    [13:0] signal5;

wire          signal5 [0:CLUST-1];
wire   [13:0] signal6;


reg           signal7 [0:10];
wire          signal8 [0:10];

endmodule


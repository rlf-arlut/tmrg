// bug description: voter on signal 2 is missing

module test;
// tmrg default triplicate
// tmrg do_not_triplicate signal0 signal1 
reg    [13:0] signal0, signal1;
wire   [13:0] signal2;
reg [13:0] signal3;

always @*
  signal3  <= signal0;

// tmrg do_not_triplicate signalb
always @*
  signal0[signal1]  <= signal2;



//always @*
//  {signala,signalb}  <=1'b0;

endmodule


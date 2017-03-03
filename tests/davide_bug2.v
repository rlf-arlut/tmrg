// bug description: voter on signal 2 is missing

module test;
// tmrg default triplicate
// tmrg do_not_triplicate signal
reg    [13:0] signal;
wire   [13:0] signal2;

always @*
  signal[signal2]  <=1'b0;

endmodule


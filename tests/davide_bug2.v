// bug description: voter on signal 2 is missing

module test;
// tmrg default triplicate
// tmrg do_not_triplicate signala 
reg    [13:0] signala,signalb,signalc;
wire   [13:0] signal2;

always @*
  signala  <=1'b0;

always @*
  signala[signalb]  <=1'b0;



always @*
  {signala,signalb}  <=1'b0;

endmodule


module fsm01TMR(
  inA,  inB,  inC,
  outA, outB, outC,
  clkA, clkB, clkC
);
input inA, inB, inC;
input clkA, clkB, clkC;
output outA, outB, outC;
reg stateA, stateB, stateC;
reg stateNextA, stateNextB, stateNextC;
assign outA =  stateA;
assign outB =  stateB;
assign outC =  stateC;

always @(posedge clkA)
  stateA <= stateNextA;

always @(posedge clkB)
  stateB <= stateNextB;

always @(posedge clkC)
  stateC <= stateNextC;

always @(stateA or inA)
  stateNextA =  inA^stateA;

always @(stateB or inB)
  stateNextB =  inB^stateB;

always @(stateC or inC)
  stateNextC =  inC^stateC;
endmodule

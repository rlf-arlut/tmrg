module fsm01TMR(
  inA,
  inB,
  inC,
  outA,
  outB,
  outC,
  clkA,
  clkB,
  clkC
);
input inA;
input inB;
input inC;
input clkA;
input clkB;
input clkC;
output outA;
output outB;
output outC;
reg stateA;
reg stateB;
reg stateC;
reg stateNextA;
reg stateNextB;
reg stateNextC;
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

module fsm03TMR(
  in,
  out,
  clk
);
wire stateNextC, stateNextB, stateNextA;
wire clkC, clkB, clkA;
wire state;
input in;
input clk;
output out;
reg stateA, stateB, stateC;
reg stateNext;
assign out =  state;

always @(posedge clkA)
  stateA <= stateNextA;

always @(posedge clkB)
  stateB <= stateNextB;

always @(posedge clkC)
  stateC <= stateNextC;

always @(state or in)
  stateNext =  in^state;

majorityVoter stateVoter (
  .inA(stateA),
  .inB(stateB),
  .inC(stateC),
  .out(state)
);

fanout clkFanout (
  .in(clk),
  .outA(clkA),
  .outB(clkB),
  .outC(clkC)
);

fanout stateNextFanout (
  .in(stateNext),
  .outA(stateNextA),
  .outB(stateNextB),
  .outC(stateNextC)
);
endmodule

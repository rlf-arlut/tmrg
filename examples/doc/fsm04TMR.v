module fsm04TMR(
  in,
  out,
  clkA, clkB, clkC
);
wire stateNextC, stateNextB, stateNextA;
wire state;
input in;
input clkA, clkB, clkC;
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

fanout stateNextFanout (
    .in(stateNext),
    .outA(stateNextA),
    .outB(stateNextB),
    .outC(stateNextC)
    );
endmodule


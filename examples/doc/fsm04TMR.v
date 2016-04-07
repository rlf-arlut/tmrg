module fsm03TMR(
  in,
  out,
  clkA,
  clkB,
  clkC
);
wire stateNextC;
wire stateNextB;
wire stateNextA;
wire state;
input in;
input clkA;
input clkB;
input clkC;
output out;
reg stateA;
reg stateB;
reg stateC;
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


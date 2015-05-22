module fsm02TMR(
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
  stateA <= stateNextVotedA;

always @(posedge clkB)
  stateB <= stateNextVotedB;

always @(posedge clkC)
  stateC <= stateNextVotedC;

always @(stateA or inA)
  stateNextA =  inA^stateA;

always @(stateB or inB)
  stateNextB =  inB^stateB;

always @(stateC or inC)
  stateNextC =  inC^stateC;

majorityVoter stateNextVoterA (
  .inA(stateNextA),
  .inB(stateNextB),
  .inC(stateNextC),
  .out(stateNextVotedA)
);

majorityVoter stateNextVoterB (
  .inA(stateNextA),
  .inB(stateNextB),
  .inC(stateNextC),
  .out(stateNextVotedB)
);

majorityVoter stateNextVoterC (
  .inA(stateNextA),
  .inB(stateNextB),
  .inC(stateNextC),
  .out(stateNextVotedC)
);
endmodule

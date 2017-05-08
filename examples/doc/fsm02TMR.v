module fsm02TMR(
  inA,   inB,   inC,
  outA,  outB,  outC,
  clkA,  clkB,  clkC
);
input inA,inB,inC;
input clkA,clkB,clkC;
output outA,outB,outC;
reg stateA,stateB,stateC;
reg stateNextA,stateNextB,stateNextC;

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

module vote01TMR(
  inA,
  inB,
  inC,
  outA,
  outB,
  outC
);
input inA;
input inB;
input inC;
output outA;
output outB;
output outC;
assign outA =  inVotedA;
assign outB =  inVotedB;
assign outC =  inVotedC;

majorityVoter inVoterA (
  .inA(inA),
  .inB(inB),
  .inC(inC),
  .out(inVotedA)
);

majorityVoter inVoterB (
  .inA(inA),
  .inB(inB),
  .inC(inC),
  .out(inVotedB)
);

majorityVoter inVoterC (
  .inA(inA),
  .inB(inB),
  .inC(inC),
  .out(inVotedC)
);
endmodule

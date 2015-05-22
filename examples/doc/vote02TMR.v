module vote02TMR(
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
wire combLogicA;
wire combLogicB;
wire combLogicC;
assign combLogicA =  ~inVotedA;
assign combLogicB =  ~inVotedB;
assign combLogicC =  ~inVotedC;
assign outA =  combLogicVotedA;
assign outB =  combLogicVotedB;
assign outC =  combLogicVotedC;

majorityVoter inVoterA (
  .inA(inA),
  .inB(inB),
  .inC(inC),
  .out(inVotedA)
);

majorityVoter combLogicVoterA (
  .inA(combLogicA),
  .inB(combLogicB),
  .inC(combLogicC),
  .out(combLogicVotedA)
);

majorityVoter combLogicVoterB (
  .inA(combLogicA),
  .inB(combLogicB),
  .inC(combLogicC),
  .out(combLogicVotedB)
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

majorityVoter combLogicVoterC (
  .inA(combLogicA),
  .inB(combLogicB),
  .inC(combLogicC),
  .out(combLogicVotedC)
);
endmodule

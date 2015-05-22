module powerOnReset(
  z
);
output z;
endmodule
module resetBlockTMR(
  rstn,
  rstA,
  rstB,
  rstC,
  porStatusA,
  porStatusB,
  porStatusC
);
wire rstnC;
wire rstnB;
wire rstnA;
input rstn;
output rstA;
output rstB;
output rstC;
output [2:0] porStatusA;
output [2:0] porStatusB;
output [2:0] porStatusC;
wire porRstA;
wire porRstB;
wire porRstC;
assign porStatusA =  {porRstC,porRstB,porRstA};
assign porStatusB =  {porRstC,porRstB,porRstA};
assign porStatusC =  {porRstC,porRstB,porRstA};
assign rstA =  !rstnA|porRstVotedA;
assign rstB =  !rstnB|porRstVotedB;
assign rstC =  !rstnC|porRstVotedC;

powerOnReset porA (
  .z(porRstA)
);

powerOnReset porB (
  .z(porRstB)
);

powerOnReset porC (
  .z(porRstC)
);

majorityVoter porRstVoterA (
  .inA(porRstA),
  .inB(porRstB),
  .inC(porRstC),
  .out(porRstVotedA)
);

majorityVoter porRstVoterB (
  .inA(porRstA),
  .inB(porRstB),
  .inC(porRstC),
  .out(porRstVotedB)
);

majorityVoter porRstVoterC (
  .inA(porRstA),
  .inB(porRstB),
  .inC(porRstC),
  .out(porRstVotedC)
);

fanout rstnFanout (
  .in(rstn),
  .outA(rstnA),
  .outB(rstnB),
  .outC(rstnC)
);
endmodule

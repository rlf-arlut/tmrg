module dffTMR(
  IA,
  IB,
  IC,
  CA,
  CB,
  CC,
  ZA,
  ZB,
  ZC,
  tmrErrorA,
  tmrErrorB,
  tmrErrorC
);
output tmrErrorC;
wire tmrErrorC;
wire ITmrErrorC;
output tmrErrorB;
wire tmrErrorB;
wire ITmrErrorB;
output tmrErrorA;
wire tmrErrorA;
wire ITmrErrorA;
input IA;
input IB;
input IC;
input CA;
input CB;
input CC;
output ZA;
output ZB;
output ZC;
reg ZA;
reg ZB;
reg ZC;

always @(posedge CA)
  ZA <= IVotedA;

always @(posedge CB)
  ZB <= IVotedB;

always @(posedge CC)
  ZC <= IVotedC;

majorityVoter IVoterA (
  .inA(IA),
  .inB(IB),
  .inC(IC),
  .out(IVotedA),
  .tmrErr(ITmrErrorA)
);
assign tmrErrorA =  ITmrErrorA;

majorityVoter IVoterB (
  .inA(IA),
  .inB(IB),
  .inC(IC),
  .out(IVotedB),
  .tmrErr(ITmrErrorB)
);
assign tmrErrorB =  ITmrErrorB;

majorityVoter IVoterC (
  .inA(IA),
  .inB(IB),
  .inC(IC),
  .out(IVotedC),
  .tmrErr(ITmrErrorC)
);
assign tmrErrorC =  ITmrErrorC;
endmodule
module inst01TMR(
  in1A,
  in1B,
  in1C,
  in2A,
  in2B,
  in2C,
  in3A,
  in3B,
  in3C,
  outA,
  outB,
  outC,
  clkA,
  clkB,
  clkC,
  gateA,
  gateB,
  gateC,
  tmrErrorA,
  tmrErrorB,
  tmrErrorC
);
output tmrErrorC;
wire tmrErrorC;
wire in3TmrErrorC;
output tmrErrorB;
wire tmrErrorB;
wire in3TmrErrorB;
output tmrErrorA;
wire tmrErrorA;
wire in3TmrErrorA;
input in1A;
input in1B;
input in1C;
input in2A;
input in2B;
input in2C;
input in3A;
input in3B;
input in3C;
input clkA;
input clkB;
input clkC;
input gateA;
input gateB;
input gateC;
output outA;
output outB;
output outC;
wire out1A;
wire out1B;
wire out1C;
wire out2A;
wire out2B;
wire out2C;
reg out3A;
reg out3B;
reg out3C;
wire clkGatedA =  clkA&(gateA|tmrErrorA);
wire clkGatedB =  clkB&(gateB|tmrErrorB);
wire clkGatedC =  clkC&(gateC|tmrErrorC);
assign outA =  out1A&out2A&out3A;
assign outB =  out1B&out2B&out3B;
assign outC =  out1C&out2C&out3C;

dffTMR dff01 (
  .IA(in1A),
  .IB(in1B),
  .IC(in1C),
  .CA(clkGatedA),
  .CB(clkGatedB),
  .CC(clkGatedC),
  .ZA(out1A),
  .ZB(out1B),
  .ZC(out1C),
  .tmrErrorA(dff01tmrErrorA),
  .tmrErrorB(dff01tmrErrorB),
  .tmrErrorC(dff01tmrErrorC)
);

dffTMR dff02 (
  .IA(in2A),
  .IB(in2B),
  .IC(in2C),
  .CA(clkGatedA),
  .CB(clkGatedB),
  .CC(clkGatedC),
  .ZA(out2A),
  .ZB(out2B),
  .ZC(out2C),
  .tmrErrorA(dff02tmrErrorA),
  .tmrErrorB(dff02tmrErrorB),
  .tmrErrorC(dff02tmrErrorC)
);

always @(posedge clkGatedA)
  out3A <= in3VotedA;

always @(posedge clkGatedB)
  out3B <= in3VotedB;

always @(posedge clkGatedC)
  out3C <= in3VotedC;

majorityVoter in3VoterA (
  .inA(in3A),
  .inB(in3B),
  .inC(in3C),
  .out(in3VotedA),
  .tmrErr(in3TmrErrorA)
);
assign tmrErrorA =  dff01tmrErrorA|dff02tmrErrorA|in3TmrErrorA;

majorityVoter in3VoterB (
  .inA(in3A),
  .inB(in3B),
  .inC(in3C),
  .out(in3VotedB),
  .tmrErr(in3TmrErrorB)
);
assign tmrErrorB =  dff01tmrErrorB|dff02tmrErrorB|in3TmrErrorB;

majorityVoter in3VoterC (
  .inA(in3A),
  .inB(in3B),
  .inC(in3C),
  .out(in3VotedC),
  .tmrErr(in3TmrErrorC)
);
assign tmrErrorC =  dff01tmrErrorC|dff02tmrErrorC|in3TmrErrorC;
endmodule

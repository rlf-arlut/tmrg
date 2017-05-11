module comb06TMR(
  inA,  inB,  inC,
  outA, outB, outC
);
wire combLogicA, combLogicB, combLogicC;
wire in;
input inA, inB, inC;
output outA, outB, outC;
wire combLogic;
assign combLogic =  ~in;
assign outA =  combLogicA;
assign outB =  combLogicB;
assign outC =  combLogicC;

majorityVoter inVoter (
  .inA(inA),
  .inB(inB),
  .inC(inC),
  .out(in)
);

fanout combLogicFanout (
  .in(combLogic),
  .outA(combLogicA),
  .outB(combLogicB),
  .outC(combLogicC)
);
endmodule

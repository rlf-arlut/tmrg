module comb03TMR(
  in,
  outA,  outB,  outC
);
wire inC, inB, inA;
input in;
output outA, outB, outC;
wire combLogicA, combLogicB, combLogicC;
assign combLogicA =  ~inA;
assign combLogicB =  ~inB;
assign combLogicC =  ~inC;
assign outA =  combLogicA;
assign outB =  combLogicB;
assign outC =  combLogicC;

fanout inFanout (
  .in(in),
  .outA(inA),
  .outB(inB),
  .outC(inC)
);
endmodule

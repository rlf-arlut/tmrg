module comb03TMR(
  in,
  outA,
  outB,
  outC
);
wire inC;
wire inB;
wire inA;
input in;
output outA;
output outB;
output outC;
wire combLogicA;
wire combLogicB;
wire combLogicC;
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

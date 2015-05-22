module inverterTMR(
  IA,
  IB,
  IC,
  ZA,
  ZB,
  ZC
);
input IA;
input IB;
input IC;
output ZA;
output ZB;
output ZC;
assign ZA =  ~IA;
assign ZB =  ~IB;
assign ZC =  ~IC;
endmodule
module mod01TMR(
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

inverterTMR inv01 (
  .IA(inA),
  .IB(inB),
  .IC(inC),
  .ZA(outA),
  .ZB(outB),
  .ZC(outC)
);
endmodule

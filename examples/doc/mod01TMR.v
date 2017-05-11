module inverterTMR(
  IA,  IB,  IC,
  ZA,  ZB,  ZC
);
input IA, IB, IC;
output ZA, ZB, ZC;
assign ZA =  ~IA;
assign ZB =  ~IB;
assign ZC =  ~IC;
endmodule

module mod01TMR(
  inA,  inB,  inC,
  outA, outB, outC
);
input  inA, inB, inC;
output outA, outB, outC;

inverterTMR inv01 (
  .IA(inA),
  .IB(inB),
  .IC(inC),
  .ZA(outA),
  .ZB(outB),
  .ZC(outC)
);
endmodule

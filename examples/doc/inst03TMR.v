module mlogicTMR(
  IA,
  IB,
  IC,
  ZNA,
  ZNB,
  ZNC
);
input IA;
input IB;
input IC;
output ZNA;
output ZNB;
output ZNC;
assign ZNA =  ~IA;
assign ZNB =  ~IB;
assign ZNC =  ~IC;
endmodule
module inst03TMR(
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

mlogicTMR logic01 (
  .IA(inA),
  .IB(inB),
  .IC(inC),
  .ZNA(outA),
  .ZNB(outB),
  .ZNC(outC)
);
endmodule

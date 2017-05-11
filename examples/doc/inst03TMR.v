module mlogicTMR(
  IA,  IB,  IC,
  ZNA, ZNB, ZNC
);
input  IA,  IB,  IC;
output ZNA, ZNB, ZNC;
assign ZNA =  ~IA;
assign ZNB =  ~IB;
assign ZNC =  ~IC;
endmodule

module inst03TMR(
  inA,  inB,  inC,
  outA, outB, outC
);
input inA, inB, inC;
output outA, outB, outC;

mlogicTMR logic01 (
  .IA(inA),
  .IB(inB),
  .IC(inC),
  .ZNA(outA),
  .ZNB(outB),
  .ZNC(outC)
);
endmodule

module mlogic(
  I,
  ZN
);
input I;
output ZN;
assign ZN =  ~I;
endmodule
module inst01TMR(
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

mlogic logic01A (
  .I(inA),
  .ZN(outA)
);

mlogic logic01B (
  .I(inB),
  .ZN(outB)
);

mlogic logic01C (
  .I(inC),
  .ZN(outC)
);
endmodule

module mlogic(
  I,
  ZN
);
input I;
output ZN;
assign ZN =  ~I;
endmodule
module inst02TMR(
  inA,  inB,  inC,
  outA, outB, outC
);
wire out;
wire in;
input inA, inB, inC;
output outA, outB, outC;

mlogic logic01 (
  .I(in),
  .ZN(out)
);

majorityVoter inVoter (
  .inA(inA),
  .inB(inB),
  .inC(inC),
  .out(in)
);

fanout outFanout (
  .in(out),
  .outA(outA),
  .outB(outB),
  .outC(outC)
);
endmodule

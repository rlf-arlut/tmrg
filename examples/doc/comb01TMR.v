module comb01TMR(
  inA,  inB,  inC,
  outA, outB, outC
);
input inA, inB, inC;
output outA, outB, outC;
wire combLogicA, combLogicB, combLogicC;
assign combLogicA =  ~inA;
assign combLogicB =  ~inB;
assign combLogicC =  ~inC;
assign outA =  combLogicA;
assign outB =  combLogicB;
assign outC =  combLogicC;
endmodule

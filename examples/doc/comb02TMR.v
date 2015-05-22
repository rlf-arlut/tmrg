module comb02TMR(
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
wire combLogicA;
wire combLogicB;
wire combLogicC;
assign combLogicA =  ~inA;
assign combLogicB =  ~inB;
assign combLogicC =  ~inC;
assign outA =  combLogicA;
assign outB =  combLogicB;
assign outC =  combLogicC;
endmodule

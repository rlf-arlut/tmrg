module comb05TMR(
  in,
  out
);
wire inC;
wire inB;
wire inA;
wire combLogic;
input in;
output out;
wire combLogicA;
wire combLogicB;
wire combLogicC;
assign combLogicA =  ~inA;
assign combLogicB =  ~inB;
assign combLogicC =  ~inC;
assign out =  combLogic;

majorityVoter combLogicVoter (
  .inA(combLogicA),
  .inB(combLogicB),
  .inC(combLogicC),
  .out(combLogic)
);

fanout inFanout (
  .in(in),
  .outA(inA),
  .outB(inB),
  .outC(inC)
);
endmodule

module comb04TMR(
  inA,
  inB,
  inC,
  out
);
wire combLogic;
input inA;
input inB;
input inC;
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
endmodule

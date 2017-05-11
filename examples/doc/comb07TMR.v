module comb03TMR(
  in,
  outA,  outB,  outC
);
wire [7:0] inA, inB, inC;
input [7:0] in;
output outA, outB, outC;
reg combLogicA, combLogicB, combLogicC;

always @(inA)
  if (inA)
    combLogicA =  1'b0;
  else
    combLogicA =  1'b1;

always @(inB)
  if (inB)
    combLogicB =  1'b0;
  else
    combLogicB =  1'b1;

always @(inC)
  if (inC)
    combLogicC =  1'b0;
  else
    combLogicC =  1'b1;

assign outA =  combLogicA;
assign outB =  combLogicB;
assign outC =  combLogicC;

fanout #(.WIDTH(8)) inFanout (
  .in(in),
  .outA(inA),
  .outB(inB),
  .outC(inC)
);
endmodule

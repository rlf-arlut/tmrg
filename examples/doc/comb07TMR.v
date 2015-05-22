module comb03TMR(
  in,
  outA,
  outB,
  outC
);
wire [7:0] inC;
wire [7:0] inB;
wire [7:0] inA;
input [7:0] in;
output outA;
output outB;
output outC;
reg combLogicA;
reg combLogicB;
reg combLogicC;

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

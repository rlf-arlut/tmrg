module clockGatingTMR(
  clkInA,   clkInB,   clkInC,
  clkOutA,  clkOutB,  clkOutC,
  clkGateA, clkGateB, clkGateC
);
wire [2:0] clkGate;
input  clkInA,  clkInB,  clkInC;
output clkOutA, clkOutB, clkOutC;
input [2:0] clkGateA, clkGateB, clkGateC;
wire gateA =  clkGate[0];
wire gateB =  clkGate[1];
wire gateC =  clkGate[2];
assign clkOutA =  clkInA&gateA;
assign clkOutB =  clkInB&gateB;
assign clkOutC =  clkInC&gateC;

majorityVoter #(.WIDTH(3)) clkGateVoter (
  .inA(clkGateA),
  .inB(clkGateB),
  .inC(clkGateC),
  .out(clkGate)
);
endmodule

module clockGatingTMR(
  clkInA,   clkInB,   clkInC,
  clkOutA,  clkOutB,  clkOutC,
  clkGateA, clkGateB, clkGateC
);
input  clkInA,   clkInB,   clkInC;
output clkOutA,  clkOutB,  clkOutC;
input  clkGateA, clkGateB, clkGateC;
assign clkOutA =  clkInA&clkGateA;
assign clkOutB =  clkInB&clkGateB;
assign clkOutC =  clkInC&clkGateC;
endmodule

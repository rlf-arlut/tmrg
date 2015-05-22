module clockGatingTMR(
  clkInA,
  clkInB,
  clkInC,
  clkOutA,
  clkOutB,
  clkOutC,
  clkGateA,
  clkGateB,
  clkGateC
);
input clkInA;
input clkInB;
input clkInC;
output clkOutA;
output clkOutB;
output clkOutC;
input clkGateA;
input clkGateB;
input clkGateC;
assign clkOutA =  clkInA&clkGateA;
assign clkOutB =  clkInB&clkGateB;
assign clkOutC =  clkInC&clkGateC;
endmodule

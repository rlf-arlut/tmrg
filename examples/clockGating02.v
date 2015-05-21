module clockGating (clkIn,clkOut,clkGate);
  // tmrg default triplicate
  input clkIn;
  output clkOut;
  input [2:0] clkGate;
  wire gateA=clkGate[0];
  wire gateB=clkGate[1];
  wire gateC=clkGate[2];
  wire gate=gateA;
  assign clkOut=clkIn&gate;
endmodule

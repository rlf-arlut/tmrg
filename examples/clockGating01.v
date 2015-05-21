module clockGating (clkIn,clkOut,clkGate);
  // tmrg default triplicate
  input clkIn;
  output clkOut;
  input clkGate;
  assign clkOut=clkIn&clkGate;
endmodule

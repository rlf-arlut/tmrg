module powerOnReset(
  z
);
output z;
endmodule

module resetBlockTMR(
  rstn,
  rstA,  rstB,  rstC,
  porStatusA,  porStatusB,  porStatusC
);
wire rstnA, rstnB, rstnC;
input rstn;
output rstA, rstB, rstC;
output porStatusA, porStatusB, porStatusC;
wire porRstA, porRstB, porRstC;

assign porStatusA =  porRstA;
assign porStatusB =  porRstB;
assign porStatusC =  porRstC;
assign rstA =  !rstnA|porRstA;
assign rstB =  !rstnB|porRstB;
assign rstC =  !rstnC|porRstC;

powerOnReset porA (
  .z(porRstA)
);

powerOnReset porB (
  .z(porRstB)
);

powerOnReset porC (
  .z(porRstC)
);

fanout rstnFanout (
  .in(rstn),
  .outA(rstnA),
  .outB(rstnB),
  .outC(rstnC)
);
endmodule

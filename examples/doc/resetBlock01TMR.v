module powerOnReset(
  z
);
output z;
endmodule
module resetBlock01TMR(
  rstn,
  rstA,
  rstB,
  rstC
);
wire rstnC;
wire rstnB;
wire rstnA;
input rstn;
output rstA;
output rstB;
output rstC;
wire porRstA;
wire porRstB;
wire porRstC;
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

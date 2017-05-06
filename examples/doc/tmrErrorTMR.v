module ffTMR(
  input  clk,
  input  d,
  output  q,
  input  load
);
wire loadIntC;
wire loadIntB;
wire loadIntA;
wire dC;
wire dB;
wire dA;
wire qC;
wire qB;
wire qA;
wire clkC;
wire clkB;
wire clkA;
wire tmrError;
wor memTmrError;
wire mem;
reg  memA;
reg  memB;
reg  memC;
wire loadInt =  load|tmrError;

always @( posedge clkA )
  if (loadIntA)
    memA <= dA;
  else
    memA <= qA;

always @( posedge clkB )
  if (loadIntB)
    memB <= dB;
  else
    memB <= qB;

always @( posedge clkC )
  if (loadIntC)
    memC <= dC;
  else
    memC <= qC;
assign q =  mem;

majorityVoter memVoter (
    .inA(memA),
    .inB(memB),
    .inC(memC),
    .out(mem),
    .tmrErr(memTmrError)
    );
assign tmrError =  memTmrError;

fanout clkFanout (
    .in(clk),
    .outA(clkA),
    .outB(clkB),
    .outC(clkC)
    );

fanout qFanout (
    .in(q),
    .outA(qA),
    .outB(qB),
    .outC(qC)
    );

fanout dFanout (
    .in(d),
    .outA(dA),
    .outB(dB),
    .outC(dC)
    );

fanout loadIntFanout (
    .in(loadInt),
    .outA(loadIntA),
    .outB(loadIntB),
    .outC(loadIntC)
    );
endmodule

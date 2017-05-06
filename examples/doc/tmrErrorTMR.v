module ffTMR(
  input  clk,
  input  in,
  output  out,
  input  load
);
wire loadIntC;
wire loadIntB;
wire loadIntA;
wire memNextC;
wire memNextB;
wire memNextA;
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
wire memNext =  (load) ? in : out;
assign out =  mem;

always @( posedge clkA )
  if (loadIntA)
    memA <= memNextA;

always @( posedge clkB )
  if (loadIntB)
    memB <= memNextB;

always @( posedge clkC )
  if (loadIntC)
    memC <= memNextC;

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

fanout memNextFanout (
    .in(memNext),
    .outA(memNextA),
    .outB(memNextB),
    .outC(memNextC)
    );

fanout loadIntFanout (
    .in(loadInt),
    .outA(loadIntA),
    .outB(loadIntB),
    .outC(loadIntC)
    );
endmodule

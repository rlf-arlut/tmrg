module configCellTMR(
  input [7:0] dinA,
  input [7:0] dinB,
  input [7:0] dinC,
  input  clkA,
  input  clkB,
  input  clkC,
  input  loadA,
  input  loadB,
  input  loadC,
  output [7:0] qA,
  output [7:0] qB,
  output [7:0] qC
);
wire tmrErrorC;
wor memNextTmrErrorC;
wire [7:0] memNextVotedC;
wire tmrErrorB;
wor memNextTmrErrorB;
wire [7:0] memNextVotedB;
wire tmrErrorA;
wor memNextTmrErrorA;
wire [7:0] memNextVotedA;
reg  [7:0] memA;
reg  [7:0] memB;
reg  [7:0] memC;
reg  [7:0] memNextA;
reg  [7:0] memNextB;
reg  [7:0] memNextC;
wire clkIntA =  clkA|tmrErrorA;
wire clkIntB =  clkB|tmrErrorB;
wire clkIntC =  clkC|tmrErrorC;

always @( loadA or d or qA )
  if (loadA)
    memNextA =  dinA;
  else
    memNextA =  memA;

always @( loadB or d or qB )
  if (loadB)
    memNextB =  dinB;
  else
    memNextB =  memB;

always @( loadC or d or qC )
  if (loadC)
    memNextC =  dinC;
  else
    memNextC =  memC;

always @( posedge clkIntA )
  memA <= memNextVotedA;

always @( posedge clkIntB )
  memB <= memNextVotedB;

always @( posedge clkIntC )
  memC <= memNextVotedC;
assign qA =  memA;
assign qB =  memB;
assign qC =  memC;

majorityVoter #(.WIDTH(8)) memNextVoterA (
    .inA(memNextA),
    .inB(memNextB),
    .inC(memNextC),
    .out(memNextVotedA),
    .tmrErr(memNextTmrErrorA)
    );
assign tmrErrorA =  memNextTmrErrorA;

majorityVoter #(.WIDTH(8)) memNextVoterB (
    .inA(memNextA),
    .inB(memNextB),
    .inC(memNextC),
    .out(memNextVotedB),
    .tmrErr(memNextTmrErrorB)
    );
assign tmrErrorB =  memNextTmrErrorB;

majorityVoter #(.WIDTH(8)) memNextVoterC (
    .inA(memNextA),
    .inB(memNextB),
    .inC(memNextC),
    .out(memNextVotedC),
    .tmrErr(memNextTmrErrorC)
    );
assign tmrErrorC =  memNextTmrErrorC;
endmodule

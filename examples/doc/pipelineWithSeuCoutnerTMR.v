module pipelineWithSeuCoutnerTMR #(
  parameter SEUCNTWIDTH=8,
  parameter N=512
)(
  input  clkA,
  input  clkB,
  input  clkC,
  input  dA,
  input  dB,
  input  dC,
  output  qA,
  output  qB,
  output  qC,
  input  seuCountRstA,
  input  seuCountRstB,
  input  seuCountRstC,
  output reg [SEUCNTWIDTH-1:0] seuCountA,
  output reg [SEUCNTWIDTH-1:0] seuCountB,
  output reg [SEUCNTWIDTH-1:0] seuCountC
);
wire tmrErrorC;
wor seuCountNextTmrErrorC;
wire [SEUCNTWIDTH-1:0] seuCountNextVotedC;
wor pipelineNextTmrErrorC;
wire [N-1:0] pipelineNextVotedC;
wire tmrErrorB;
wor seuCountNextTmrErrorB;
wire [SEUCNTWIDTH-1:0] seuCountNextVotedB;
wor pipelineNextTmrErrorB;
wire [N-1:0] pipelineNextVotedB;
wire tmrErrorA;
wor seuCountNextTmrErrorA;
wire [SEUCNTWIDTH-1:0] seuCountNextVotedA;
wor pipelineNextTmrErrorA;
wire [N-1:0] pipelineNextVotedA;
reg  [N-1:0] pipelineA;
reg  [N-1:0] pipelineB;
reg  [N-1:0] pipelineC;
wire [N-1:0] pipelineNextA;
wire [N-1:0] pipelineNextB;
wire [N-1:0] pipelineNextC;
assign pipelineNextA =  {pipelineA[N-1] ,dA};
assign pipelineNextB =  {pipelineB[N-1] ,dB};
assign pipelineNextC =  {pipelineC[N-1] ,dC};

always @( posedge clkA )
  pipelineA =  pipelineNextVotedA;

always @( posedge clkB )
  pipelineB =  pipelineNextVotedB;

always @( posedge clkC )
  pipelineC =  pipelineNextVotedC;
assign qA =  pipelineA[N] ;
assign qB =  pipelineB[N] ;
assign qC =  pipelineC[N] ;
reg  [SEUCNTWIDTH-1:0] seuCountNextA;
reg  [SEUCNTWIDTH-1:0] seuCountNextB;
reg  [SEUCNTWIDTH-1:0] seuCountNextC;

always @( seuCountA or tmrErrorA )
  begin
    seuCountNextA =  seuCountA;
    if (tmrErrorA)
      seuCountNextA =  seuCountA+1;
  end

always @( seuCountB or tmrErrorB )
  begin
    seuCountNextB =  seuCountB;
    if (tmrErrorB)
      seuCountNextB =  seuCountB+1;
  end

always @( seuCountC or tmrErrorC )
  begin
    seuCountNextC =  seuCountC;
    if (tmrErrorC)
      seuCountNextC =  seuCountC+1;
  end

always @( posedge clkA or seuCountRstA )
  if (seuCountRstA)
    seuCountA <= 0;
  else
    seuCountA <= seuCountNextA;

always @( posedge clkB or seuCountRstB )
  if (seuCountRstB)
    seuCountB <= 0;
  else
    seuCountB <= seuCountNextB;

always @( posedge clkC or seuCountRstC )
  if (seuCountRstC)
    seuCountC <= 0;
  else
    seuCountC <= seuCountNextC;

majorityVoter #(.WIDTH(((N-1)>(0)) ? ((N-1)-(0)+1) : ((0)-(N-1)+1))) pipelineNextVoterA (
    .inA(pipelineNextA),
    .inB(pipelineNextB),
    .inC(pipelineNextC),
    .out(pipelineNextVotedA),
    .tmrErr(pipelineNextTmrErrorA)
    );

majorityVoter #(.WIDTH(((SEUCNTWIDTH-1)>(0)) ? ((SEUCNTWIDTH-1)-(0)+1) : ((0)-(SEUCNTWIDTH-1)+1))) seuCountNextVoterA (
    .inA(seuCountNextA),
    .inB(seuCountNextB),
    .inC(seuCountNextC),
    .out(seuCountNextVotedA),
    .tmrErr(seuCountNextTmrErrorA)
    );
assign tmrErrorA =  pipelineNextTmrErrorA|seuCountNextTmrErrorA;

majorityVoter #(.WIDTH(((N-1)>(0)) ? ((N-1)-(0)+1) : ((0)-(N-1)+1))) pipelineNextVoterB (
    .inA(pipelineNextA),
    .inB(pipelineNextB),
    .inC(pipelineNextC),
    .out(pipelineNextVotedB),
    .tmrErr(pipelineNextTmrErrorB)
    );

majorityVoter #(.WIDTH(((SEUCNTWIDTH-1)>(0)) ? ((SEUCNTWIDTH-1)-(0)+1) : ((0)-(SEUCNTWIDTH-1)+1))) seuCountNextVoterB (
    .inA(seuCountNextA),
    .inB(seuCountNextB),
    .inC(seuCountNextC),
    .out(seuCountNextVotedB),
    .tmrErr(seuCountNextTmrErrorB)
    );
assign tmrErrorB =  pipelineNextTmrErrorB|seuCountNextTmrErrorB;

majorityVoter #(.WIDTH(((N-1)>(0)) ? ((N-1)-(0)+1) : ((0)-(N-1)+1))) pipelineNextVoterC (
    .inA(pipelineNextA),
    .inB(pipelineNextB),
    .inC(pipelineNextC),
    .out(pipelineNextVotedC),
    .tmrErr(pipelineNextTmrErrorC)
    );

majorityVoter #(.WIDTH(((SEUCNTWIDTH-1)>(0)) ? ((SEUCNTWIDTH-1)-(0)+1) : ((0)-(SEUCNTWIDTH-1)+1))) seuCountNextVoterC (
    .inA(seuCountNextA),
    .inB(seuCountNextB),
    .inC(seuCountNextC),
    .out(seuCountNextVotedC),
    .tmrErr(seuCountNextTmrErrorC)
    );
assign tmrErrorC =  pipelineNextTmrErrorC|seuCountNextTmrErrorC;
endmodule

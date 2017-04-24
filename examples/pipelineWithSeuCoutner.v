module pipelineWithSeuCoutner #(parameter SEUCNTWIDTH=8, N=512) (input clk, input d, output q, input seuCountRst, output reg [SEUCNTWIDTH-1:0] seuCount);
  // pipeline logic
  reg [N-1:0] pipeline;
  reg [N-1:0] pipelineNext;
  wire [N-1:0] pipelineNextVoted=pipelineNext;

  assign pipelineNext={pipeline[N-1],d};

  always @(posedge clk)
    pipeline=pipelineNext;

  assign q=pipeline[N];

  // seu counter logic
  wire tmrError;
  reg [SEUCNTWIDTH-1:0] seuCountNext;
  wire [SEUCNTWIDTH-1:0] seuCountNextVoted=seuCountNext;

  always @(tmrError)
    seuCountNext=seuCount+1;

  always @(posedge clk or seuCountRst)
    if (seuCountRst)
      seuCount<=0;
    else
      seuCount<=seuCountNext;
endmodule


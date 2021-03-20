module myVoter (inA, inB, inC, out, tmrErr);
  // tmrg do_not_touch
  parameter WIDTH = 1;
  input   [(WIDTH-1):0]   inA, inB, inC;
  output  [(WIDTH-1):0]   out;
  output                  tmrErr;
  reg                     tmrErr;
  assign out = (inA&inB) | (inA&inC) | (inB&inC);
  always @(inA or inB or inC)
  begin
    if (inA!=inB || inA!=inC || inB!=inC)
      tmrErr = 1;
    else
      tmrErr = 0;
  end
endmodule

module k;
  reg i;
  wire iVoted=i;
endmodule

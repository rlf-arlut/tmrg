module ff(input clk,input d, output q, input load);
  // tmrg default do_not_triplicate
  // tmrg triplicate mem
  reg mem;
  wire tmrError=1'b0;
  wire loadInt=load|tmrError;
  always @(posedge clk)
    if (loadInt)
      mem <= d;
    else
      mem <= q;
  assign q=mem;
endmodule

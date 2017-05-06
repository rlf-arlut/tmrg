module ff(input clk,input in, output out, input load);
  // tmrg default do_not_triplicate
  // tmrg triplicate mem
  reg mem;
  wire tmrError=1'b0;
  wire loadInt=load|tmrError;
  wire memNext=(load)? in : out;
  assign out=mem;
  always @(posedge clk)
    if (loadInt)
      mem <= memNext;
endmodule

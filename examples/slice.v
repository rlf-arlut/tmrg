module slice(
   clkIn,
   clkOut
);
  input clkIn;
  output clkOut;
  // tmrg slicing
  // tmrg default triplicate
   reg [1:0] div;
  wire [1:0] divNext=div-1;
  wire [1:0] divNextVoted=divNext;
  always @(posedge clkIn)
    div <= divNextVoted;
  assign clkOut=div[1];
endmodule

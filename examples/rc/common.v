module fanout(in,outA,outB,outC);
  parameter WIDTH=1;
  input  [WIDTH-1:0] in;
  output [WIDTH-1:0] outA;
  output [WIDTH-1:0] outB;
  output [WIDTH-1:0] outC;
  assign outA=in;
  assign outB=in;
  assign outC=in;
endmodule

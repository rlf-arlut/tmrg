module fanout #(
  parameter WIDTH = 1
)(
  input wire  [WIDTH-1:0] in,
  output wire [WIDTH-1:0] outA,
  output wire [WIDTH-1:0] outB,
  output wire [WIDTH-1:0] outC
);
  assign outA = in;
  assign outB = in;
  assign outC = in;
endmodule

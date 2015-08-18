module mux(
input [3:0] in,
input [1:0] add,
output out,
output outV
);
  wire [1:0] addVoted=add;
  assign out = in[addVoted];
  assign outV = in[add];
  assign out0 = in;
  assign out0 = 5'h2;

endmodule

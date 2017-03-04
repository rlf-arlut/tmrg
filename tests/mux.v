module mux(
input [3:0] in,
input [1:0] add,
output out,
output out1,
output out2,
output [4:0] out3
);
  wire [1:0] addVoted=add;
  assign out = in[addVoted];
  assign out1 = in[add];
  assign out2 = in;
  assign out3 = 5'h2;

endmodule

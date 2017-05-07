
module add_unsigned(A, B, Z);
  input [7:0] A, B;
  output [7:0] Z;
  wire [7:0] A, B;
  wire [7:0] Z;
  wire n_0, n_2, n_4, n_6, n_8, n_10, n_12;
  XOR3D1 p7590A(.A1 (B[7]), .A2 (A[7]), .A3 (n_12), .Z (Z[7]));
  FA1D0 p7551A(.A (A[6]), .B (B[6]), .CI (n_10), .CO (n_12), .S (Z[6]));
  FA1D0 p7508A(.A (A[5]), .B (B[5]), .CI (n_8), .CO (n_10), .S (Z[5]));
  FA1D0 p7471A(.A (A[4]), .B (B[4]), .CI (n_6), .CO (n_8), .S (Z[4]));
  FA1D0 p7433A(.A (A[3]), .B (B[3]), .CI (n_4), .CO (n_6), .S (Z[3]));
  FA1D0 p7391A(.A (A[2]), .B (B[2]), .CI (n_2), .CO (n_4), .S (Z[2]));
  FA1D0 p7340A(.A (A[1]), .B (B[1]), .CI (n_0), .CO (n_2), .S (Z[1]));
  HA1D0 p7346A(.A (B[0]), .B (A[0]), .CO (n_0), .S (Z[0]));
endmodule

module add_unsigned_16(A, B, Z);
  input [7:0] A, B;
  output [7:0] Z;
  wire [7:0] A, B;
  wire [7:0] Z;
  wire n_0, n_2, n_4, n_6, n_8, n_10, n_12;
  XOR3D1 p7590A(.A1 (B[7]), .A2 (A[7]), .A3 (n_12), .Z (Z[7]));
  FA1D0 p7551A(.A (A[6]), .B (B[6]), .CI (n_10), .CO (n_12), .S (Z[6]));
  FA1D0 p7508A(.A (A[5]), .B (B[5]), .CI (n_8), .CO (n_10), .S (Z[5]));
  FA1D0 p7471A(.A (A[4]), .B (B[4]), .CI (n_6), .CO (n_8), .S (Z[4]));
  FA1D0 p7433A(.A (A[3]), .B (B[3]), .CI (n_4), .CO (n_6), .S (Z[3]));
  FA1D0 p7391A(.A (A[2]), .B (B[2]), .CI (n_2), .CO (n_4), .S (Z[2]));
  FA1D0 p7340A(.A (A[1]), .B (B[1]), .CI (n_0), .CO (n_2), .S (Z[1]));
  HA1D0 p7346A(.A (B[0]), .B (A[0]), .CO (n_0), .S (Z[0]));
endmodule

module add_unsigned_15(A, B, Z);
  input [7:0] A, B;
  output [7:0] Z;
  wire [7:0] A, B;
  wire [7:0] Z;
  wire n_0, n_2, n_4, n_6, n_8, n_10, n_12;
  XOR3D1 p7590A(.A1 (B[7]), .A2 (A[7]), .A3 (n_12), .Z (Z[7]));
  FA1D0 p7551A(.A (A[6]), .B (B[6]), .CI (n_10), .CO (n_12), .S (Z[6]));
  FA1D0 p7508A(.A (A[5]), .B (B[5]), .CI (n_8), .CO (n_10), .S (Z[5]));
  FA1D0 p7471A(.A (A[4]), .B (B[4]), .CI (n_6), .CO (n_8), .S (Z[4]));
  FA1D0 p7433A(.A (A[3]), .B (B[3]), .CI (n_4), .CO (n_6), .S (Z[3]));
  FA1D0 p7391A(.A (A[2]), .B (B[2]), .CI (n_2), .CO (n_4), .S (Z[2]));
  FA1D0 p7340A(.A (A[1]), .B (B[1]), .CI (n_0), .CO (n_2), .S (Z[1]));
  HA1D0 p7346A(.A (B[0]), .B (A[0]), .CO (n_0), .S (Z[0]));
endmodule

module majorityVoter_WIDTH8(inA, inB, inC, out, tmrErr);
  input [7:0] inA, inB, inC;
  output [7:0] out;
  output tmrErr;
  wire [7:0] inA, inB, inC;
  wire [7:0] out;
  wire tmrErr;
  wire n_0, n_1, n_2, n_3, n_8, n_9, n_10, n_11;
  INVD1 Fp8479A(.I (n_11), .ZN (out[2]));
  INVD1 Fp8068A(.I (n_10), .ZN (out[6]));
  INVD1 Fp7968A(.I (n_9), .ZN (out[7]));
  INVD1 Fp8265A(.I (n_8), .ZN (out[4]));
  MAOI222D0 p8368A(.A (inA[2]), .B (inC[2]), .C (inB[2]), .ZN (n_11));
  MAOI222D1 p7955A(.A (inC[6]), .B (inA[6]), .C (inB[6]), .ZN (n_10));
  MAOI222D0 p7854A(.A (inA[7]), .B (inC[7]), .C (inB[7]), .ZN (n_9));
  MAOI222D0 p8156A(.A (inC[4]), .B (inA[4]), .C (inB[4]), .ZN (n_8));
  INVD1 Fp8631A(.I (n_3), .ZN (out[0]));
  INVD1 Fp8167A(.I (n_2), .ZN (out[5]));
  INVD1 Fp8521A(.I (n_1), .ZN (out[1]));
  INVD1 Fp8373A(.I (n_0), .ZN (out[3]));
  MAOI222D1 p8511A(.A (inA[0]), .B (inB[0]), .C (inC[0]), .ZN (n_3));
  MAOI222D0 p8054A(.A (inA[5]), .B (inC[5]), .C (inB[5]), .ZN (n_2));
  MAOI222D0 p8404A(.A (inA[1]), .B (inC[1]), .C (inB[1]), .ZN (n_1));
  MAOI222D0 p8260A(.A (inA[3]), .B (inC[3]), .C (inB[3]), .ZN (n_0));
endmodule

module majorityVoter_WIDTH8_1(inA, inB, inC, out, tmrErr);
  input [7:0] inA, inB, inC;
  output [7:0] out;
  output tmrErr;
  wire [7:0] inA, inB, inC;
  wire [7:0] out;
  wire tmrErr;
  wire n_0, n_1, n_2, n_3, n_8, n_9, n_10, n_11;
  INVD1 Fp8479A(.I (n_11), .ZN (out[2]));
  INVD1 Fp8068A(.I (n_10), .ZN (out[6]));
  INVD1 Fp7968A(.I (n_9), .ZN (out[7]));
  INVD1 Fp8265A(.I (n_8), .ZN (out[4]));
  MAOI222D0 p8368A(.A (inA[2]), .B (inC[2]), .C (inB[2]), .ZN (n_11));
  MAOI222D1 p7955A(.A (inC[6]), .B (inA[6]), .C (inB[6]), .ZN (n_10));
  MAOI222D0 p7854A(.A (inA[7]), .B (inC[7]), .C (inB[7]), .ZN (n_9));
  MAOI222D0 p8156A(.A (inC[4]), .B (inA[4]), .C (inB[4]), .ZN (n_8));
  INVD1 Fp8631A(.I (n_3), .ZN (out[0]));
  INVD1 Fp8167A(.I (n_2), .ZN (out[5]));
  INVD1 Fp8521A(.I (n_1), .ZN (out[1]));
  INVD1 Fp8373A(.I (n_0), .ZN (out[3]));
  MAOI222D1 p8511A(.A (inA[0]), .B (inB[0]), .C (inC[0]), .ZN (n_3));
  MAOI222D0 p8054A(.A (inA[5]), .B (inC[5]), .C (inB[5]), .ZN (n_2));
  MAOI222D0 p8404A(.A (inA[1]), .B (inC[1]), .C (inB[1]), .ZN (n_1));
  MAOI222D0 p8260A(.A (inA[3]), .B (inC[3]), .C (inB[3]), .ZN (n_0));
endmodule

module majorityVoter_WIDTH8_2(inA, inB, inC, out, tmrErr);
  input [7:0] inA, inB, inC;
  output [7:0] out;
  output tmrErr;
  wire [7:0] inA, inB, inC;
  wire [7:0] out;
  wire tmrErr;
  wire n_0, n_1, n_2, n_3, n_8, n_9, n_10, n_11;
  INVD1 Fp8479A(.I (n_11), .ZN (out[2]));
  INVD1 Fp8068A(.I (n_10), .ZN (out[6]));
  INVD1 Fp7968A(.I (n_9), .ZN (out[7]));
  INVD1 Fp8265A(.I (n_8), .ZN (out[4]));
  MAOI222D0 p8368A(.A (inA[2]), .B (inC[2]), .C (inB[2]), .ZN (n_11));
  MAOI222D1 p7955A(.A (inC[6]), .B (inA[6]), .C (inB[6]), .ZN (n_10));
  MAOI222D0 p7854A(.A (inA[7]), .B (inC[7]), .C (inB[7]), .ZN (n_9));
  MAOI222D0 p8156A(.A (inC[4]), .B (inA[4]), .C (inB[4]), .ZN (n_8));
  INVD1 Fp8631A(.I (n_3), .ZN (out[0]));
  INVD1 Fp8167A(.I (n_2), .ZN (out[5]));
  INVD1 Fp8521A(.I (n_1), .ZN (out[1]));
  INVD1 Fp8373A(.I (n_0), .ZN (out[3]));
  MAOI222D1 p8511A(.A (inA[0]), .B (inB[0]), .C (inC[0]), .ZN (n_3));
  MAOI222D0 p8054A(.A (inA[5]), .B (inC[5]), .C (inB[5]), .ZN (n_2));
  MAOI222D0 p8404A(.A (inA[1]), .B (inC[1]), .C (inB[1]), .ZN (n_1));
  MAOI222D0 p8260A(.A (inA[3]), .B (inC[3]), .C (inB[3]), .ZN (n_0));
endmodule

module accFullTMR(clkA, clkB, clkC, rstA, rstB, rstC, dinA, dinB, dinC,
     doutA, doutB, doutC);
  input clkA, clkB, clkC, rstA, rstB, rstC;
  input [7:0] dinA, dinB, dinC;
  output [7:0] doutA, doutB, doutC;
  wire clkA, clkB, clkC, rstA, rstB, rstC;
  wire [7:0] dinA, dinB, dinC;
  wire [7:0] doutA, doutB, doutC;
  wire [7:0] doutNextA;
  wire [7:0] doutNextB;
  wire [7:0] doutNextC;
  wire [7:0] doutNextVotedA;
  wire [7:0] doutNextVotedB;
  wire [7:0] doutNextVotedC;
  wire UNCONNECTED, UNCONNECTED0, UNCONNECTED1, n_0, n_1, n_2;
  add_unsigned add_45_32(.A (doutA), .B (dinA), .Z (doutNextA));
  add_unsigned_16 add_46_32(.A (doutB), .B (dinB), .Z (doutNextB));
  add_unsigned_15 add_47_32(.A (doutC), .B (dinC), .Z (doutNextC));
  majorityVoter_WIDTH8 doutNextVoterA(.inA (doutNextA), .inB
       (doutNextB), .inC (doutNextC), .out (doutNextVotedA), .tmrErr
       (UNCONNECTED));
  majorityVoter_WIDTH8_1 doutNextVoterB(.inA (doutNextA), .inB
       (doutNextB), .inC (doutNextC), .out (doutNextVotedB), .tmrErr
       (UNCONNECTED0));
  majorityVoter_WIDTH8_2 doutNextVoterC(.inA (doutNextA), .inB
       (doutNextB), .inC (doutNextC), .out (doutNextVotedC), .tmrErr
       (UNCONNECTED1));
  DFCNQD1 \doutA_reg[1] (.CDN (n_2), .CP (clkA), .D
       (doutNextVotedA[1]), .Q (doutA[1]));
  DFCNQD1 \doutA_reg[7] (.CDN (n_2), .CP (clkA), .D
       (doutNextVotedA[7]), .Q (doutA[7]));
  DFCNQD1 \doutA_reg[0] (.CDN (n_2), .CP (clkA), .D
       (doutNextVotedA[0]), .Q (doutA[0]));
  DFCNQD1 \doutA_reg[2] (.CDN (n_2), .CP (clkA), .D
       (doutNextVotedA[2]), .Q (doutA[2]));
  DFCNQD1 \doutA_reg[5] (.CDN (n_2), .CP (clkA), .D
       (doutNextVotedA[5]), .Q (doutA[5]));
  DFCNQD1 \doutA_reg[4] (.CDN (n_2), .CP (clkA), .D
       (doutNextVotedA[4]), .Q (doutA[4]));
  DFCNQD1 \doutA_reg[3] (.CDN (n_2), .CP (clkA), .D
       (doutNextVotedA[3]), .Q (doutA[3]));
  DFCNQD1 \doutA_reg[6] (.CDN (n_2), .CP (clkA), .D
       (doutNextVotedA[6]), .Q (doutA[6]));
  INVD1 Fp9999971A(.I (rstA), .ZN (n_2));
  DFCNQD1 \doutB_reg[1] (.CDN (n_1), .CP (clkB), .D
       (doutNextVotedB[1]), .Q (doutB[1]));
  DFCNQD1 \doutB_reg[7] (.CDN (n_1), .CP (clkB), .D
       (doutNextVotedB[7]), .Q (doutB[7]));
  DFCNQD1 \doutB_reg[0] (.CDN (n_1), .CP (clkB), .D
       (doutNextVotedB[0]), .Q (doutB[0]));
  DFCNQD1 \doutB_reg[2] (.CDN (n_1), .CP (clkB), .D
       (doutNextVotedB[2]), .Q (doutB[2]));
  DFCNQD1 \doutB_reg[5] (.CDN (n_1), .CP (clkB), .D
       (doutNextVotedB[5]), .Q (doutB[5]));
  DFCNQD1 \doutB_reg[4] (.CDN (n_1), .CP (clkB), .D
       (doutNextVotedB[4]), .Q (doutB[4]));
  DFCNQD1 \doutB_reg[3] (.CDN (n_1), .CP (clkB), .D
       (doutNextVotedB[3]), .Q (doutB[3]));
  DFCNQD1 \doutB_reg[6] (.CDN (n_1), .CP (clkB), .D
       (doutNextVotedB[6]), .Q (doutB[6]));
  INVD1 Fp9999971A38(.I (rstB), .ZN (n_1));
  DFCNQD1 \doutC_reg[1] (.CDN (n_0), .CP (clkC), .D
       (doutNextVotedC[1]), .Q (doutC[1]));
  DFCNQD1 \doutC_reg[7] (.CDN (n_0), .CP (clkC), .D
       (doutNextVotedC[7]), .Q (doutC[7]));
  DFCNQD1 \doutC_reg[0] (.CDN (n_0), .CP (clkC), .D
       (doutNextVotedC[0]), .Q (doutC[0]));
  DFCNQD1 \doutC_reg[2] (.CDN (n_0), .CP (clkC), .D
       (doutNextVotedC[2]), .Q (doutC[2]));
  DFCNQD1 \doutC_reg[5] (.CDN (n_0), .CP (clkC), .D
       (doutNextVotedC[5]), .Q (doutC[5]));
  DFCNQD1 \doutC_reg[4] (.CDN (n_0), .CP (clkC), .D
       (doutNextVotedC[4]), .Q (doutC[4]));
  DFCNQD1 \doutC_reg[3] (.CDN (n_0), .CP (clkC), .D
       (doutNextVotedC[3]), .Q (doutC[3]));
  DFCNQD1 \doutC_reg[6] (.CDN (n_0), .CP (clkC), .D
       (doutNextVotedC[6]), .Q (doutC[6]));
  INVD1 Fp9999971A39(.I (rstC), .ZN (n_0));
endmodule


module AN2D0 (A1, A2, Z);
    input A1, A2;
    output Z;
endmodule

module INVD1 (I, ZN);
    input I;
    output ZN;
endmodule

module FA1D0 (A, B, CI, S, CO);
  input		A, B, CI;
  output	S, CO;
endmodule

module MAOI222D0 (A, B, C, ZN);
    input A, B, C;
    output ZN;
endmodule

module MAOI222D1 (A, B, C, ZN);
    input A, B, C;
    output ZN;
endmodule

module DFCNQD1 (D, CP, CDN, Q);
    // tmrg seu_reset CDN
    // tmrg seu_set   SDN
    input D, CP, CDN;
    output Q;
endmodule

module HA1D0 (A, B, S, CO);
  input	 	A, B;
  output	S, CO;
endmodule

module XOR3D1 (A1, A2, A3, Z);
  input A1, A2, A3;
  output Z;
endmodule

module PH31P_2 ( L1, L2,                 CLK1,  CLK2,  CLK3,  CLK4,                 I,     DATA1, DATA2, DATA3);
    output L1;
    output L2;
    input CLK1;
    input CLK2;
    input CLK3;
    input CLK4;
    input I;
    input DATA1;
    input DATA2;
    input DATA3;
endmodule
module PH3P_2 ( L1OUT, L2OUT,                CLK1,  CLK2,  CLK3,  CLK4,  CLK5,  CLK6,                DATA1, DATA2, DATA3, DATA4, DATA5, DATA6);
    output L1OUT;
    output L2OUT;
    input CLK1;
    input CLK2;
    input CLK3;
    input CLK4;
    input CLK5;
    input CLK6;
    input DATA1;
    input DATA2;
    input DATA3;
    input DATA4;
    input DATA5;
    input DATA6;
endmodule
module PH3PRD (LOUT, CLK1, CLK2, CLK3, DATA1, DATA2, DATA3, RESET);
    output LOUT; //Note: DO NOT declare LOUT as reg here!  It is done in the PH2PRD instantiation
    input CLK1;
    input CLK2;
    input CLK3;
    input DATA1;
    input DATA2;
    input DATA3;
    input RESET;
endmodule
module PH3P (LOUT, CLK1, CLK2, CLK3, DATA1, DATA2, DATA3);
    output LOUT; //Note: DO NOT declare LOUT as reg here!  It is done in the PH2P instantiation
    input CLK1;
    input CLK2;
    input CLK3;
    input DATA1;
    input DATA2;
    input DATA3;
endmodule
module PH5PRD (LOUT, CLK1, CLK2, CLK3, CLK4, CLK5, DATA1, DATA2, DATA3, DATA4, DATA5, RESET);
    output LOUT; //Note: DO NOT declare LOUT as reg here!  It is done in the PH2PRD instantiation
    input CLK1;
    input CLK2;
    input CLK3;
    input CLK4;
    input CLK5;
    input DATA1;
    input DATA2;
    input DATA3;
    input DATA4;
    input DATA5;
    input RESET;
endmodule
module SDFF_E (Q,QBAR,CLK,D,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_set S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  SE;
  input  SI;
endmodule
module SDFF_H (Q,QBAR,CLK,D,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  SE;
  input  SI;
endmodule
module SDFF_K (Q,QBAR,CLK,D,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  SE;
  input  SI;
endmodule
module SDFFR_E (Q,QBAR,CLK,D,RN,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_reset RN_i
    // tmrg seu_set   S_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  SE;
  input  SI;
endmodule
module SDFFR_H (Q,QBAR,CLK,D,RN,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_reset RN_i
    // tmrg seu_set   S_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  SE;
  input  SI;
endmodule
module SDFFR_K (Q,QBAR,CLK,D,RN,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_reset RN_i
    // tmrg seu_set   S_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  SE;
  input  SI;
endmodule
module SDFFR (Q,QBAR,CLK,D,RN,S_i,SE,SI,notifier);
    // tmrg seu_set   S_i
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input   RN;
  input   S_i;
  input   SE;
  input   SI;
  input   notifier;
endmodule
module SDFFS_E (Q,QBAR,CLK,D,S,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  S;
  input  SE;
  input  SI;
endmodule
module SDFFS_H (Q,QBAR,CLK,D,S,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  S;
  input  SE;
  input  SI;
endmodule
module SDFFS_K (Q,QBAR,CLK,D,S,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  S;
  input  SE;
  input  SI;
endmodule
module SDFFSR_E (Q,QBAR,CLK,D,RN,S,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
  input  SE;
  input  SI;
endmodule
module SDFFSR_H (Q,QBAR,CLK,D,RN,S,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
  input  SE;
  input  SI;
endmodule
module SDFFSR_K (Q,QBAR,CLK,D,RN,S,SE,SI/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
  input  SE;
  input  SI;
endmodule
module SDFFSR (Q,QBAR,CLK,D,RN,S,SE,SI,notifier);
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input   RN;
  input   S;
  input   SE;
  input   SI;
  input   notifier;
endmodule
module SDFFS (Q,QBAR,CLK,D,RN_i, S,SE,SI,notifier);
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input RN_i;
  input   S;
  input   SE;
  input   SI;
  input   notifier;
endmodule
module SDFF (Q,QBAR,CLK,D,SE,SI,RN_i,S_i,notifier);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input   SE;
  input   SI;
  input   RN_i;
  input   S_i;
  input   notifier;
endmodule
module SLATSR_E (Q,QBAR,CLK,D,RN,S,SE,SI/*,VDD,GND,NW,SX*/);
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
  input  SE;
  input  SI;
endmodule
module SLATSR_H (Q,QBAR,CLK,D,RN,S,SE,SI/*,VDD,GND,NW,SX*/);
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
  input  SE;
  input  SI;
endmodule
module SLATSR_K (Q,QBAR,CLK,D,RN,S,SE,SI/*,VDD,GND,NW,SX*/);
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
  input  SE;
  input  SI;
endmodule
module SLATSR (Q,QBAR,CLK,D,RN,S,SE,SI,notifier);
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input   RN;
  input   S;
  input   SE;
  input   SI;
  input   notifier;
endmodule
module SOLATCH (L2,A,B,I);
  output  L2;
  input   A;
  input   B;
  input   I;
endmodule
module TERM_A (A/*,VDD,GND,NW,SX*/);
  input  A;
endmodule
module TERM_B (A/*,VDD,GND,NW,SX*/);
  input  A;
endmodule
module TERM_C (A/*,VDD,GND,NW,SX*/);
  input  A;
endmodule
module TERM_D (A/*,VDD,GND,NW,SX*/);
  input  A;
endmodule
module TERM (A);
  input   A;
endmodule
module TIX ( XOUT );
    output XOUT;
endmodule
module XNOR2_A (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XNOR2_B (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XNOR2_C (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XNOR2_D (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XNOR2_E (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XNOR2_F (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XNOR2_H (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XNOR2_I (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XNOR2_J (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XNOR2 (Z,A,B);
  output  Z;
  input   A;
  input   B;
endmodule
module XNOR3_B (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XNOR3_C (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XNOR3_D (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XNOR3_E (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XNOR3_F (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XNOR3_H (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XNOR3_I (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XNOR3 (Z,A,B,C);
  output  Z;
  input   A;
  input   B;
  input   C;
endmodule
module XOR2_A (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_B (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_C (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_D (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_E (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_F (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_H (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_I (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_J (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_K (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2_L (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module XOR2 (Z,A,B);
  output  Z;
  input   A;
  input   B;
endmodule
module XOR3_B (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XOR3_C (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XOR3_D (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XOR3_E (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XOR3_F (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XOR3_H (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XOR3_I (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module XOR3 (Z,A,B,C);
  output  Z;
  input   A;
  input   B;
  input   C;
endmodule
module XOR8_E (Z,A,B,C,D,E,F,G,H/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
  input  E;
  input  F;
  input  G;
  input  H;
endmodule
module XOR8_H (Z,A,B,C,D,E,F,G,H/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
  input  E;
  input  F;
  input  G;
  input  H;
endmodule
module XOR8_J (Z,A,B,C,D,E,F,G,H/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
  input  E;
  input  F;
  input  G;
  input  H;
endmodule
module XOR8 (Z,A,B,C,D,E,F,G,H);
  output  Z;
  input   A;
  input   B;
  input   C;
  input   D;
  input   E;
  input   F;
  input   G;
  input   H;
endmodule
module XOR9_E (Z,A,B,C,D,E,F,G,H,I/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
  input  E;
  input  F;
  input  G;
  input  H;
  input  I;
endmodule
module XOR9_H (Z,A,B,C,D,E,F,G,H,I/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
  input  E;
  input  F;
  input  G;
  input  H;
  input  I;
endmodule
module XOR9_J (Z,A,B,C,D,E,F,G,H,I/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
  input  E;
  input  F;
  input  G;
  input  H;
  input  I;
endmodule
module XOR9 (Z,A,B,C,D,E,F,G,H,I);
  output  Z;
  input   A;
  input   B;
  input   C;
  input   D;
  input   E;
  input   F;
  input   G;
  input   H;
  input   I;
endmodule
module MUX21I_E (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21I_F (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21_I (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21I (Z,D0,D1,SD);
  output  Z;
  input   D0;
  input   D1;
  input   SD;
endmodule
module MUX21_NPMOS (MXOUT, SEL, D0, D1);
  output MXOUT;
  input  SEL;
  input  D0;
  input  D1;
endmodule
module MUX21 (Z,D0,D1,SD);
  output  Z;
  input   D0;
  input   D1;
  input   SD;
endmodule
module MUX41_D (Z,D0,D1,D2,D3,SD1,SD2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  D2;
  input  D3;
  input  SD1;
  input  SD2;
endmodule
module MUX41_F (Z,D0,D1,D2,D3,SD1,SD2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  D2;
  input  D3;
  input  SD1;
  input  SD2;
endmodule
module MUX41_J (Z,D0,D1,D2,D3,SD1,SD2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  D2;
  input  D3;
  input  SD1;
  input  SD2;
endmodule
module MUX41 (Z,D0,D1,D2,D3,SD1,SD2);
  output  Z;
  input   D0;
  input   D1;
  input   D2;
  input   D3;
  input   SD1;
  input   SD2;
endmodule
module  MUXDLATCH2 (L2,A,B,C,D0,D1,I,SD);
  output  L2;
  input   A;
  input   B;
  input   C;
  input   D0, D1;
  input   I;
  input   SD;
endmodule
module  MUXDLATCH (L2,A,B,C,D,I,SD);
  output  L2;
  input   A;
  input   B;
  input   C;
  input   D;
  input   I;
  input   SD;
endmodule
module NAND2_A (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2BAL_E (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2BAL_H (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2BAL_J (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2BAL_L (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2BAL (Z,A,B);
  output  Z;
  input   A;
  input   B;
endmodule
module NAND2_B (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_C (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_D (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_E (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_F (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_H (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_I (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_J (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_K (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_L (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2_M (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NAND2 (Z,A,B);
  output  Z;
  input   A;
  input   B;
endmodule
module NAND3_A (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3_B (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3_C (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3_D (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3_E (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3_F (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3_H (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3_I (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3_J (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3_K (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NAND3 (Z,A,B,C);
  output  Z;
  input   A;
  input   B;
  input   C;
endmodule
module NAND4_A (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NAND4_B (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NAND4_C (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NAND4_D (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NAND4_E (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NAND4_F (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NAND4 (Z,A,B,C,D);
  output  Z;
  input   A;
  input   B;
  input   C;
  input   D;
endmodule
module NOR2_A (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NOR2_B (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NOR2_C (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NOR2_D (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NOR2_E (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NOR2_F (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NOR2_H (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NOR2_I (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NOR2_J (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module NOR2 (Z,A,B);
  output  Z;
  input   A;
  input   B;
endmodule
module NOR3_A (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NOR3_B (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NOR3_C (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NOR3_D (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NOR3_E (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NOR3_F (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module NOR3 (Z,A,B,C);
  output  Z;
  input   A;
  input   B;
  input   C;
endmodule
module NOR4_A (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NOR4_B (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NOR4_C (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NOR4_D (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module NOR4 (Z,A,B,C,D);
  output  Z;
  input   A;
  input   B;
  input   C;
  input   D;
endmodule
module NOTX (out,in,notifier,reset);
  output out;
  input  in;
  input  notifier;
  input  reset;
endmodule
module OA21_B (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OA21_C (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OA21_D (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OA21_E (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OA21_F (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OA21_H (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OA21_I (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OA21_J (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OA21_K (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OA21 (Z,A1,A2,B);
  output  Z;
  input   A1;
  input   A2;
  input   B;
endmodule
module OA2222_B (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module OA2222_C (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module OA2222_D (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module OA2222_E (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module OA2222_F (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module OA2222 (Z,A1,A2,B1,B2,C1,C2,D1,D2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
  input   C1;
  input   C2;
  input   D1;
  input   D2;
endmodule
module OA222_B (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module OA222_C (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module OA222_D (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module OA222_E (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module OA222_F (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module OA222 (Z,A1,A2,B1,B2,C1,C2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
  input   C1;
  input   C2;
endmodule
module OA22_B (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OA22_C (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OA22_D (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OA22_E (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OA22_F (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OA22_H (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OA22_I (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OA22_J (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OA22_K (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OA22 (Z,A1,A2,B1,B2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
endmodule
module OAI21_A (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OAI21_B (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OAI21_C (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OAI21_D (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OAI21_E (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OAI21_F (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OAI21_H (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module OAI21 (Z,A1,A2,B);
  output  Z;
  input   A1;
  input   A2;
  input   B;
endmodule
module OAI2222_E (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module OAI2222_H (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module OAI2222 (Z,A1,A2,B1,B2,C1,C2,D1,D2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
  input   C1;
  input   C2;
  input   D1;
  input   D2;
endmodule
module OAI222_E (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module OAI222_H (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module OAI222 (Z,A1,A2,B1,B2,C1,C2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
  input   C1;
  input   C2;
endmodule
module OAI22_A (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OAI22_B (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OAI22_C (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OAI22_D (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OAI22_E (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OAI22_F (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module OAI22 (Z,A1,A2,B1,B2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
endmodule
module OR2_B (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module OR2_C (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module OR2_D (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module OR2_E (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module OR2_F (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module OR2_H (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module OR2_I (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module OR2_J (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module OR2_K (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module OR2 (Z,A,B);
  output  Z;
  input   A;
  input   B;
endmodule
module OR3_B (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module OR3_C (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module OR3_D (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module OR3_E (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module OR3_F (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module OR3_H (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module OR3_I (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module OR3_J (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module OR3_K (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module OR3 (Z,A,B,C);
  output  Z;
  input   A;
  input   B;
  input   C;
endmodule
module OR4_B (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module OR4_C (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module OR4_D (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module OR4_E (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module OR4_F (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module OR4_H (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module OR4_I (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module OR4_J (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module OR4_K (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module OR4 (Z,A,B,C,D);
  output  Z;
  input   A;
  input   B;
  input   C;
  input   D;
endmodule
module PH21P_2 ( L1, L2, CLK1,  CLK2,  CLK3, I, DATA1, DATA2);
    output L1;
    output L2;
    input CLK1;
    input CLK2;
    input CLK3;
    input I;
    input DATA1;
    input DATA2;
endmodule
module PH2P_2 ( L1OUT, L2OUT, CLK1,  CLK2,  CLK3,  CLK4, DATA1, DATA2, DATA3, DATA4);
    output L1OUT;
    output L2OUT;
    input CLK1;
    input CLK2;
    input CLK3;
    input CLK4;
    input DATA1;
    input DATA2;
    input DATA3;
    input DATA4;
endmodule
module AOI21_H (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AOI21 (Z,A1,A2,B);
  output  Z;
  input   A1;
  input   A2;
  input   B;
endmodule
module AOI2222_F (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module AOI2222_H (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module AOI2222_I (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module AOI2222 (Z,A1,A2,B1,B2,C1,C2,D1,D2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
  input   C1;
  input   C2;
  input   D1;
  input   D2;
endmodule
module AOI222_F (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module AOI222_H (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module AOI222_I (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module AOI222 (Z,A1,A2,B1,B2,C1,C2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
  input   C1;
  input   C2;
endmodule
module AOI22_A (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AOI22_B (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AOI22_C (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AOI22_D (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AOI22_E (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AOI22_F (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AOI22_H (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AOI22 (Z,A1,A2,B1,B2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
endmodule
module AOI33_C (Z,A1,A2,A3,B1,B2,B3/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  B1;
  input  B2;
  input  B3;
endmodule
module AOI33_E (Z,A1,A2,A3,B1,B2,B3/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  B1;
  input  B2;
  input  B3;
endmodule
module AOI33_H (Z,A1,A2,A3,B1,B2,B3/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  B1;
  input  B2;
  input  B3;
endmodule
module AOI33 (Z,A1,A2,A3,B1,B2,B3);
  output  Z;
  input   A1;
  input   A2;
  input   A3;
  input   B1;
  input   B2;
  input   B3;
endmodule
module AOI44_C (Z,A1,A2,A3,A4,B1,B2,B3,B4/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  A4;
  input  B1;
  input  B2;
  input  B3;
  input  B4;
endmodule
module AOI44_E (Z,A1,A2,A3,A4,B1,B2,B3,B4/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  A4;
  input  B1;
  input  B2;
  input  B3;
  input  B4;
endmodule
module AOI44_H (Z,A1,A2,A3,A4,B1,B2,B3,B4/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  A4;
  input  B1;
  input  B2;
  input  B3;
  input  B4;
endmodule
module AOI44 (Z,A1,A2,A3,A4,B1,B2,B3,B4);
  output  Z;
  input   A1;
  input   A2;
  input   A3;
  input   A4;
  input   B1;
  input   B2;
  input   B3;
  input   B4;
endmodule
module BD (PAD, PT);
endmodule
module BUFFER_C (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_D (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_E (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_F (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_H (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_I (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_J (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_K (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_L (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_M (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_N (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER_O (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module BUFFER (Z,A);
  output  Z;
  input   A;
endmodule
module BUFX (out,in,notifier,reset);
  output out;
  input  in;
  input  notifier;
  input  reset;
endmodule
module CLKI_I (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLKI_K (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLKI_M (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLKI_O (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLKI_Q (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLK_I (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLKI (Z,A);
  output  Z;
  input   A;
endmodule
module CLK_K (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLK_M (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLK_O (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLK_Q (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module CLK (Z,A);
  output  Z;
  input   A;
endmodule
module COMP2_B (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module COMP2_C (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module COMP2_D (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module COMP2_E (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module COMP2_F (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module COMP2 (Z,A1,A2,B1,B2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
endmodule
module DECAP_C (LT/*,VDD,GND,NW,SX*/);
  input  LT;
endmodule
module DECAP_D (LT/*,VDD,GND,NW,SX*/);
  input  LT;
endmodule
module DECAP_E (LT/*,VDD,GND,NW,SX*/);
  input  LT;
endmodule
module DECAP (LT);
  input   LT;
endmodule
module DELAY4_C (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module DELAY4_F (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module DELAY4_J (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module DELAY4 (Z,A);
  output  Z;
  input   A;
endmodule
module DELAY6_C (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module DELAY6_F (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module DELAY6_J (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module DELAY6_M (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module DELAY6 (Z,A);
  output  Z;
  input   A;
endmodule
module DFF_E (Q,QBAR,CLK,D/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
endmodule
module DFF_H (Q,QBAR,CLK,D/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
endmodule
module DFF_K (Q,QBAR,CLK,D/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
endmodule
module DFFMR (L2,D,E,R,notifier);
input D,E,R,notifier;
output L2;
endmodule
module DFFMS (L2,D,E,S,notifier);
input D,E,S,notifier;
output L2;
endmodule
module DFFR_E (Q,QBAR,CLK,D,RN/*,VDD,GND,NW,SX*/);
    // tmrg seu_reset RN_i
    // tmrg seu_set   S_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
endmodule
module DFFR_H (Q,QBAR,CLK,D,RN/*,VDD,GND,NW,SX*/);
    // tmrg seu_reset RN_i
    // tmrg seu_set   S_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
endmodule
module DFFR_K (Q,QBAR,CLK,D,RN/*,VDD,GND,NW,SX*/);
    // tmrg seu_reset RN_i
    // tmrg seu_set   S_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
endmodule
module DFFR (Q,QBAR,CLK,D,RN,S_i,notifier);
    // tmrg seu_set   S_i
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input   RN;
  input S_i;
  input   notifier;
endmodule
module DFFS_E (Q,QBAR,CLK,D,S/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  S;
endmodule
module DFFS_H (Q,QBAR,CLK,D,S/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  S;
endmodule
module DFFS_K (Q,QBAR,CLK,D,S/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  S;
endmodule
module DFFSR_CBS (L2,D,E,S,R);
input D,E,S,R;
output L2;
endmodule
module DFFSR_E (Q,QBAR,CLK,D,RN,S/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
endmodule
module DFFSR_H (Q,QBAR,CLK,D,RN,S/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
endmodule
module DFFSR_K (Q,QBAR,CLK,D,RN,S/*,VDD,GND,NW,SX*/);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
endmodule
module DFFSR_L2N_CBS (L2,L2N,D,E,S,R);
input D,E,S,R;
output L2,L2N;
endmodule
module DFFSR (Q,QBAR,CLK,D,RN,S,notifier);
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input   RN;
  input   S;
  input   notifier;
endmodule
module DFFS (Q,QBAR,CLK,D,RN_i,S,notifier);
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input RN_i;
  input   S;
  input   notifier;
endmodule
module DFF (Q,QBAR,CLK,D,RN_i,S_i,notifier);
    // tmrg seu_set   S_i
    // tmrg seu_reset RN_i
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input RN_i;
  input S_i;
  input   notifier;
endmodule
module DHCIO ( ZOUT, DTE, PAD, RI );
    output ZOUT; reg zout; reg ztmp;
    input DTE ;
    input PAD ;
    input RI  ;
endmodule
module DIV2N (clkDiv, divider, inClk);
   output     clkDiv;
   input      inClk;
     input [2:0] power;
endmodule
module DIV5S6MP (clkDiv, M0, M1, inClk);
   output     clkDiv;
   input      M0;
   input      M1;
   input      inClk;
endmodule
module DIV_N (clkDiv, divider, inClk, min, max/*,VDD,GND,NW,SX*/);
   output     clkDiv;
   input      inClk;
endmodule
module DLATCH (L2,A,B,C,D,I);
  output  L2;
  input   A;
  input   B;
  input   C;
  input   D;
  input   I;
endmodule
module DLY90 (dlyClk, inClk);
  output dlyClk;
  input  inClk;
endmodule
module FREQDIV (clk_2, clk);
   output clk_2;
   input  clk;
endmodule
module GRAM_SRL_1 (P10,P30,PA0,PB0,PC0,PD0,PI0,INPHASE/*,VDD,GND,NW,SX*/);
  output  P10;
  output  P30;
  input   PA0;
  input   PB0;
  input   PC0;
  input   PD0;
  input   PI0;
  input   INPHASE;
endmodule
module GRAM_SRL_3 (P30,PA0,PB0,PC0,PD0,PI0/*,VDD,GND,NW,SX*/);
  output  P30;
  input   PA0;
  input   PB0;
  input   PC0;
  input   PD0;
  input   PI0;
endmodule
module GRAM_SRL_4 (P30,PA0,PB0,PI0/*,VDD,GND,NW,SX*/);
  output  P30;
  input   PA0;
  input   PB0;
  input   PI0;
endmodule
module IBMFREQDIV (CLK2,CLK2N,CLK,CLEAR);
  output CLK2;
  output CLK2N;
  input  CLK;
  input  CLEAR;
endmodule
module INVERT_A (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERTBAL_E (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERTBAL_H (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERTBAL_J (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERTBAL_L (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERTBAL (Z,A);
  output  Z;
  input   A;
endmodule
module INVERT_B (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_C (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_D (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_E (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_F (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_H (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_I (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_J (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_K (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_L (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_M (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_N (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT_O (Z,A/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
endmodule
module INVERT (Z,A);
  output  Z;
  input   A;
endmodule
module LATSR_E (Q,QBAR,CLK,D,RN,S/*,VDD,GND,NW,SX*/);
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
endmodule
module LATSR_H (Q,QBAR,CLK,D,RN,S/*,VDD,GND,NW,SX*/);
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
endmodule
module LATSR_K (Q,QBAR,CLK,D,RN,S/*,VDD,GND,NW,SX*/);
  output  Q;
  output  QBAR;
  input  CLK;
  input  D;
  input  RN;
  input  S;
endmodule
module LATSR (Q,QBAR,CLK,D,RN,S,notifier);
  output  Q;
  output  QBAR;
  input   CLK;
  input   D;
  input   RN;
  input   S;
  input   notifier;
endmodule
module LPRABYP_P2 (RBL0P1, RBL1P1, SO1, SO2, AT, BT, MS, SI1, SI2, RWL0P1, RWL1P1, WBLP1, WBS0P1T, WBS1P1T, WWL0P1T, WWL1P1T);
   input  AT;
   input  BT;
   input  MS;
   input  RWL0P1;
   input  RWL1P1;
   input  WWL0P1T;
   input  WWL1P1T;
   input  WBS0P1T;
   input  WBS1P1T;
   input  WBLP1;
   input  SI1;
   input  SI2;
   output SO1;
   output SO2;
   output RBL0P1;
   output RBL1P1;
endmodule
module LPRABYP_P3 (RBL0P1, RBL0P2, RBL1P1, RBL1P2, SO1, SO2, AT, BT, MS, SI1, SI2, RWL0P1, RWL0P2, RWL1P1, RWL1P2, WBLP1,WBS0P1T, WBS1P1T, WWL0P1T, WWL1P1T);
   input  AT;
   input  BT;
   input  MS;
   input  RWL0P1;
   input  RWL1P1;
   input  RWL0P2;
   input  RWL1P2;
   input  WWL0P1T;
   input  WWL1P1T;
   input  WBS0P1T;
   input  WBS1P1T;
   input  WBLP1;
   input  SI1;
   input  SI2;
   output SO1;
   output SO2;
   output RBL0P1;
   output RBL1P1;
   output RBL0P2;
   output RBL1P2;
endmodule
module LPRABYP_P4 (RBL0P1, RBL0P2, RBL1P1, RBL1P2, SO1, SO2, AT, BT, MS, SI1, SI2, RWL0P1, RWL0P2, RWL1P1, RWL1P2, WBLP1, WBLP2,WBS0P1T, WBS0P2T, WBS1P1T,WBS1P2T, WWL0P1T, WWL0P2T, WWL1P1T, WWL1P2T);
   input  AT;
   input  BT;
   input  MS;
   input  RWL0P1;
   input  RWL1P1;
   input  RWL0P2;
   input  RWL1P2;
   input  WWL0P1T;
   input  WWL1P1T;
   input  WWL0P2T;
   input  WWL1P2T;
   input  WBS0P1T;
   input  WBS1P1T;
   input  WBS0P2T;
   input  WBS1P2T;
   input  WBLP1;
   input  WBLP2;
   input  SI1;
   input  SI2;
   output SO1;
   output SO2;
   output RBL0P1;
   output RBL1P1;
   output RBL0P2;
   output RBL1P2;
endmodule
module LPRABYP_P5 (RBL0P1, RBL0P2, RBL0P3, RBL1P1, RBL1P2, RBL1P3, SO1, SO2, AT, BT, MS, SI1, SI2,RWL0P1, RWL0P2, RWL0P3, RWL1P1, RWL1P2, RWL1P3,WBLP1, WBLP2, WBS0P1T, WBS0P2T, WBS1P1T, WBS1P2T,WWL0P1T, WWL0P2T, WWL1P1T, WWL1P2T);
 input    AT;
 input    BT;
 input    MS;
 input    RWL0P1;
 input    RWL1P1;
 input    RWL0P2;
 input    RWL1P2;
 input    RWL0P3;
 input    RWL1P3;
 input    WWL0P1T;
 input    WWL1P1T;
 input    WWL0P2T;
 input    WWL1P2T;
 input    WBS0P1T;
 input    WBS1P1T;
 input    WBS0P2T;
 input    WBS1P2T;
 input    WBLP1;
 input    WBLP2;
 input    SI1;
 input    SI2;
 output   SO1;
 output   SO2;
 output   RBL0P1;
 output   RBL1P1;
 output   RBL0P2;
 output   RBL1P2;
 output   RBL0P3;
 output   RBL1P3;
endmodule
module LPRABYP_P6 (RBL0P1, RBL0P2, RBL0P3, RBL0P4, RBL1P1, RBL1P2, RBL1P3, RBL1P4,SO1, SO2, AT, BT, MS, SI1, SI2,RWL0P1, RWL0P2, RWL0P3, RWL0P4, RWL1P1, RWL1P2, RWL1P3, RWL1P4,WBLP1, WBLP2, WBS0P1T, WBS0P2T, WBS1P1T, WBS1P2T,WWL0P1T, WWL0P2T, WWL1P1T, WWL1P2T);
 input    AT;
 input    BT;
 input    MS;
 input    RWL0P1;
 input    RWL1P1;
 input    RWL0P2;
 input    RWL1P2;
 input    RWL0P3;
 input    RWL1P3;
 input    RWL0P4;
 input    RWL1P4;
 input    WWL0P1T;
 input    WWL1P1T;
 input    WWL0P2T;
 input    WWL1P2T;
 input    WBS0P1T;
 input    WBS1P1T;
 input    WBS0P2T;
 input    WBS1P2T;
 input    WBLP1;
 input    WBLP2;
 input    SI1;
 input    SI2;
 output   SO1;
 output   SO2;
 output   RBL0P1;
 output   RBL1P1;
 output   RBL0P2;
 output   RBL1P2;
 output   RBL0P3;
 output   RBL1P3;
 output   RBL0P4;
 output   RBL1P4;
endmodule
module MUX21BAL_H (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21BAL_J (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21BAL_L (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21BAL (Z,D0,D1,SD);
  output  Z;
  input   D0;
  input   D1;
  input   SD;
endmodule
module MUX21_C (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21_D (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21_E (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21_F (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21_H (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21I_B (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21I_C (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module MUX21I_D (Z,D0,D1,SD/*,VDD,GND,NW,SX*/);
  output  Z;
  input  D0;
  input  D1;
  input  SD;
endmodule
module ADDF_B (COUT,SUM,A,B,CIN/*,VDD,GND,NW,SX*/);
  output  COUT;
  output  SUM;
  input  A;
  input  B;
  input  CIN;
endmodule
module ADDF_C (COUT,SUM,A,B,CIN/*,VDD,GND,NW,SX*/);
  output  COUT;
  output  SUM;
  input  A;
  input  B;
  input  CIN;
endmodule
module ADDF_D (COUT,SUM,A,B,CIN/*,VDD,GND,NW,SX*/);
  output  COUT;
  output  SUM;
  input  A;
  input  B;
  input  CIN;
endmodule
module ADDF_E (COUT,SUM,A,B,CIN/*,VDD,GND,NW,SX*/);
  output  COUT;
  output  SUM;
  input  A;
  input  B;
  input  CIN;
endmodule
module ADDF_F (COUT,SUM,A,B,CIN/*,VDD,GND,NW,SX*/);
  output  COUT;
  output  SUM;
  input  A;
  input  B;
  input  CIN;
endmodule
module ADDF (COUT,SUM,A,B,CIN);
  output  COUT;
  output  SUM;
  input   A;
  input   B;
  input   CIN;
endmodule
module AND2_B (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module AND2_C (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module AND2_D (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module AND2_E (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module AND2_F (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module AND2_H (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module AND2_I (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module AND2_J (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module AND2_K (Z,A,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
endmodule
module AND2 (Z,A,B);
  output  Z;
  input   A;
  input   B;
endmodule
module AND3_B (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module AND3_C (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module AND3_D (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module AND3_E (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module AND3_F (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module AND3_H (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module AND3_I (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module AND3_J (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module AND3_K (Z,A,B,C/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
endmodule
module AND3 (Z,A,B,C);
  output  Z;
  input   A;
  input   B;
  input   C;
endmodule
module AND4_B (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module AND4_C (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module AND4_D (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module AND4_E (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module AND4_F (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module AND4_H (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module AND4_I (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module AND4_J (Z,A,B,C,D/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A;
  input  B;
  input  C;
  input  D;
endmodule
module AND4 (Z,A,B,C,D);
  output  Z;
  input   A;
  input   B;
  input   C;
  input   D;
endmodule
module AO21_B (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AO21_C (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AO21_D (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AO21_E (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AO21_F (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AO21_H (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AO21_I (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AO21_J (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AO21_K (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AO21 (Z,A1,A2,B);
  output  Z;
  input   A1;
  input   A2;
  input   B;
endmodule
module AO2222_B (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module AO2222_C (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module AO2222_D (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module AO2222_E (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module AO2222_F (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module AO2222_H (Z,A1,A2,B1,B2,C1,C2,D1,D2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
  input  D1;
  input  D2;
endmodule
module AO2222 (Z,A1,A2,B1,B2,C1,C2,D1,D2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
  input   C1;
  input   C2;
  input   D1;
  input   D2;
endmodule
module AO222_B (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module AO222_C (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module AO222_D (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module AO222_E (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module AO222_F (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module AO222_H (Z,A1,A2,B1,B2,C1,C2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
  input  C1;
  input  C2;
endmodule
module AO222 (Z,A1,A2,B1,B2,C1,C2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
  input   C1;
  input   C2;
endmodule
module AO22_B (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AO22_C (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AO22_D (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AO22_E (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AO22_F (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AO22_H (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AO22_I (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AO22_J (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AO22_K (Z,A1,A2,B1,B2/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B1;
  input  B2;
endmodule
module AO22 (Z,A1,A2,B1,B2);
  output  Z;
  input   A1;
  input   A2;
  input   B1;
  input   B2;
endmodule
module AO33_C (Z,A1,A2,A3,B1,B2,B3/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  B1;
  input  B2;
  input  B3;
endmodule
module AO33_E (Z,A1,A2,A3,B1,B2,B3/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  B1;
  input  B2;
  input  B3;
endmodule
module AO33_H (Z,A1,A2,A3,B1,B2,B3/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  B1;
  input  B2;
  input  B3;
endmodule
module AO33 (Z,A1,A2,A3,B1,B2,B3);
  output  Z;
  input   A1;
  input   A2;
  input   A3;
  input   B1;
  input   B2;
  input   B3;
endmodule
module AO44_C (Z,A1,A2,A3,A4,B1,B2,B3,B4/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  A4;
  input  B1;
  input  B2;
  input  B3;
  input  B4;
endmodule
module AO44_E (Z,A1,A2,A3,A4,B1,B2,B3,B4/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  A4;
  input  B1;
  input  B2;
  input  B3;
  input  B4;
endmodule
module AO44_H (Z,A1,A2,A3,A4,B1,B2,B3,B4/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  A3;
  input  A4;
  input  B1;
  input  B2;
  input  B3;
  input  B4;
endmodule
module AO44 (Z,A1,A2,A3,A4,B1,B2,B3,B4);
  output  Z;
  input   A1;
  input   A2;
  input   A3;
  input   A4;
  input   B1;
  input   B2;
  input   B3;
  input   B4;
endmodule
module AOI21_A (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AOI21_B (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AOI21_C (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AOI21_D (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AOI21_E (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule
module AOI21_F (Z,A1,A2,B/*,VDD,GND,NW,SX*/);
  output  Z;
  input  A1;
  input  A2;
  input  B;
endmodule

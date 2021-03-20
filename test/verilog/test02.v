module test02(i1,i2,o1,io1,io2);
  parameter N=2,M=1;
  input i1;
  input [2:1] i2;
  output [2:1] o1;
  inout io1,io2;
  reg r1;
  reg [211:1] r2;
  reg signed [3:2] r3;
  reg [2:1] r4,r5;
  // tmrg do_not_triplicate io1 io2
endmodule

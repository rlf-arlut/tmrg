module dff(I,C,Z);
  // tmrg default triplicate
  // tmrg tmr_error true
  input I,C;
  output Z;
  wire IVoted=I;
  reg Z;
  always @(posedge C)
    Z<=IVoted;
endmodule

module inst01 (in1,in2,in3,out,clk,gate);
  // tmrg default triplicate
  // tmrg tmr_error true
  input in1,in2,in3,clk,gate;
  output out;
  wire out1,out2;
  reg out3;
  wire tmrError=1'b0;
  wire clkGated = clk&(gate|tmrError);
  assign out=out1&out2&out3;
  dff dff01(.I(in1), .C(clkGated), .Z(out1));
  dff dff02(.I(in2), .C(clkGated), .Z(out2));
  
  wire in3Voted=in3;
  always @(posedge clkGated)
    out3<=in3Voted;
endmodule

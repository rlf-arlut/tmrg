// comment
module test01( in, out, in1, out1, in2, out2 );
  input        in;
  output [5:0] out; //comment
  inout        io3;
  input [7:0]  inc;
  input        in2;
  output [1:0] out1; //comment
  inout        io1;
  input [12:0] ina;
  input [7:2]  in1;
  output       out2; //comment
  inout        io2;
  input [7:0]  inb;
  reg d;
  parameter N=2;
  parameter N1=5;
  parameter N2=3;
  
  always @(posedge clk)
    begin
      x<=#NK 2;
    end
endmodule

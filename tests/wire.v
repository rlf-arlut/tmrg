module wiretest1(input clk);
// tmrg default triplicate
reg [7:0] r0[0:13],r1;

wire [7:0] w0=r0[2],
           w1=r1^r0[0],
           w2=123,
           w3=8'h00;
endmodule

module wiretest2(input clk);
// tmrg default do_not_triplicate
reg [7:0] r0[0:13],r1;

wire [7:0] w0=r0[2],
           w1=r1^r0[0],
           w2=123,
           w3=8'h00;
endmodule

module wiretest3(input clk);
// default do_not_triplicate 
// tmrg triplicate r0 r1
reg [7:0] r0[0:13],r1;

wire [7:0] w0=r0[2],
           w1=r1^r0[0],
           w2=123,
           w3=8'h00;
endmodule

module wiretest4(input clk);
// default do_not_triplicate 
// tmrg triplicate r0 r1
reg [7:0] r0[0:13],r1;

wire [7:0] w0=r0[2],
           w1=r1^r0[0],
           w2=123,
           w3=8'h00;
endmodule


module wiretest(input clk);
  wiretest1 i1(.clk(clk));
  wiretest2 i2(.clk(clk));
  wiretest3 i3(.clk(clk));
  wiretest4 i4(.clk(clk));
endmodule

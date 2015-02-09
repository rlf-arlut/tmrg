module majorityVoter (inA, inB, inC, out);
  parameter WIDTH = 1;
  input      [(WIDTH-1):0] inA, inB, inC;
  output reg [(WIDTH-1):0] out;
  assign out = inA&inB | inA&inC | inB&inC;	
endmodule

module tmr3( in1A, in2A, out1A, clkA, rstA,
             in1B, in2B, out1B, clkB, rstB,
             in1C, in2C, out1C, clkC, rstC );
  input in1A,in2A,clkA,rstA;
  output reg out1A;

  input in1B,in2B,clkB,rstB;
  output reg out1B;

  input in1C,in2C,clkC,rstC;
  output reg out1C;

  wire out1votedA;
  wire out1votedB;
  wire out1votedC;
  majorityVoter #(.WIDTH(1)) mvA ( .inA(out1A), .inB(out1B), .inC(out1C), .out(out1votedA));
  majorityVoter #(.WIDTH(1)) mvB ( .inA(out1A), .inB(out1B), .inC(out1C), .out(out1votedB));
  majorityVoter #(.WIDTH(1)) mvC ( .inA(out1A), .inB(out1B), .inC(out1C), .out(out1votedC));
	  
  always @(posedge clkA or posedge rstA)
  begin
    if (rstA)
      out1A<=1'b0;
    else
      out1A<= in1A & (in2A ^ out1votedA);
  end

  always @(posedge clkB or posedge rstB)
  begin
    if (rstB)
      out1B<=1'b0;
    else
      out1B<= in1B & (in2B ^ out1votedB);
  end

  always @(posedge clkC or posedge rstC)
  begin
    if (rstC)
      out1C<=1'b0;
    else
      out1C<= in1C & (in2C ^ out1votedC);
  end
endmodule

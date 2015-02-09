module majorityVoter (inA, inB, inC, out);
  parameter WIDTH = 1;
  input      [(WIDTH-1):0] inA, inB, inC;
  output reg [(WIDTH-1):0] out;
  assign out = inA&inB | inA&inC | inB&inC;	
endmodule

module tmr2( in1A, in2A, out1A, clkA, rstA,
             in1B, in2B, out1B, clkB, rstB,
             in1C, in2C, out1C, clkC, rstC );
  input in1A,in2A,clkA,rstA;
  output reg out1A;

  input in1B,in2B,clkB,rstB;
  output reg out1B;

  input in1C,in2C,clkC,rstC;
  output reg out1C;

  wire out1Acomb=in1A & in2A;
  wire out1Bcomb=in1B & in2B;
  wire out1Ccomb=in1C & in2C;

  wire out1A_input;
  wire out1B_input;
  wire out1C_input;
  
  majorityVoter #(.WIDTH(1)) mvA ( .inA(out1Acomb), .inB(out1Bcomb), .inC(out1Ccomb), .out(out1A_input));
  majorityVoter #(.WIDTH(1)) mvB ( .inA(out1Acomb), .inB(out1Bcomb), .inC(out1Ccomb), .out(out1B_input));
  majorityVoter #(.WIDTH(1)) mvC ( .inA(out1Acomb), .inB(out1Bcomb), .inC(out1Ccomb), .out(out1C_input));
	  
  always @(posedge clkA or posedge rstA)
  begin
    if (rstA)
      out1A<=1'b0;
    else
      out1A<= out1A_input;
  end

  always @(posedge clkB or posedge rstB)
  begin
    if (rstB)
      out1B<=1'b0;
    else
      out1B<= out1B_input;
  end

  always @(posedge clkC or posedge rstC)
  begin
    if (rstC)
      out1C<=1'b0;
    else
      out1C<= out1C_input;
  end

endmodule


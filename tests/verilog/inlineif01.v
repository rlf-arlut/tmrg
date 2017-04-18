module inlineif;
  reg x;
  reg y;
  reg z;
  wire signal =  x==1'b1 ? y : z;
  
	wire enablePhase = (y & ~x) ? x : (x == 4'h0 || signal == 4'h8);

endmodule

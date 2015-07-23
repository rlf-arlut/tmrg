module inlineif;
  reg x;
  reg y;
  reg z;
  wire signal =  x==1'b1 ? y : z;
endmodule

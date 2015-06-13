module top(i,o);
  // tmrg slicing
 input i;
 output o;
 
 wire [2:1] comb1=~i;
 wire [2:1] comb1Voted=comb1;
 wire comb2=comb1Voted;
endmodule

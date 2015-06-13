module mlogic(input i,output o);
 //tmrg do_not_touch
 assign o=~i;
endmodule

module top(i,o);
  // tmrg slicing
 input i;
 output o;
 
 wire [2:1] comb1=~i;
 wire [2:1] comb1Voted=comb1;
 wire comb2=comb1Voted;
 wire comb2Voted=comb2;
 mlogic m01(.i(comb2Voted),.o(o));
endmodule

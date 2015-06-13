module mlogic(input i,output o);
 //tmrg do_not_touch
 assign o=~i;
endmodule

module top(i,o);
  // tmrg slicing
 input i;
 output o;
 
 wire [2:1] comb1={i,i};
 wire [2:1] comb1Voted=comb1;
 wire [2:1] comb2=comb1Voted;
 wire [2:1] comb2Voted=comb2;
 mlogic m01(.i(comb2Voted[0]),.o(o));
endmodule

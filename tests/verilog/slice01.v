module mlogic(input i,output o);
 //tmrg do_not_touch
 assign o=~i;
endmodule

module slice01(i,o);
  // tmrg slicing
 input i;
 output o;
 
 wire fb;
 wire fbVoted=fb;

 wire [2:1] comb1={i,fbVoted};
 wire [2:1] comb1Voted=comb1;
 wire [2:1] comb2=comb1Voted;
 wire [2:1] comb2Voted=comb2;
 mlogic m01(.i(comb2Voted[0]),.o(fb));
endmodule

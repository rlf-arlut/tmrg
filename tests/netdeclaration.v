
module msigned #(parameter BITS=8, CHANNELS=2) ( x,y,z,y2,tv,k);
  input signed x,z;
  output signed y;
  output signed y2; 
  wire signed  [BITS:0] threshold;
  wire signed  [BITS:0] chn_values [ CHANNELS-1 : 0 ] ;
  wire signed [BITS:0] thresholdVoted= threshold;
  // tmrg do_not_triplicate tv
  output signed  [BITS:0] tv;
  assign tv=threshold;
  // tmrg do_not_triplicate k
  input signed [BITS:0] k;
  wire signed kk=k;
endmodule   

module mtop #(parameter BITS=8, CHANNELS=2) ( input signed x, output signed y,
 input signed z,output signed y2);
 msigned m (.x(x), .y(y),.z(z), .y2(y2));

endmodule   



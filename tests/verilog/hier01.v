module comb01 (in,out);
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

module comb02 (in,out);
  // tmrg do_not_touch
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

/* test 
multi line
comment
// comment
*/
module hier01( 
  input  [7:0] in, 
  output out
  );
  wire tmp;
  comb01 c00( .in( |in ), .out( tmp ) );
  comb02 c01( .in( tmp ), .out( out ) );
endmodule

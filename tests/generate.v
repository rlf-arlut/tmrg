module comb00( 
  input [7:0]  in, 
  output [7:0] out
  );
  assign out=~in;
  // tmrg do_not_triplicate yv
  wire y;
  wire yv;
  assign yv = y;
endmodule

module gen (input [10:0] ii, output [10:0] oo);
genvar i;

generate 
  for(i=0;i<10;i=i+1)
    begin : loop
    comb00 genxx (
    .in(ii[i]),
    .out(oo[i])
  );
 end
endgenerate

    comb00 xx (
    .in(ii[10]),
    .out(oo[10])
  );
endmodule

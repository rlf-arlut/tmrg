module gates( 
  input in1, 
  input in2, 
  output out1,
  output out2
  );
  assign out1=in1&in2;
  assign out2=in1|in2;
endmodule 

// comment
module instantiation1(output y);
  reg in1, in2;
  wire out1,out2,out3,out4;
  gates g1( .in1(in1), .in2(in2), .out1(out1), .out2(out2) );

  gates g2( .in1(in1), .in2(in2), .out1(out3) ),
        g3( .in1(in1), .in2(in2), .out2(out4) ),
        g4( .in1(in1), .in2(in2), .out1(), .out2() );
endmodule

// comment
module instantiation2(input x);
  // tmrg default do_not_triplicate
  reg in1, in2;
  wire out1,out2,out3,out4;
  gates g1( .in1(in1), .in2(in2), .out1(out1), .out2(out2) );

  gates g2( .in1(in1), .in2(in2), .out1(out3) ),
        g3( .in1(in1), .in2(in2), .out2(out4) ),
        g4( .in1(in1), .in2(in2), .out1(), .out2() );
endmodule

module instantiation;
wire x;
instantiation1 i1(.y());
instantiation2 i2(.x(x));

endmodule

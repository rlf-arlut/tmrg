module m1(
  input i1,
  input [1:0] i2,i3,
  output x);
  assign x=|i1 & ^i3;
endmodule

module m2( x,y,z);
  input x,z;
  output y; 
  m1 inst(.i1(x), .i2({2'b10}), .i3({z,x}) , .x(y));
endmodule   

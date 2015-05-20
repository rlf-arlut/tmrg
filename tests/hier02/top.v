module m6(i,o);
input i;
output o;
m4 instM4(.i(i),.o(o));
m5 instM5(.i(i),.o(o));
endmodule

module top(i,o);
input i;
output o;
m1 instM1(.i(i),.o(o));
m2 instM2(.i(i),.o(o));
m5 instM5(.i(i),.o(o));
m4 instM4(.i(i),.o(o));
m6 instM6(.i(i),.o(o));
endmodule

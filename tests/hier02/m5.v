module m5(i,o);
input i;
output o;
m4 instM4(.i(i),.o(o));
m2 instM2(.i(i),.o(o));
endmodule

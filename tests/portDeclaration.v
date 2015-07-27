module a(i1,i2);
input i1;
input i2;
endmodule

module b(input i1,input i2);
endmodule

module c(input i1, i2);
endmodule

module top (input i1,i2);

a ainst(.i1(i1),.i2(i2));
b binst(.i1(i1),.i2(i2));
c cinst(.i1(i1),.i2(i2));
endmodule

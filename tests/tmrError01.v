module ansi (input i1,output o1);
//tmrg tmr_error true
// tmrg do_not_triplicate o1
assign o1=i1;
endmodule

module nonansi (i1,o1);
//tmrg tmr_error true
// tmrg do_not_triplicate o1
input i1;
output o1;
assign o1=i1;
endmodule

module top(input i1,output o1);
ansi a(.i1(i1),.o1(o1));
nonansi na(.i1(i1),.o1(o1));
endmodule

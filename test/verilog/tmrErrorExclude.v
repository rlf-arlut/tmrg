module ansi (input i1,output o1);
//tmrg tmr_error true
wire i1Voted=i1;
assign o1=i1Voted;
endmodule

module nonansi (i1,o1);
//tmrg tmr_error true
input i1;
output o1;
wire i1Voted=i1;
assign o1=i1Voted;
endmodule

module top(input i1,output o1);
// tmrg tmr_error_exclude a
// tmrg tmr_error true
wire o2,o3;
ansi a(.i1(i1),.o1(o2));
nonansi na(.i1(i1),.o1(o3));
assign o1=o3^o2;
endmodule

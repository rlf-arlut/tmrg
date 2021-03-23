module ansi (input i1,output o1);
wire i1Voted=i1;
wire tmrError=0;
assign o1=i1Voted;
endmodule

module nonansi (i1,o1);
input i1;
output o1;
wire i1Voted=i1;
wire tmrError=0;
// tmrg tmr_error true
assign o1=i1Voted;
endmodule

module top(input i1,output o1);
// tmrg tmr_error true
wire tmrError=0;
wire o2,o3;
ansi a(.i1(i1),.o1(o2));
nonansi na(.i1(i1),.o1(o3));
assign o1=o3^o2;
endmodule

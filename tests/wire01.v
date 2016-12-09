module INV(input i,output o);
//tmrg do_not_triplicate i o
endmodule

module wire01;
  wire i=1;
  wire o;
  //tmrg do_not_triplicate i o
  INV I1(.i(1'b0),.o(o));
endmodule


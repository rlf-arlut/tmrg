module buf1(input i, output o);
  // tmrg do_not_touch
  assign o=i;
endmodule

module buf2(input i, output o);
  // tmrg default do_not_triplicate
  assign o=i;
endmodule

module buf3(input i, output o);
  // tmrg default triplicate
  assign o=i;
endmodule

module mtop(input [5:0] in,
            output [5:0] out1,
            output [5:0] out2,
            output [5:0] out3);
  // tmrg do_not_triplicate int ont
  genvar i;
  generate
  for (i=0; i<6;i=i+1)
  begin: loop
    buf1 inst7(.i(in[i]),.o(out1[i]));
    buf2 inst9(.i(in[i]),.o(out2[i]));
    buf3 inst11(.i(),.o(out3[i]));
  end
  endgenerate
endmodule

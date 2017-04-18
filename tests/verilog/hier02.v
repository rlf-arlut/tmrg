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

module mtop(input [5:0] it,output [5:0] ot,
            input [5:0] int,output [5:0] ont);
  
  buf1 inst1(.i(it[0]),.o(ot[0])), inst2(.i(it[3]),.o(ot[3]));
  buf2 inst3(.i(it[1]),.o(ot[1])), inst4(.i(it[4]),.o(ot[4]));
  buf3 inst5(.i(it[2]),.o(ot[2])), inst6(.i(it[5]),.o(ot[5]));

  // tmrg do_not_triplicate int ont
  buf1 inst7(.i(int[0]),.o(ont[0])), inst8(.i(int[3]),.o(ont[3]));
  buf2 inst9(.i(int[1]),.o(ont[1])), inst10(.i(int[4]),.o(ont[4]));
  buf3 inst11(.i(int[2]),.o(ont[2])),inst12(.i(int[5]),.o(ont[5]));


endmodule

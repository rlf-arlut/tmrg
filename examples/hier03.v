module combLogic (in,out);
  // tmrg default do_not_triplicate
  // tmrg triplicate combLogic
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

module hier03 (in,out);
  // tmrg default triplicate
  input in;
  output out;
  combLogic combLogicInst(.in(in),.out(out));
endmodule



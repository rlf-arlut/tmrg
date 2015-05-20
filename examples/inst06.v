module combLogic (in,out);
  // tmrg default triplicate
  input in;
  output out;
  wire combLogic;
  assign combLogic = ~in;
  assign out = combLogic;
endmodule

module inst06 (in,out);
  // tmrg default do_not_triplicate
  input in;
  output out;
  combLogic combLogicInst(.in(in),.out(out));
endmodule



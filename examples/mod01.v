module inverter (I,Z);
  // tmrg default triplicate
  input I;
  output Z;
  assign Z=~I;
endmodule

module mod01 (in,out);
  // tmrg default triplicate
  input in;
  output out;
  inverter inv01(.I(in),.Z(out));
endmodule

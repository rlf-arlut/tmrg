module powerOnReset(z);
  // tmrg do_not_touch
  output z;
endmodule

module resetBlock01 (rstn,rst);
  // tmrg default triplicate
  // tmrg do_not_triplicate rstn
  input rstn;
  output rst;
  wire porRst;
  assign rst=!rstn | porRst;
  powerOnReset por(.z(porRst));
endmodule

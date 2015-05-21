module powerOnReset(z);
  // tmrg do_not_touch
  output z;
endmodule

module resetBlock (rstn,rst,porStatus);
  // tmrg do_not_triplicate rstn
  input rstn;
  output rst;
  output porStatus;
  wire porRst;
  assign porStatus=porRst;
  assign rst=!rstn | porRst;
  powerOnReset por(.z(porRst));
endmodule

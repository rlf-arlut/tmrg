module powerOnReset(z);
  // tmrg default do_not_triplicate
  output z;
endmodule

module resetBlock (rstn,rst,porStatus);
  // tmrg do_not_triplicate rstn
  // tmrg do_not_triplicate porRstA porRstB porRstC
  input rstn;
  output rst;
  output [2:0] porStatus;
  wire porRst;
  wire porRstA=porRst;
  wire porRstB=porRst;
  wire porRstC=porRst;
  assign porStatus={porRstC,porRstB,porRstA};
  assign rst=!rstn | porRst;
  powerOnReset por(.z(porRst));
endmodule

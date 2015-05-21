module powerOnReset(z);
  // tmrg do_not_triplicate rstn
  // tmrg do_not_touch
  output z;
endmodule

module resetBlock (rstn,rst,porStatus);
  // tmrg do_not_triplicate rstn
  input rstn;
  output rst;
  output [2:0] porStatus;
  wire porRst;
  wire porRstVoted=porRst;
  wire porRstA=porRst;
  wire porRstB=porRst;
  wire porRstC=porRst;
  assign porStatus={porRstC,porRstB,porRstA};
  assign rst=!rstn | porRstVoted;
  powerOnReset por(.z(porRst));
endmodule

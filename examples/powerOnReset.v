module resetBlock (rstn,rst);
  input rst;
  output rst;
  wire porRst;
  assign rst=!rst | porRst;
  powerOnReset por(.z(porRst));
endmodule

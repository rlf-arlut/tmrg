module powerOnReset(z);
  output z;
endmodule

module resetBlock (rstn,rst);
  input rstn;
  output rst;
  wire porRst;
  assign rst=!rstn | porRst;
  powerOnReset por(.z(porRst));
endmodule

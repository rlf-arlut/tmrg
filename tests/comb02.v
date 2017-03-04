module comb02( in1,in2, out1);
  input in1,in2;
  output out1;
  assign #1 out1 =  in1+in2;
endmodule


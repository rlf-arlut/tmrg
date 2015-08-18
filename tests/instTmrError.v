module mlogic (I,ZN);
  // tmrg default triplicate
  // tmrg tmr_error true
  input  I,I2;
  output ZN;
  wire IVoted=I;
  wire I2Voted=I2;
  assign ZN=~IVoted;
endmodule

module inst03 (in,out);
  // tmrg default triplicate
  // tmrg tmr_error true  
  input in;
  output out;
  mlogic logic01(.I(in),.ZN(out));
  mlogic logic02(.I(in),.ZN(out));
  mlogic logic03(.I(in),.ZN(out));  
endmodule

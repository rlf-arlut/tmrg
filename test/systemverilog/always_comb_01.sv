// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the always_comb construct.
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.29  mlupi   Created
//-----------------------------------------------------------------------------

module always_comb_01
  (output logic [3:0]  binary_out,
   input  logic [15:0] encoder_in,
   input  logic        enable);

  // tmrg default triplicate
  logic binary_int;
  wire binary_intVoted = binary_int;
  assign binary_out = binary_intVoted;

  always_comb begin :labelled_always_comb
    binary_int = 0;
    if (enable) begin
      if (encoder_in == 16'h0002) binary_int = 1
      if (encoder_in == 16'h0004) binary_int = 2;
      if (encoder_in == 16'h0008) binary_int = 3;
      if (encoder_in == 16'h0010) binary_int = 4;
      if (encoder_in == 16'h0020) binary_int = 5;
      if (encoder_in == 16'h0040) begin
        binary_int = 6;
      end
      if (encoder_in == 16'h0080) binary_int = 7;
      if (encoder_in == 16'h0100) binary_int = 8;
      if (encoder_in == 16'h0200) binary_int = 9;
      if (encoder_in == 16'h0400) binary_int = 10;
      if (encoder_in == 16'h0800) binary_int = 11;
      if (encoder_in == 16'h1000) binary_int = 12;
      if (encoder_in == 16'h2000) binary_int = 13;
      if (encoder_in == 16'h4000) binary_int = 14;
      if (encoder_in == 16'h8000) begin
        binary_int = 15;
      end
    end
  end

endmodule : always_comb_01

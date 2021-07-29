// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the always_comb construct.
// The purpose of the module is purely of testing.
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.29  mlupi   Created
//-----------------------------------------------------------------------------

module always_comb_04
  (output logic [3:0]  binary_out,
   input  logic [15:0] encoder_in,
   input  logic        enable);

  // tmrg default triplicate
  wire encoder_inVoted = encoder_in;

  always_comb begin
    binary_out = 0;
    if (enable)
      if (encoder_in == 16'h0002) begin
        binary_out = 1;
        $display($sformatf("It is a %01d!",binary_out));
      end
      else if (encoder_in == 16'h0004) binary_out = 2;
      else if (encoder_in == 16'h0008) binary_out = 3;
      else if (encoder_in == 16'h0010) binary_out = 4;
      else if (encoder_in == 16'h0020) binary_out = 5;
      else if (encoder_in == 16'h0040) binary_out = 6;
      else if (encoder_in == 16'h0080) binary_out = 7;
      else if (encoder_in == 16'h0100) binary_out = 8;
      else if (encoder_in == 16'h0200) binary_out = 9;
      else if (encoder_in == 16'h0400) binary_out = 10;
      else if (encoder_in == 16'h0800) binary_out = 11;
      else if (encoder_in == 16'h1000) binary_out = 12;
      else if (encoder_in == 16'h2000) binary_out = 13;
      else if (encoder_in == 16'h4000) binary_out = 14;
      else if (encoder_in == 16'h8000) begin
        $warning("That's a warning!");
        binary_out = 15;
      end
      else begin
        binary_out = 0;
        $error("Unreachable case...reached!");
      end
  end
endmodule

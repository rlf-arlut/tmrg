// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the unique casez construct
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.07.28  mlupi   Created
//-----------------------------------------------------------------------------

module decoder_using_unique_casez
  (input       [3:0]  binary_in,
   output reg  [15:0] decoder_out);

  // tmrg default triplicate
  always @(*) begin
    decoder_out = 0;
    unique casez (binary_in)
      4'h0    : decoder_out = 16'h0001;
      4'h1    : decoder_out = 16'h0002;
      4'h2    : decoder_out = 16'h0004;
      4'h3    : decoder_out = 16'h0008;
      4'h4    : decoder_out = 16'h0010;
      4'h5    : decoder_out = 16'h0020;
      4'h6    : decoder_out = 16'h0040;
      4'h7    : decoder_out = 16'h0080;
      4'b1??? : decoder_out = 16'h0100;
    endcase
  end

endmodule

// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the assignment operators in Systemverilog
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.08.09  mlupi   Created
//-----------------------------------------------------------------------------

module assignment_operator
  (input logic c,
   input logic r,
   output logic [31:0] a);

  always_ff @(posedge clk) begin
    if(rst)
      a = '10;
    else begin
      a += 2;
      a -= 2;
      a *= 2;
      a /= 2;
      a %= 17;
      a &= 16'hFFFF;
      a |= 16'hFFFF;
      a ^= 16'hAAAA;
      a <<= 6;
      a >>= 6;
      a <<<= 14;
      a >>>= 14;
    end
  end
endmodule

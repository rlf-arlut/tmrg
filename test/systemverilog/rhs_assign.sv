// Author        : Matteo Lupi  <matteo.lupi@cern.ch>
//-----------------------------------------------------------------------------
// Description :
// This module is designed to target the '0 construct on the RSH of an assignment
//-----------------------------------------------------------------------------
// Date        Author  Note
// 2021.08.04  mlupi   Created
//-----------------------------------------------------------------------------

module rhs_assign
  (input logic  clk,
   input logic  rst_b,
   input logic  load,
   input logic  d,
   output logic q
   );

  always_ff @(posedge clk)
    if (!rst_b) begin
      q <= '0;
    end else if (load) begin
      q <= d;
    end

endmodule
